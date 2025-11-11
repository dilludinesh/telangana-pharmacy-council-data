# TGPC Pharmacist Search API

Simple Flask API for searching pharmacist records from SQLite database.

## Endpoints

### GET /api/search
Search pharmacists by name or registration number.

**Parameters:**
- `q` (required): Search query (min 2 characters)
- `limit` (optional): Max results to return (default: 100)

**Example:**
```
GET /api/search?q=syama&limit=10
```

**Response:**
```json
{
  "query": "syama",
  "count": 1,
  "results": [
    {
      "serial_number": 82611,
      "registration_number": "TG076262",
      "name": "Syama Prasad K",
      "father_name": "K Venkateshwar Rao",
      "category": "DPharm"
    }
  ]
}
```

### GET /api/stats
Get database statistics.

**Response:**
```json
{
  "total_records": 82611,
  "by_category": {
    "BPharm": 57533,
    "DPharm": 16112,
    "MPharm": 2354,
    "PharmD": 6352,
    "QC": 29,
    "QP": 231
  }
}
```

### GET /api/health
Health check endpoint.

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

API will be available at: http://localhost:5000
