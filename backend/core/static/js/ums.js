// UMS Attendance Management JavaScript
// Implements pending tick UX with API integration

let MEMBERS = [];
let pending = {};
let currentDate = new Date().toISOString().split('T')[0];

// Get CSRF token for POST requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Fetch members from API
async function fetchMembers(search = '') {
    try {
        let url = '/api/members/';
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch members');
        }
        
        const data = await response.json();
        MEMBERS = data.results || data;
        renderTable();
    } catch (error) {
        console.error('Error fetching members:', error);
        showMessage('Failed to load members. Please refresh the page.', 'error');
    }
}

// Render members table
function renderTable() {
    const tbody = document.getElementById('membersTable');
    tbody.innerHTML = '';
    
    if (MEMBERS.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-4 py-8 text-center text-gray-500">
                    No members found
                </td>
            </tr>
        `;
        return;
    }
    
    MEMBERS.forEach(member => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';
        
        const isPending = pending[member.id];
        const paidAmount = isPending ? isPending.paid_amount : 0;
        const isPresent = isPending ? isPending.present : false;
        
        tr.innerHTML = `
            <td class="px-4 py-3 text-sm">${member.full_name}</td>
            <td class="px-4 py-3 text-sm">${member.phone || '-'}</td>
            <td class="px-4 py-3 text-sm">${member.membership_label || ''}</td>
            <td class="px-4 py-3 text-sm ${member.balance > 0 ? 'text-red-600' : 'text-green-600'}">
                ₹${parseFloat(member.balance).toFixed(2)}
            </td>
            <td class="px-4 py-3">
                <input type="number" 
                       min="0" 
                       step="0.01" 
                       id="paid-${member.id}" 
                       value="${paidAmount}"
                       class="border rounded px-2 py-1 w-24 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                       ${isPresent ? '' : 'disabled'} />
            </td>
            <td class="px-4 py-3 text-center">
                <input type="checkbox" 
                       id="chk-${member.id}" 
                       ${isPresent ? 'checked' : ''}
                       class="w-5 h-5 cursor-pointer accent-blue-600" />
            </td>
        `;
        
        tbody.appendChild(tr);
        
        // Add event listeners
        const checkbox = document.getElementById(`chk-${member.id}`);
        const paidInput = document.getElementById(`paid-${member.id}`);
        
        checkbox.addEventListener('change', function(e) {
            handleCheckboxChange(member.id, e.target.checked, paidInput);
        });
        
        paidInput.addEventListener('input', function(e) {
            handlePaidAmountChange(member.id, parseFloat(e.target.value) || 0);
        });
    });
}

// Handle checkbox change
function handleCheckboxChange(memberId, checked, paidInput) {
    if (checked) {
        const paidVal = parseFloat(paidInput.value) || 0;
        pending[memberId] = {
            member_id: memberId,
            present: true,
            paid_amount: paidVal,
            method: 'cash'
        };
        paidInput.disabled = false;
    } else {
        delete pending[memberId];
        paidInput.disabled = true;
        paidInput.value = 0;
    }
    updatePendingUI();
}

// Handle paid amount change
function handlePaidAmountChange(memberId, amount) {
    if (pending[memberId]) {
        pending[memberId].paid_amount = amount;
        updatePendingUI();
    }
}

// Update pending sidebar UI
function updatePendingUI() {
    const list = document.getElementById('pendingList');
    const totalPendingEl = document.getElementById('totalPending');
    const totalAmountEl = document.getElementById('totalAmount');
    const submitBtn = document.getElementById('submitAttendance');
    
    list.innerHTML = '';
    let total = 0;
    let count = 0;
    
    if (Object.keys(pending).length === 0) {
        list.innerHTML = '<li class="text-sm text-gray-500">No pending entries</li>';
        submitBtn.disabled = true;
    } else {
        submitBtn.disabled = false;
        
        for (const id in pending) {
            const p = pending[id];
            const member = MEMBERS.find(m => m.id == id);
            
            if (member) {
                const li = document.createElement('li');
                li.className = 'text-sm bg-gray-50 p-2 rounded flex justify-between items-center';
                li.innerHTML = `
                    <span class="flex-1">${member.full_name}</span>
                    <span class="text-green-600 font-semibold">₹${(p.paid_amount || 0).toFixed(2)}</span>
                `;
                list.appendChild(li);
                
                total += Number(p.paid_amount || 0);
                count++;
            }
        }
    }
    
    totalPendingEl.textContent = count;
    totalAmountEl.textContent = '₹' + total.toFixed(2);
}

// Submit attendance to API
async function submitAttendance() {
    const entries = Object.values(pending);
    
    if (entries.length === 0) {
        showMessage('No pending attendance to submit', 'warning');
        return;
    }
    
    if (!confirm(`Submit attendance for ${entries.length} member(s)?`)) {
        return;
    }
    
    const submitBtn = document.getElementById('submitAttendance');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch('/api/attendance/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                date: currentDate,
                entries: entries
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit attendance');
        }
        
        const result = await response.json();
        
        if (result.status === 'ok') {
            showMessage(
                `Successfully submitted ${result.submitted_count} attendance records. Total received: ₹${result.total_received.toFixed(2)}`,
                'success'
            );
            
            // Clear pending
            pending = {};
            updatePendingUI();
            
            // Refresh members list
            await fetchMembers(document.getElementById('search').value);
        } else {
            throw new Error(result.message || 'Submission failed');
        }
    } catch (error) {
        console.error('Error submitting attendance:', error);
        showMessage('Failed to submit attendance: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Attendance';
    }
}

// Generate PDF report
function generatePDF() {
    const url = `/api/report/daily/?date=${currentDate}`;
    window.open(url, '_blank');
}

// Show message notification
function showMessage(message, type = 'info') {
    // Simple alert for now - can be replaced with toast notification
    alert(message);
}

// Initialize date inputs and display
function initializeDates() {
    const todayDateEl = document.getElementById('todayDate');
    const dateSelectorEl = document.getElementById('dateSelector');
    
    const today = new Date();
    const formattedDate = today.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    todayDateEl.textContent = formattedDate;
    dateSelectorEl.value = currentDate;
    
    dateSelectorEl.addEventListener('change', function(e) {
        currentDate = e.target.value;
        todayDateEl.textContent = new Date(currentDate).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        // Clear pending when date changes
        pending = {};
        updatePendingUI();
        renderTable();
    });
}

// Initialize search
function initializeSearch() {
    const searchInput = document.getElementById('search');
    let debounceTimer;
    
    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchMembers(e.target.value);
        }, 300);
    });
}

// Initialize event listeners
function initialize() {
    initializeDates();
    initializeSearch();
    
    document.getElementById('submitAttendance').addEventListener('click', submitAttendance);
    document.getElementById('generatePDF').addEventListener('click', generatePDF);
    
    // Load initial data
    fetchMembers();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}
