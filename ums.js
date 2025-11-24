// UMS Attendance Page JavaScript
// ============================================================================
// IMPORTANT: ALL DATA IS LOADED DYNAMICALLY FROM GOOGLE SHEETS
// ============================================================================
// 
// This page does NOT contain any hardcoded member data.
// When the page loads, it automatically fetches all member data from the
// Google Apps Script backend, which reads from your private Google Sheets.
// 
// DATA FLOW:
// 1. Page loads → loadMembers() is called
// 2. Sends GET request to Apps Script: ?action=getMembers&date=2024-11-24
// 3. Apps Script reads from "Members" sheet and "Attendance" sheet
// 4. Returns JSON with all member data
// 5. allMembers array is populated with the data
// 6. renderTable() creates table rows dynamically from allMembers
// 7. When date changes, loadMembers() is called again with new date
// 
// ============================================================================

// Check authentication
function checkAuth() {
    if (sessionStorage.getItem('isLoggedIn') !== 'true') {
        console.log('User not logged in, redirecting to login page');
        window.location.href = 'login.html';
    } else {
        console.log('User authenticated');
    }
}

// Verify config is loaded
if (typeof APPS_SCRIPT_URL === 'undefined') {
    console.error('CRITICAL: APPS_SCRIPT_URL is not defined! Check if config.js is loaded.');
    alert('Configuration error: APPS_SCRIPT_URL not found. Please check config.js file.');
} else {
    console.log('Config loaded successfully');
}

checkAuth();

// Global variables
let allMembers = [];          // Stores ALL members loaded from Google Sheets
let filteredMembers = [];     // Stores filtered members (after search)
let tempAttendance = new Set(); // Stores temporarily checked member IDs (not saved until Submit)
let selectedDate = '';        // Currently selected date in YYYY-MM-DD format

// Initialize page on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Starting initialization');
    
    try {
        // Set today's date as default and display it
        const today = new Date().toISOString().split('T')[0];
        selectedDate = today;
        console.log('Selected date:', selectedDate);
        
        displayCurrentDate();
        
        // Load members from Google Sheets for today's date
        loadMembers();
        
        // Set up event listeners
        const searchBox = document.getElementById('searchBox');
        if (searchBox) {
            searchBox.addEventListener('input', handleSearch);
        } else {
            console.error('Search box element not found');
        }
        
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', handleSubmit);
        } else {
            console.error('Submit button element not found');
        }
        
        // Toggle floating summary
        const toggleBtn = document.getElementById('toggleBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleSummary);
        } else {
            console.error('Toggle button element not found');
        }
        
        console.log('Initialization complete');
    } catch (error) {
        console.error('Error during initialization:', error);
        alert('Error initializing page: ' + error.message);
    }
});

/**
 * Display the current date in a readable format
 */
function displayCurrentDate() {
    try {
        const dateElement = document.getElementById('currentDate');
        if (!dateElement) {
            console.error('Current date element not found');
            return;
        }
        
        const date = new Date(selectedDate);
        console.log('Displaying date:', date);
        
        // Try multiple date formatting options for better mobile compatibility
        try {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            dateElement.textContent = date.toLocaleDateString('en-US', options);
        } catch (e) {
            // Fallback for browsers with limited locale support
            console.warn('Locale formatting failed, using fallback:', e);
            dateElement.textContent = date.toDateString();
        }
    } catch (error) {
        console.error('Error displaying date:', error);
    }
}

/**
 * Toggle the floating summary box
 */
function toggleSummary() {
    try {
        const summaryContent = document.getElementById('summaryContent');
        const toggleBtn = document.getElementById('toggleBtn');
        
        if (!summaryContent || !toggleBtn) {
            console.error('Summary elements not found');
            return;
        }
        
        const icon = toggleBtn.querySelector('i');
        
        summaryContent.classList.toggle('collapsed');
        
        if (icon) {
            if (summaryContent.classList.contains('collapsed')) {
                icon.className = 'fas fa-chevron-down';
            } else {
                icon.className = 'fas fa-chevron-up';
            }
        }
    } catch (error) {
        console.error('Error toggling summary:', error);
    }
}

/**
 * Load members from Google Sheets via Apps Script backend
 * 
 * This function is called:
 * - When the page first loads
 * - When the date is changed
 * - After attendance is submitted (to refresh and show updated counts)
 * 
 * IMPORTANT: This is a dynamic fetch - NO hardcoded data!
 * 
 * REQUEST: GET to Apps Script URL
 * Format: ?action=getMembers&date=2024-11-24
 * 
 * RESPONSE: JSON object
 * {
 *   "success": true,
 *   "members": [
 *     {
 *       "id": "M001",
 *       "name": "John Doe",
 *       "phone": "9876543210",
 *       "type": "UMS",
 *       "count": "15/26",
 *       "balance": 2000,
 *       "paid": 3000,
 *       "attendanceMarked": false
 *     },
 *     ...
 *   ]
 * }
 * 
 * The response is stored in allMembers[] and then rendered into the table.
 */
async function loadMembers() {
    console.log('=== Starting loadMembers ===');
    console.log('APPS_SCRIPT_URL:', APPS_SCRIPT_URL);
    console.log('Selected date:', selectedDate);
    
    try {
        showLoading(true);
        
        // Build the GET request URL with query parameters
        // APPS_SCRIPT_URL comes from config.js
        const url = `${APPS_SCRIPT_URL}?action=getMembers&date=${selectedDate}`;
        console.log('Fetching from URL:', url);
        
        // Fetch data from Google Apps Script with proper configuration
        const response = await fetch(url, {
            method: 'GET',
            redirect: 'follow',
            mode: 'cors',
            cache: 'no-cache'
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            console.error('HTTP error! status:', response.status);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse JSON response
        const data = await response.json();
        console.log('Received data:', data);
        
        // Check if response indicates success
        if (!data.success) {
            console.error('Backend returned error:', data.error);
            throw new Error(data.error || 'Unknown error from backend');
        }
        
        // Populate allMembers with data from Google Sheets
        // This is the ONLY source of data - nothing is hardcoded!
        allMembers = data.members || [];
        filteredMembers = [...allMembers]; // Copy for search functionality
        
        console.log('Loaded members count:', allMembers.length);
        
        // Clear temporary attendance checkboxes after reload
        tempAttendance.clear();
        
        // Render the table with the loaded data
        renderTable();
        
        // Update bottom bar statistics
        updateStats();
        
        showLoading(false);
        console.log('=== loadMembers completed successfully ===');
        
    } catch (error) {
        console.error('=== Error loading members ===');
        console.error('Error type:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        showLoading(false);
        
        // More detailed error message
        let errorMsg = 'Error loading members: ' + error.message + '\n\n';
        errorMsg += 'Please check:\n';
        errorMsg += '1. Internet connection\n';
        errorMsg += '2. APPS_SCRIPT_URL in config.js\n';
        errorMsg += '3. Apps Script deployment settings\n';
        errorMsg += '4. Browser console for detailed errors';
        
        alert(errorMsg);
    }
}

/**
 * Render table with current filtered members
 * 
 * IMPORTANT: This function creates table rows DYNAMICALLY from the data
 * loaded from Google Sheets. No rows are hardcoded in the HTML.
 * 
 * The table body starts empty, and this function:
 * 1. Clears any existing rows
 * 2. Loops through filteredMembers[] array (data from Google Sheets)
 * 3. Creates a new <tr> for each member
 * 4. Populates all 9 columns with data from the member object
 * 
 * Data source: filteredMembers[] which comes from allMembers[] which comes
 * from the Google Sheets via Apps Script API call.
 */
function renderTable() {
    console.log('Rendering table with', filteredMembers.length, 'members');
    
    const tbody = document.getElementById('membersTableBody');
    if (!tbody) {
        console.error('Table body element not found');
        return;
    }
    
    tbody.innerHTML = ''; // Clear existing rows
    
    if (filteredMembers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">No members found</td></tr>';
        return;
    }
    
    // Loop through each member from Google Sheets and create a table row
    try {
        filteredMembers.forEach(member => {
            const row = createMemberRow(member);
            tbody.appendChild(row);
        });
        console.log('Table rendered successfully');
    } catch (error) {
        console.error('Error rendering table:', error);
    }
}

/**
 * Create a single member row dynamically
 * 
 * Takes a member object (from Google Sheets) and creates a complete table row
 * with all 9 columns populated from the member data.
 * 
 * @param {Object} member - Member object from Google Sheets with structure:
 *   {
 *     id: "M001",
 *     name: "John Doe",
 *     phone: "9876543210",
 *     type: "UMS" or "Trial",
 *     count: "15/26",
 *     balance: 2000,
 *     paid: 3000,
 *     attendanceMarked: true/false
 *   }
 * @return {HTMLTableRowElement} Complete table row element
 */
function createMemberRow(member) {
    const row = document.createElement('tr');
    row.dataset.memberId = member.id;
    
    // Profile
    const profileCell = document.createElement('td');
    profileCell.innerHTML = `<div class="profile-avatar">${getInitial(member.name)}</div>`;
    
    // Name
    const nameCell = document.createElement('td');
    nameCell.textContent = member.name;
    
    // Phone
    const phoneCell = document.createElement('td');
    phoneCell.textContent = member.phone;
    
    // Type (UMS/Trial)
    const typeCell = document.createElement('td');
    typeCell.innerHTML = `<span class="type-badge ${member.type.toLowerCase()}">${member.type}</span>`;
    
    // Count
    const countCell = document.createElement('td');
    countCell.textContent = member.count;
    
    // Balance
    const balanceCell = document.createElement('td');
    balanceCell.textContent = `₹${member.balance}`;
    
    // Paid
    const paidCell = document.createElement('td');
    paidCell.textContent = `₹${member.paid}`;
    
    // Attendance
    const attendanceCell = document.createElement('td');
    if (member.attendanceMarked) {
        // Already marked for this date - show permanent green tick
        attendanceCell.innerHTML = '<span class="permanent-tick">✓</span>';
    } else {
        // Show checkbox for temporary marking
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'attendance-checkbox';
        checkbox.checked = tempAttendance.has(member.id);
        checkbox.addEventListener('change', (e) => handleAttendanceToggle(member.id, e.target.checked));
        attendanceCell.appendChild(checkbox);
    }
    
    // Edit
    const editCell = document.createElement('td');
    editCell.innerHTML = '<button class="btn-edit" onclick="handleEdit(\'' + member.id + '\')">Edit</button>';
    
    row.appendChild(profileCell);
    row.appendChild(nameCell);
    row.appendChild(phoneCell);
    row.appendChild(typeCell);
    row.appendChild(countCell);
    row.appendChild(balanceCell);
    row.appendChild(paidCell);
    row.appendChild(attendanceCell);
    row.appendChild(editCell);
    
    return row;
}

// Get first initial from name
function getInitial(name) {
    return name.charAt(0).toUpperCase();
}

// Handle attendance checkbox toggle (temporary)
function handleAttendanceToggle(memberId, isChecked) {
    if (isChecked) {
        tempAttendance.add(memberId);
    } else {
        tempAttendance.delete(memberId);
    }
    updateTempStats();
}

// Note: Date change functionality removed as date is now auto-fetched and displayed
// The page always shows current date attendance

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredMembers = [...allMembers];
    } else {
        filteredMembers = allMembers.filter(member => 
            member.name.toLowerCase().includes(searchTerm)
        );
    }
    
    renderTable();
}

// Handle submit button
async function handleSubmit() {
    if (tempAttendance.size === 0) {
        alert('Please select at least one member to mark attendance.');
        return;
    }
    
    if (!confirm(`Submit attendance for ${tempAttendance.size} member(s)?`)) {
        return;
    }
    
    try {
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        
        // Prepare data
        const attendanceData = {
            action: 'submitAttendance',
            date: selectedDate,
            memberIds: Array.from(tempAttendance)
        };
        
        // Send to backend using GET method with query parameters to avoid CORS preflight
        const params = new URLSearchParams({
            action: 'submitAttendance',
            date: selectedDate,
            memberIds: JSON.stringify(Array.from(tempAttendance))
        });
        
        const response = await fetch(`${APPS_SCRIPT_URL}?${params.toString()}`, {
            method: 'GET',
            redirect: 'follow'
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit attendance');
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert('Attendance submitted successfully!');
            // Reload data to show updated counts and permanent ticks
            await loadMembers();
        } else {
            throw new Error(result.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error submitting attendance:', error);
        alert('Error submitting attendance. Please try again.');
    } finally {
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    }
}

// Update statistics in bottom bar
function updateStats() {
    console.log('Updating stats');
    
    try {
        // Total members
        const totalMembersEl = document.getElementById('totalMembers');
        if (totalMembersEl) {
            totalMembersEl.textContent = allMembers.length;
        }
        
        // Present today (already marked + temporary)
        const markedCount = allMembers.filter(m => m.attendanceMarked).length;
        const tempCount = tempAttendance.size;
        const presentTodayEl = document.getElementById('presentToday');
        if (presentTodayEl) {
            presentTodayEl.textContent = markedCount + tempCount;
        }
        
        // Total amount (from members already marked)
        const totalAmount = allMembers
            .filter(m => m.attendanceMarked)
            .reduce((sum, m) => sum + m.paid, 0);
        const totalAmountEl = document.getElementById('totalAmount');
        if (totalAmountEl) {
            totalAmountEl.textContent = `₹${totalAmount}`;
        }
        
        console.log('Stats updated successfully');
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update stats when temporary attendance changes
function updateTempStats() {
    try {
        const markedCount = allMembers.filter(m => m.attendanceMarked).length;
        const tempCount = tempAttendance.size;
        const presentTodayEl = document.getElementById('presentToday');
        if (presentTodayEl) {
            presentTodayEl.textContent = markedCount + tempCount;
        }
    } catch (error) {
        console.error('Error updating temp stats:', error);
    }
}

// Show/hide loading indicator
function showLoading(show) {
    console.log('Show loading:', show);
    
    try {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
        
        const membersTable = document.getElementById('membersTable');
        if (membersTable) {
            membersTable.style.display = show ? 'none' : 'table';
        }
    } catch (error) {
        console.error('Error toggling loading state:', error);
    }
}

// Handle edit button click
function handleEdit(memberId) {
    alert(`Edit functionality for member ${memberId} - Coming soon!`);
}
