import requests
import base64
import json
from urllib.parse import urlparse, parse_qs
import random
from datetime import datetime

# ────────────────────────────────────────────────
# تنظیمات اصلی
# ────────────────────────────────────────────────

SUB_URL = "https://raw.githubusercontent.com/punez/Repo-5/main/alive.txt"  # لینک زنده‌های Repo-5
OUTPUT_FILE = "strong_3000.txt"
MAX_OUTPUT = 3000

# لیست سیاه sni/host (رایج در فیلترینگ ایران)
BLACKLIST_SNI = {
    "google.com", "www.google.com", "youtube.com", "youtu.be",
    "cloudflare.com", "1.1.1.1", "dns.google", "8.8.8.8",
    "microsoft.com", "office.com", "live.com", "bing.com",
    # اضافه کن اگر چیز خاصی دیدی
}

# لیست سیاه IP/host شناخته‌شده فیلترشده (چند نمونه)
BLACKLIST_HOST = {
    "104.16.0.0/12", "162.158.0.0/15",  # بعضی رنج‌های cloudflare که فیلتر می‌شن
    # می‌تونی رنج‌های بیشتری اضافه کنی
}

# اولویت پروتکل (امتیاز بالاتر = اولویت بیشتر)
PROTOCOL_SCORE = {
    "hysteria2": 10,
    "hy2": 10,
    "tuic": 9,
    "vless+reality": 8.5,
    "vless+vision": 8,
    "trojan+xtls": 7.5,
    "trojan+tls": 7,
    "vless+tls": 6.5,
    "vmess+ws+tls": 5.5,
    "ss": 2,
    "ss-obfs": 3,
}

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}")

def download():
    try:
        r = requests.get(SUB_URL, timeout=15)
        r.raise_for_status()
        return r.text.splitlines()
    except Exception as e:
        log(f"خطا در دانلود: {e}")
        return []

def get_protocol_score(line):
    lower = line.lower()
    if "hysteria2" in lower or "hy2://" in lower:
        return 10
    if "tuic" in lower:
        return 9
    if "reality" in lower:
        return 8.5
    if "vision" in lower:
        return 8
    if "xtls" in lower:
        return 7.5
    if "trojan://" in lower:
        return 7
    if "vless://" in lower:
        return 6.5
    if "vmess://" in lower:
        return 5
    if "ss://" in lower:
        return 2
    return 1

def is_blacklisted(host, sni):
    if sni.lower() in BLACKLIST_SNI:
        return True
    if host.lower() in BLACKLIST_HOST:
        return True
    return False

def get_fingerprint_strong(line):
    """dedup قوی‌تر با sni هم"""
    line = line.strip()
    if not line:
        return None

    try:
        if line.startswith("vmess://"):
            raw = line[8:].split("#")[0]
            data = json.loads(base64.b64decode(raw + "===").decode(errors="ignore"))
            return "|".join([
                data.get("add", ""),
                str(data.get("port", "")),
                data.get("id", ""),
                data.get("fp", ""),
                data.get("path", ""),
                data.get("net", ""),
                data.get("security", ""),
                data.get("sni", ""),
            ]).lower()

        elif line.startswith(("vless://", "trojan://")):
            u = urlparse(line.split("#")[0])
            qs = parse_qs(u.query)
            return "|".join([
                u.hostname or "",
                str(u.port or 443),
                u.username or "",
                qs.get("fp", [""])[0],
                qs.get("path", [""])[0] or qs.get("serviceName", [""])[0],
                qs.get("security", [""])[0],
                qs.get("sni", [""])[0],
            ]).lower()

        else:
            return line.split("#")[0].lower()
    except:
        return None

def main():
    log("شروع فیلتر قوی از Repo-5")

    lines = [l.strip() for l in download() if l.strip()]
    log(f"خطوط ورودی: {len(lines):,}")

    candidates = []
    seen = set()

    for line in lines:
        fp = get_fingerprint_strong(line)
        if not fp:
            continue
        if fp in seen:
            continue
        seen.add(fp)

        score = get_protocol_score(line)

        # چک لیست سیاه
        try:
            u = urlparse(line.split("#")[0])
            host = u.hostname
            qs = parse_qs(u.query)
            sni = qs.get("sni", [host])[0]
            if is_blacklisted(host, sni):
                continue
        except:
            pass

        # چک پورت‌های رایج و مقاوم
        port_ok = any(p in line for p in ["443", "8443", "2053", "8080"])
        if not port_ok and score < 7:
            continue

        candidates.append((score, line))

    # سورت بر اساس امتیاز (بالاتر بهتر)
    candidates.sort(key=lambda x: x[0], reverse=True)

    # فقط بهترین‌ها رو نگه دار
    final = [line for score, line in candidates[:MAX_OUTPUT]]

    # shuffle برای تنوع
    random.shuffle(final)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final) + "\n")

    log(f"فیلتر تمام شد → {len(final):,} نود قوی → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
