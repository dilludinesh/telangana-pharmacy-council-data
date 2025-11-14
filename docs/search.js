// Supabase Configuration
// Replace these with your actual Supabase credentials
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// DOM elements
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const statsDiv = document.getElementById('stats');

// Debounce function to avoid too many requests
let searchTimeout;
function debounce(func, delay) {
    return function(...args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Load total count on page load
async function loadStats() {
    try {
        const { count, error } = await supabase
            .from('rx')
            .select('*', { count: 'exact', head: true });
        
        if (error) throw error;
        
        statsDiv.innerHTML = `📊 Total Records: ${count.toLocaleString()}`;
    } catch (error) {
        console.error('Error loading stats:', error);
        statsDiv.innerHTML = '📊 Database connected';
    }
}

// Search function
async function search(query) {
    // Clear previous results
    resultsDiv.style.display = 'none';
    errorDiv.innerHTML = '';
    
    // Don't search if query is too short
    if (query.length < 2) {
        return;
    }
    
    // Show loading
    loadingDiv.style.display = 'block';
    
    try {
        // Search in registration_number, name, father_name, and category
        const { data, error } = await supabase
            .from('rx')
            .select('*')
            .or(`registration_number.ilike.%${query}%,name.ilike.%${query}%,father_name.ilike.%${query}%,category.ilike.%${query}%`)
            .order('registration_number', { ascending: false })
            .limit(50);
        
        if (error) throw error;
        
        // Hide loading
        loadingDiv.style.display = 'none';
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        loadingDiv.style.display = 'none';
        errorDiv.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
    }
}

// Display search results
function displayResults(data) {
    resultsDiv.style.display = 'block';
    
    if (data.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No results found. Try a different search term.</div>';
        return;
    }
    
    const html = data.map(record => `
        <div class="result-item">
            <div class="result-reg">${record.registration_number}</div>
            <div class="result-name">${record.name}</div>
            <div class="result-details">
                Father's Name: ${record.father_name || 'N/A'}
            </div>
            <span class="result-category">${record.category}</span>
        </div>
    `).join('');
    
    resultsDiv.innerHTML = html;
}

// Event listeners
searchInput.addEventListener('input', debounce((e) => {
    search(e.target.value.trim());
}, 500));

// Load stats on page load
loadStats();

// Focus search input
searchInput.focus();
