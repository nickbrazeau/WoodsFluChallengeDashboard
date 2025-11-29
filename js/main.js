// Woods Lab Dashboard - Main JavaScript Utilities

// Format large numbers with commas
function formatNumber(num) {
    return num.toLocaleString();
}

// Format dates consistently
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show/hide loading indicator
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"></div><p>Loading...</p>';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

// Display error message
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-warning">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
}

// Export table data to CSV
function exportTableToCSV(tableData, filename) {
    // Convert array of objects to CSV
    if (tableData.length === 0) {
        alert('No data to export');
        return;
    }

    const headers = Object.keys(tableData[0]);
    const csvRows = [];

    // Add header row
    csvRows.push(headers.join(','));

    // Add data rows
    tableData.forEach(row => {
        const values = headers.map(header => {
            const value = row[header] || '';
            // Escape quotes and wrap in quotes if contains comma
            const escaped = String(value).replace(/"/g, '""');
            return escaped.includes(',') ? `"${escaped}"` : escaped;
        });
        csvRows.push(values.join(','));
    });

    // Create blob and download
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Create pagination controls
function createPagination(totalItems, itemsPerPage, currentPage, onPageChange) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    let html = '<div class="pagination" style="display: flex; justify-content: center; gap: 0.5rem; margin: 1rem 0;">';

    // Previous button
    if (currentPage > 1) {
        html += `<button class="btn" onclick="${onPageChange}(${currentPage - 1})">Previous</button>`;
    }

    // Page numbers
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage < maxPagesToShow - 1) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    if (startPage > 1) {
        html += `<button class="btn" onclick="${onPageChange}(1)">1</button>`;
        if (startPage > 2) html += '<span style="padding: 0.75rem;">...</span>';
    }

    for (let i = startPage; i <= endPage; i++) {
        const activeStyle = i === currentPage ? 'background-color: var(--royal-blue);' : '';
        html += `<button class="btn" style="${activeStyle}" onclick="${onPageChange}(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += '<span style="padding: 0.75rem;">...</span>';
        html += `<button class="btn" onclick="${onPageChange}(${totalPages})">${totalPages}</button>`;
    }

    // Next button
    if (currentPage < totalPages) {
        html += `<button class="btn" onclick="${onPageChange}(${currentPage + 1})">Next</button>`;
    }

    html += '</div>';
    html += `<p class="text-center" style="color: var(--graphite); margin-top: 0.5rem;">
        Page ${currentPage} of ${totalPages} (${totalItems.toLocaleString()} total items)
    </p>`;

    return html;
}

// Filter array of objects by search term
function filterData(data, searchTerm, fields) {
    if (!searchTerm) return data;

    const term = searchTerm.toLowerCase();
    return data.filter(item => {
        return fields.some(field => {
            const value = item[field];
            return value && String(value).toLowerCase().includes(term);
        });
    });
}

// Sort array of objects by field
function sortData(data, field, ascending = true) {
    return [...data].sort((a, b) => {
        let aVal = a[field];
        let bVal = b[field];

        // Handle null/undefined
        if (aVal == null) return 1;
        if (bVal == null) return -1;

        // Handle numbers
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            return ascending ? aVal - bVal : bVal - aVal;
        }

        // Handle strings
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();

        if (ascending) {
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        } else {
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
        }
    });
}

// Get unique values from array of objects for a given field
function getUniqueValues(data, field) {
    const values = data.map(item => item[field]).filter(val => val != null);
    return [...new Set(values)].sort();
}

// Create select dropdown from array of values
function createSelectOptions(values, selectedValue = '') {
    let html = '<option value="">All</option>';
    values.forEach(value => {
        const selected = value === selectedValue ? 'selected' : '';
        html += `<option value="${value}" ${selected}>${value}</option>`;
    });
    return html;
}

// Check if all required data files exist
async function checkDataFiles() {
    const requiredFiles = [
        'data/config.json',
        'data/sample_statistics.json',
        'data/studies.json'
    ];

    const results = await Promise.all(
        requiredFiles.map(file =>
            fetch(file)
                .then(response => ({ file, exists: response.ok }))
                .catch(() => ({ file, exists: false }))
        )
    );

    const missing = results.filter(r => !r.exists).map(r => r.file);

    if (missing.length > 0) {
        console.error('Missing data files:', missing);
        return false;
    }

    return true;
}

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch('data/config.json');
        return await response.json();
    } catch (error) {
        console.error('Error loading config:', error);
        return null;
    }
}

// Initialize navigation active state
function initializeNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.style.borderBottom = '2px solid var(--persimmon)';
            link.style.paddingBottom = '0.25rem';
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
});
