# 🚀 Nutrition Club Setup Guide

## ✅ What You've Done So Far

- ✓ Created Google Spreadsheet
- ✓ Created "Members" sheet with data
- ✓ Created "Attendance" sheet with headers
- ✓ Updated SPREADSHEET_ID in Code.gs (line 118)

**Great! You're halfway done. Follow the remaining steps below.**

---

## 📋 Next Steps (10 minutes)

### Step 1: Deploy Google Apps Script (3 minutes)

**Note:** This step is required regardless of hosting option. The Apps Script acts as your backend API.

1. **Copy the Code.gs content**
   - Open the `Code.gs` file from your Nutrition Club folder
   - Select all content (Ctrl+A)
   - Copy it (Ctrl+C)

2. **Open Apps Script Editor**
   - Go to your Google Spreadsheet
   - Click **Extensions** → **Apps Script**
   - A new tab will open with the script editor

3. **Paste the Code**
   - Delete any existing code in the editor
   - Paste your Code.gs content (Ctrl+V)
   - The SPREADSHEET_ID should already be updated (line 118)

4. **Save the Script**
   - Click the 💾 Save icon (or press Ctrl+S)
   - Give it a moment to save

5. **Deploy as Web App**
   - Click **Deploy** (top right) → **New deployment**
   - Click the ⚙️ gear icon next to "Select type"
   - Choose **Web app**
   - Fill in:
     - **Description**: Nutrition Club API
     - **Execute as**: Me (your email address)
     - **Who has access**: **Anyone**
   - Click **Deploy**
   
6. **Authorize the Script**
   - A popup will appear asking for permissions
   - Click **Authorize access**
   - Choose your Google account
   - Click **Advanced** → **Go to Nutrition Club (unsafe)**
   - Click **Allow**

7. **Copy the Web App URL**
   - After authorization, you'll see a deployment success message
   - **IMPORTANT**: Copy the **Web app URL**
   - It looks like: `https://script.google.com/macros/s/AKfycbx.../exec`
   - Keep this URL safe - you'll need it in the next step!

---

### Step 2: Update Frontend Configuration (30 seconds)

1. **Open config.js**
   - In your Nutrition Club folder, open `config.js`

2. **Paste Your Web App URL**
   - Find line 3:
     ```javascript
     const APPS_SCRIPT_URL = 'YOUR_APPS_SCRIPT_WEB_APP_URL_HERE';
     ```
   - Replace `YOUR_APPS_SCRIPT_WEB_APP_URL_HERE` with your copied URL
   - Example:
     ```javascript
     const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxABC123.../exec';
     ```
   - Save the file (Ctrl+S)

---

### Step 3: Host Your Website (5-7 minutes)

You want to host this as a public website so anyone can access it. Here are the **best FREE options**:

---

## 🌐 Option 1: GitHub Pages (RECOMMENDED - Forever Free)

**Best for:** Technical users, permanent hosting, version control

**Steps:**

1. **Create GitHub Account** (if you don't have one)
   - Go to https://github.com
   - Sign up for free

2. **Install GitHub Desktop** (easiest method)
   - Download from: https://desktop.github.com
   - Install and login with your GitHub account

3. **Create New Repository**
   - Open GitHub Desktop
   - Click "Create a New Repository"
   - Name: `nutrition-club`
   - Local Path: Choose your Desktop
   - Click "Create Repository"

4. **Copy Your Files**
   - Copy ALL files from your "Nutrition Club" folder
   - Paste into the new `nutrition-club` folder created by GitHub Desktop
   - **Important:** Make sure `config.js` has your Web App URL updated!

5. **Publish to GitHub**
   - In GitHub Desktop, you'll see all files listed
   - Add a summary: "Initial commit"
   - Click "Commit to main"
   - Click "Publish repository"
   - Uncheck "Keep this code private" (or keep it private if you want)
   - Click "Publish repository"

6. **Enable GitHub Pages**
   - Go to https://github.com/YOUR_USERNAME/nutrition-club
   - Click "Settings" (top menu)
   - Scroll to "Pages" in left sidebar
   - Under "Source", select "main" branch
   - Click "Save"
   - Wait 1-2 minutes

7. **Get Your Website URL**
   - Your site will be at: `https://YOUR_USERNAME.github.io/nutrition-club/`
   - Share this URL with anyone!

**Pros:**
- ✅ 100% Free forever
- ✅ Custom domain possible
- ✅ HTTPS included
- ✅ Unlimited bandwidth
- ✅ Version control (track changes)
- ✅ Easy updates (just push new changes)

**Cons:**
- ❌ Requires GitHub account
- ❌ Slightly technical

---

## 🌐 Option 2: Netlify (Easiest - Forever Free)

**Best for:** Non-technical users, drag-and-drop simplicity

**Steps:**

1. **Create Netlify Account**
   - Go to https://www.netlify.com
   - Sign up (use GitHub, Google, or Email)

2. **Deploy Your Site**
   - After login, you'll see "Add new site"
   - Click "Deploy manually"
   - **Drag and drop your entire "Nutrition Club" folder** onto the upload area
   - Wait 30 seconds while it uploads
   - Done! You'll get a random URL like: `https://random-name-12345.netlify.app`

3. **Change Your Site Name (Optional)**
   - Click "Site settings"
   - Click "Change site name"
   - Choose a name: `nutrition-club-your-name`
   - Your URL becomes: `https://nutrition-club-your-name.netlify.app`

4. **Update Your Site Later**
   - Go to "Deploys" tab
   - Drag and drop updated files anytime
   - Instant updates!

**Pros:**
- ✅ 100% Free forever (generous limits)
- ✅ Easiest option (drag and drop)
- ✅ Instant deployment
- ✅ HTTPS included
- ✅ Custom domain possible
- ✅ Fast global CDN

**Cons:**
- ❌ To update, you must re-upload files

---

## 🌐 Option 3: Vercel (Similar to Netlify)

**Best for:** Modern, fast deployment

**Steps:**

1. Go to https://vercel.com
2. Sign up (GitHub/Google/Email)
3. Click "Add New" → "Project"
4. Import your GitHub repo OR drag-and-drop files
5. Click "Deploy"
6. Get URL: `https://your-project.vercel.app`

**Pros/Cons:** Same as Netlify

---

## 🌐 Option 4: Render (Another Alternative)

**Best for:** More control, free static hosting

**Steps:**

1. Go to https://render.com
2. Sign up free
3. Click "New" → "Static Site"
4. Connect GitHub repo or upload files
5. Deploy automatically

**Pros/Cons:** Similar to above

---

## 🎯 My Recommendation

**For You:** Use **Netlify** if you want the easiest setup (drag and drop)

**For Team:** Use **GitHub Pages** if you want:
- Version control
- Easy collaboration
- Professional setup

---

## 🔐 Important: Security for Public Website

Since anyone can access your website, you might want to:

**Option A: Keep current simple login**
- Current: `admin` / `admin123` (change these in login.js)
- Anyone with credentials can login
- Fine for small teams

**Option B: Add backend authentication (advanced)**
- Move login validation to Apps Script
- More secure but requires additional setup

**For now, just change the password in login.js:**

1. Open `login.js`
2. Change line 2-3:
   ```javascript
   const VALID_USERNAME = 'yourclub';
   const VALID_PASSWORD = 'SecurePassword123!';
   ```
3. Save and re-upload to your hosting

---

## 📱 Testing Your Website

After hosting:

1. **Test on Desktop**
   - Open your website URL
   - Login
   - Click UMS
   - Mark attendance

2. **Test on Mobile**
   - Open same URL on phone
   - Should be fully responsive
   - All features work

3. **Share with Team**
   - Share the URL: `https://your-site.netlify.app` (or GitHub Pages URL)
   - Share login credentials
   - Everyone can access from anywhere!

---

## 🎉 You're Done!

Your Nutrition Club is now live on the internet!

---

## 🔧 Optional: Change Login Credentials

If you want to change the default login:

1. Open `login.js`
2. Find lines 2-3:
   ```javascript
   const VALID_USERNAME = 'admin';
   const VALID_PASSWORD = 'admin123';
   ```
3. Change to your preferred username/password
4. Save the file

---

## 🆘 Troubleshooting

### "Error loading members" when opening UMS page

**Solution:**
1. Check that you pasted the correct Web App URL in `config.js`
2. Make sure the URL ends with `/exec` (not `/dev`)
3. Verify the script is deployed with "Who has access: Anyone"

### Script authorization issues

**Solution:**
1. In Apps Script editor, click Deploy → Manage deployments
2. Click the edit icon (pencil)
3. Change version to "New version"
4. Click Deploy
5. Copy the new URL and update `config.js` again

### No data showing in UMS table

**Solution:**
1. Check your "Members" sheet has data in rows 2 and below
2. Make sure column headers match exactly:
   - Column A: ID
   - Column B: Name
   - Column C: Phone
   - Column D: Type
   - Column E: PresentDays
   - Column F: TotalDays
   - Column G: Balance
   - Column H: Paid

### Attendance not submitting

**Solution:**
1. Check your "Attendance" sheet has headers in row 1:
   - Column A: MemberID
   - Column B: MemberName
   - Column C: Date
   - Column D: Timestamp
   - Column E: Type
2. Make sure the sheet name is exactly "Attendance" (capital A)

---

## 📊 How It Works

```
You open UMS page
    ↓
Frontend calls your Web App URL
    ↓
Apps Script reads your Google Sheets
    ↓
Data sent back to browser
    ↓
Table displays with your members
    ↓
You mark attendance and click Submit
    ↓
Apps Script writes to Attendance sheet
    ↓
Counts updated in Members sheet
```

All data comes from your Google Sheets - nothing is hardcoded!

---

## 🔄 Updating Your Website

### If using Netlify:
1. Make changes to your files locally
2. Go to Netlify dashboard
3. Drag and drop updated files
4. Done! Changes are live

### If using GitHub Pages:
1. Make changes to your files
2. Open GitHub Desktop
3. Commit changes
4. Push to GitHub
5. Website updates automatically in 1-2 minutes

---

## 📱 Next Steps After Setup

1. **Add more members** - Just add rows to your Google Sheets Members sheet
2. **Start tracking** - Mark daily attendance from the website
3. **View records** - Check the Attendance sheet for history
4. **Share the website** - Give the URL to your team members

---

## 🎓 File Structure (Simple)

```
Your Folder/
├── index.html          → Entry point (opens login)
├── login.html          → Login page
├── home.html           → Dashboard
├── ums.html            → Attendance tracking
├── config.js           → ⚠️ UPDATE THIS with Web App URL
├── Code.gs             → ✅ ALREADY UPDATED - Deploy this
├── styles.css          → All styling
└── (other files)       → Supporting files
```

---

## ✅ Setup Checklist

Mark off as you complete:

**Backend Setup:**
- [x] Created Google Spreadsheet
- [x] Added Members sheet with data
- [x] Added Attendance sheet with headers
- [x] Updated SPREADSHEET_ID in Code.gs
- [ ] Copied Code.gs to Apps Script editor
- [ ] Deployed as Web App
- [ ] Copied Web App URL
- [ ] Updated config.js with Web App URL

**Website Hosting:**
- [ ] Choose hosting option (Netlify/GitHub Pages/Vercel)
- [ ] Create account on chosen platform
- [ ] Upload/Deploy website files
- [ ] Get public website URL
- [ ] Test on desktop browser
- [ ] Test on mobile browser
- [ ] Change login password (optional but recommended)
- [ ] Share URL with team

---

## 🌟 Summary

**What you're doing:**
1. ✅ Google Sheets = Your database (already done!)
2. ⏳ Apps Script = Your backend API (deploy now)
3. ⏳ Netlify/GitHub = Your website hosting (choose one)

**Result:** A professional website accessible from anywhere in the world!

**Total time needed: ~10-15 minutes** ⏱️

---

**Need help? Check the troubleshooting section above or re-read the steps carefully.**
