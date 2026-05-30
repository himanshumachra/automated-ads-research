import asyncio
import threading
from playwright.async_api import async_playwright

# Optional import for human-like behavior utilities
try:
    from human_behavior import HumanBehavior
except Exception:
    HumanBehavior = None

class RealisticBrowser:
    """Launches a Chromium instance that behaves like a real user.
    It uses optional human_behavior utilities to move the mouse, type with realistic delays,
    and click with proper event ordering.
    """
    def __init__(self, url: str, config: dict, log_callback=None):
        self.url = url
        self.config = config
        self.log = log_callback or (lambda msg: print(msg))
        self._playwright = None
        self._browser = None
        self._page = None
        self._thread = None
        self._hb = HumanBehavior() if HumanBehavior else None

    def _log(self, msg: str):
        self.log(f"[Browser] {msg}")

    def start(self):
        """Start the browser in a background thread (non‑blocking for the GUI)."""
        self._thread = threading.Thread(target=self._run_async, daemon=True)
        self._thread.start()
        self._log("Browser thread started")

    def _run_async(self):
        asyncio.run(self._launch())

    async def _launch(self):
        self._log("Launching Chromium (headful) with stealth options")
        async with async_playwright() as p:
            self._playwright = p
            self._browser = await p.chromium.launch(headless=False, slow_mo=self.config.get('slow_mo', 50))
            context = await self._browser.new_context()
            # apply stealth if available
            try:
                from playwright_stealth import stealth_async
                await stealth_async(context)
                self._log("Stealth applied")
            except Exception as e:
                self._log(f"Stealth not applied: {e}")
            self._page = await context.new_page()
            await self._page.goto(self.url)
            self._log(f"Navigated to {self.url}")
            # keep alive until closed externally
            await self._page.wait_for_event("close")
            self._log("Browser window closed")
            await self._browser.close()
            self._log("Browser shut down")

    async def click(self, selector: str):
        """Perform a realistic click on the given selector."""
        if self._hb:
            await self._hb.move_to(self._page, selector)
            await self._hb.random_delay(100, 300)
        await self._page.click(selector)
        self._log(f"Clicked {selector}")

    async def type_text(self, selector: str, text: str):
        """Type text into an input field with human‑like delays."""
        if self._hb:
            await self._hb.move_to(self._page, selector)
            await self._hb.random_delay(100, 300)
        await self._page.fill(selector, "")
        await self._page.type(selector, text, delay=self.config.get('type_delay', 100))
        self._log(f"Typed text into {selector}")

    def stop(self):
        """Close the browser if it is still running."""
        if self._page:
            asyncio.run(self._page.close())
        if self._browser:
            asyncio.run(self._browser.close())
        self._log("Stop requested")
}
