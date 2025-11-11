# Deployment Guide

## Database + Web Search Interface

Your TGPC data is now available as both a database and a searchable website.

### What's Been Set Up

1. **SQLite Database** (optional, for advanced use)
   - Schema: `tgpc/database/schema.py`
   - Location: `data/pharmacists.db` (gitignored)
   - Can be used for complex queries, analytics, etc.

2. **Web Search Interface** (main solution)
   - Location: `web/` directory
   - Simple HTML/JS - no backend needed
   - Searches 82,000+ records instantly
   - Mobile responsive

### Deploy to GitHub Pages (Recommended - FREE)

1. Go to your repo: https://github.com/dilludx/tgpc
2. Click **Settings** > **Pages**
3. Under "Source", select:
   - Branch: `main`
   - Folder: `/web`
4. Click **Save**
5. Wait 1-2 minutes
6. Your site will be live at: `https://dilludx.github.io/tgpc/`

### Alternative: Deploy to Netlify (FREE)

1. Go to https://netlify.com
2. Click "Add new site" > "Import an existing project"
3. Connect your GitHub repo
4. Set:
   - Base directory: `web`
   - Build command: (leave empty)
   - Publish directory: `.` (or leave empty)
5. Deploy!

### Local Testing

```bash
cd web
python3 -m http.server 8000
```

Visit: http://localhost:8000

### How It Works

- The GitHub Action automatically updates `web/data.json` when new pharmacists are added
- The website loads this JSON file and searches it client-side (no server needed)
- Fast, simple, and free to host

### File Sizes

- `data/rx.json`: 13.4 MB (source data)
- `web/data.json`: 13.4 MB (same data, for web)
- Both grow slowly (~6 records/day = ~1KB/day)

### Future Growth

At current rate (6 records/day):
- 1 year: +2,190 records (+350 KB)
- 5 years: +10,950 records (+1.7 MB)
- 10 years: +21,900 records (+3.5 MB)

The website will handle 100,000+ records easily.
