# Money Thunder — KOL Performance Dashboard

แดชบอร์ดติดตามยอดวิวและเอนเกจเมนต์ของ KOL แคมเปญ Money Thunder
ดึงข้อมูลจริงจาก TikTok อัตโนมัติทุก 30 นาทีผ่าน GitHub Actions

## โครงสร้าง

```
├── index.html               ← แดชบอร์ด (เปิดดูได้เลย)
├── scrape_results.json      ← ข้อมูล KOL + ยอดที่ scrape มา
├── scripts/
│   └── tiktok_scraper.py    ← ตัวดึงยอดจาก TikTok (yt-dlp)
└── .github/workflows/
    └── auto-update.yml      ← cron ทุก 30 นาที
```

## Deploy ขึ้น GitHub Pages

```bash
cd mt-kol-dashboard
git init && git add . && git commit -m "Initial commit"
gh repo create mt-kol-dashboard --public --source=. --push
gh api -X POST repos/:owner/mt-kol-dashboard/pages -f source[branch]=main -f source[path]=/
gh workflow run auto-update.yml
```

URL: `https://<username>.github.io/mt-kol-dashboard/`

## เติมข้อมูลช่องทางอื่น (FB / IG / YT)

KOL ที่ไม่มีลิงก์ TikTok จะขึ้นสถานะ **"รอเติม"** — แก้ที่ `scrape_results.json` โดยตรง:

```json
{
  "name": "Mild.Natt",
  "status": "manual",
  "views": 120000,
  "likes": 3400,
  "comments": 210,
  "shares": 89
}
```

ตั้ง `"status": "manual"` เพื่อให้ scraper ข้ามและไม่เขียนทับ

## Override ยอดคลิปที่ดึงไม่ได้

แก้ `MANUAL_OVERRIDE` ใน `scripts/tiktok_scraper.py`:

```python
MANUAL_OVERRIDE = {
    'มาวิน': {'views': 2700000, 'likes': 45000, 'comments': 320, 'shares': 1200},
}
```

## รันเองในเครื่อง

```bash
pip install yt-dlp
python3 scripts/tiktok_scraper.py
python3 -m http.server 8000   # เปิด http://localhost:8000
```
