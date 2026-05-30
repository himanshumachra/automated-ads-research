"""
Automation Engine — 5-phase full session orchestrator (Expert Mode).

Phase 1: Organic warmup trail
Phase 2: Navigate to target
Phase 3: Fast page overview (expert scroll-scan)
Phase 4: Persona-driven deep reading + button interaction (60% click rate)
Phase 5: Ad detection, click, post-click engagement

Expert skill level is randomly 6-10/10 per session.
"""

import asyncio
import random
import time

from user_persona import generate_random_persona, persona_to_behavior_config
from website_visitor import WebsiteVisitor
from config import (
    TARGET_DWELL_RANGE, AD_CLICK_DELAY_RANGE,
    MAX_AD_CLICKS_RANGE, POST_CLICK_DWELL_RANGE,
)


class AutomationSession:
    """Orchestrates one full automated browsing + ad-click session (Expert Mode)."""

    def __init__(self, session_id: str, browser_session, log_fn=print):
        self.sid      = session_id
        self.bs       = browser_session          # BrowserSession
        self.log      = log_fn
        self.persona  = generate_random_persona()
        self.behavior = persona_to_behavior_config(self.persona)
        self.visitor  = None
        self.stats    = {
            "pre_visits": 0,
            "ads_clicked": 0,
            "pages": 0,
            "buttons_clicked": 0,
            "errors": 0,
        }
        self._stop    = False

    def cancel(self):
        self._stop = True

    async def run_full_session(self, target_url: str, config: dict = None) -> dict:
        config  = config or {}
        results = {"session_id": self.sid, "success": False, "stats": self.stats}

        skill   = self.persona.skill_level
        self.log(
            f"[👤] Expert Persona: Age {self.persona.age} | Skill {skill}/10 "
            f"| Style: {self.persona.browsing_style} | WPM: {self.persona.typing_speed_wpm}"
        )

        # Attach behavior profile to human engine
        self.bs.human.profile = self.behavior

        self.visitor = WebsiteVisitor(
            self.bs.page, self.bs.human, self.behavior, self.log
        )

        try:
            # ── PHASE 1: Organic warmup trail ─────────────────────────────
            if config.get("enable_pre_visits", True) and not self._stop:
                self.log("[Phase 1] Building organic browsing trail...")
                await self.visitor.create_organic_trail(target_url)
                self.stats["pre_visits"] = len(self.visitor.visit_history)
                self.log(f"[Phase 1] ✓ Visited {self.stats['pre_visits']} warmup sites")

            if self._stop:
                return results

            # ── PHASE 2: Navigate to target ───────────────────────────────
            self.log(f"[Phase 2] Navigating to target: {target_url}")
            ok = await self.bs.navigate(target_url)
            if not ok:
                results["error"] = "Target navigation failed"
                return results
            self.stats["pages"] += 1

            # Brief landing pause — expert scans URL/title first
            await asyncio.sleep(random.uniform(0.6, 1.8))

            # ── PHASE 3: Fast page overview (expert scroll-scan) ──────────
            self.log("[Phase 3] Fast overview scroll — scanning page layout...")
            await self.bs.human.fast_overview_scroll()
            self.log("[Phase 3] ✓ Overview complete. Returning to top.")

            if self._stop:
                return results

            # Brief re-orientation pause after returning to top
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # ── PHASE 4: Deep reading + button interaction ─────────────────
            dwell = random.uniform(*TARGET_DWELL_RANGE)
            dwell *= self.behavior.get("page_dwell_mult", 1.0)
            dwell  = min(dwell, 90)
            self.log(f"[Phase 4] Reading page for {dwell:.0f}s + button scan...")

            # Run reading and button scan concurrently (split time)
            read_time   = dwell * 0.55    # 55% of dwell on reading
            button_time = dwell * 0.45    # 45% on interactive elements

            await self._persona_read(read_time)

            if not self._stop:
                # Expert behavior: scan visible interactive elements and click 60%
                self.log("[Phase 4] Scanning clickable elements...")
                # Determine max clicks based on persona skill (higher skill = more exploration)
                max_btn_clicks = skill - 2   # skill 6→4, 7→5, 8→6, 9→7, 10→8
                clicked = await self.bs.human.scan_and_click_buttons(
                    click_rate=0.60,
                    max_clicks=max_btn_clicks,
                    safe_only=True
                )
                self.stats["buttons_clicked"] += clicked
                self.log(f"[Phase 4] ✓ Interacted with {clicked} clickable element(s)")

                # Brief post-interaction read
                await self._persona_read(button_time * 0.4)

            if self._stop:
                return results

            # ── PHASE 5: Ad interaction ────────────────────────────────────
            max_clicks  = random.randint(*MAX_AD_CLICKS_RANGE)
            if config.get("max_ad_clicks"):
                max_clicks = min(max_clicks, int(config["max_ad_clicks"]))
            popup_mode  = config.get("popup_mode", False)

            self.log(f"[Phase 5] Looking for ads (max {max_clicks} clicks)...")

            for i in range(max_clicks):
                if self._stop:
                    break

                # Pre-click delay (organic, shorter for experts)
                delay = random.uniform(*AD_CLICK_DELAY_RANGE)
                delay *= self.behavior.get("page_dwell_mult", 1.0)
                # Expert: scale delay down slightly (they find things faster)
                delay *= max(0.6, 1.0 - (skill - 6) * 0.06)
                await asyncio.sleep(min(delay, 22))

                # Try to click ad
                clicked = await self.bs.human.find_and_click_ad(popup_mode)

                if clicked:
                    self.stats["ads_clicked"] += 1
                    self.log(f"[✓] Ad click #{self.stats['ads_clicked']} — waiting on landing page...")

                    # Post-click dwell on landing page (experts engage briefly)
                    post_dwell = random.uniform(*POST_CLICK_DWELL_RANGE)
                    await self._persona_read(post_dwell)

                    # Sometimes go back (natural behavior)
                    if random.random() < self.behavior.get("back_button_chance", 0.35):
                        try:
                            await self.bs.page.go_back()
                            await asyncio.sleep(random.uniform(1.0, 3.0))
                        except Exception:
                            pass
                else:
                    self.log(f"[!] No ad found on attempt {i+1}")

                # Random micro-interaction between attempts
                if random.random() < 0.40:
                    await self.bs.human.random_interaction()

            results["success"] = True
            results["stats"]   = self.stats

        except Exception as e:
            self.stats["errors"] += 1
            results["error"] = str(e)
            self.log(f"[✗] Session error: {e}")

        return results

    async def _persona_read(self, duration: float):
        """
        Persona-flavored page reading for `duration` seconds.
        Expert: more scroll/hover, less idle pause, faster rhythm.
        """
        t0 = time.time()
        while time.time() - t0 < duration and not self._stop:
            left = duration - (time.time() - t0)
            if left < 0.5:
                break

            # Expert weighting: more scroll+hover, less pause, almost no distraction
            action = random.choices(
                ["scroll",  "mouse",  "pause", "wiggle", "hover",  "distract"],
                weights=[0.38,    0.20,   0.18,    0.08,    0.14,     0.02]
            )[0]

            try:
                if action == "scroll":
                    cmin, cmax = self.behavior.get("scroll_chunk_range", (100, 280))
                    dir_ = 1 if random.random() < 0.82 else -1
                    # Expert: larger scroll amounts, smoother
                    steps = random.randint(2, 5)
                    total = random.uniform(cmin, cmax) * dir_
                    for _ in range(steps):
                        await self.bs.page.mouse.wheel(0, total / steps)
                        await asyncio.sleep(random.uniform(0.01, 0.04))
                    await asyncio.sleep(random.uniform(0.15, 0.7))

                elif action == "mouse":
                    vp = await self.bs.page.evaluate("()=>({w:window.innerWidth,h:window.innerHeight})")
                    await self.bs.human.move_to(
                        random.uniform(40, vp.get("w", 1920) - 40),
                        random.uniform(40, vp.get("h", 1080) - 40)
                    )

                elif action == "pause":
                    rmin, rmax = self.behavior.get("scroll_reading_pause_range", (0.5, 2.5))
                    await asyncio.sleep(random.uniform(rmin, rmax))

                elif action == "wiggle":
                    for _ in range(random.randint(1, 3)):
                        await self.bs.page.mouse.move(
                            self.bs.human._last_x + random.gauss(0, 7),
                            self.bs.human._last_y + random.gauss(0, 7)
                        )
                        await asyncio.sleep(random.uniform(0.02, 0.07))

                elif action == "hover":
                    # Expert: hover purposefully on links/buttons
                    els = await self.bs.page.query_selector_all("a, button, [role='button']")
                    if els:
                        el  = random.choice(els[:20])
                        box = await el.bounding_box()
                        if box:
                            await self.bs.human.move_to(
                                box["x"] + box["width"] / 2,
                                box["y"] + box["height"] / 2
                            )
                            await asyncio.sleep(random.uniform(0.15, 0.7))

                elif action == "distract":
                    # Experts get distracted very rarely, very briefly
                    dmin, dmax = self.behavior.get("distraction_pause_range", (0.5, 2.5))
                    await asyncio.sleep(random.uniform(dmin, dmax))

            except Exception:
                await asyncio.sleep(0.2)
