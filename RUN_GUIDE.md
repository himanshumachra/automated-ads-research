# PhantomBrowser Pro — Run Guide

## Quick Start

```
Step 1:  Double-click install_deps.py   (installs packages)
Step 2:  Double-click launch.bat        (starts the app)
```

Or from terminal:
```bash
cd "C:\Users\himanshu\Desktop\browser to automate"
pip install playwright aiohttp
python -m playwright install chromium
python main_gui.py
```

---

## First-Time Setup (do this once)

### 1. Generate Fingerprint Library
- Open the app → go to **🔒 Fingerprints** tab
- Click **🏗 Generate 10K Library**
- Wait ~30 seconds — creates 10,000 unique device profiles
- Status bar will show "Fingerprints: 10000"

### 2. Load Your Proxies
- Go to **🌐 Proxies** tab
- **Option A — Paste directly:**
  Paste your proxy list into the text box, then click **📥 Import**
- **Option B — Load from file:**
  Click **📂 Load File** → select your `.txt` proxy file

**Supported proxy formats (one per line):**
```
host:port
host:port:username:password
username:password@host:port
http://host:port
https://user:pass@host:port
socks5://user:pass@host:port
socks4://host:port
```

### 3. Validate Proxies (optional but recommended)
- Click **🔍 Validate All** — tests each proxy against ip-api.com
- Failed proxies get marked; click **🗑 Clear Failed** to remove them
- Click **🧹 Dedup vs Used** to remove any proxy IPs already used

---

## Running Automation

### Basic Run
1. Go to **🤖 Automation** tab
2. Enter your **Target URL** (the page with ads)
3. Set **Sessions** count (or leave at 1 for continuous mode)
4. Set **Max Clicks** per session (default: 2)
5. Click **▶ START**

### Continuous Mode (runs until proxies exhausted)
- Set Sessions to **0** — the engine will keep creating sessions
  until there are no fresh proxy IPs left
- Each session uses 1 unique proxy, never reused
- When all proxies are consumed, automation stops automatically
- Status bar shows remaining fresh proxies in real-time

### Options Explained

| Option | What it does |
|--------|-------------|
| **Target URL** | The website to visit and interact with ads on |
| **Sessions** | Number of sessions to run. Set **0** for continuous (until proxies exhausted) |
| **Max Clicks** | Maximum ad clicks per session (1-4 recommended) |
| **Pop-up Ad Mode** | Check this if the target uses pop-up/redirect ads instead of banner ads |
| **Use Proxies** | Uncheck to run without proxies (not recommended) |
| **Pre-visit Sites** | Visits 1-4 random sites before target (builds organic browsing trail) |
| **Match Proxy Country** | Matches proxy country to fingerprint country (more realistic) |

---

## Auto-Surfer (Background Mode)

The Auto-Surfer runs continuous background browsing sessions automatically.

1. Go to **🤖 Auto-Surfer** tab
2. Set **Min/Max Delay** between runs (in seconds)
3. Set **Pages/Run** (how many sites per surf session)
4. Optionally enter a **Target URL** (will include it in surf rotation)
5. Click **▶ Start Auto-Surfer**

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl + 9** | ⏹ Stop current automation (sessions finish gracefully) |
| **Ctrl + 4** | ❌ Close entire application |

---

## Proxy Management

### Where proxies are stored
```
proxies/proxies.json    — full proxy database with status
proxies/used_ips.txt    — list of all IPs that have been used (never reused)
```

### Proxy lifecycle
1. You import proxies → status: `unused`
2. Session starts → proxy locked to that session → status: `active`
3. Session ends → proxy IP added to `used_ips.txt` → status: `used`
4. That IP will **never** be assigned again

### Proxy buttons explained

| Button | What it does |
|--------|-------------|
| **📥 Import** | Add proxies from the text box |
| **📂 Load File** | Import from a .txt file |
| **🔍 Validate All** | Test all unused proxies for connectivity |
| **🧹 Dedup vs Used** | Remove any proxy whose IP is in the used list |
| **♻ Reset Used IPs** | Clear the used list (allows IPs to be reused) |
| **🗑 Clear Failed** | Remove proxies that failed validation 3+ times |
| **🔄 Reset All** | Reset everything — all proxies back to unused |

### Adding fresh proxies mid-run
You can import new proxies at any time — even while automation is running.
The system automatically checks new imports against `used_ips.txt`
so previously-used IPs are skipped.

---

## Fingerprint Management

### Where fingerprints are stored
```
fingerprints/fp_library_full.json   — the 10K fingerprint library
fingerprints/fp_state.json          — tracks which fingerprints are used/locked
```

### Fingerprint buttons

| Button | What it does |
|--------|-------------|
| **🏗 Generate 10K Library** | Creates 10,000 unique device profiles |
| **🔄 Reset All Used** | Marks all fingerprints as unused again |

---

## File Structure

```
browser to automate/
├── main_gui.py              ← Run this to start
├── launch.bat               ← Double-click to auto-install + start
├── install_deps.py          ← Installs pip packages + Chromium
├── check_system.py          ← Verifies everything is working
├── requirements.txt         ← pip dependencies
├── config.py                ← All settings (edit to customize)
├── proxy_manager.py         ← Proxy lifecycle management
├── stealth_injector.py      ← 22-layer JS fingerprint patches
├── tls_spoofer.py           ← TLS/JA3 spoofing profiles
├── fingerprint_generator.py ← Generates 10K device profiles
├── fingerprint_manager.py   ← Tracks fingerprint usage
├── user_persona.py          ← Creates realistic user personas
├── human_behavior.py        ← Mouse, scroll, typing simulation
├── browser_engine.py        ← Playwright stealth sessions
├── automation_engine.py     ← 4-phase session orchestrator
├── website_visitor.py       ← Organic browsing trail builder
├── auto_surfer.py           ← Background auto-surf scheduler
├── fingerprints/            ← Generated fingerprint library
├── proxies/                 ← Proxy database + used IPs
├── logs/                    ← Session logs
├── sessions/                ← Session data
└── data/                    ← Misc data
```

---

## Customizing Behavior (config.py)

Open `config.py` to adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `BROWSER_HEADLESS` | `False` | Set True to hide browser windows |
| `BROWSER_MAX_CONCURRENT` | `5` | Max simultaneous browser sessions |
| `PRE_VISIT_SITES_RANGE` | `(1, 5)` | How many warmup sites to visit |
| `TARGET_DWELL_RANGE` | `(15, 75)` | Seconds spent on target page |
| `AD_CLICK_DELAY_RANGE` | `(3, 18)` | Seconds before clicking an ad |
| `MAX_AD_CLICKS_RANGE` | `(1, 4)` | Ad clicks per session |
| `MOUSE_SPEED_RANGE` | `(0.3, 2.0)` | Mouse movement speed multiplier |
| `TYPING_WPM_RANGE` | `(15, 90)` | Typing speed range |
| `MISTAKE_RATE_RANGE` | `(0.0, 0.15)` | Typo probability |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No fingerprints available" | Go to Fingerprints tab → Generate 10K Library |
| "No fresh proxy available" | Import more proxies, or Reset Used IPs |
| Browser doesn't open | Run: `python -m playwright install chromium` |
| tkinter error | Reinstall Python with "tcl/tk" checked |
| Proxies all fail validation | Check proxy format, ensure they're residential/active |
| App won't start | Run `python check_system.py` to diagnose |
