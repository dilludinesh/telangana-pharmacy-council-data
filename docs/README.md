# TGPC Search Website

Simple search interface for TGPC pharmacist records.

## Setup

1. Open `search.js`
2. Replace these values with your Supabase credentials:
   ```javascript
   const SUPABASE_URL = 'YOUR_SUPABASE_URL';
   const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';
   ```

3. Get your credentials from Supabase:
   - Go to your Supabase project dashboard
   - Click Settings → API
   - Copy "Project URL" and "anon public" key

## Deploy to GitHub Pages

1. Go to your GitHub repo → Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, Folder: `/docs`
4. Click Save

Your website will be live at: `https://yourusername.github.io/tgpc`

## Features

- 🔍 Real-time search
- 📱 Mobile responsive
- ⚡ Fast (queries Supabase directly)
- 🎨 Clean, modern UI
- 🔒 Read-only (uses anon key)

## Search Tips

- Search by registration number: `TS001234`
- Search by name: `Kumar`
- Search by category: `BPharm`
- Search by father's name: `Reddy`
