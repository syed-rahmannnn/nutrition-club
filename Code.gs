/**
 * GOOGLE APPS SCRIPT BACKEND FOR NUTRITION CLUB WEB APP
 * 
 * ============================================================================
 * IMPORTANT: ALL DATA IS FETCHED DYNAMICALLY FROM GOOGLE SHEETS
 * ============================================================================
 * 
 * This script runs under YOUR Google account, so it can access your private sheets.
 * The frontend (website) does NOT directly access your sheets.
 * Instead, the frontend calls this script via HTTP, and this script reads/writes data.
 * 
 * DATA FLOW:
 * 1. User opens UMS page in browser
 * 2. Frontend sends GET request: ?action=getMembers&date=2024-11-24
 * 3. This script reads from "Members" sheet and "Attendance" sheet
 * 4. Script returns JSON with all member data
 * 5. Frontend displays the data in a table
 * 6. User marks attendance and clicks Submit
 * 7. Frontend sends POST request with selected member IDs
 * 8. This script writes to "Attendance" sheet and updates "Members" sheet
 * 
 * ============================================================================
 * SETUP INSTRUCTIONS:
 * ============================================================================
 * 
 * 1. Open Google Sheets and create a new spreadsheet
 * 2. Create two sheets (tabs) in the spreadsheet:
 *    - "Members" (for member data)
 *    - "Attendance" (for attendance log)
 * 
 * 3. In "Members" sheet, create these columns in Row 1 (headers):
 *    ┌────┬──────┬───────┬──────┬────────────┬──────────┬─────────┬──────┐
 *    │ A  │  B   │   C   │  D   │     E      │    F     │    G    │  H   │
 *    ├────┼──────┼───────┼──────┼────────────┼──────────┼─────────┼──────┤
 *    │ ID │ Name │ Phone │ Type │PresentDays │TotalDays │ Balance │ Paid │
 *    └────┴──────┴───────┴──────┴────────────┴──────────┴─────────┴──────┘
 * 
 * 4. In "Attendance" sheet, create these columns in Row 1 (headers):
 *    ┌──────────┬────────────┬──────┬───────────┬──────┐
 *    │    A     │     B      │  C   │     D     │  E   │
 *    ├──────────┼────────────┼──────┼───────────┼──────┤
 *    │ MemberID │ MemberName │ Date │ Timestamp │ Type │
 *    └──────────┴────────────┴──────┴───────────┴──────┘
 * 
 * 5. Add sample data to Members sheet (starting from row 2):
 *    Example:
 *    M001 | John Doe    | 9876543210 | UMS   | 15 | 26 | 2000 | 3000
 *    M002 | Jane Smith  | 9876543211 | Trial | 2  | 3  | 0    | 500
 *    M003 | Mike Wilson | 9876543212 | UMS   | 20 | 26 | 1000 | 4000
 * 
 * 6. Copy this entire script to Tools > Script Editor in your Google Sheet
 * 
 * 7. Replace SPREADSHEET_ID below with your spreadsheet ID:
 *    - Look at your Google Sheet URL
 *    - URL format: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
 *    - Copy the long string of letters/numbers between /d/ and /edit
 *    - Paste it in SPREADSHEET_ID constant below (line 68)
 * 
 * 8. Deploy as Web App:
 *    - Click Deploy > New deployment
 *    - Click gear icon next to "Select type"
 *    - Choose "Web app"
 *    - Set "Execute as" to: Me (your email)
 *    - Set "Who has access" to: Anyone
 *    - Click Deploy
 *    - Authorize the script when prompted
 *    - COPY THE WEB APP URL (you'll need this!)
 * 
 * 9. Update config.js in your frontend code:
 *    - Open config.js
 *    - Paste the web app URL in APPS_SCRIPT_URL
 * 
 * 10. (Optional) Update login credentials in login.js if needed
 * 
 * ============================================================================
 * JSON RESPONSE STRUCTURE (when frontend requests data):
 * ============================================================================
 * 
 * GET Request: ?action=getMembers&date=2024-11-24
 * 
 * Response:
 * {
 *   "success": true,
 *   "members": [
 *     {
 *       "id": "M001",              // From Members sheet column A
 *       "name": "John Doe",        // From Members sheet column B
 *       "phone": "9876543210",     // From Members sheet column C
 *       "type": "UMS",             // From Members sheet column D
 *       "count": "15/26",          // Constructed from columns E/F
 *       "balance": 2000,           // From Members sheet column G
 *       "paid": 3000,              // From Members sheet column H
 *       "attendanceMarked": false  // Checked against Attendance sheet for this date
 *     },
 *     {
 *       "id": "M002",
 *       "name": "Jane Smith",
 *       "phone": "9876543211",
 *       "type": "Trial",
 *       "count": "2/3",
 *       "balance": 0,
 *       "paid": 500,
 *       "attendanceMarked": true   // This member is already marked present for this date
 *     }
 *   ]
 * }
 * 
 * The frontend receives this JSON and dynamically creates table rows.
 * NO data is hardcoded in the frontend - everything comes from your Google Sheet!
 */

// ==================== CONFIGURATION ====================
// Replace with your Google Spreadsheet ID
const SPREADSHEET_ID = '1Y3T-6zYiGn_AMMCwkspAR8zBXNNmZemppkxKD4ec5gg';

// Sheet names
const MEMBERS_SHEET_NAME = 'Members';
const ATTENDANCE_SHEET_NAME = 'Attendance';

// ==================== MAIN HANDLERS ====================

/**
 * Handle GET requests
 * Used to fetch member data and submit attendance
 */
function doGet(e) {
  try {
    const action = e.parameter.action;
    
    if (action === 'getMembers') {
      const date = e.parameter.date || getTodayDate();
      const members = getMembers(date);
      
      return createJsonResponse({
        success: true,
        members: members
      });
    }
    
    if (action === 'submitAttendance') {
      const date = e.parameter.date;
      const memberIdsJson = e.parameter.memberIds;
      
      if (!date || !memberIdsJson) {
        throw new Error('Invalid data: date and memberIds required');
      }
      
      const memberIds = JSON.parse(memberIdsJson);
      
      if (!memberIds || memberIds.length === 0) {
        throw new Error('No members selected');
      }
      
      submitAttendance(date, memberIds);
      
      return createJsonResponse({
        success: true,
        message: 'Attendance submitted successfully'
      });
    }
    
    return createJsonResponse({
      success: false,
      error: 'Invalid action'
    });
    
  } catch (error) {
    Logger.log('Error in doGet: ' + error.toString());
    return createJsonResponse({
      success: false,
      error: error.toString()
    });
  }
}

/**
 * Handle POST requests
 * Used to submit attendance
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;
    
    if (action === 'submitAttendance') {
      const date = data.date;
      const memberIds = data.memberIds;
      
      if (!date || !memberIds || memberIds.length === 0) {
        throw new Error('Invalid data: date and memberIds required');
      }
      
      submitAttendance(date, memberIds);
      
      return createJsonResponse({
        success: true,
        message: 'Attendance submitted successfully'
      });
    }
    
    return createJsonResponse({
      success: false,
      error: 'Invalid action'
    });
    
  } catch (error) {
    return createJsonResponse({
      success: false,
      error: error.toString()
    });
  }
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Get all members with their attendance status for a specific date
 * 
 * DATA SOURCE: Reads from the "Members" sheet in your Google Spreadsheet
 * 
 * SHEET STRUCTURE (Members sheet):
 * Row 1 (Headers): ID | Name | Phone | Type | PresentDays | TotalDays | Balance | Paid
 * Row 2+: Data rows (one per member)
 * 
 * COLUMN MAPPING:
 * Column A (row[0]) = Member ID (e.g., "M001")
 * Column B (row[1]) = Member Name (e.g., "John Doe")
 * Column C (row[2]) = Phone Number (e.g., "9876543210")
 * Column D (row[3]) = Type (either "UMS" or "Trial")
 * Column E (row[4]) = Present Days (number, e.g., 15)
 * Column F (row[5]) = Total Days (26 for UMS, 3 for Trial)
 * Column G (row[6]) = Balance amount in ₹ (e.g., 2000)
 * Column H (row[7]) = Paid amount in ₹ (e.g., 3000)
 * 
 * RETURNS: Array of member objects with this structure:
 * {
 *   id: "M001",                    // From column A
 *   name: "John Doe",              // From column B
 *   phone: "9876543210",           // From column C
 *   type: "UMS",                   // From column D
 *   count: "15/26",                // Constructed from columns E/F
 *   balance: 2000,                 // From column G
 *   paid: 3000,                    // From column H
 *   attendanceMarked: true/false   // Calculated from Attendance sheet for the given date
 * }
 * 
 * @param {string} date - Date in YYYY-MM-DD format (e.g., "2024-11-24")
 * @return {Array} Array of member objects with attendance status
 */
function getMembers(date) {
  // Open the spreadsheet using the ID configured above
  // NOTE: This script runs under YOUR account, so it has access to your private sheets
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  
  // Get references to both sheets
  const membersSheet = ss.getSheetByName(MEMBERS_SHEET_NAME);      // "Members" sheet
  const attendanceSheet = ss.getSheetByName(ATTENDANCE_SHEET_NAME); // "Attendance" sheet
  
  // Read ALL data from Members sheet (includes header row)
  // This reads the entire data range and returns a 2D array
  const membersData = membersSheet.getDataRange().getValues();
  const members = [];
  
  // Build a map of which members are present on the requested date
  // This prevents showing checkboxes for already-marked members
  const attendanceData = attendanceSheet.getDataRange().getValues();
  const attendanceMap = {}; // Format: { "M001": true, "M002": true, ... }
  
  // Loop through attendance records (skip header row at index 0)
  for (let i = 1; i < attendanceData.length; i++) {
    const recordDate = formatDate(attendanceData[i][2]);  // Column C: Date
    const memberId = attendanceData[i][0];                // Column A: MemberID
    
    // If attendance record matches the requested date, mark this member as present
    if (recordDate === date) {
      attendanceMap[memberId] = true;
    }
  }
  
  // Process each member row (skip header row at index 0)
  for (let i = 1; i < membersData.length; i++) {
    const row = membersData[i];
    
    // Skip empty rows (in case there are gaps in the sheet)
    if (!row[0]) continue;
    
    // Map sheet columns to JSON object
    // This is the EXACT structure sent to the frontend
    const member = {
      id: row[0],                                    // Column A: Member ID
      name: row[1],                                  // Column B: Name
      phone: row[2],                                 // Column C: Phone
      type: row[3],                                  // Column D: Type (UMS/Trial)
      count: row[4] + '/' + row[5],                  // Columns E/F: PresentDays/TotalDays
      balance: parseInt(row[6]) || 0,                // Column G: Balance
      paid: parseInt(row[7]) || 0,                   // Column H: Paid
      attendanceMarked: attendanceMap[row[0]] === true  // Calculated: true if present on this date
    };
    
    members.push(member);
  }
  
  return members;
}

/**
 * Submit attendance for multiple members
 */
function submitAttendance(date, memberIds) {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const membersSheet = ss.getSheetByName(MEMBERS_SHEET_NAME);
  const attendanceSheet = ss.getSheetByName(ATTENDANCE_SHEET_NAME);
  
  const timestamp = new Date();
  const membersData = membersSheet.getDataRange().getValues();
  
  // Process each member
  memberIds.forEach(memberId => {
    // Check if attendance already exists for this member and date
    if (attendanceExists(attendanceSheet, memberId, date)) {
      return; // Skip if already marked
    }
    
    // Find member in members sheet
    let memberRow = -1;
    let memberName = '';
    let memberType = '';
    
    for (let i = 1; i < membersData.length; i++) {
      if (membersData[i][0] === memberId) {
        memberRow = i + 1; // +1 for 1-based index
        memberName = membersData[i][1];
        memberType = membersData[i][3];
        break;
      }
    }
    
    if (memberRow === -1) {
      return; // Member not found
    }
    
    // Add attendance record
    attendanceSheet.appendRow([
      memberId,
      memberName,
      date,
      timestamp,
      'Present'
    ]);
    
    // Update count in members sheet
    const currentPresentDays = membersSheet.getRange(memberRow, 5).getValue();
    const newPresentDays = parseInt(currentPresentDays) + 1;
    membersSheet.getRange(memberRow, 5).setValue(newPresentDays);
  });
}

/**
 * Check if attendance already exists for a member on a specific date
 */
function attendanceExists(attendanceSheet, memberId, date) {
  const data = attendanceSheet.getDataRange().getValues();
  
  for (let i = 1; i < data.length; i++) {
    const recordMemberId = data[i][0];
    const recordDate = formatDate(data[i][2]);
    
    if (recordMemberId === memberId && recordDate === date) {
      return true;
    }
  }
  
  return false;
}

/**
 * Format date to YYYY-MM-DD
 */
function formatDate(date) {
  if (typeof date === 'string') {
    return date;
  }
  
  if (date instanceof Date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  return '';
}

/**
 * Get today's date in YYYY-MM-DD format
 */
function getTodayDate() {
  return formatDate(new Date());
}

/**
 * Create JSON response with CORS headers
 */
function createJsonResponse(data) {
  const output = ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
  
  return output;
}

/**
 * Test function to verify setup
 * Run this from Script Editor to test your configuration
 */
function testSetup() {
  Logger.log('Testing setup...');
  
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    Logger.log('✓ Spreadsheet found');
    
    const membersSheet = ss.getSheetByName(MEMBERS_SHEET_NAME);
    if (membersSheet) {
      Logger.log('✓ Members sheet found');
      const memberCount = membersSheet.getLastRow() - 1;
      Logger.log(`  ${memberCount} members in sheet`);
    } else {
      Logger.log('✗ Members sheet NOT found');
    }
    
    const attendanceSheet = ss.getSheetByName(ATTENDANCE_SHEET_NAME);
    if (attendanceSheet) {
      Logger.log('✓ Attendance sheet found');
    } else {
      Logger.log('✗ Attendance sheet NOT found');
    }
    
    Logger.log('Setup test complete!');
    
  } catch (error) {
    Logger.log('✗ Error: ' + error.toString());
  }
}
