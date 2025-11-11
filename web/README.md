# TGPC Pharmacist Search - Web Interface

Simple, fast search interface for Telangana State Pharmacy Council registered pharmacists.

## Features

- 🔍 Real-time search by name or registration number
- 📊 Live statistics (total records, by category)
- ⚡ Fast client-side search (no backend needed)
- 📱 Mobile responsive
- 🎨 Clean, modern UI

## Deployment

This is a static website that can be deployed to:

### GitHub Pages (Free)
1. Push to GitHub
2. Go to Settings > Pages
3. Select branch and `/web` folder
4. Done!

### Netlify (Free)
1. Connect your GitHub repo
2. Set publish directory to `web`
3. Deploy

### Vercel (Free)
1. Import your GitHub repo
2. Set root directory to `web`
3. Deploy

## Local Development

Simply open `index.html` in a browser, or use a local server:

```bash
cd web
python -m http.server 8000
```

Then visit: http://localhost:8000

## Data Update

The `data.json` file is automatically generated from `data/rx.json`:

```bash
python -m tgpc.database.export_web
```

This is done automatically by the GitHub Action on each update.
