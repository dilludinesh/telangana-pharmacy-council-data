// Supabase Configuration
const SUPABASE_URL = 'https://vhgpyvzgmvhijqgsapnk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoZ3B5dnpnbXZoaWpxZ3NhcG5rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4Njc1MjAsImV4cCI6MjA3ODQ0MzUyMH0.Cp4oyw2M72RCFnsKeLg49hSMvGs4pm6-ul0sFmAasRs';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// State
let currentResults = [];
let displayedResults = [];
let currentFilters = {
    category: 'all'
};
let currentSort = 'reg-desc';
let searchTimeout;
let currentPage = 1;
const RESULTS_PER_PAGE = 100;


// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkConnection();
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

    // Filter chips
    document.querySelectorAll('.filter-chip').forEach(btn => {
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

// Check database connection status
async function checkConnection() {
    const statusEl = document.getElementById('connectionStatus');

    try {
        // Get current date text if it exists
        const dateEl = document.getElementById('lastUpdated');
        const dateText = dateEl ? dateEl.textContent : 'Loading...';

        statusEl.className = 'header-status connecting';
        statusEl.innerHTML = `<span class="status-dot"></span><span>Busy</span><span class="status-separator">|</span><span class="status-date" id="lastUpdated">${dateText}</span>`;

        // Try a simple query to check connection
        const { data, error } = await supabase
            .from('rx')
            .select('id')
            .limit(1);

        if (error) throw error;

        // Connected successfully
        // Get date text again in case it changed while we were waiting
        const currentDateEl = document.getElementById('lastUpdated');
        const currentDateText = currentDateEl ? currentDateEl.textContent : dateText;

        statusEl.className = 'header-status connected';
        statusEl.innerHTML = `<span class="status-dot"></span><span>Live</span><span class="status-separator">|</span><span class="status-date" id="lastUpdated">${currentDateText}</span>`;

    } catch (error) {
        console.error('Connection error:', error);

        // Get date text again
        const dateEl = document.getElementById('lastUpdated');
        const dateText = dateEl ? dateEl.textContent : 'Loading...';

        statusEl.className = 'header-status error';
        statusEl.innerHTML = `<span class="status-dot"></span><span>Offline</span><span style="margin-left: 8px; color: inherit; font-weight: 500;" id="lastUpdated">${dateText}</span>`;
    }
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

            // Check if cached data has the new format (with categories object)
            if (data.categories) {
                // Display cached data immediately
                displayAnalytics(data);

                // If cache is fresh (less than 1 hour old), we're done
                if (age < CACHE_DURATION) {
                    console.log('✓ Analytics loaded from cache (age: ' + Math.round(age / 60000) + ' min)');
                    return;
                }

                console.log('Cache expired, fetching fresh data...');
            } else {
                // Old cache format, clear it and fetch fresh
                console.log('Old cache format detected, clearing and fetching fresh data...');
                localStorage.removeItem(CACHE_KEY);
            }
        } else {
            // No cache, show loading state
            document.getElementById('totalRecords').textContent = '...';
        }

        // Fetch fresh data from Supabase
        const { count: total, error: totalError } = await supabase
            .from('rx')
            .select('*', { count: 'exact', head: true });

        if (totalError) throw totalError;

        // Get all unique categories using a more efficient query
        // We'll query each known category plus check for others
        const knownCategories = ['BPharm', 'DPharm', 'MPharm', 'PharmD'];

        // First, get counts for known categories
        const knownPromises = knownCategories.map(cat =>
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', cat)
        );

        // Also get a sample to check for other categories
        const { data: sampleData, error: sampleError } = await supabase
            .from('rx')
            .select('category')
            .limit(10000);

        if (sampleError) throw sampleError;

        // Get all unique categories from sample
        const allUniqueCategories = [...new Set(sampleData.map(r => r.category))].filter(c => c).sort();
        console.log('All unique categories found:', allUniqueCategories);

        // Find categories not in known list
        const additionalCategories = allUniqueCategories.filter(cat => !knownCategories.includes(cat));

        // Get counts for additional categories
        const additionalPromises = additionalCategories.map(cat =>
            supabase.from('rx').select('*', { count: 'exact', head: true }).eq('category', cat)
        );

        const allPromises = [...knownPromises, ...additionalPromises];
        const allResults = await Promise.all(allPromises);
        const allCategories = [...knownCategories, ...additionalCategories];

        const stats = {
            total: total,
            categories: {}
        };

        allCategories.forEach((cat, index) => {
            const count = allResults[index]?.count || 0;
            stats.categories[cat] = count;
            console.log(`Category ${cat}: ${count}`);
        });

        console.log('✓ Analytics loaded from Supabase:', stats);

        // Save to cache
        localStorage.setItem(CACHE_KEY, JSON.stringify({
            data: stats,
            timestamp: now
        }));

        // Display fresh data
        displayAnalytics(stats);

    } catch (error) {
        console.error('Error loading analytics:', error);
        // Fallback to approximate values if query fails
        displayAnalytics({
            total: 82621,
            categories: {
                'BPharm': 57543,
                'DPharm': 16112,
                'MPharm': 2354,
                'PharmD': 6352
            }
        });
    }
}

// Display analytics on the page
function displayAnalytics(stats) {
    console.log('displayAnalytics called with:', stats);

    document.getElementById('totalRecords').textContent = stats.total.toLocaleString();

    if (stats.categories) {
        console.log('All categories found:', Object.keys(stats.categories));

        // Update all categories
        Object.keys(stats.categories).forEach(cat => {
            const elementId = cat.toLowerCase() + 'Count';
            const element = document.getElementById(elementId);
            console.log(`Looking for element: ${elementId}, found:`, element);
            if (element) {
                element.textContent = stats.categories[cat].toLocaleString();
                console.log(`Set ${cat} to ${stats.categories[cat]}`);
            } else {
                console.warn(`Element not found for category: ${cat}`);
            }
        });

        // Get the stats grid and filters container
        const statsGrid = document.querySelector('.stats-grid');
        const filtersContainer = document.querySelector('.filters');

        // Remove any previously added dynamic elements
        statsGrid.querySelectorAll('.stat-card.dynamic').forEach(card => card.remove());
        filtersContainer.querySelectorAll('.filter-chip.dynamic').forEach(chip => chip.remove());

        // Get all categories sorted
        const allCategories = Object.keys(stats.categories).sort();
        const knownCategories = ['BPharm', 'DPharm', 'MPharm', 'PharmD'];
        const additionalCategories = allCategories.filter(cat => !knownCategories.includes(cat));

        // Add stat cards and filter chips for additional categories
        additionalCategories.forEach(cat => {
            // Add stat card
            const card = document.createElement('div');
            card.className = 'stat-card dynamic';
            card.innerHTML = `
                <div class="stat-header">
                    <div class="stat-content">
                        <h3>${cat}</h3>
                        <div class="stat-value">${stats.categories[cat].toLocaleString()}</div>
                    </div>
                </div>
            `;
            statsGrid.appendChild(card);

            // Add filter chip
            const chip = document.createElement('button');
            chip.className = 'filter-chip dynamic';
            chip.setAttribute('data-filter', 'category');
            chip.setAttribute('data-value', cat);
            chip.textContent = cat;
            chip.addEventListener('click', function () {
                document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilters.category = cat;
                const query = document.getElementById('searchInput').value.trim();
                if (query.length >= 2) {
                    performSearch();
                }
            });
            filtersContainer.appendChild(chip);
        });

        console.log('Displayed categories:', allCategories);
        if (additionalCategories.length > 0) {
            console.log('Additional categories added:', additionalCategories);
        }
    }

    // Set last updated date with time
    // Custom format: TUE 02DEC2025 AT 00:00
    const now = new Date();

    const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
    const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

    const dayName = days[now.getDay()];
    const dayNum = String(now.getDate()).padStart(2, '0');
    const monthName = months[now.getMonth()];
    const year = now.getFullYear();

    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');

    const dateStr = `${dayNum}${monthName}${year}`;
    const timeStr = `${hours}:${minutes}`;

    console.log('About to set lastUpdated element');
    const lastUpdatedEl = document.getElementById('lastUpdated');
    console.log('lastUpdatedEl:', lastUpdatedEl);
    if (lastUpdatedEl) {
        lastUpdatedEl.textContent = `${dateStr} ${timeStr}`;
        console.log('Successfully set date to:', `${dateStr} ${timeStr}`);
    } else {
        console.error('lastUpdated element not found');
    }
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

        const { data, error } = await queryBuilder.limit(5000);

        if (error) throw error;

        currentResults = data;
        currentPage = 1;
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

    switch (sortValue) {
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

    currentPage = 1;
    displayResults(sorted);
}

// Load more results
function loadMore() {
    currentPage++;
    displayResults(displayedResults, true);
}

// Display results with pagination
function displayResults(data, append = false) {
    const resultsDiv = document.getElementById('results');
    const resultsCount = document.getElementById('resultsCount');

    displayedResults = data;
    resultsCount.textContent = data.length.toLocaleString();

    if (data.length === 0) {
        resultsDiv.innerHTML = '<div class="empty-state">No results found. Try different search terms or filters.</div>';
        return;
    }

    // Calculate pagination
    const startIndex = append ? (currentPage - 1) * RESULTS_PER_PAGE : 0;
    const endIndex = currentPage * RESULTS_PER_PAGE;
    const paginatedData = data.slice(0, endIndex);
    const hasMore = endIndex < data.length;

    const tableHtml = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Registration Number</th>
                    <th>Name</th>
                    <th>Father's Name</th>
                    <th>Category</th>
                </tr>
            </thead>
            <tbody>
                ${paginatedData.map(record => `
                    <tr>
                        <td><span class="reg-number">${record.registration_number}</span></td>
                        <td>${record.name}</td>
                        <td>${record.father_name || 'N/A'}</td>
                        <td><span class="badge ${record.category.toLowerCase()}">${record.category}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    const loadMoreHtml = hasMore ? `
        <div style="text-align: center; margin-top: 24px; padding-top: 24px; border-top: 1px solid #f4f4f5;">
            <button class="btn btn-secondary" onclick="loadMore()">
                Load More (${Math.min(RESULTS_PER_PAGE, data.length - endIndex)} of ${data.length - endIndex} remaining)
            </button>
        </div>
    ` : '';

    resultsDiv.innerHTML = tableHtml + loadMoreHtml;
}

// Reset search
function resetSearch() {
    // Clear search input
    document.getElementById('searchInput').value = '';

    // Reset filters to "All Categories"
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.value === 'all') {
            btn.classList.add('active');
        }
    });
    currentFilters.category = 'all';

    // Reset sort to default
    document.getElementById('sortSelect').value = 'reg-desc';
    currentSort = 'reg-desc';

    // Clear results
    currentResults = [];
    displayedResults = [];
    currentPage = 1;

    // Hide results panel
    document.getElementById('resultsPanel').style.display = 'none';
    document.getElementById('error').innerHTML = '';
    document.getElementById('loading').style.display = 'none';
}

// Export results to PDF
function exportResults() {
    if (currentResults.length === 0) {
        alert('No results to export. Please perform a search first.');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Add title
    doc.setFontSize(18);
    doc.setTextColor(0, 204, 102);
    doc.text('TGPC Rx Registry', 14, 20);

    // Add subtitle with date
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    const dateStr = new Date().toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
    doc.text(`Search Results - ${dateStr}`, 14, 27);
    doc.text(`Total Records: ${currentResults.length}`, 14, 32);

    // Prepare table data
    const tableData = currentResults.map(record => [
        record.registration_number,
        record.name,
        record.father_name || 'N/A',
        record.category
    ]);

    // Add table
    doc.autoTable({
        startY: 38,
        head: [['Registration Number', 'Name', 'Father\'s Name', 'Category']],
        body: tableData,
        theme: 'striped',
        headStyles: {
            fillColor: [0, 204, 102],
            textColor: [255, 255, 255],
            fontStyle: 'bold',
            fontSize: 10
        },
        bodyStyles: {
            fontSize: 9
        },
        alternateRowStyles: {
            fillColor: [250, 250, 250]
        },
        columnStyles: {
            0: { cellWidth: 40 },
            1: { cellWidth: 60 },
            2: { cellWidth: 50 },
            3: { cellWidth: 30 }
        },
        margin: { top: 38, left: 14, right: 14 }
    });

    // Save PDF
    doc.save(`tgpc_rx_search_${new Date().toISOString().split('T')[0]}.pdf`);
}
