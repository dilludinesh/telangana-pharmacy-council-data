# Design Document: TGPC Pharmacist Search Website

## Overview

A simple, cloud-based search website that uses Supabase (free PostgreSQL database) to store TGPC pharmacist records and provides instant search functionality without requiring users to download large files. The system automatically syncs data daily from rx.json to Supabase using GitHub Actions.

## Architecture

### High-Level Architecture

```
TGPC Portal → GitHub Actions → rx.json → Supabase Database
                                              ↓
                                    GitHub Pages Website
                                              ↓
                                         User Browser
```

### Component Breakdown

1. **Data Collection** - GitHub Actions (existing + new Supabase sync)
2. **Data Storage** - Supabase PostgreSQL (cloud database)
3. **Presentation** - GitHub Pages (static website)
4. **User Interface** - Browser (search only, no downloads)

## Data Models

### Supabase Database Schema

```sql
CREATE TABLE rx (
    id BIGSERIAL PRIMARY KEY,
    serial_number INTEGER,
    registration_number TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    father_name TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast search
CREATE INDEX idx_registration ON rx(registration_number);
CREATE INDEX idx_name ON rx(name);
CREATE INDEX idx_father ON rx(father_name);
```


## Components

### 1. Supabase Sync Script

**File:** `scripts/sync_to_supabase.py`

Syncs rx.json data to Supabase database daily.

```python
import json
import os
from supabase import create_client

def sync_to_supabase():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    supabase = create_client(url, key)
    
    with open('data/rx.json', 'r') as f:
        records = json.load(f)
    
    for record in records:
        supabase.table('rx').upsert(record).execute()
    
    print(f"Synced {len(records)} records")
```

### 2. GitHub Actions Workflow

Add to `.github/workflows/daily-update.yml`:

```yaml
- name: Sync to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
  run: python scripts/sync_to_supabase.py
```

### 3. Search Website

**File:** `docs/index.html`

Simple search interface that queries Supabase.

```html
<!DOCTYPE html>
<html>
<head>
    <title>TGPC Search</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>TGPC Pharmacist Search</h1>
    <input type="text" id="search" placeholder="Search...">
    <button onclick="search()">Search</button>
    <div id="results"></div>
    
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script src="search.js"></script>
</body>
</html>
```

**File:** `docs/search.js`

```javascript
const supabase = supabase.createClient(
    'YOUR_SUPABASE_URL',
    'YOUR_SUPABASE_ANON_KEY'
);

async function search() {
    const query = document.getElementById('search').value;
    
    const { data } = await supabase
        .from('rx')
        .select('*')
        .or(`registration_number.ilike.%${query}%,name.ilike.%${query}%`)
        .limit(50);
    
    displayResults(data);
}

function displayResults(results) {
    const html = results.map(r => `
        <div>
            <strong>${r.registration_number}</strong> - ${r.name}
            <br>Father: ${r.father_name} | Category: ${r.category}
        </div>
    `).join('');
    
    document.getElementById('results').innerHTML = html;
}
```


## Deployment Steps

### 1. Supabase Setup (One-time)

1. Go to supabase.com and create free account
2. Create new project
3. Run SQL schema in SQL Editor
4. Get API credentials from Settings → API
5. Add to GitHub Secrets:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`

### 2. Update GitHub Actions

1. Add `supabase-py` to requirements.txt
2. Create `scripts/sync_to_supabase.py`
3. Update workflow to include sync step
4. Test manually

### 3. Deploy Website

1. Create `docs/` folder
2. Add `index.html` and `search.js`
3. Update Supabase credentials in search.js
4. Enable GitHub Pages (Settings → Pages → docs folder)
5. Access at `https://yourusername.github.io/tgpc`

### 4. Initial Data Load

1. Run sync script to populate database
2. Verify in Supabase dashboard
3. Test search on website

## Error Handling

- Sync errors: Log and continue with next record
- Search errors: Show user-friendly message
- Network errors: Retry with timeout

## Testing

1. Test sync script locally
2. Test search with various queries
3. Test on mobile device
4. Test on weak network (throttle in DevTools)

## Performance

- Database queries: < 200ms
- Page load: < 2 seconds
- Search results: < 500ms
- Works on 2G/3G networks

## Security

- Use Supabase Row Level Security (RLS) for read-only access
- Anon key safe for client-side (read-only)
- Service key kept secret in GitHub Secrets

## Cost: $0 Forever

- Supabase Free: 500 MB database, 2 GB bandwidth/month
- GitHub Pages: Free
- GitHub Actions: Free (2,000 minutes/month)

Sufficient for 100+ years of data growth and personal use.
