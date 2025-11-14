// Supabase Configuration
const SUPABASE_URL = 'https://vhgpyvzgmvhijqgsapnk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoZ3B5dnpnbXZoaWpxZ3NhcG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4Njc1MjAsImV4cCI6MjA3ODQ0MzUyMH0.Cp4oyw2M72RCFnsKeLg49hSMvGs4pm6-ul0sFmAasRs';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// DOM elements
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const filterBtns = document.querySelectorAll('.filter-btn');

// State
let currentCategory = 'all';
let searchTimeout;

// Search function with instant results
async function search(query) {
    resultsDiv.style.display = 'none';
    errorDiv.innerHTML = '';
    
    if (query.length < 2) {
        return;
    }
    
    loadingDiv.style.display = 'block';
    
    try {
        let queryBuilder = supabase
            .from('rx')
            .select('registration_number,name,father_name,category')
            .or(`registration_number.ilike.%${query}%,name.ilike.%${query}%,father_name.ilike.%${query}%`);
        
        // Apply category filter
        if (currentCategory !== 'all') {
            queryBuilder = queryBuilder.eq('category', currentCategory);
        }
        
        const { data, error } = await queryBuilder
            .order('registration_number', { ascending: false })
            .limit(100);
        
        if (error) throw error;
        
        loadingDiv.style.display = 'none';
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        loadingDiv.style.display = 'none';
        errorDiv.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
    }
}

// Display results in table format
function displayResults(data) {
    resultsDiv.style.display = 'block';
    
    if (data.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
        return;
    }
    
    const html = `
        <table class="results-table">
            <thead>
                <tr>
                    <th>Registration</th>
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
                        <td><span class="category-badge">${record.category}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    resultsDiv.innerHTML = html;
}

// Debounce function - reduced delay for faster response
function debounce(func, delay) {
    return function(...args) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Event listeners
searchInput.addEventListener('input', debounce((e) => {
    search(e.target.value.trim());
}, 300)); // Reduced from 500ms to 300ms

// Filter buttons
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.dataset.category;
        
        // Re-run search if there's a query
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            search(query);
        }
    });
});

// Focus search input
searchInput.focus();
