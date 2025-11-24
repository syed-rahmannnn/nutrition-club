# 🚀 How to Redeploy Your Apps Script (CRITICAL FIX)

## ⚠️ THE ISSUE
Your Apps Script is currently deployed but has CORS issues preventing the website from loading data.

## ✅ THE SOLUTION
You need to create a **NEW deployment** (not update the existing one).

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Open Apps Script Editor
1. Go to your Google Sheet: **Nutrition Club**
2. Click **Extensions** → **Apps Script**
3. You should see your Code.gs file

### Step 2: Copy the Updated Code
1. **Select ALL** the code in Code.gs (Ctrl+A)
2. **DELETE** it
3. Open the file: `Code.gs` from your project folder
4. **Copy ALL** the content from that file
5. **Paste** it into the Apps Script editor
6. Click **Save** (💾 icon or Ctrl+S)

### Step 3: Create a NEW Deployment
⚠️ **IMPORTANT: Do NOT click "Manage deployments"**

1. Click **Deploy** → **New deployment**
2. Click the **⚙️ gear icon** next to "Select type"
3. Select **Web app**
4. Configure these settings:
   ```
   Description: Nutrition Club API v2
   Execute as: Me (your email address)
   Who has access: Anyone
   ```
5. Click **Deploy**
6. Click **Authorize access** if prompted
7. Select your Google account
8. Click **Advanced** → **Go to Untitled project (unsafe)**
9. Click **Allow**

### Step 4: Copy the NEW Web App URL
1. After authorization, you'll see: **"Deployment successfully created"**
2. **COPY** the new Web app URL
   - It looks like: `https://script.google.com/macros/s/AKfycby...NEW_ID.../exec`
   - ⚠️ This will be DIFFERENT from your old URL
3. Click **Done**

### Step 5: Update config.js
1. Open the file: `config.js` in your project
2. Replace the old URL with the NEW URL you just copied:

```javascript
const APPS_SCRIPT_URL = 'PASTE_YOUR_NEW_URL_HERE';
```

3. Save the file (Ctrl+S)

### Step 6: Test the Connection
1. Go to: http://localhost:8080/test-backend.html
2. Click **"Test Get Members"**
3. You should see: ✅ **Request successful!** with your members listed

### Step 7: Test the Main UMS Page
1. Go to: http://localhost:8080/login.html
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Click on **UMS** button
4. You should now see all 9 members from your Google Sheet!

---

## 🔍 VERIFY YOUR DEPLOYMENT

### Check these settings in Apps Script:
1. Click **Deploy** → **Manage deployments**
2. You should see TWO deployments now:
   - ❌ Old one (Archive this if you want)
   - ✅ New one (Active - this is what you'll use)

3. For the NEW deployment, verify:
   - **Execute as:** Me (your-email@gmail.com)
   - **Who has access:** Anyone ← MUST be "Anyone"
   - **Status:** Active

---

## ⚠️ TROUBLESHOOTING

### If you still get "Failed to fetch":
1. Make sure you created a **NEW** deployment (not updated old one)
2. Make sure "Who has access" is set to **Anyone**
3. Make sure you authorized the script when prompted
4. Try opening the Web App URL directly in your browser - you should see JSON

### If you get "Authorization required":
1. Go to Apps Script
2. Run the `testSetup()` function
3. Click **Review Permissions**
4. Authorize the script
5. Create a NEW deployment again

### If members still don't load:
1. Run `testSetup()` function in Apps Script
2. Check **View** → **Logs**
3. Should show:
   ```
   ✓ Spreadsheet found
   ✓ Members sheet found
     9 members in sheet
   ✓ Attendance sheet found
   ```

---

## 📝 FINAL CHECKLIST

- [ ] Copied updated Code.gs to Apps Script
- [ ] Saved the script
- [ ] Created NEW deployment (not updated old one)
- [ ] Set "Who has access" to **Anyone**
- [ ] Authorized the script
- [ ] Copied the NEW web app URL
- [ ] Updated config.js with NEW URL
- [ ] Tested with test-backend.html - sees members
- [ ] Tested UMS page - sees members

---

## 🎉 SUCCESS!
Once you complete these steps, your UMS page will load all 9 members from your Google Sheet!
