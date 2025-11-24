# ⚡ Quick Reference Card

## 📖 Which File to Read?

1. **README.md** - Start here for overview
2. **HOSTING_OPTIONS.md** - Compare free hosting platforms
3. **SETUP_GUIDE.md** - Complete step-by-step setup

---

## 🎯 Quick Decision: Which Hosting?

**Want easiest?** → **Netlify** (drag & drop, 2 minutes)

**Want professional?** → **GitHub Pages** (version control, 7 minutes)

**Want modern?** → **Vercel** (fast & easy, 3 minutes)

---

## 📋 What You Need to Do

### ✅ Already Done:
- Google Spreadsheet created
- Members data added
- Attendance sheet ready
- SPREADSHEET_ID set in Code.gs

### ⏳ To Do Now:

**Step 1:** Deploy Apps Script (Required)
- Copy Code.gs to Google Apps Script
- Deploy as Web App
- Get Web App URL

**Step 2:** Update Frontend
- Paste Web App URL in config.js

**Step 3:** Host Website (Choose One)

**Option A: Netlify (Recommended)**
```
1. Go to netlify.com
2. Sign up
3. Drag "Nutrition Club" folder
4. Get URL: nutrition-club-yourname.netlify.app
```

**Option B: GitHub Pages**
```
1. Install GitHub Desktop
2. Create repository
3. Add files and publish
4. Enable Pages
5. Get URL: username.github.io/nutrition-club
```

**Option C: Vercel**
```
1. Go to vercel.com
2. Sign up
3. Upload files
4. Get URL: nutrition-club.vercel.app
```

---

## 🔑 Default Login

- Username: `admin`
- Password: `admin123`

**Change in:** `login.js` (lines 2-3)

---

## 🆘 Quick Troubleshooting

**"Error loading members"**
→ Check config.js has correct Web App URL

**Can't deploy Apps Script**
→ Make sure "Who has access" is set to "Anyone"

**Website not loading**
→ Make sure all files are uploaded including config.js

**Login not working**
→ Check username/password in login.js

---

## 📞 Support

1. Read SETUP_GUIDE.md thoroughly
2. Check HOSTING_OPTIONS.md for hosting help
3. Verify all steps completed in order

---

## ⏱️ Time Estimates

- Apps Script setup: 3 minutes
- Config update: 30 seconds
- Netlify hosting: 2 minutes
- GitHub Pages hosting: 7 minutes
- Vercel hosting: 3 minutes

**Total: 10-15 minutes to go live!**

---

## 🎉 After Setup

1. Test login
2. Click UMS
3. Mark attendance
4. Share URL with team
5. Enjoy!

---

**Everything free. Everything forever. ✨**
