"""Simple Flask API for pharmacist search."""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tgpc.database.schema import PharmacistDB

app = Flask(__name__)
CORS(app)

# Use absolute path to database
db_path = Path(__file__).parent.parent / "data" / "pharmacists.db"
db = PharmacistDB(str(db_path))


@app.route('/api/search')
def search():
    """Search pharmacists."""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Query must be at least 2 characters'}), 400
    
    db.connect()
    results = db.search(query, limit)
    db.close()
    
    return jsonify({
        'query': query,
        'count': len(results),
        'results': results
    })


@app.route('/api/stats')
def stats():
    """Get database statistics."""
    db.connect()
    stats = db.get_stats()
    db.close()
    
    return jsonify(stats)


@app.route('/api/health')
def health():
    """Health check."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
