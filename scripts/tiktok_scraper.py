#!/usr/bin/env python3
"""
Money Thunder — TikTok Scraper (v2, retry-resilient)
- ยิงเฉพาะคลิปที่ยัง pending (ไม่แตะตัวที่ได้ยอดแล้ว)
- retry เยอะขึ้น + delay นานขึ้น + สลับ user-agent เพื่อเลี่ยง rate-limit
Usage: python3 scripts/tiktok_scraper.py
"""
import json, os, subprocess, time, random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, 'scrape_results.json')

MANUAL_OVERRIDE = {}   # ใส่ยอดมือได้ที่นี่ ถ้าอยากเติมเอง

UAS = [
 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
]

def scrape(url, timeout=90):
    for attempt in range(5):
        ua = UAS[attempt % len(UAS)]
        try:
            r = subprocess.run(
                ['yt-dlp','--dump-json','--no-download','--no-warnings','--user-agent',ua,url],
                capture_output=True, text=True, timeout=timeout)
            if r.returncode == 0:
                info = json.loads(r.stdout)
                if info.get('view_count') is not None:
                    return {
                        'views': info.get('view_count'),
                        'likes': info.get('like_count'),
                        'comments': info.get('comment_count'),
                        'shares': info.get('repost_count'),
                        'handle': info.get('uploader') or info.get('uploader_id') or '',
                        'upload_date': info.get('upload_date') or '',
                    }
            # backoff เพิ่มขึ้นเรื่อยๆ
            time.sleep(5 + attempt*5 + random.uniform(0,4))
        except subprocess.TimeoutExpired:
            time.sleep(5)
        except Exception as e:
            print(f"    EXC: {str(e)[:100]}")
            time.sleep(4)
    return None

def main():
    rows = json.load(open(RESULTS, encoding='utf-8'))
    ok = fail = skip = kept = 0
    for row in rows:
        name = row['name']
        if name in MANUAL_OVERRIDE:
            row.update(MANUAL_OVERRIDE[name]); row['status']='manual'; ok+=1; continue
        if not row.get('tiktok'):
            row['status']='no_tiktok'; skip+=1; continue
        # ยิงเฉพาะตัวที่ยังไม่มียอด — ตัวที่ได้แล้วคงไว้
        if row.get('views') is not None:
            kept+=1; continue
        print(f"[SCRAPE] {name}")
        data = scrape(row['tiktok'])
        if data:
            row.update(data); row['status']='ok'
            print(f"    OK views={data['views']:,}"); ok+=1
        else:
            row['status']='pending'; fail+=1
            print("    -> pending (ยังโดน rate-limit ไว้รอบหน้า)")
        time.sleep(random.uniform(8,15))   # ช้าลงเพื่อเลี่ยงโดนบล็อก
    json.dump(rows, open(RESULTS,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    total = sum(r.get('views') or 0 for r in rows)
    done = sum(1 for r in rows if r.get('views') is not None)
    print(f"\n=== new OK {ok} | kept {kept} | still pending {fail} | no_tiktok {skip} ===")
    print(f"=== รวม {done}/25 คลิป | Total views {total:,} ===")

if __name__ == '__main__':
    main()
