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
        window.location.href = 'login.html';
    }
}

checkAuth();

// Global variables
let allMembers = [];          // Stores ALL members loaded from Google Sheets
let filteredMembers = [];     // Stores filtered members (after search)
let tempAttendance = new Set(); // Stores temporarily checked member IDs (not saved until Submit)
let selectedDate = '';        // Currently selected date in YYYY-MM-DD format

// Initialize page on load
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('attendanceDate').value = today;
    selectedDate = today;
    
    // Load members from Google Sheets for today's date
    loadMembers();
    
    // Set up event listeners
    document.getElementById('attendanceDate').addEventListener('change', handleDateChange);
    document.getElementById('searchBox').addEventListener('input', handleSearch);
    document.getElementById('submitBtn').addEventListener('click', handleSubmit);
});

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
    try {
        showLoading(true);
        
        // Build the GET request URL with query parameters
        // APPS_SCRIPT_URL comes from config.js
        const url = `${APPS_SCRIPT_URL}?action=getMembers&date=${selectedDate}`;
        
        // Fetch data from Google Apps Script
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to fetch members');
        }
        
        // Parse JSON response
        const data = await response.json();
        
        // Populate allMembers with data from Google Sheets
        // This is the ONLY source of data - nothing is hardcoded!
        allMembers = data.members || [];
        filteredMembers = [...allMembers]; // Copy for search functionality
        
        // Clear temporary attendance checkboxes after reload
        tempAttendance.clear();
        
        // Render the table with the loaded data
        renderTable();
        
        // Update bottom bar statistics
        updateStats();
        
        showLoading(false);
        
    } catch (error) {
        console.error('Error loading members:', error);
        showLoading(false);
        alert('Error loading members. Please check your backend configuration.\n\nMake sure:\n1. APPS_SCRIPT_URL is set in config.js\n2. Apps Script is deployed as web app\n3. Your Google Sheets has data in the Members sheet');
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
    const tbody = document.getElementById('membersTableBody');
    tbody.innerHTML = ''; // Clear existing rows
    
    if (filteredMembers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="no-data">No members found</td></tr>';
        return;
    }
    
    // Loop through each member from Google Sheets and create a table row
    filteredMembers.forEach(member => {
        const row = createMemberRow(member);
        tbody.appendChild(row);
    });
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

// Handle date change
function handleDateChange(e) {
    selectedDate = e.target.value;
    loadMembers(); // Reload data for new date
}

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
        
        // Send to backend
        const response = await fetch(APPS_SCRIPT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(attendanceData)
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
    // Total members
    document.getElementById('totalMembers').textContent = allMembers.length;
    
    // Present today (already marked + temporary)
    const markedCount = allMembers.filter(m => m.attendanceMarked).length;
    const tempCount = tempAttendance.size;
    document.getElementById('presentToday').textContent = markedCount + tempCount;
    
    // Total amount (from members already marked)
    const totalAmount = allMembers
        .filter(m => m.attendanceMarked)
        .reduce((sum, m) => sum + m.paid, 0);
    document.getElementById('totalAmount').textContent = `₹${totalAmount}`;
}

// Update stats when temporary attendance changes
function updateTempStats() {
    const markedCount = allMembers.filter(m => m.attendanceMarked).length;
    const tempCount = tempAttendance.size;
    document.getElementById('presentToday').textContent = markedCount + tempCount;
}

// Show/hide loading indicator
function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
    document.getElementById('membersTable').style.display = show ? 'none' : 'table';
}

// Handle edit button click
function handleEdit(memberId) {
    alert(`Edit functionality for member ${memberId} - Coming soon!`);
}
