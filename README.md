
# 🔐 PortSwigger 2FA Brute Force Lab – Python Automation

This repository contains my solution for the **PortSwigger "2FA broken logic" lab**.

https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack

<img width="1152" height="542" alt="1" src="https://github.com/user-attachments/assets/607f75f3-4396-4d7a-a55e-92c9eb6513d0" />



Instead of relying on **Burp Suite’s Intruder** or **Macros** (which are powerful but often very slow for large brute force ranges especially if you don't have the professional edition), I crafted a **custom Python script** that performs the brute force efficiently using concurrency.

---

## 📚 Lab Description

The target web application implements a **two-factor authentication (2FA)** mechanism:

1. The attacker first logs in with username and password.
2. They are then asked to enter a 4-digit one-time authentication code (0000-9999).
3. The server **does not lock accounts** and allows unlimited attempts, but resets the flow after two wrong codes if done manually.

### Vulnerability

* Lack of proper brute force protections.
* The workflow can be abused by automating re-logins and re-submitting the MFA step for every possible 4-digit code.

---

## 🚀 My Approach

I saved the requests and created the script of them

<img width="1920" height="1080" alt="Screenshot_2025-08-27_23_21_33" src="https://github.com/user-attachments/assets/aa30d34c-da17-48e3-b01d-eb9a44ea3384" />

creating the Script

<img width="1920" height="1080" alt="Screenshot_2025-08-27_23_22_04" src="https://github.com/user-attachments/assets/9ac40c3d-3895-4438-8215-6ba2c53f574d" />

to solve this lab using my script only you need to select the target
open the script in a text editor write your lab's url instead of mine

1 install the dependencies first
2 open the script in a text editor write your lab's url instead of mine (edit the target)
3 then python mfa_bruteforce.py


Instead of:

* **Burp Intruder:** Very slow for 10,000 payloads.
* **Burp Macros:** Work, but are clunky and limited in parallelization.

I built a **Python brute force script** using:

* [`requests`](https://docs.python-requests.org/) – to manage sessions.
* [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/) – to extract CSRF tokens dynamically.
* [`concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html) – to run concurrent login attempts and speed up testing.

This script simulates the full login flow for each code until the correct one is found (detected via `302 Found` redirect).

---

## 🖥️ Usage



```bash
git clone https:/moehabx/github.com//portswigger-2fa-bruteforce.git
cd portswigger-2fa-bruteforce
pip install -r requirements.txt

python mfa_bruteforce.py
```

### Configurable Settings inside `mfa_bruteforce.py`:

```python
TARGET = "https://<your-lab>.web-security-academy.net"
USERNAME = "carlos"
PASSWORD = "montoya"
MAX_WORKERS = 30    # threads for concurrency
```

---

## ⚡ Example Run
we run and found the correct code that sents back the cookie

```
Target: https://0a5a00b5047ee854809c7688004000f5.web-security-academy.net | username: carlos | concurrency: 30

[0000] tried... (info: status 200)
[0100] tried... (info: status 200)
...

[+] SUCCESS! code = 1234 | 302 Found -> /my-account
[+] Set-Cookie: session=AbCdEf123456789; Secure; HttpOnly

Found code: 1234 (details: redirected to /my-account) in 12.3s
Valid Cookie: session=AbCdEf123456789; Secure; HttpOnly
```

---


<img width="926" height="245" alt="Screenshot_2025-08-27_23_22_19" src="https://github.com/user-attachments/assets/fcce141f-b1b7-4211-bd8a-c237c8594863" />

we replace our cookie with the found cookie
<img width="1920" height="1080" alt="Screenshot_2025-08-27_23_16_46" src="https://github.com/user-attachments/assets/c876f809-9896-4621-b0f2-44303587d69f" />

now we go back to the main page and go to my account 
boom we got carlos's account

<img width="1920" height="1080" alt="Screenshot_2025-08-27_23_19_51" src="https://github.com/user-attachments/assets/2628f4e7-f366-4ef5-9193-47dc72a67f98" />




