"""
Browser Engine — Playwright-based stealth browser session.
Each session is fully isolated: unique fingerprint, dedicated proxy (1-use),
all stealth scripts injected before page load, route handler for header cleanup.
"""

import asyncio
import random
import time
import uuid
import threading
from typing import Optional, Callable, Dict, List

from stealth_injector import get_stealth_script
from tls_spoofer import get_tls_profile, get_sec_ch_ua, get_header_order, get_network_profile
from human_behavior import HumanBehaviorEngine
from proxy_manager import ProxyManager, Proxy
from fingerprint_manager import FingerprintManager
from config import BROWSER_MAX_CONCURRENT


# ── Country → approximate geolocation ────────────────────────────────────────
_GEO = {
    "US": (37.09, -95.71), "GB": (51.50, -0.12), "DE": (52.52, 13.40),
    "FR": (48.85,  2.35),  "IN": (20.59, 78.96), "JP": (35.67,139.65),
    "CA": (43.65, -79.38), "AU": (-33.86,151.20), "BR": (-15.78,-47.92),
    "CN": (39.90, 116.40), "SG": ( 1.35, 103.81), "AE": (25.20,  55.27),
    "MX": (19.43, -99.13), "KR": (37.56, 126.97), "NL": (52.37,   4.89),
    "SE": (59.33,  18.06), "PL": (52.22,  21.01), "ZA": (-26.20,  28.04),
    "NZ": (-36.86, 174.76),"IT": (41.90,  12.49), "ES": (40.41,  -3.70),
}


class BrowserSession:
    """One isolated stealth browser session."""

    def __init__(self, session_id: str, fingerprint: dict,
                 proxy: Optional[Proxy], log_fn: Callable = print):
        self.session_id  = session_id
        self.fingerprint = fingerprint
        self.proxy       = proxy
        self.log         = log_fn
        self.browser     = None
        self.context     = None
        self.page        = None
        self.human: Optional[HumanBehaviorEngine] = None
        self._pw         = None
        self._net        = get_network_profile()
        self.stats       = {"pages": 0, "ads_clicked": 0, "start": time.time()}

    # ── Launch ────────────────────────────────────────────────────────────────
    async def start(self) -> bool:
        try:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()

            fp     = self.fingerprint
            screen = fp.get("screen", {})
            sw     = screen.get("width",  1920)
            sh     = screen.get("height", 1080)
            lang   = fp.get("language",  "en-US")
            browser_name = fp.get("browser", "Chrome")

            # ── Launch args (maximum anti-detect) ────────────────────────────
            args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions-except=",
                "--disable-plugins-discovery",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-ipc-flooding-protection",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-breakpad",
                "--disable-features=TranslateUI,IsolateOrigins,"
                    "ImprovedCookieControls,LazyFrameLoading,"
                    "GlobalMediaControls,DestroyProfileOnBrowserClose,"
                    "MediaRouter,DialMediaRouteProvider",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--metrics-recording-only",
                "--password-store=basic",
                "--use-mock-keychain",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--allow-running-insecure-content",
                f"--lang={lang}",
                f"--window-size={sw},{sh}",
                "--window-position=0,0",
                "--force-device-scale-factor=" + str(screen.get("pixel_ratio", 1.0)),
            ]

            # Add touch args for mobile fingerprints
            if fp.get("max_touch_points", 0) > 0:
                args += ["--enable-touchpad-four-finger-swipe",
                         "--touch-events=enabled"]

            self.browser = await self._pw.chromium.launch(
                headless=False,
                args=args,
                ignore_default_args=["--enable-automation"],
            )

            # ── Context (fully isolated) ──────────────────────────────────────
            ctx_opts = {
                "viewport":          {"width": sw, "height": sh},
                "user_agent":        fp.get("user_agent", ""),
                "locale":            lang,
                "timezone_id":       fp.get("timezone", "America/New_York"),
                "color_scheme":      "light",
                "device_scale_factor": screen.get("pixel_ratio", 1.0),
                "is_mobile":         fp.get("max_touch_points", 0) > 0,
                "has_touch":         fp.get("max_touch_points", 0) > 0,
                "java_script_enabled": True,
                "permissions":       [],
                "geolocation":       self._geolocation(),
                "extra_http_headers": self._extra_headers(),
                "ignore_https_errors": True,
            }
            if self.proxy:
                ctx_opts["proxy"] = self.proxy.playwright_proxy

            self.context = await self.browser.new_context(**ctx_opts)

            # ── Inject stealth script into every new page ─────────────────────
            stealth_js = get_stealth_script(fp, self.session_id)
            await self.context.add_init_script(stealth_js)

            # ── Route handler — strip automation traces from requests ──────────
            await self.context.route("**/*", self._route_handler)

            # ── Open first page ───────────────────────────────────────────────
            self.page  = await self.context.new_page()
            self.human = HumanBehaviorEngine(self.page, {})

            # Belt-and-suspenders webdriver removal
            await self.page.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
                "delete navigator.__proto__.webdriver;"
            )

            self.log(f"[✓] Session {self.session_id[:8]} | FP:{fp.get('id')} | "
                     f"OS:{fp.get('os','')} | Browser:{fp.get('browser','')} | "
                     f"Proxy:{self.proxy.host if self.proxy else 'none'}")
            return True

        except Exception as e:
            self.log(f"[✗] Session start failed: {e}")
            return False

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _geolocation(self) -> dict:
        country = self.fingerprint.get("country", "US")
        lat, lon = _GEO.get(country, (37.09, -95.71))
        return {
            "latitude":  lat + random.uniform(-0.5, 0.5),
            "longitude": lon + random.uniform(-0.5, 0.5),
            "accuracy":  random.uniform(15, 80),
        }

    def _extra_headers(self) -> dict:
        fp   = self.fingerprint
        lang = fp.get("language", "en-US")
        lc   = lang.split("-")[0]
        browser = fp.get("browser", "Chrome")
        version = fp.get("browser_version", "124.0.0.0")
        ch_ua = get_sec_ch_ua(browser, version)
        headers = {
            "Accept-Language":          f"{lang},{lc};q=0.9,en;q=0.8",
            "Accept":                   "text/html,application/xhtml+xml,application/xml;q=0.9,"
                                        "image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":          "gzip, deflate, br",
            "Upgrade-Insecure-Requests":"1",
            "Cache-Control":            "max-age=0",
            "Sec-Fetch-Dest":           "document",
            "Sec-Fetch-Mode":           "navigate",
            "Sec-Fetch-Site":           "none",
            "Sec-Fetch-User":           "?1",
        }
        headers.update(ch_ua)
        return headers

    async def _route_handler(self, route):
        """Clean up automation-revealing headers from every request."""
        req  = route.request
        hdrs = dict(req.headers)
        # Strip known automation headers
        for h in ["x-devtools-emulate-network-conditions-client-id",
                  "x-client-data", "x-forwarded-for"]:
            hdrs.pop(h, None)
        # Simulate realistic network delay (RTT jitter)
        jitter_ms = self._net["base_rtt"] * random.uniform(0.8, 1.2)
        await asyncio.sleep(jitter_ms / 1000.0 * 0.1)   # small fraction
        await route.continue_(headers=hdrs)

    # ── Navigation ────────────────────────────────────────────────────────────
    async def navigate(self, url: str, wait_for: str = "domcontentloaded") -> bool:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            self.log(f"[→] {url}")
            await asyncio.sleep(random.uniform(0.4, 1.8))
            resp = await self.page.goto(url, wait_until=wait_for, timeout=32000)
            if resp and resp.status >= 400:
                self.log(f"[!] HTTP {resp.status}")
                return False
            await asyncio.sleep(random.uniform(0.8, 2.5))
            self.stats["pages"] += 1
            return True
        except Exception as e:
            self.log(f"[✗] Nav error: {e}")
            return False

    # ── Close ─────────────────────────────────────────────────────────────────
    async def close(self):
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                await self.browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                await self._pw.stop()
        except Exception:
            pass


# ── Browser Engine (session factory) ──────────────────────────────────────────
class BrowserEngine:
    """Creates and manages multiple isolated browser sessions."""

    def __init__(self, log_callback: Callable = None):
        self.log          = log_callback or print
        self.fp_manager   = FingerprintManager()
        self.proxy_manager= ProxyManager()
        self._sessions: Dict[str, BrowserSession] = {}
        self._lock        = threading.Lock()

    def create_session(self, url: str, config: dict = None) -> str:
        config = config or {}

        # Concurrency limit enforcement (not more than 5 windows at a time)
        max_concurrent = config.get("max_concurrent", BROWSER_MAX_CONCURRENT)
        is_running = config.get("is_running_callback", lambda: True)

        while True:
            if not is_running():
                self.log("[ℹ] Session launch aborted (automation stopped)")
                return ""
            with self._lock:
                current_count = len(self._sessions)
            if current_count < max_concurrent:
                break
            self.log(f"[⏳] Active windows limit reached ({current_count}/{max_concurrent} running). Waiting for a window to close...")
            time.sleep(2)

        # Determine if we need a proxy
        proxy = None
        proxy_country = ""
        if config.get("use_proxy", True):
            # Acquire proxy first to know its country
            session_id_temp = str(uuid.uuid4())
            # If we want to match fingerprint to proxy country, pass '' now; we'll filter later
            proxy = self.proxy_manager.acquire_proxy(session_id_temp, "")
            if not proxy:
                self.log("[!] No fresh proxy available for this session")
            else:
                proxy_country = proxy.country.upper() if proxy.country else ""
        # Acquire fingerprint, strictly restricting to USA, Canada, and Australia (US, CA, AU)
        if proxy_country in {"US", "CA", "AU"}:
            allowed = [proxy_country]
            target_cc = proxy_country
        else:
            allowed = ["US", "CA", "AU"]
            target_cc = ""
        fp = self.fp_manager.acquire(country=target_cc, allowed_countries=allowed)
        if not fp:
            self.log("[!] No fingerprints available — generate the library first!")
            # Release the proxy if we fetched one but no fingerprint
            if proxy:
                self.proxy_manager.release_proxy(proxy.id, success=False)
            return ""
        fp_country = fp.get("country", "")
        # If we have a proxy but its country didn't match fingerprint, release it (only if proxy country is in our target set)
        if config.get("match_proxy_country", True) and proxy and proxy_country and proxy_country in {"US", "CA", "AU"} and proxy_country != fp_country:
            self.log(f"[!] Proxy country {proxy_country} mismatch fingerprint country {fp_country}, releasing proxy")
            self.proxy_manager.release_proxy(proxy.id, success=False)
            proxy = None
        sid = str(uuid.uuid4())
        session = BrowserSession(sid, fp, proxy, self.log)

        with self._lock:
            self._sessions[sid] = session

        # Run in its own event loop thread
        thread = threading.Thread(
            target=self._run_thread,
            args=(session, url, config),
            daemon=True,
        )
        thread.start()
        return sid

    def _run_thread(self, session: BrowserSession, url: str, config: dict):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._run_session(session, url, config))
        finally:
            loop.close()

    async def _run_session(self, session: BrowserSession, url: str, config: dict):
        from automation_engine import AutomationSession
        started = await session.start()
        if not started:
            self._cleanup(session)
            return
        try:
            auto    = AutomationSession(session.session_id, session, self.log)
            results = await auto.run_full_session(url, config)
            self.log(f"[✓] Session {session.session_id[:8]} done | "
                     f"ads={results['stats']['ads_clicked']} "
                     f"pages={results['stats']['pages']}")
        except Exception as e:
            self.log(f"[✗] Session error: {e}")
        finally:
            await session.close()
            self._cleanup(session)

    def _cleanup(self, session: BrowserSession):
        """Release fingerprint and proxy after session ends."""
        self.fp_manager.release(session.fingerprint["id"], mark_used=True)
        if session.proxy:
            self.proxy_manager.release_proxy(
                session.proxy.id, success=True
            )
        with self._lock:
            self._sessions.pop(session.session_id, None)

    @property
    def active_count(self) -> int:
        return len(self._sessions)
