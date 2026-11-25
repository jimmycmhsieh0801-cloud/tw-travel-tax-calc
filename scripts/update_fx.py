"""
每日自動抓取最新 JPY / KRW 對 TWD 匯率，更新 index.html 與 sitemap.xml，
並透過 IndexNow 主動通知搜尋引擎重新抓取。
"""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "index.html"
SITEMAP_XML = ROOT / "sitemap.xml"

INDEXNOW_KEY = "414799b062aa4cbbb5e9ec821e4e955c"
SITE_URL = "https://jimmycmhsieh0801-cloud.github.io/tw-travel-tax-calc/"


def fetch_rate(currency: str) -> float:
    url = f"https://open.er-api.com/v6/latest/{currency}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return round(float(data["rates"]["TWD"]), 4)


def update_files(jpy_twd: float, krw_twd: float, today_str: str) -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")

    badge_html = (
        f'<div class="badge" id="fxBadge">'
        f"每日自動匯率更新：1 JPY ≈ {jpy_twd:.4f} TWD ｜ 1 KRW ≈ {krw_twd:.4f} TWD（{today_str}）"
        f"</div>"
    )
    if 'id="fxBadge"' in html:
        html = re.sub(r'<div class="badge" id="fxBadge">.*?</div>', badge_html, html, count=1)
    else:
        html = re.sub(r'<div class="badge">.*?</div>', badge_html, html, count=1)

    html = re.sub(
        r'(<label for="fxRate">).*?(</label>)',
        rf"\g<1>參考匯率（1 外幣 = ? 台幣，今日日圓約 {jpy_twd:.4f} / 韓元約 {krw_twd:.4f}）\g<2>",
        html,
        count=1,
    )
    html = re.sub(
        r'(<input type="number" id="fxRate" value=")[^"]+(")',
        rf"\g<1>{jpy_twd:.4f}\g<2>",
        html,
        count=1,
    )
    INDEX_HTML.write_text(html, encoding="utf-8")

    if SITEMAP_XML.exists():
        sm = SITEMAP_XML.read_text(encoding="utf-8")
        sm = re.sub(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", f"<lastmod>{today_str}</lastmod>", sm)
        SITEMAP_XML.write_text(sm, encoding="utf-8")


def ping_indexnow() -> None:
    payload = {
        "host": "jimmycmhsieh0801-cloud.github.io",
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://jimmycmhsieh0801-cloud.github.io/{INDEXNOW_KEY}.txt",
        "urlList": [SITE_URL],
    }
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[IndexNow] HTTP {r.status} pinged {SITE_URL}")
    except Exception as e:
        print(f"[IndexNow] skipped or failed: {e}")


def main() -> None:
    tw_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(tw_tz).strftime("%Y-%m-%d")
    jpy_twd = fetch_rate("JPY")
    krw_twd = fetch_rate("KRW")
    update_files(jpy_twd, krw_twd, today_str)
    print(f"[OK] Updated {today_str}: JPY={jpy_twd:.4f}, KRW={krw_twd:.4f}")
    ping_indexnow()


if __name__ == "__main__":
    main()
