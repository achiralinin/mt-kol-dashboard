#!/usr/bin/env python3
"""
Money Thunder — TikTok Scraper
ดึงยอด views / likes / comments / shares จากลิงก์ TikTok จริง
รันอัตโนมัติทุก 30 นาทีผ่าน GitHub Actions

Usage: python3 scripts/tiktok_scraper.py
"""

import json
import os
import subprocess
import time
import random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, 'scrape_results.json')

# ============================================================
#  MANUAL OVERRIDE — สำหรับคลิปที่ดึงอัตโนมัติไม่ได้ / ช่องอื่น (FB/IG/YT)
#  ใส่ key เป็นชื่อ KOL ตรงตามใน scrape_results.json
#  ตัวอย่าง:
#  'Mild.Natt': {'views': 120000, 'likes': 3400, 'comments': 210, 'shares': 89},
# ============================================================
MANUAL_OVERRIDE = {}

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')


def scrape(url, timeout=90):
    """ดึง metadata จาก TikTok ด้วย yt-dlp"""
    for attempt in range(3):
        try:
            r = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-download', '--no-warnings',
                 '--user-agent', UA, url],
                capture_output=True, text=True, timeout=timeout
            )
            if r.returncode != 0:
                if attempt < 2:
                    time.sleep(4 + attempt * 3)
                    continue
                print(f"    ERROR: {r.stderr.strip()[:160]}")
                return None
            info = json.loads(r.stdout)
            return {
                'views': info.get('view_count'),
                'likes': info.get('like_count'),
                'comments': info.get('comment_count'),
                'shares': info.get('repost_count'),
                'handle': info.get('uploader') or info.get('uploader_id') or '',
                'upload_date': info.get('upload_date') or '',
            }
        except subprocess.TimeoutExpired:
            print("    TIMEOUT")
            if attempt < 2:
                continue
            return None
        except Exception as e:
            print(f"    EXC: {str(e)[:120]}")
            return None
    return None


def main():
    rows = json.load(open(RESULTS, encoding='utf-8'))
    ok = fail = skip = 0

    for row in rows:
        name = row['name']

        if name in MANUAL_OVERRIDE:
            row.update(MANUAL_OVERRIDE[name])
            row['status'] = 'manual'
            print(f"[MANUAL] {name}")
            ok += 1
            continue

        if not row.get('tiktok'):
            row['status'] = 'no_tiktok'
            print(f"[SKIP]   {name} — ไม่มีลิงก์ TikTok")
            skip += 1
            continue

        print(f"[SCRAPE] {name}")
        data = scrape(row['tiktok'])
        if data and data.get('views') is not None:
            row.update(data)
            row['status'] = 'ok'
            print(f"    views={data['views']:,} likes={data.get('likes') or 0:,}")
            ok += 1
        else:
            # ดึงไม่ได้ — คงค่า null ไว้ ห้ามใส่ตัวเลขมั่ว
            row['status'] = 'pending'
            fail += 1
            print(f"    -> pending (ดึงไม่สำเร็จ)")

        time.sleep(random.uniform(1.5, 3.5))

    json.dump(rows, open(RESULTS, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    total = sum(r.get('views') or 0 for r in rows)
    print(f"\n=== OK {ok} | FAIL {fail} | SKIP {skip} | Total views {total:,} ===")


if __name__ == '__main__':
    main()
