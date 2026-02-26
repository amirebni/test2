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

def is_good_node(line):
    line_lower = line.lower()

    # حداقل پروتکل معتبر
    if not any(p in line_lower for p in ["vless://", "vmess://", "trojan://"]):
        return False

    try:
        base = line.split("#")[0]
        u = urlparse(base)
        qs = parse_qs(u.query)

        # پورت غیراستاندارد (بر اساس نمونه‌ها)
        port = u.port or 443
        if port in [80, 443] or port <= 1024:
            return False

        # fp خوب (از نمونه‌ها)
        fp = qs.get("fp", [""])[0].lower()
        if fp and fp not in ["chrome", "firefox", "safari", "edge"]:
            return False

        # sni/host وجود داشته باشه (نمونه‌ها همه داشتن)
        sni = qs.get("sni", [""])[0]
        host = qs.get("host", [""])[0] or u.hostname or ""
        if not sni and not host:
            return False

        # حذف دامنه‌های عمومی بلاک‌شده
        if "google" in sni.lower() or "cloudflare.com" in sni.lower() or "microsoft" in sni.lower():
            return False

        # برای vless: ws + tls ترجیحاً
        if line_lower.startswith("vless://"):
            if qs.get("type", [""])[0] != "ws":
                return False
            if qs.get("security", [""])[0] != "tls":
                return False

        # برای vmess: tcp یا ws بدون tls هم قبول
        if line_lower.startswith("vmess://"):
            pass  # همه vmess رو نگه دار (نمونه خریدی بدون tls بود)

        return True

    except:
        return True  # اگر parse نشد ولی لینک معتبر بود، نگه دار

def main():
    log("فیلتر هدفمند بر اساس نمونه‌های کاری شروع شد")
    lines = download()
    log(f"تعداد ورودی: {len(lines):,}")

    good = [line for line in lines if is_good_node(line)]

    log(f"بعد فیلتر: {len(good):,} نود")

    random.shuffle(good)
    final = good[:MAX_OUTPUT]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final) + "\n")

    log(f"تمام شد → {len(final):,} نود → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
