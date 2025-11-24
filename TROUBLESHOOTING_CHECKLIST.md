# 🔍 Troubleshooting Checklist - Members Not Loading

## Step 1: Test Your Backend Connection
1. Open http://localhost:8080/test-backend.html
2. Click "Test Get Members" button
3. Read the error message carefully

---

## Step 2: Verify Google Sheets Structure

### Open your Google Sheet and check:

✅ **Sheet 1 Name: Must be exactly "Members"** (case-sensitive)
- Not "members" or "MEMBERS" or "Member List"
- Exactly: **Members**

✅ **Sheet 2 Name: Must be exactly "Attendance"**
- Not "attendance" or "ATTENDANCE"  
- Exactly: **Attendance**

✅ **Members Sheet - Column Headers (Row 1):**
```
A       B       C       D       E           F           G       H
ID   | Name | Phone | Type | PresentDays | TotalDays | Balance | Paid
```

✅ **Members Sheet - Sample Data (Row 2+):**
```
M001 | John Doe    | 9876543210 | UMS   | 0  | 26 | 0    | 5000
M002 | Jane Smith  | 9876543211 | Trial | 0  | 3  | 0    | 500
M003 | Mike Wilson | 9876543212 | UMS   | 0  | 26 | 0    | 5000
```

✅ **Attendance Sheet - Column Headers (Row 1):**
```
A          B            C       D           E
MemberID | MemberName | Date | Timestamp | Type
```

---

## Step 3: Verify Apps Script Deployment

### In Google Sheets:
1. Go to **Extensions > Apps Script**
2. Check if the `SPREADSHEET_ID` in Code.gs matches your sheet

### To get your Spreadsheet ID:
- Look at your Google Sheets URL:
- `https://docs.google.com/spreadsheets/d/`**`1Y3T-6zYiGn_AMMCwkspAR8zBXNNmZemppkxKD4ec5gg`**`/edit`
- The long string is your SPREADSHEET_ID
- Make sure it matches the one in Code.gs (line 68)

### Current Spreadsheet ID in Code.gs:
```
1Y3T-6zYiGn_AMMCwkspAR8zBXNNmZemppkxKD4ec5gg
```

---

## Step 4: Test Apps Script Directly

### In Google Sheets Apps Script Editor:
1. Open **Extensions > Apps Script**
2. Find the `testSetup()` function at the bottom
3. Click the **Run** button (▶️) next to the function name
4. Check the **Execution log** (View > Logs)

### Expected Output:
```
Testing setup...
✓ Spreadsheet found
✓ Members sheet found
  3 members in sheet
✓ Attendance sheet found
Setup test complete!
```

---

## Step 5: Verify Web App Deployment

### In Apps Script Editor:
1. Click **Deploy > Manage deployments**
2. Check the deployment settings:
   - ✅ **Execute as:** Me (your email)
   - ✅ **Who has access:** Anyone
3. Copy the **Web app URL**
4. Make sure it matches the one in `config.js`

### Current URL in config.js:
```
https://script.google.com/macros/s/AKfycbxXtchjzEOyp8Mlcqq3yORND65XdAPrI2KLaUD7O6s1im9GHywsuFQuiHroGSh7Qxs/exec
```

---

## Step 6: Common Issues & Solutions

### ❌ "No members found"
**Cause:** Empty Members sheet or wrong sheet name
**Solution:** 
- Check sheet is named exactly "Members"
- Add at least one row of data below the headers

### ❌ "HTTP error! status: 404"
**Cause:** Wrong Apps Script URL or deployment not public
**Solution:**
- Redeploy Apps Script as web app
- Set "Who has access" to "Anyone"
- Update URL in config.js

### ❌ "Script function not found: doGet"
**Cause:** Apps Script not saved or deployed
**Solution:**
- Save the script (Ctrl+S)
- Deploy as NEW deployment (not update existing)

### ❌ "Authorization required"
**Cause:** Apps Script needs permission
**Solution:**
- Run `testSetup()` function in Apps Script
- Grant permissions when prompted
- Redeploy after authorization

### ❌ "Cannot read property 'getRange'"
**Cause:** Sheet doesn't exist or wrong SPREADSHEET_ID
**Solution:**
- Verify SPREADSHEET_ID in Code.gs
- Verify sheet names are exactly "Members" and "Attendance"

---

## Step 7: Manual Data Entry Test

### Add this test data to your Members sheet:

```
Row 1 (Headers):
ID    | Name          | Phone      | Type  | PresentDays | TotalDays | Balance | Paid
------+---------------+------------+-------+-------------+-----------+---------+------
M001  | Test Member 1 | 9999999991 | UMS   | 0           | 26        | 0       | 5000
M002  | Test Member 2 | 9999999992 | Trial | 0           | 3         | 0       | 500
M003  | Test Member 3 | 9999999993 | UMS   | 0           | 26        | 0       | 5000
```

After adding data:
1. Save the sheet
2. Run `testSetup()` in Apps Script
3. Refresh your UMS page
4. Click "Test Get Members" in test page

---

## Need More Help?

### Run the test page:
1. Open: http://localhost:8080/test-backend.html
2. Click "Test Get Members"
3. Share the exact error message

### Check browser console:
1. Press F12 to open Developer Tools
2. Go to Console tab
3. Look for red error messages
4. Share the error details
