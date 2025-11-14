// Supabase Configuration
const SUPABASE_URL = 'https://vhgpyvzgmvhijqgsapnk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoZ3B5dnpnbXZoaWpxZ3NhcG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4Njc1MjAsImV4cCI6MjA3ODQ0MzUyMH0.Cp4oyw2M72RCFnsKeLg49hSMvGs4pm6-ul0sFmAasRs';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// State
let currentResults = [];
let currentFilters = {
    category: 'all'
};
let currentSort = 'reg-desc';
let searchTimeout;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadAnalytics();
});

function setupEventListeners() {
    // Search input with debounce
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (e.target.value.trim().length >= 2) {
                performSearch();
            }
        }, 300);
    });

    // Enter key to search
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const filterType = btn.dataset.filter;
            const filterValue = btn.dataset.value;
            
            // Update active state
            document.querySelectorAll(`[data-filter="${filterType}"]`).forEach(b => {
                b.classList.remove('active');
            });
            btn.classList.add('active');
            
            // Update filter
            currentFilters[filterType] = filterValue;
            
            // Re-search if there's a query
            const query = document.getElementById('searchInput').value.trim();
            if (query.length >= 2) {
                performSearch();
            }
        });
    });
}

// Load analytics with localStorage caching for instant display
async function loadAnalytics() {
    const CACHE_KEY = 'tgpc_analytics';
    const CACHE_DURATION = 60 * 60 * 1000; // 1 hour in milliseconds
    
    try {
        // Try to load from cache first
        const cached = localStorage.getItem(CACHE_KEY);
        const now = Date.now();
        
        if (cached) {
            const { data, timestamp } = JSON.parse(cached);
            const age = now - timestamp;
            
            // Display cached data immediately
            displayAnalytics(data);
            
            // If cache is fresh (less than 1 hour old), we're done
            if (age < CACHE_DURATION) {
                console.log('✓ Analytics loaded from cache (age: ' + Math.round(age / 60000) + ' min)');
                return;
            }
            
            console.log('Cache expired, fetching fresh data...');
        } else {
            // No cache, show loading state
            document.getElementById('totalRecords').textContent = '...';
            document.getElementById('bpharmCount').textContent = '...';
            document.getElementById('dpharmCount').textContent = '...';
            document.getElementById('mpharmCount').textContent = '...';
            document.getElementById('pharmdCount').textContent = '...';
        }
        
        // Fetch fresh data from Supabase
        const { count: total, error: totalError } = await supabase
            .from('rx')
            .select('*', { count: 'exact', head: true });
        
        if (totalError) throw totalError;
        
        // Get counts by category in parallel
        const [bpharmRes, dpharmRes, mpharmRes, pharmdRes] = await Promise.all([
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', 'BPharm'),
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', 'DPharm'),
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', 'MPharm'),
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', 'PharmD')
        ]);
        
        const stats = {
            total: total,
            bpharm: bpharmRes.count || 0,
            dpharm: dpharmRes.count || 0,
            mpharm: mpharmRes.count || 0,
            pharmd: pharmdRes.count || 0
        };
        
        // Save to cache
        localStorage.setItem(CACHE_KEY, JSON.stringify({
            data: stats,
            timestamp: now
        }));
        
        // Display fresh data
        displayAnalytics(stats);
        
        console.log('✓ Analytics loaded from Supabase and cached:', stats);
        
    } catch (error) {
        console.error('Error loading analytics:', error);
        // Fallback to approximate values if query fails
        displayAnalytics({
            total: 82621,
            bpharm: 57543,
            dpharm: 16112,
            mpharm: 2354,
            pharmd: 6352
        });
    }
}

// Display analytics on the page
function displayAnalytics(stats) {
    document.getElementById('totalRecords').textContent = stats.total.toLocaleString();
    document.getElementById('bpharmCount').textContent = stats.bpharm.toLocaleString();
    document.getElementById('dpharmCount').textContent = stats.dpharm.toLocaleString();
    document.getElementById('mpharmCount').textContent = stats.mpharm.toLocaleString();
    document.getElementById('pharmdCount').textContent = stats.pharmd.toLocaleString();
    
    // Set last updated date
    const today = new Date().toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
    });
    document.getElementById('lastUpdated').textContent = today;
}

// Perform search
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const resultsPanel = document.getElementById('resultsPanel');
    
    if (query.length < 2) {
        resultsPanel.style.display = 'none';
        return;
    }
    
    loadingDiv.style.display = 'block';
    resultsPanel.style.display = 'none';
    errorDiv.innerHTML = '';
    
    try {
        let queryBuilder = supabase
            .from('rx')
            .select('registration_number,name,father_name,category')
            .or(`registration_number.ilike.%${query}%,name.ilike.%${query}%,father_name.ilike.%${query}%`);
        
        // Apply category filter
        if (currentFilters.category !== 'all') {
            queryBuilder = queryBuilder.eq('category', currentFilters.category);
        }
        
        const { data, error } = await queryBuilder.limit(200);
        
        if (error) throw error;
        
        currentResults = data;
        loadingDiv.style.display = 'none';
        resultsPanel.style.display = 'block';
        
        sortResults();
        
    } catch (error) {
        console.error('Search error:', error);
        loadingDiv.style.display = 'none';
        errorDiv.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
    }
}

// Sort results
function sortResults() {
    const sortValue = document.getElementById('sortSelect').value;
    currentSort = sortValue;
    
    let sorted = [...currentResults];
    
    switch(sortValue) {
        case 'reg-desc':
            sorted.sort((a, b) => b.registration_number.localeCompare(a.registration_number));
            break;
        case 'reg-asc':
            sorted.sort((a, b) => a.registration_number.localeCompare(b.registration_number));
            break;
        case 'name-asc':
            sorted.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            sorted.sort((a, b) => b.name.localeCompare(a.name));
            break;
    }
    
    displayResults(sorted);
}

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const resultsCount = document.getElementById('resultsCount');
    
    resultsCount.textContent = data.length.toLocaleString();
    
    if (data.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No results found. Try different search terms or filters.</div>';
        return;
    }
    
    const html = `
        <table class="results-table">
            <thead>
                <tr>
                    <th>Registration Number</th>
                    <th>Name</th>
                    <th>Father's Name</th>
                    <th>Category</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(record => `
                    <tr>
                        <td><span class="reg-number">${record.registration_number}</span></td>
                        <td>${record.name}</td>
                        <td>${record.father_name || 'N/A'}</td>
                        <td><span class="category-badge ${record.category.toLowerCase()}">${record.category}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    resultsDiv.innerHTML = html;
}

// Export results to CSV
function exportResults() {
    if (currentResults.length === 0) {
        alert('No results to export. Please perform a search first.');
        return;
    }
    
    // Create CSV content
    const headers = ['Registration Number', 'Name', 'Father\'s Name', 'Category'];
    const rows = currentResults.map(record => [
        record.registration_number,
        record.name,
        record.father_name || 'N/A',
        record.category
    ]);
    
    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.map(cell => `"${cell}"`).join(',') + '\n';
    });
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `tgpc_rx_search_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
