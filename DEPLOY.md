# วิธี Deploy — Money Thunder KOL Dashboard

รันจากในโฟลเดอร์ `repo/` นี้ (ต้อง `gh auth login` ให้เรียบร้อยก่อน)

```bash
git init -b main
git add .
git commit -m "Initial commit: MT KOL dashboard"

# สร้าง repo + push (public)
gh repo create mt-kol-dashboard --public --source=. --push

# เปิด GitHub Pages (branch main / root)
gh api -X POST repos/{owner}/mt-kol-dashboard/pages -f "source[branch]=main" -f "source[path]=/"

# สั่ง scrape รอบแรกทันที (ไม่ต้องรอ cron)
gh workflow run auto-update.yml
```

Live URL: `https://<username>.github.io/mt-kol-dashboard/`

- GitHub Actions จะ scrape ยอด TikTok จริงทุก 30 นาที แล้ว commit `scrape_results.json` กลับเข้า repo
- ยอดในแดชบอร์ดจะเปลี่ยนจาก "รอดึง" เป็นตัวเลขจริง หลัง workflow รันรอบแรกเสร็จ (~2-3 นาที)
