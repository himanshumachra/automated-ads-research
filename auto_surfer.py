"""
Auto Surfer — scheduled background surfing engine.
Runs independently of manual sessions: continuously opens browser sessions
to random warmup sites on a configurable delay schedule.
Proxy and fingerprint are rotated automatically per run.
"""

import threading
import random
import time
import asyncio
from typing import Callable, Optional

from config import (
    WARMUP_WEBSITES, SURFER_MIN_DELAY_SEC,
    SURFER_MAX_DELAY_SEC, SURFER_MAX_PAGES_PER_RUN,
    BROWSER_MAX_CONCURRENT,
)


class AutoSurfer:
    """
    Schedules and runs automatic background surfing sessions.
    Each run uses a fresh proxy + fingerprint (via BrowserEngine).
    """

    def __init__(self, browser_engine, log_fn: Callable = print):
        self.engine       = browser_engine
        self.log          = log_fn
        self._running     = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event  = threading.Event()

        # Configurable settings (can be updated from GUI)
        self.min_delay    = SURFER_MIN_DELAY_SEC
        self.max_delay    = SURFER_MAX_DELAY_SEC
        self.pages_per_run= SURFER_MAX_PAGES_PER_RUN
        self.use_proxy    = True
        self.target_url   = ""          # if set, include target in surf run
        self.total_runs   = 0
        self.total_pages  = 0

    # ── Control ───────────────────────────────────────────────────────────────
    def start(self):
        if self._running:
            return
        self._running    = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.log("[🤖 AutoSurfer] Started")

    def stop(self):
        self._running = False
        self._stop_event.set()
        self.log("[🤖 AutoSurfer] Stopping...")

    def is_running(self) -> bool:
        return self._running

    # ── Main loop ─────────────────────────────────────────────────────────────
    def _loop(self):
        while self._running and not self._stop_event.is_set():
            try:
                self._do_run()
                self.total_runs += 1
            except Exception as e:
                self.log(f"[🤖 AutoSurfer] Run error: {e}")

            if self._stop_event.is_set():
                break

            delay = random.uniform(self.min_delay, self.max_delay)
            self.log(f"[🤖 AutoSurfer] Next run in {delay:.0f}s "
                     f"(total runs: {self.total_runs})")
            self._stop_event.wait(timeout=delay)

        self._running = False
        self.log("[🤖 AutoSurfer] Stopped")

    def _do_run(self):
        """Execute one surf run: visit N random sites."""
        n_pages = random.randint(1, self.pages_per_run)
        sites   = random.sample(WARMUP_WEBSITES, k=min(n_pages, len(WARMUP_WEBSITES)))

        # Optionally append the target URL
        if self.target_url:
            sites.append(self.target_url)

        self.log(f"[🤖 AutoSurfer] Run #{self.total_runs + 1} — "
                 f"visiting {len(sites)} pages")

        # Build a quick surfing config
        config = {
            "use_proxy":          self.use_proxy,
            "enable_pre_visits":  False,   # auto-surfer doesn't do pre-visits
            "match_proxy_country": True,
            "max_ad_clicks":      0 if not self.target_url else 2,
            "popup_mode":         False,
            "max_concurrent":     BROWSER_MAX_CONCURRENT,
            "is_running_callback": lambda: self._running,
        }

        # Use target if set, else use first warmup site as "target"
        # The engine does warmup internally but we skip it here to keep it clean
        primary = self.target_url if self.target_url else sites[0]
        sid     = self.engine.create_session(primary, config)
        if sid:
            self.total_pages += len(sites)
            self.log(f"[🤖 AutoSurfer] Session {sid[:8]} launched")
        else:
            self.log("[🤖 AutoSurfer] Could not create session (no FP/proxy?)")

    # ── Stats ─────────────────────────────────────────────────────────────────
    @property
    def stats(self) -> dict:
        return {
            "running":     self._running,
            "total_runs":  self.total_runs,
            "total_pages": self.total_pages,
            "min_delay":   self.min_delay,
            "max_delay":   self.max_delay,
        }
