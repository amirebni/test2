import requests
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# ورودی از فایل زنده‌های Repo-5
SUB_URL = "https://raw.githubusercontent.com/punez/Repo-5/main/alive.txt"
OUTPUT_FILE = "strong_3000.txt"
MAX_OUTPUT = 3000

def log(msg):
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}] {msg}")

def download():
    try:
        r = requests.get(SUB_URL, timeout=15)
        r.raise_for_status()
        return [l.strip() for l in r.text.splitlines() if l.strip()]
    except Exception as e:
        log(f"خطا در دانلود: {e}")
        return []

def is_good_vless(line):
    line_lower = line.lower()

    # فقط vless
    if not line.startswith("vless://"):
        return False

    try:
        u = urlparse(line.split("#")[0])
        qs = parse_qs(u.query)

        # شرط‌های اصلی از نمونه‌ها
        if qs.get("type", [""])[0] != "ws":
            return False

        if qs.get("security", [""])[0] != "tls":
            return False

        fp = qs.get("fp", [""])[0].lower()
        if fp not in ["chrome", "firefox", "safari", "edge"]:
            return False

        # sni باید وجود داشته باشه (نمونه‌ها همه sni ایرانی داشتن)
        sni = qs.get("sni", [""])[0].lower()
        if not sni:
            return False

        # پورت غیراستاندارد (نمونه‌ها 2087 و 8443 بودن)
        port = u.port or 443
        if port in [80, 443]:
            return False  # پورت‌های استاندارد معمولاً فیلتر می‌شن

        return True

    except:
        return False

def main():
    log("فیلتر vless + ws + tls شروع شد")
    lines = download()
    log(f"تعداد ورودی: {len(lines):,}")

    good = [line for line in lines if is_good_vless(line)]

    log(f"بعد فیلتر: {len(good):,} نود")

    random.shuffle(good)
    final = good[:MAX_OUTPUT]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final) + "\n")

    log(f"تمام شد → {len(final):,} نود → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
