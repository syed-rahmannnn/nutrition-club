# 🎯 QUICK FIX - 3 Minutes

## The Problem
❌ "Failed to fetch" error = Apps Script deployment issue

## The Solution (3 steps)

### 1️⃣ Copy the Updated Code.gs
```
1. In your project folder, open: Code.gs
2. Select ALL (Ctrl+A) and Copy (Ctrl+C)
3. Go to Apps Script Editor (Extensions > Apps Script)
4. Select ALL existing code and DELETE it
5. Paste the new code (Ctrl+V)
6. Save (Ctrl+S)
```

### 2️⃣ Create NEW Deployment
```
1. Click: Deploy → New deployment
2. Click gear icon → Select "Web app"
3. Set:
   Execute as: Me
   Who has access: Anyone  ← CRITICAL!
4. Click Deploy
5. Authorize if prompted
6. COPY the new URL (starts with https://script.google.com/macros/s/...)
```

### 3️⃣ Update config.js
```
1. Open: config.js in your project
2. Replace the APPS_SCRIPT_URL with your NEW URL
3. Save
4. Refresh your UMS page
```

## Test It
```
1. Go to: http://localhost:8080/test-backend.html
2. Click "Test Get Members"
3. Should show: ✅ Request successful! Found 9 members
```

---

## Why This Happens
- Apps Script deployments can have stale configurations
- Old deployment doesn't accept requests from localhost
- Creating a NEW deployment fixes CORS and permission issues
- The NEW deployment gets a NEW URL

## Important
- Do NOT click "Manage deployments"
- Do NOT click "Test deployments"  
- Always create a **NEW deployment**
- Always set "Who has access" to **Anyone**

---

## Your Data is Fine! ✅
Your Google Sheet has 9 members with correct data:
- M001: S MD Abdur Rahman
- M002: S NAZNEEN NAZAR
- M003: Balaji Rajput
- M004: Shalini Rajput
- M005: Y Lakshmi
- M006: Guru Sekhar
- M007: Keerthi
- M008: JayRam
- M009: G Lakshmi

The data is there - we just need to fix the connection!
