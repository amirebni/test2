import requests
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

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
        log(f"خطا دانلود: {e}")
        return []

def is_good_vless(line):
    line_lower = line.lower()

    # فقط vless
    if not line.startswith("vless://"):
        return False

    try:
        # جدا کردن remark
        base = line.split("#")[0]
        u = urlparse(base)
        qs = parse_qs(u.query)

        # شرط‌های ضروری (بر اساس نمونه‌های کاری)
        if qs.get("type", [""])[0] != "ws":
            return False

        if qs.get("security", [""])[0] != "tls":
            return False

        fp = qs.get("fp", [""])[0].lower()
        if fp not in ["chrome", "firefox", "safari"]:
            return False

        # sni باید وجود داشته باشه
        sni = qs.get("sni", [""])[0]
        if not sni:
            return False

        # host هم باید باشه
        host = qs.get("host", [""])[0]
        if not host:
            return False

        # پورت بالا (مثل نمونه‌ها)
        port = u.port or 443
        if port <= 1024:  # پورت‌های خیلی پایین معمولاً بد
            return False

        # اگر path خاص باشه (مثل /admin.php یا /download.php) امتیاز مثبت
        path = qs.get("path", [""])[0]
        if path and path != "/":
            pass  # خوبه

        return True

    except Exception as e:
        return False

def main():
    log("فیلتر vless + ws + tls هدفمند شروع شد")
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
