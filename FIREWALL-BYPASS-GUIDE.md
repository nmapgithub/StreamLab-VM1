# 🛡️ Firewall Bypass Challenge - Guide

## 🎯 Challenge Overview

Before accessing the live news stream, students must bypass a Web Application Firewall (WAF). This challenge teaches common WAF bypass techniques used in penetration testing.

---

## 🔒 The Challenge

When accessing `https://ann-news.live`, users are greeted with:
- **Error:** WAF_403_FORBIDDEN
- **Message:** Access Denied - Web Application Firewall Active
- **Goal:** Bypass the firewall to access the live stream

---

## 💡 Bypass Methods (5 Ways to Solve)

### Method 1: URL Parameter Bypass ⭐ (Easiest)

**Technique:** Add special parameter to URL

**Solutions:**
```bash
# Option A: access parameter
https://ann-news.live/stream.html?access=granted

# Option B: bypass parameter  
https://ann-news.live/stream.html?bypass=firewall

# Option C: admin parameter
https://ann-news.live/stream.html?admin=true
```

**Using curl:**
```bash
curl -k "https://ann-news.live/stream.html?access=granted"
```

**Flag:** `PENTESTER{w4f_byp4ss_m4st3r}`

---

### Method 2: Cookie Manipulation ⭐⭐

**Technique:** Set bypass cookie using browser console or curl

**Browser Console (F12):**
```javascript
document.cookie = 'firewall_bypass=true; path=/';
window.location.reload();
```

**Using curl:**
```bash
curl -k -b "firewall_bypass=true" https://ann-news.live/stream.html
```

**Alternative cookie:**
```bash
curl -k -b "admin_access=1" https://ann-news.live/stream.html
```

**Flag:** `PENTESTER{w4f_byp4ss_m4st3r}`

---

### Method 3: HTML Source Code Analysis ⭐⭐

**Technique:** Read HTML comments for hints

**Steps:**
1. Visit `https://ann-news.live`
2. Press `Ctrl+U` or right-click → "View Page Source"
3. Search for "HINT" or "SECRET"
4. Find hidden bypass URLs in comments

**What you'll find:**
```html
<!-- HINT: Try adding ?access=granted to the URL -->
<!-- HINT: Or set cookie: firewall_bypass=true -->
<!-- SECRET_BYPASS_CODE: /stream-direct?key=WAF_BYPASS_2025 -->
```

**Flag:** `PENTESTER{w4f_byp4ss_m4st3r}`

---

### Method 4: Browser Console Hints ⭐⭐⭐

**Technique:** Check browser console for developer hints

**Steps:**
1. Visit `https://ann-news.live`
2. Press `F12` to open Developer Tools
3. Go to "Console" tab
4. Read the security analysis hints

**What you'll see:**
```
🔍 Security Analysis
Looking for bypass methods? Check:
1. URL parameters (?access=granted)
2. Cookies (firewall_bypass=true)
3. HTTP Headers (X-Firewall-Bypass: letmein)
4. HTML comments in page source
```

**Flag:** `PENTESTER{w4f_byp4ss_m4st3r}`

---

### Method 5: Emergency Access Link (Easter Egg) ⭐⭐⭐⭐

**Technique:** Wait for hidden link to appear

**Steps:**
1. Visit `https://ann-news.live`
2. Wait 5 seconds
3. Hidden link appears at bottom: "← Emergency Access (Authorized Personnel Only)"
4. Click the link

**Direct URL:**
```
https://ann-news.live/stream.html?access=granted
```

**Flag:** `PENTESTER{w4f_byp4ss_m4st3r}`

---

## 🔧 Advanced Techniques

### HTTP Header Bypass (Mentioned in hints)

While not implemented in the current client-side check, students can try:

```bash
# Using custom headers
curl -k -H "X-Firewall-Bypass: letmein" https://ann-news.live/stream.html
curl -k -H "X-Bypass: true" https://ann-news.live/stream.html
curl -k -H "X-Admin: true" https://ann-news.live/stream.html
```

**Note:** These would require server-side implementation to work.

---

## 🎓 Educational Value

### Students Learn:

1. **Web Application Firewalls (WAF)**
   - How they work
   - Common bypass techniques
   - Security vs usability tradeoffs

2. **Client-Side Security**
   - Why client-side checks are insufficient
   - JavaScript security bypass
   - Cookie manipulation

3. **Reconnaissance Techniques**
   - HTML source analysis
   - Browser console investigation
   - Hidden endpoints discovery

4. **Common Bypass Methods**
   - URL parameter manipulation
   - Cookie injection
   - Header modification
   - Hidden link discovery

---

## 📊 Difficulty Levels

| Method | Difficulty | Time | Skill Level |
|--------|-----------|------|-------------|
| URL Parameter | ⭐ Easy | 1 min | Beginner |
| Cookie Manipulation | ⭐⭐ Medium | 2 min | Beginner-Intermediate |
| Source Code Analysis | ⭐⭐ Medium | 3 min | Intermediate |
| Console Hints | ⭐⭐⭐ Medium | 2 min | Intermediate |
| Easter Egg Link | ⭐⭐⭐⭐ Easy (if patient) | 5 min | Any |

---

## 🚀 Quick Start for Students

### Option 1: Fastest Method
```
1. Go to: https://ann-news.live
2. Add to URL: /stream.html?access=granted
3. Success! You're in!
```

### Option 2: Learning Method
```
1. Go to: https://ann-news.live
2. Press Ctrl+U to view source
3. Search for "HINT"
4. Try the methods you discover
```

### Option 3: Console Hacker Method
```
1. Go to: https://ann-news.live
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Type: document.cookie = 'firewall_bypass=true; path=/'
5. Refresh page
```

---

## 🎯 Testing Your Solution

After successful bypass, you should see:
- ✅ Live news stream with video player
- ✅ Live comments section on the left
- ✅ Breaking news ticker at top
- ✅ Console message: "Firewall Bypassed!"
- ✅ Flag in console: `PENTESTER{w4f_byp4ss_m4st3r}`

---

## 🔐 Security Lessons

### Why This Works (And Why It's Bad)

1. **Client-Side Validation Only**
   - Check happens in browser JavaScript
   - Can be bypassed by disabling JavaScript
   - No server-side verification

2. **Predictable Parameters**
   - `access=granted` is obvious
   - No entropy or randomization
   - Easy to guess

3. **Weak Cookie Values**
   - Simple boolean cookies
   - No cryptographic signing
   - Can be easily forged

### Proper Implementation Would Have:

1. **Server-Side Authentication**
   - JWT tokens
   - Session management
   - Database verification

2. **Strong Secrets**
   - Cryptographic keys
   - Random token generation
   - Time-limited access

3. **Rate Limiting**
   - Brute force protection
   - IP-based restrictions
   - Request throttling

---

## 📚 Additional Challenges

After bypassing the firewall, students can:

1. **Hijack the Stream**
   - Use API vulnerabilities to change video
   - Method: `/api/switch-video`

2. **Capture All Flags**
   - Firewall bypass flag: `PENTESTER{w4f_byp4ss_m4st3r}`
   - API bypass flag: `PENTESTER{uns3cur3_4p1_n0_4uth}`
   - Plus 4 more in the system!

3. **Chain Vulnerabilities**
   - Bypass firewall → Access management API → Hijack stream

---

## 🎮 For Instructors

### Assessment Questions:

1. What bypass method did you use? Why?
2. Why is client-side security insufficient?
3. How would you fix this firewall?
4. What other bypass techniques could work?
5. Document your penetration test methodology

### Scoring Rubric:

- Found and bypassed firewall: **20 points**
- Identified multiple bypass methods: **10 points**
- Explained security weaknesses: **20 points**
- Proposed proper fixes: **15 points**
- Documented methodology: **10 points**
- **Total: 75 points**

---

## 🏆 Success Criteria

✅ Bypassed firewall to access stream  
✅ Captured flag: `PENTESTER{w4f_byp4ss_m4st3r}`  
✅ Understood why it works  
✅ Can explain to others  
✅ Ready for next challenge  

---

**Happy Hacking! 🎯🔓**

