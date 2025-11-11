# Deployment Guide

## SQLite Database + API Solution

Your TGPC data uses SQLite database instead of loading huge JSON files.

### What's Been Set Up

1. **SQLite Database** (main storage)
   - Location: `data/pharmacists.db` (15 MB, committed to repo)
   - Indexed for fast searches
   - Much more efficient than JSON for queries
   - Auto-synced by GitHub Action

2. **Flask API** 
   - Location: `api/app.py`
   - Endpoints: `/api/search`, `/api/stats`
   - Queries the database efficiently

3. **Web Search Interface**
   - Location: `web/index.html`
   - Calls the API for searches
   - No huge file downloads needed

### File Sizes Comparison

- `data/rx.json`: 13.4 MB (source, kept for compatibility)
- `data/pharmacists.db`: 15 MB (indexed database)
- **Total**: 28.4 MB (vs 26.8 MB if we duplicated JSON)

### Why Database is Better

- **Efficient queries**: Only returns matching records, not entire dataset
- **Indexed searches**: Fast lookups on name, registration number
- **Scalable**: Handles millions of records easily
- **No client-side load**: Browser doesn't download 13MB JSON

### Local Development

```bash
# Initialize database (first time only)
python3 scripts/init_database.py

# Start API server
python3 api/app.py

# In another terminal, serve web files
cd web && python3 -m http.server 8000
```

Visit: http://localhost:8000

### Deployment Options

**Option 1: Railway.app (FREE)**
- Supports SQLite databases
- Free tier: 500 hours/month
- Deploy: Connect GitHub repo, set start command to `python api/app.py`

**Option 2: Render.com (FREE)**
- Free tier with persistent disk
- Deploy: Connect repo, select Python, add start command

**Option 3: PythonAnywhere (FREE)**
- Free tier includes SQLite support
- Upload database file, deploy Flask app

### Future Growth

At 6 records/day:
- JSON: +1KB/day = +365KB/year
- Database: +1.2KB/day = +438KB/year (includes indexes)

Both will stay under 100MB for 100+ years at this rate.
