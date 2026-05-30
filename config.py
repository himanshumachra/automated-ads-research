"""
Central Configuration — all paths, constants, behavior ranges, site pools.
Single source of truth for the entire PhantomBrowser Pro system.
"""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
FINGERPRINTS_DIR  = os.path.join(BASE_DIR, "fingerprints")
PROXIES_DIR       = os.path.join(BASE_DIR, "proxies")
LOGS_DIR          = os.path.join(BASE_DIR, "logs")
SESSIONS_DIR      = os.path.join(BASE_DIR, "sessions")
DATA_DIR          = os.path.join(BASE_DIR, "data")

for _d in [FINGERPRINTS_DIR, PROXIES_DIR, LOGS_DIR, SESSIONS_DIR, DATA_DIR]:
    os.makedirs(_d, exist_ok=True)

# ── Fingerprint Library ───────────────────────────────────────────────────────
FP_LIBRARY_SIZE   = 10000
FP_LIBRARY_FILE   = os.path.join(FINGERPRINTS_DIR, "fp_library_full.json")
FP_STATE_FILE     = os.path.join(FINGERPRINTS_DIR, "fp_state.json")

# ── Proxy ─────────────────────────────────────────────────────────────────────
PROXY_TIMEOUT_MS       = 10000
PROXY_MAX_FAILURES     = 3
PROXY_SWITCH_AFTER_CLICKS = 1   # 1 proxy per session, switched on close

# ── Browser Engine ────────────────────────────────────────────────────────────
BROWSER_HEADLESS        = False
BROWSER_TIMEOUT_MS      = 30000
BROWSER_MAX_CONCURRENT  = 5

# ── Human Behavior Ranges ─────────────────────────────────────────────────────
MOUSE_SPEED_RANGE        = (0.3, 2.0)
CLICK_DELAY_RANGE        = (0.5, 4.0)
SCROLL_PAUSE_RANGE       = (0.3, 5.0)
TYPING_WPM_RANGE         = (15, 90)
MISTAKE_RATE_RANGE       = (0.0, 0.15)
PAGE_READ_TIME_RANGE     = (5.0, 60.0)
IDLE_RANGE               = (0.5, 10.0)

# ── Automation Session ────────────────────────────────────────────────────────
PRE_VISIT_SITES_RANGE    = (1, 5)
PRE_VISIT_DWELL_RANGE    = (8, 40)
TARGET_DWELL_RANGE       = (15, 75)
AD_CLICK_DELAY_RANGE     = (3, 18)
MAX_AD_CLICKS_RANGE      = (1, 4)
POST_CLICK_DWELL_RANGE   = (8, 35)

# ── Auto-Surfer ───────────────────────────────────────────────────────────────
SURFER_MIN_DELAY_SEC     = 30    # minimum seconds between surf sessions
SURFER_MAX_DELAY_SEC     = 300   # maximum seconds between surf sessions
SURFER_MAX_PAGES_PER_RUN = 5     # pages visited per surf run

# ── Persona ───────────────────────────────────────────────────────────────────
PERSONA_AGE_RANGE        = (13, 82)
PERSONA_SKILL_RANGE      = (2, 10)

# ── Warmup / Pre-visit Website Pool ──────────────────────────────────────────
WARMUP_WEBSITES = [
    "https://www.google.com",        "https://www.youtube.com",
    "https://www.facebook.com",      "https://www.twitter.com",
    "https://www.instagram.com",     "https://www.reddit.com",
    "https://www.wikipedia.org",     "https://www.amazon.com",
    "https://www.ebay.com",          "https://www.linkedin.com",
    "https://www.pinterest.com",     "https://www.quora.com",
    "https://www.imdb.com",          "https://www.stackoverflow.com",
    "https://www.github.com",        "https://www.medium.com",
    "https://www.bbc.com",           "https://www.cnn.com",
    "https://www.nytimes.com",       "https://news.ycombinator.com",
    "https://www.weather.com",       "https://www.espn.com",
    "https://www.walmart.com",       "https://www.target.com",
    "https://www.etsy.com",          "https://www.twitch.tv",
    "https://www.spotify.com",       "https://www.netflix.com",
    "https://www.yahoo.com",         "https://www.bing.com",
    "https://www.cnet.com",          "https://www.techcrunch.com",
    "https://www.theverge.com",      "https://www.wired.com",
    "https://www.forbes.com",        "https://www.businessinsider.com",
    "https://www.msn.com",           "https://www.duckduckgo.com",
    "https://www.craigslist.org",    "https://www.zillow.com",
    "https://www.indeed.com",        "https://www.glassdoor.com",
    "https://www.yelp.com",          "https://www.tripadvisor.com",
]

# ── Search Engines ────────────────────────────────────────────────────────────
SEARCH_ENGINES = [
    "https://www.google.com/search?q=",
    "https://www.bing.com/search?q=",
    "https://duckduckgo.com/?q=",
    "https://search.yahoo.com/search?p=",
]

# ── Search Terms Pool ─────────────────────────────────────────────────────────
SEARCH_TERMS = [
    "best deals online", "how to make money online", "free games to play",
    "weather today", "latest news headlines", "funny cat videos",
    "cheap flights to europe", "online shopping discount codes",
    "work from home jobs", "best smartphones 2024", "movie reviews 2024",
    "easy cooking recipes", "home workout routine", "learn python programming",
    "best travel destinations", "car insurance quotes compare",
    "credit card cashback rewards", "pet care advice dogs",
    "home improvement tips", "lose weight fast", "stock market today",
    "dating advice for men", "parenting tips toddlers", "best tech reviews",
    "streaming services comparison", "electric car best buy",
    "solar panels cost", "cryptocurrency news", "real estate investment",
    "healthy breakfast ideas", "meditation for beginners",
    "best running shoes", "gaming laptop review", "cloud storage free",
    "vpn service review", "online course free", "freelance jobs website",
]

# ── GUI Settings ──────────────────────────────────────────────────────────────
GUI_TITLE        = "PhantomBrowser Pro — Anti-Detect Engine"
GUI_WIDTH        = 1300
GUI_HEIGHT       = 860
GUI_THEME_BG     = "#0a0e17"
GUI_THEME_FG     = "#c9d1d9"
GUI_THEME_ACCENT = "#58a6ff"
GUI_THEME_SUCCESS= "#3fb950"
GUI_THEME_WARNING= "#d29922"
GUI_THEME_DANGER = "#f85149"
GUI_THEME_SURFACE= "#141b27"
GUI_THEME_BORDER = "#21262d"
GUI_FONT_FAMILY  = "Segoe UI"
GUI_FONT_SIZE    = 10
GUI_MONO_FONT    = "Consolas"
