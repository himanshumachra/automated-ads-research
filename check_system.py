"""
PhantomBrowser Pro — Full System Check
Run this: python check_system.py
Verifies all packages, imports, and cross-references.
"""

import sys
import os

print("=" * 60)
print("  PhantomBrowser Pro — System Check")
print("=" * 60)
print()

# ── 1. Python version ────────────────────────────────────────────
print(f"[1] Python: {sys.version}")
if sys.version_info < (3, 8):
    print("    ⚠ WARNING: Python 3.8+ recommended")
else:
    print("    ✓ OK")
print()

# ── 2. Required packages ─────────────────────────────────────────
PACKAGES = {
    "playwright":  "playwright",
    "aiohttp":     "aiohttp",
    "tkinter":     "tkinter",
    "asyncio":     "asyncio",
    "json":        "json",
    "hashlib":     "hashlib",
    "dataclasses": "dataclasses",
    "threading":   "threading",
    "uuid":        "uuid",
    "math":        "math",
    "random":      "random",
    "time":        "time",
    "re":          "re",
    "os":          "os",
}

print("[2] Checking packages:")
missing = []
for name, module in PACKAGES.items():
    try:
        __import__(module)
        ver = ""
        try:
            m = __import__(module)
            ver = getattr(m, "__version__", "")
        except Exception:
            pass
        print(f"    ✓ {name:20s} {ver}")
    except ImportError:
        print(f"    ✗ {name:20s} MISSING")
        missing.append(name)

if missing:
    print(f"\n    ⚠ Missing packages: {', '.join(missing)}")
    print(f"    Fix: pip install {' '.join(missing)}")
else:
    print("    ✓ All packages installed")
print()

# ── 3. Playwright browsers ───────────────────────────────────────
print("[3] Checking Playwright browsers:")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--dry-run"],
        capture_output=True, text=True, timeout=15
    )
    # If dry-run doesn't work, just check if chromium exists
    from playwright._impl._driver import compute_driver_executable
    driver_path = os.path.dirname(compute_driver_executable())
    browser_path = os.path.join(driver_path, "..", "chromium-*")
    import glob
    chromium_dirs = glob.glob(os.path.join(os.path.dirname(driver_path), "chromium-*"))
    if chromium_dirs:
        print(f"    ✓ Chromium found: {os.path.basename(chromium_dirs[0])}")
    else:
        print("    ⚠ Chromium not found — run: python -m playwright install chromium")
except Exception as e:
    print(f"    ⚠ Could not verify: {e}")
    print("    Run: python -m playwright install chromium")
print()

# ── 4. Project file imports ───────────────────────────────────────
print("[4] Checking project module imports:")
# Add project dir to path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

MODULES = [
    ("config",               "config.py"),
    ("tls_spoofer",          "tls_spoofer.py"),
    ("proxy_manager",        "proxy_manager.py"),
    ("stealth_injector",     "stealth_injector.py"),
    ("fingerprint_generator","fingerprint_generator.py"),
    ("fingerprint_manager",  "fingerprint_manager.py"),
    ("user_persona",         "user_persona.py"),
    ("human_behavior",       "human_behavior.py"),
    ("website_visitor",      "website_visitor.py"),
    ("auto_surfer",          "auto_surfer.py"),
    ("automation_engine",    "automation_engine.py"),
    ("browser_engine",       "browser_engine.py"),
    ("main_gui",             "main_gui.py"),
]

import_errors = []
for mod_name, filename in MODULES:
    filepath = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"    ✗ {mod_name:25s} FILE MISSING: {filename}")
        import_errors.append(mod_name)
        continue
    try:
        __import__(mod_name)
        print(f"    ✓ {mod_name:25s} OK")
    except Exception as e:
        err_msg = str(e).split('\n')[0][:60]
        print(f"    ✗ {mod_name:25s} ERROR: {err_msg}")
        import_errors.append(mod_name)

if import_errors:
    print(f"\n    ⚠ Failed imports: {', '.join(import_errors)}")
else:
    print("    ✓ All modules import successfully")
print()

# ── 5. Cross-reference checks ────────────────────────────────────
print("[5] Cross-reference checks:")
checks_passed = 0
checks_total = 0

def check(desc, condition):
    global checks_passed, checks_total
    checks_total += 1
    if condition:
        checks_passed += 1
        print(f"    ✓ {desc}")
    else:
        print(f"    ✗ {desc}")

try:
    from config import FP_LIBRARY_FILE, WARMUP_WEBSITES, SEARCH_TERMS
    check("config.FP_LIBRARY_FILE defined", bool(FP_LIBRARY_FILE))
    check("config.WARMUP_WEBSITES has entries", len(WARMUP_WEBSITES) > 10)
    check("config.SEARCH_TERMS has entries", len(SEARCH_TERMS) > 10)
except Exception as e:
    print(f"    ✗ config check failed: {e}")

try:
    from fingerprint_generator import generate_single_fingerprint
    fp = generate_single_fingerprint(1)
    check("fingerprint_generator produces valid FP", "id" in fp and "user_agent" in fp)
    check("FP has screen data", "screen" in fp and "width" in fp["screen"])
    check("FP has webgl_vendor", bool(fp.get("webgl_vendor")))
    check("FP has timezone", bool(fp.get("timezone")))
    check("FP has canvas_noise", fp.get("canvas_noise", 0) > 0)
    check("FP has fonts list", len(fp.get("fonts", [])) > 0)
    check("FP has plugins list", isinstance(fp.get("plugins"), list))
    check("FP has country code", len(fp.get("country", "")) == 2)
except Exception as e:
    print(f"    ✗ fingerprint_generator check failed: {e}")

try:
    from stealth_injector import get_stealth_script
    fp = generate_single_fingerprint(99)
    js = get_stealth_script(fp, "test_session")
    check("stealth_injector produces JS", len(js) > 1000)
    check("JS contains navigator patch", "navigator" in js)
    check("JS contains WebGL patch", "37445" in js)
    check("JS contains timezone patch", fp["timezone"] in js)
except Exception as e:
    print(f"    ✗ stealth_injector check failed: {e}")

try:
    from tls_spoofer import get_tls_profile, get_doh_provider, get_network_profile
    profile = get_tls_profile("Chrome")
    check("TLS profile has ciphers", len(profile.get("ciphers", [])) > 5)
    check("DoH provider returns URL", get_doh_provider().startswith("https://"))
    net = get_network_profile()
    check("Network profile has RTT", net.get("base_rtt", 0) > 0)
except Exception as e:
    print(f"    ✗ tls_spoofer check failed: {e}")

try:
    from user_persona import generate_random_persona, persona_to_behavior_config
    p = generate_random_persona()
    cfg = persona_to_behavior_config(p)
    check("Persona generates valid age", 10 <= p.age <= 90)
    check("Persona has skill_level", 1 <= p.skill_level <= 10)
    check("Behavior config has mouse_speed_mult", "mouse_speed_mult" in cfg)
    check("Behavior config has typing_delay_range", "typing_delay_range" in cfg)
    check("Behavior config has scroll_chunk_range", "scroll_chunk_range" in cfg)
except Exception as e:
    print(f"    ✗ user_persona check failed: {e}")

try:
    from proxy_manager import ProxyManager, Proxy
    pm = ProxyManager()
    check("ProxyManager instantiates", pm is not None)
    check("ProxyManager has stats", "total" in pm.stats)
    p = Proxy(host="1.2.3.4", port=8080)
    check("Proxy object creates", p.url == "http://1.2.3.4:8080")
    check("Proxy has playwright_proxy", "server" in p.playwright_proxy)
except Exception as e:
    print(f"    ✗ proxy_manager check failed: {e}")

try:
    from fingerprint_manager import FingerprintManager
    fm = FingerprintManager()
    check("FingerprintManager instantiates", fm is not None)
    check("FingerprintManager has stats", "total" in fm.stats)
except Exception as e:
    print(f"    ✗ fingerprint_manager check failed: {e}")

print(f"\n    Result: {checks_passed}/{checks_total} checks passed")
print()

# ── 6. Directory structure ────────────────────────────────────────
print("[6] Directory structure:")
REQUIRED_DIRS = ["fingerprints", "proxies", "logs", "sessions", "data"]
for d in REQUIRED_DIRS:
    full = os.path.join(PROJECT_DIR, d)
    exists = os.path.isdir(full)
    print(f"    {'✓' if exists else '✗'} {d}/")
    if not exists:
        os.makedirs(full, exist_ok=True)
        print(f"      → Created")
print()

# ── Summary ───────────────────────────────────────────────────────
print("=" * 60)
if not missing and not import_errors and checks_passed == checks_total:
    print("  ✅ ALL CHECKS PASSED — System ready!")
    print("  Run: python main_gui.py")
else:
    print("  ⚠ Some checks failed — see details above")
    if missing:
        print(f"  Fix packages: pip install {' '.join(missing)}")
    if import_errors:
        print(f"  Fix imports: check files {', '.join(import_errors)}")
print("=" * 60)
