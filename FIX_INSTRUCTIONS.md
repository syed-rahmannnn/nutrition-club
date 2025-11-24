# Bug Fix Instructions

## Problem Identified
The website couldn't load data from Google Sheets due to a **CORS (Cross-Origin Resource Sharing)** configuration issue between your GitHub Pages site and Google Apps Script.

## What Was Fixed

### 1. Frontend Changes (ums.js)
- ✅ Updated `fetch()` calls to use proper configuration with `redirect: 'follow'`
- ✅ Changed attendance submission from POST to GET method (avoids CORS preflight)
- ✅ Added better error messages with details

### 2. Backend Changes (Code.gs)
- ✅ Updated `doGet()` to handle both fetching members AND submitting attendance
- ✅ Added support for attendance submission via GET parameters

## Next Steps - REDEPLOY YOUR APPS SCRIPT

**You MUST redeploy the Apps Script for the fix to work!**

### Step-by-Step:

1. **Open your Apps Script**
   - Go to: https://script.google.com/u/0/home/projects/12ba7RubEEFzaBCtKZbOyslVfUMxVYkc6tJ_1YqQZjlqKRFsHuFO0emAs/edit
   - Or: Open your Google Sheet → Extensions → Apps Script

2. **Replace the code**
   - Select ALL the code in Code.gs
   - Delete it
   - Copy the ENTIRE content from your local `Code.gs` file
   - Paste it into the Apps Script editor

3. **Deploy as NEW version**
   - Click **Deploy** button (top right)
   - Click **Manage deployments**
   - Click the **Edit** icon (pencil) next to "Nutrition Club API"
   - Under "Version", select **"New version"**
   - Click **Deploy**
   - **IMPORTANT**: Copy the new Web App URL if it changed

4. **Test the deployment**
   - Open your website: https://syed-rahmannnn.github.io/UMS Attendance
   - Check the browser console (F12) for any errors
   - The members should now load from your Google Sheet

## Verification Checklist

After redeploying, verify:

- [ ] Apps Script is deployed with **"Execute as: Me"**
- [ ] Apps Script is deployed with **"Who has access: Anyone"**
- [ ] The Web App URL in `config.js` matches the deployed URL
- [ ] Your Google Sheet has:
  - [ ] "Members" sheet with data
  - [ ] "Attendance" sheet (can be empty)
  - [ ] Correct column headers in both sheets

## What the Fix Does

### Before Fix:
```
Browser (GitHub Pages) → [CORS Error] ❌ → Google Apps Script
```

### After Fix:
```
Browser (GitHub Pages) → [GET with redirect] ✅ → Google Apps Script → Google Sheets
```

The fix uses GET requests with proper redirect handling, which Google Apps Script supports without CORS issues.

## Testing Steps

1. **Open your website**
   ```
   https://syed-rahmannnn.github.io/UMS%20Attendance
   ```

2. **Open Browser Console** (Press F12)
   - Look for any red error messages
   - Should see: "Loading members..." then data appears

3. **Check the table**
   - Should see all members from your Google Sheet
   - Names, phone numbers, balances should match your sheet

4. **Test attendance submission**
   - Select a member checkbox
   - Click "Submit"
   - Should see "Attendance submitted successfully!"
   - Refresh the page - checkbox should become a green tick ✓

## If Still Not Working

1. **Check the console errors** (F12)
   - Copy the exact error message

2. **Verify the Apps Script URL**
   - Open `config.js`
   - Make sure URL ends with `/exec`
   - Should look like: `https://script.google.com/macros/s/AKfycbx.../exec`

3. **Test Apps Script directly**
   - Copy your Apps Script URL
   - Add this to the end: `?action=getMembers&date=2024-11-24`
   - Paste in browser
   - Should see JSON with your members data

4. **Check Google Sheet**
   - Open your Google Sheet
   - Verify "Members" sheet has data in rows 2+
   - Verify column headers match exactly:
     ```
     ID | Name | Phone | Type | PresentDays | TotalDays | Balance | Paid
     ```

## Common Issues

### "Failed to fetch members"
- **Cause**: Apps Script not deployed or URL wrong
- **Fix**: Redeploy Apps Script, update config.js

### "Execution completed" but no data
- **Cause**: Google Sheet is empty or column names don't match
- **Fix**: Check your Members sheet has data starting from row 2

### Members load but submit doesn't work
- **Cause**: Old Apps Script code still deployed
- **Fix**: Deploy as NEW VERSION (step 3 above)

## Contact
If you still face issues after following these steps, provide:
1. Screenshot of browser console (F12) showing errors
2. Screenshot of your Google Sheet Members tab
3. The Apps Script Web App URL from config.js
