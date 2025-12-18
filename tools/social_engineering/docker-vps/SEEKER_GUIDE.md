# Seeker - Complete Usage Guide

## 📖 Table of Contents
1. [What is Seeker?](#what-is-seeker)
2. [Quick Start (Local Testing)](#quick-start-local-testing)
3. [Docker Setup](#docker-setup)
4. [Exposing to Internet](#exposing-to-internet)
5. [Usage Scenarios](#usage-scenarios)
6. [Understanding the Data](#understanding-the-data)
7. [Protection & Defense](#protection--defense)
8. [Legal & Ethical Guidelines](#legal--ethical-guidelines)

---

## What is Seeker?

**Seeker** is a geolocation social engineering tool that creates fake web pages (Google, Facebook, Instagram, etc.) to trick visitors into revealing their location and device information.

### 🎯 Purpose:
- **Security Awareness Training**: Demonstrate location tracking risks
- **Red Team Assessments**: Test employee susceptibility to social engineering
- **Research & Education**: Understand how geolocation attacks work

### ⚙️ How It Works:
```
1. Seeker creates a fake webpage (looks like Google, Facebook, etc.)
2. Webpage requests browser location permission
3. If victim grants permission:
   → Precise GPS coordinates captured
   → IP address logged
   → Device information collected (OS, browser, screen resolution)
   → ISP and location details gathered
4. Data displayed in real-time to the attacker
```

### 🔍 What Data It Collects:
- **Geolocation**: Latitude, longitude, accuracy (can be within 5-10 meters)
- **IP Address**: Public IPv4/IPv6 address
- **Device Info**: OS, browser, screen resolution, CPU cores
- **Network Info**: ISP, organization, city, country, timezone
- **Timestamps**: When the victim accessed the link

**⚠️ CRITICAL**: Only use with **explicit written permission** or on yourself for education!

---

## Quick Start (Local Testing)

### Method 1: Using Provided Scripts (Easiest)

```bash
# Navigate to docker-vps directory
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps

# Make sure Docker VPS is running
docker-compose up -d

# Run the demo script (guided walkthrough)
./demo-seeker.sh
```

The script will:
1. Start Seeker on port 9999
2. Show available templates (Google, Facebook, Instagram, etc.)
3. Display the local URL: `http://localhost:9999`
4. You can test it on yourself by visiting that URL in your browser

### Method 2: Manual Docker Execution

```bash
# Start the Docker VPS
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps
docker-compose up -d

# Access the VPS shell
docker exec -it whitehacking-vps bash

# Navigate to Seeker directory
cd /opt/seeker

# Run Seeker
python3 seeker.py -p 9999

# Choose a template (type number and press Enter):
# 0 = NearYou (generic location request)
# 1 = Google Drive
# 2 = WhatsApp
# 3 = Telegram
# 4 = Zoom
# 5 = Instagram
# 6 = Google reCAPTCHA (most convincing)
```

### Method 3: Direct Local Testing (No Docker)

If you want to run Seeker directly on your Mac:

```bash
# Clone Seeker (if not already in Docker)
git clone https://github.com/thewhiteh4t/seeker.git
cd seeker

# Install dependencies
pip3 install requests

# Run Seeker
python3 seeker.py -p 9999

# Visit http://localhost:9999 in your browser
```

---

## Docker Setup

### Architecture

```
Your Mac
    ↓
Docker Container (whitehacking-vps)
    ↓
Seeker (/opt/seeker/)
    ↓
PHP Server (serves fake webpages)
    ↓
Tunneling Service (ngrok/cloudflare)
    ↓
PUBLIC INTERNET
```

### Starting the VPS

```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps

# Start VPS
docker-compose up -d

# Check it's running
docker ps | grep whitehacking-vps

# Access the shell
docker exec -it whitehacking-vps bash
```

### Stopping the VPS

```bash
# Stop VPS
docker-compose down

# Or just stop without removing
docker-compose stop
```

### Rebuilding (after Dockerfile changes)

```bash
docker-compose up -d --build
```

---

## Exposing to Internet

**⚠️ WARNING**: Only expose to internet for authorized security testing with written permission!

### Option 1: ngrok (Recommended - Easiest)

**Why ngrok?**
- ✅ Instant HTTPS (looks more legitimate)
- ✅ No router configuration needed
- ✅ Works behind firewalls/corporate networks
- ✅ Free tier available (no credit card required)
- ✅ Most reliable and beginner-friendly option

---

## 📋 Complete ngrok Setup (Step-by-Step)

### Step 1: Install ngrok on macOS

**Option A: Using Homebrew (Recommended)**
```bash
# Install via Homebrew
brew install ngrok/ngrok/ngrok

# Verify installation
ngrok version
# Should show: ngrok version 3.x.x
```

**Option B: Manual Download**
```bash
# Download from official site
open https://ngrok.com/download

# Or use curl
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip
unzip ngrok-v3-stable-darwin-amd64.zip
sudo mv ngrok /usr/local/bin/
ngrok version
```

---

### Step 2: Create Free ngrok Account

1. **Visit ngrok signup page:**
   ```bash
   open https://dashboard.ngrok.com/signup
   ```

2. **Sign up options:**
   - Sign up with Google (fastest)
   - Sign up with GitHub
   - Sign up with email

3. **No credit card required** for free tier

4. **You'll be redirected to dashboard** after signup

---

### Step 3: Get Your Auth Token

1. **After login, you're on the dashboard:**
   ```
   https://dashboard.ngrok.com/get-started/setup
   ```

2. **Your auth token is displayed** (looks like this):
   ```
   2abcDEFghiJKLmnoPQRstuvWXYZ_123456789AbCdEfGhIjKlMnOpQr
   ```

3. **Copy the token** (click the copy button or select and Cmd+C)

**⚠️ IMPORTANT**: Never share your auth token - it's like a password!

---

### Step 4: Configure ngrok with Your Token

```bash
# Add your auth token (replace with YOUR actual token)
ngrok config add-authtoken 2abcDEFghiJKLmnoPQRstuvWXYZ_123456789AbCdEfGhIjKlMnOpQr

# You should see:
# Authtoken saved to configuration file: /Users/yourusername/Library/Application Support/ngrok/ngrok.yml
```

**Verify configuration:**
```bash
# Check config file was created (macOS location)
cat ~/Library/Application\ Support/ngrok/ngrok.yml

# Should show:
# version: "3"
# agent:
#     authtoken: YOUR_TOKEN_HERE

# NOTE: On Linux, the path would be: ~/.config/ngrok/ngrok.yml
```

---

### Step 5: Start Your Docker VPS

```bash
# Navigate to docker-vps directory
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps

# Start the Docker container
docker-compose up -d

# Verify it's running
docker ps | grep whitehacking-vps
# Should show: whitehacking-vps   Up X seconds
```

**Troubleshooting:**
```bash
# If container isn't running:
docker-compose down
docker-compose up -d --build

# View logs if there are issues:
docker logs whitehacking-vps
```

---

### Step 6: Start Seeker (Terminal 1)

**Open your first terminal window and run:**

```bash
# Start Seeker inside Docker container
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"
```

**You'll see this prompt:**
```
[*] Choose a Template:

[0] NearYou
[1] Google Drive  
[2] WhatsApp
[3] Telegram
[4] Zoom
[5] Instagram
[6] Google reCAPTCHA

[>] Select Template: 
```

**Type `6` and press Enter** (Google reCAPTCHA is most convincing)

**Seeker starts and shows:**
```
[*] PHP Server started on port 9999
[*] Waiting for victim...
[*] Send this link to target: http://localhost:9999
```

**✅ Leave this terminal running!** Don't close it.

---

### Step 7: Expose with ngrok (Terminal 2)

**Open a NEW terminal window** (Cmd+T or Cmd+N) and run:

```bash
# Expose Seeker to the internet
ngrok http 9999
```

**You'll see output like this:**
```
ngrok                                                                   
                                                                        
Build better APIs with ngrok. Early access: ngrok.com/early-access      
                                                                        
Session Status                online                                    
Account                       your-email@example.com (Plan: Free)      
Version                       3.5.0                                     
Region                        United States (us)                        
Latency                       45ms                                      
Web Interface                 http://127.0.0.1:4040                     
Forwarding                    https://abc123def456.ngrok-free.app -> http://localhost:9999
                                                                        
Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**🎯 The important line is:**
```
Forwarding   https://abc123def456.ngrok-free.app -> http://localhost:9999
```

**This URL** (`https://abc123def456.ngrok-free.app`) is what you send to your target.

**✅ Leave this terminal running too!** Don't close it.

---

### Step 8: Access the ngrok Web Interface (Optional)

ngrok provides a local web dashboard:

```bash
# Open the web interface
open http://127.0.0.1:4040
```

**The dashboard shows:**
- All HTTP requests in real-time
- Request/response details
- Timing information
- Ability to replay requests

**This is VERY useful for debugging!**

---

### Step 9: Test Your Setup

**Before sending to anyone, TEST IT YOURSELF:**

1. **Copy your ngrok URL** from Terminal 2:
   ```
   https://abc123def456.ngrok-free.app
   ```

2. **Open it in a browser** (Safari, Chrome, Firefox)

3. **You'll see the Google reCAPTCHA page** (fake)

4. **Click "I'm not a robot"**

5. **Grant location permission** when prompted

6. **Go back to Terminal 1** (where Seeker is running)

**You should see YOUR location data:**
```
[+] Victim IP: 203.0.113.45
[+] User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...
[+] Latitude: 37.7749
[+] Longitude: -122.4194
[+] Accuracy: 12 meters
[+] ISP: Comcast Cable
[+] City: San Francisco
[+] Google Maps: https://www.google.com/maps?q=37.7749,-122.4194
```

**✅ If you see this, your setup is working perfectly!**

---

### Step 10: Send Link to Target (With Permission!)

**Once you've verified it works:**

1. **Copy your ngrok URL:**
   ```
   https://abc123def456.ngrok-free.app
   ```

2. **Create a convincing message** (for authorized testing only!):
   ```
   Option 1 (IT Security Test):
   "Hi team, IT is upgrading our security system. 
   Please verify your identity here: [LINK]"

   Option 2 (Survey):
   "Quick survey for remote workers about office locations: [LINK]"

   Option 3 (Prize/Giveaway):
   "Congrats! You're eligible for a free gift. 
   Verify your location to claim: [LINK]"
   ```

3. **Send via:**
   - Email
   - SMS/text message
   - Slack/Teams
   - WhatsApp

4. **Monitor Terminal 1** for victim connections

**⚠️ REMINDER**: Only do this with written permission!

---

### Step 11: Monitor Results in Real-Time

**When someone clicks your link, watch Terminal 1:**

```
[INFO] New connection from: 198.51.100.42
[INFO] User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_0...)
[INFO] Waiting for location permission...

# If they grant permission:
[+] Location Permission: GRANTED
[+] Latitude: 40.7128
[+] Longitude: -74.0060
[+] Accuracy: 8 meters
[+] ISP: Verizon Wireless
[+] City: New York
[+] Device: iPhone 13
[+] Google Maps: https://www.google.com/maps?q=40.7128,-74.0060

# If they deny permission:
[!] Location Permission: DENIED
[INFO] Only IP-based location available
[+] Approximate Location (from IP): New York, US
```

**Also check ngrok Web Interface** (http://127.0.0.1:4040) to see:
- All HTTP requests
- Headers sent
- Browser fingerprints
- Timing data

---

### Step 12: Stop Everything When Done

**When your test is complete:**

1. **Stop Seeker (Terminal 1):**
   ```bash
   # Press Ctrl+C
   ^C
   [*] Seeker stopped
   ```

2. **Stop ngrok (Terminal 2):**
   ```bash
   # Press Ctrl+C
   ^C
   # ngrok tunnel closed
   ```

3. **Stop Docker VPS (optional):**
   ```bash
   cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps
   docker-compose down
   ```

4. **Save results (optional):**
   ```bash
   # Copy logs from Docker to your Mac
   docker cp whitehacking-vps:/home/vpsuser/results/ ./seeker-results/
   ```

5. **Delete collected data** (if this was a test)

---

## 🎓 ngrok Tips & Tricks

### Tip 1: Custom Subdomains (Paid - $8/month)

**Free tier gives random URLs:**
```
https://abc123def456.ngrok-free.app  # Changes every time
```

**Paid tier gives custom subdomains:**
```bash
# Use custom subdomain
ngrok http 9999 --subdomain=security-test

# Your URL becomes:
# https://security-test.ngrok-free.app
```

**More professional and easier to remember!**

---

### Tip 2: Use URL Shorteners

**Make ngrok URLs less obvious:**

1. **Copy your ngrok URL:**
   ```
   https://abc123def456.ngrok-free.app
   ```

2. **Shorten it:**
   ```bash
   # Option 1: Bitly (https://bitly.com)
   # Creates: https://bit.ly/3xY2zQ1

   # Option 2: TinyURL (https://tinyurl.com)  
   # Creates: https://tinyurl.com/y9z8x7w6

   # Option 3: Your own domain (most professional)
   # Register: security-check.com
   # Redirect to ngrok URL
   ```

**⚠️ Warning**: Some people are suspicious of shortened URLs. Use wisely.

---

### Tip 3: ngrok Configuration File

**Create custom configurations:**

```bash
# Edit ngrok config (macOS path)
nano ~/Library/Application\ Support/ngrok/ngrok.yml

# Or on Linux:
# nano ~/.config/ngrok/ngrok.yml
```

**Add custom settings:**
```yaml
version: "3"
agent:
  authtoken: YOUR_TOKEN_HERE
tunnels:
  seeker:
    proto: http
    addr: 9999
    # Add custom domain if you have paid plan:
    # subdomain: security-test
    # Add custom hostname if you own domain:
    # hostname: security.yourdomain.com
```

**Then start with:**
```bash
ngrok start seeker
```

---

### Tip 4: Multiple Tunnels (Paid)

**Run multiple Seeker instances:**

```bash
# Terminal 1: Start first Seeker (port 9999)
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"

# Terminal 2: Expose first instance
ngrok http 9999 --subdomain=test1

# Terminal 3: Start second Seeker (port 8888) 
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 8888"

# Terminal 4: Expose second instance
ngrok http 8888 --subdomain=test2
```

**Use cases:**
- Test different templates simultaneously
- Run tests for different departments
- A/B testing which template is most effective

---

### Tip 5: ngrok Regions

**Choose server region for better latency:**

```bash
# US (default)
ngrok http 9999 --region=us

# Europe
ngrok http 9999 --region=eu

# Asia Pacific
ngrok http 9999 --region=ap

# Australia
ngrok http 9999 --region=au

# South America
ngrok http 9999 --region=sa

# Japan
ngrok http 9999 --region=jp

# India
ngrok http 9999 --region=in
```

**Choose region closest to your target** for faster loading.

---

## ❌ Common ngrok Issues & Solutions

### Issue 1: "command not found: ngrok"

**Problem**: ngrok not in PATH

**Solution:**
```bash
# Check where ngrok is installed
which ngrok

# If nothing shows, reinstall
brew install ngrok/ngrok/ngrok

# Or add to PATH manually
export PATH="$PATH:/usr/local/bin"
```

---

### Issue 2: "ERROR: authentication failed"

**Problem**: Auth token not configured or invalid

**Solution:**
```bash
# Remove old config (macOS)
rm ~/Library/Application\ Support/ngrok/ngrok.yml

# Or on Linux:
# rm ~/.config/ngrok/ngrok.yml

# Get new token from dashboard
open https://dashboard.ngrok.com/get-started/your-authtoken

# Add new token
ngrok config add-authtoken YOUR_NEW_TOKEN

# Verify it was saved
cat ~/Library/Application\ Support/ngrok/ngrok.yml
```

---

### Issue 3: "tunnel not found"

**Problem**: Free account trying to use custom subdomain

**Solution:**
```bash
# Remove --subdomain flag (requires paid plan)
ngrok http 9999

# OR upgrade to paid plan ($8/month)
open https://dashboard.ngrok.com/billing/plan
```

---

### Issue 4: "ERR_NGROK_108"

**Problem**: Free account has usage limits

**Solution:**
```bash
# Free tier limits:
# - 1 online tunnel at a time
# - 40 connections/minute
# - Tunnel alive for 2 hours max

# If you hit limits:
# 1. Wait a few minutes
# 2. Restart ngrok
# 3. Or upgrade to paid plan
```

---

### Issue 5: ngrok Page Shows "Visit Site" Button

**Problem**: ngrok interstitial page (anti-abuse)

**Solution**: This is intentional on free tier. Victims need to click "Visit Site" before seeing your page.

**Workarounds:**
1. Upgrade to paid plan (removes interstitial)
2. Use Cloudflare Tunnel instead (no interstitial)
3. Explain in your message: "Click 'Visit Site' to continue"

---

### Issue 6: "failed to bind to port 9999"

**Problem**: Port already in use

**Solution:**
```bash
# Find what's using port 9999
lsof -i :9999

# Kill the process (replace PID with actual number)
kill -9 PID

# Or use different port
python3 seeker.py -p 8888
ngrok http 8888
```

---

## 📊 ngrok vs. Alternatives

| Feature | ngrok Free | ngrok Paid | Cloudflare Tunnel | Port Forward |
|---------|------------|------------|-------------------|---------------|
| **Setup Time** | 5 min | 5 min | 10 min | 30+ min |
| **HTTPS** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Custom Domain** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Interstitial Page** | ⚠️ Yes | ✅ No | ✅ No | ✅ No |
| **Firewall Bypass** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Speed** | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡⚡⚡ |
| **Cost** | Free | $8/mo | Free | Free |
| **Best For** | Quick tests | Professional | Long-term | Advanced |

---

## 🔒 Security Considerations

### What ngrok Sees:

**ngrok can see ALL traffic** passing through their servers:
- Victim IP addresses
- Geolocation data
- User agents
- All HTTP requests/responses

**Free tier limitations:**
- Logs retained for 24 hours
- Traffic visible in your dashboard

**Paid tier features:**
- Longer log retention
- IP whitelisting
- Password protection
- OAuth

### Best Practices:

1. **Don't send sensitive data through ngrok** in real attacks
2. **Use Cloudflare Tunnel for maximum privacy** (they log less)
3. **For red team exercises**, get your own VPS (no third party)
4. **Review ngrok privacy policy**: https://ngrok.com/privacy

---

## 📖 Further Reading

**Official ngrok docs:**
- Getting Started: https://ngrok.com/docs/getting-started/
- Configuration: https://ngrok.com/docs/secure-tunnels/ngrok-agent/reference/config/
- Pricing: https://ngrok.com/pricing

**Video tutorials:**
- ngrok Quickstart: Search YouTube for "ngrok tutorial"
- Seeker with ngrok: Search for "Seeker geolocation ngrok"

---

**✅ You're now a ngrok expert! The summary:**

```bash
# Terminal 1: Start Seeker
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"

# Terminal 2: Expose with ngrok  
ngrok http 9999

# Copy the HTTPS URL and send to target (with permission!)
# Monitor Terminal 1 for results
```

**Remember**: Only use for authorized security testing!

---

### Option 2: Cloudflare Tunnel (Free, More Permanent)

**Why Cloudflare Tunnel?**
- ✅ Free forever
- ✅ Can use custom domain (if you own one)
- ✅ More stable than ngrok free tier
- ✅ Better performance

**Setup:**

```bash
# 1. Install cloudflared
brew install cloudflared

# 2. Authenticate
cloudflared tunnel login
# This opens browser - sign in with Cloudflare account (create free account if needed)

# 3. Start Seeker in Docker (Terminal 1)
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"

# 4. Expose via Cloudflare Tunnel (Terminal 2)
cloudflared tunnel --url http://localhost:9999
```

**You'll get a URL like:**
```
https://random-words-1234.trycloudflare.com
```

---

### Option 3: Port Forwarding (Advanced - Most Control)

**Only if you need full control and don't mind exposing your real IP.**

**Steps:**

1. **Find your Mac's local IP:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Find your public IP:**
   ```bash
   curl ifconfig.me
   ```

3. **Configure router:**
   - Log into router (usually `192.168.1.1` or `192.168.0.1`)
   - Find "Port Forwarding" section
   - Forward external port 9999 → your Mac's local IP, port 9999

4. **Configure macOS firewall:**
   ```bash
   # Allow port 9999
   sudo pfctl -a com.apple/firewall -f /etc/pf.conf
   ```

5. **Start Seeker:**
   ```bash
   docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"
   ```

6. **Your public URL:** `http://YOUR_PUBLIC_IP:9999`

**⚠️ Downsides:**
- Exposes your real IP address
- May violate ISP terms of service
- Requires router access
- Your home IP is in the logs

---

## Usage Scenarios

### Scenario 1: Self-Testing (Learn What Data You Expose)

```bash
# 1. Start Seeker locally
./demo-seeker.sh

# 2. Visit http://localhost:9999 in your browser

# 3. Try different templates to see which looks most convincing

# 4. Grant location permission and see what data is captured

# 5. Review the terminal output to understand what attackers see
```

**What you'll learn:**
- How accurate browser geolocation is (often scary accurate)
- What device information is exposed
- How legitimate these fake pages can look

---

### Scenario 2: Authorized Security Awareness Training

**Objective**: Demonstrate to employees how easy it is to fall for location-based social engineering.

**Workflow:**

```bash
# 1. Get WRITTEN PERMISSION from management
# Document: "Security awareness exercise to demonstrate location tracking risks"

# 2. Start Seeker with professional template
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"
# Choose option 6 (Google reCAPTCHA)

# 3. Expose via ngrok
ngrok http 9999
# Note the HTTPS URL: https://abc123.ngrok-free.app

# 4. Send to employee with realistic context:
# "Hey team, please verify your identity for the new security system: [LINK]"

# 5. Monitor Seeker terminal - when they click:
# - Their location appears in real-time
# - Device info displayed
# - IP and ISP logged

# 6. After test:
# - Immediately inform them it was a test
# - Show them the data you collected
# - Educate on protection strategies
# - DELETE all collected data
```

---

### Scenario 3: Red Team Engagement

**Objective**: Test organization's security posture against social engineering.

**Pre-requisites:**
- ✅ Signed contract with scope definition
- ✅ Rules of engagement documented
- ✅ Emergency contact list
- ✅ Legal approval obtained

**Execution:**

```bash
# 1. Setup production-grade hosting
# Use Cloudflare Tunnel with custom domain you own
cloudflared tunnel --url http://localhost:9999

# Or use paid ngrok with custom subdomain
ngrok http 9999 --subdomain=yourcompany-security

# 2. Create convincing social engineering pretext:
# Example: "IT Security Update - Verify Your Location for MFA Setup"

# 3. Customize Seeker template (edit HTML files in /opt/seeker/template/)
# Make it match company branding

# 4. Send links and monitor results

# 5. Document findings:
# - How many employees clicked?
# - How many granted location permission?
# - Time to click (immediate vs. cautious)
# - Device types (mobile more vulnerable?)

# 6. Generate report with recommendations
```

---

## Understanding the Data

### Seeker Output Breakdown

When a victim accesses your Seeker link, you'll see:

```
[INFO] Victim IP: 203.0.113.45
[INFO] User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)...
[INFO] Location Permission: Granted
[+] Latitude: 37.7749
[+] Longitude: -122.4194
[+] Accuracy: 12 meters
[+] ISP: Comcast Cable
[+] City: San Francisco
[+] Country: United States
[+] Organization: AS7922 Comcast Cable Communications
[+] Google Maps: https://www.google.com/maps?q=37.7749,-122.4194
```

### What This Reveals:

1. **Exact Location**: Latitude/Longitude pinpoints them to a specific building
2. **Device Type**: iPhone (from User-Agent) - indicates mobile user
3. **Network**: Comcast (home internet, not work VPN)
4. **Accuracy**: 12 meters = within ~40 feet of exact position
5. **Behavioral**: They granted permission immediately (low security awareness)

### Attack Vectors This Enables:

**For Authorized Testing:**
- Physical security assessment (know when they're not home/at office)
- Tailgating opportunities (know when they arrive at work)
- Spear phishing (reference their location: "I saw you at [coffee shop]")
- Social engineering (pretend to be local: "I'm also in San Francisco...")

---

## Protection & Defense

### For Users:

#### 1. **Never Grant Location to Unknown Sites**

```
✅ SAFE: Google Maps, Uber, food delivery apps (legitimate use case)
❌ DANGER: Random survey sites, "win a prize" pages, unknown links
❌ DANGER: Any site from a shortened URL (bit.ly, tinyurl, etc.)
```

#### 2. **Check URL Carefully**

```
❌ Suspicious: https://g00gle-drive.xyz
❌ Suspicious: https://abc123.ngrok.io
❌ Suspicious: https://random-words.trycloudflare.com
✅ Legitimate: https://drive.google.com
✅ Legitimate: https://www.facebook.com
```

#### 3. **Browser Settings - Block by Default**

**Chrome:**
```
Settings → Privacy and Security → Site Settings → Location
→ "Don't allow sites to see your location"
```

**Safari:**
```
Preferences → Websites → Location
→ "Deny" for all websites by default
→ Only allow when you specifically need it
```

**Firefox:**
```
Settings → Privacy & Security → Permissions → Location → Settings
→ Check "Block new requests asking to access your location"
```

#### 4. **Use VPN**

Even if you accidentally grant location, VPN:
- Hides your real IP address
- Masks your ISP
- Shows VPN server location instead of real location

#### 5. **Browser Extensions**

Install these for protection:
- **uBlock Origin**: Blocks tracking scripts
- **Privacy Badger**: Blocks location trackers
- **NoScript**: Prevents JavaScript from running on untrusted sites

---

### For Organizations:

#### 1. **Employee Training**

Quarterly security awareness training covering:
- How location tracking attacks work
- Real examples (show them Seeker demo)
- How to verify legitimate location requests
- Reporting suspicious links

#### 2. **Technical Controls**

```bash
# Network-level blocking of common tunneling services
# Add to firewall/proxy:
*.ngrok.io
*.ngrok-free.app
*.trycloudflare.com
*.serveo.net
*.localhost.run
```

#### 3. **Mobile Device Management (MDM)**

For company devices:
- Enforce location permission policies
- Restrict browser settings
- Audit installed apps
- Geo-fence company property

#### 4. **Phishing Simulations**

Use Seeker (with permission) to test employees:
```bash
# Monthly phishing test
# Track click rates
# Provide immediate training to those who fall for it
# Measure improvement over time
```

---

## Legal & Ethical Guidelines

### ✅ LEGAL USES:

1. **Self-Testing**: Always OK to test yourself
2. **Authorized Training**: With written permission from organization
3. **Red Team Engagements**: With signed contract and scope definition
4. **Educational Demos**: Controlled classroom environment
5. **Research**: Academic studies with IRB approval

### ❌ ILLEGAL USES:

1. **Stalking**: Tracking someone without permission = **CRIME**
2. **Harassment**: Using location data to intimidate = **CRIME**
3. **Corporate Espionage**: Unauthorized targeting of competitors = **CRIME**
4. **Identity Theft**: Collecting location for fraudulent purposes = **CRIME**
5. **Doxxing**: Publishing someone's location online = **CRIME**

### 📋 Required Documentation:

For any authorized test, you MUST have:

**1. Scope of Work Document**
```
- Target individuals/organization
- Start and end dates
- Allowed techniques
- Out-of-scope items
- Emergency contacts
```

**2. Rules of Engagement**
```
- Approved templates
- Approved hosting services
- Data retention policy
- Notification procedures
```

**3. Legal Agreement**
```
- Indemnification clause
- Confidentiality agreement
- Data destruction timeline
- Reporting requirements
```

### 🌍 Jurisdiction Considerations:

- **GDPR (Europe)**: Requires explicit consent, right to deletion
- **CCPA (California)**: Requires opt-out mechanism
- **POPIA (South Africa)**: Requires lawful processing
- **CFAA (USA)**: Unauthorized access is a federal crime

**Bottom line**: If you don't have written permission, **DON'T USE THIS TOOL**.

---

## Advanced Tips

### Customizing Templates

Templates are in `/opt/seeker/template/` (inside Docker container):

```bash
# Access Docker container
docker exec -it whitehacking-vps bash

# Navigate to templates
cd /opt/seeker/template

# List available templates
ls -l
# nearyou/  google/  whatsapp/  telegram/  zoom/  instagram/  recaptcha/

# Customize (example: Google template)
cd google
nano index.html

# Edit HTML to match your target's branding
# Add company logo
# Modify text to be more convincing
```

### URL Shortening (Make ngrok Links Less Obvious)

```bash
# After getting your ngrok URL: https://abc123.ngrok-free.app

# Use a URL shortener:
# Option 1: Bitly (https://bitly.com) - custom short links
# Option 2: TinyURL (https://tinyurl.com) - free, random
# Option 3: Your own domain with redirect

# Professional approach: Buy domain like "security-check.com"
# Set up redirect to your ngrok/cloudflare URL
```

### Logging and Analysis

Seeker logs are displayed in terminal. To save for analysis:

```bash
# Run Seeker with output redirect
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999 | tee /home/vpsuser/results/seeker-$(date +%Y%m%d-%H%M%S).log"

# Copy logs from container to Mac
docker cp whitehacking-vps:/home/vpsuser/results/ ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/docker-vps/seeker-results/
```

---

## Troubleshooting

### Issue 1: "Port already in use"

```bash
# Kill existing Seeker processes
docker exec -it whitehacking-vps pkill -f seeker.py

# Or use different port
python3 seeker.py -p 8888
```

### Issue 2: "No location permission popup"

**Cause**: Modern browsers require HTTPS for geolocation API.

**Solution**: Always use ngrok or Cloudflare Tunnel (they provide HTTPS).

### Issue 3: Victim granted permission but no data

**Possible reasons:**
1. They're using VPN (location will be VPN server)
2. Browser blocked geolocation
3. Device GPS is disabled
4. Network timeout

### Issue 4: ngrok tunnel not starting

```bash
# Check if ngrok is configured
ngrok config check

# Re-authenticate
ngrok config add-authtoken YOUR_TOKEN

# Try different port
ngrok http 8888
```

---

## Additional Resources

### Related Tools:
- **Social-Engineer Toolkit (SET)**: Broader social engineering framework
- **BeEF (Browser Exploitation Framework)**: Browser-based attacks
- **Gophish**: Phishing campaign platform
- **King Phisher**: Phishing campaign toolkit

### Learning Resources:
- **OWASP Top 10**: Web security fundamentals
- **PortSwigger Web Security Academy**: Free courses
- **HackerOne Hacktivity**: Real-world bug bounty reports
- **SANS SEC504**: Hacker tools and techniques

### Books:
- "Social Engineering: The Art of Human Hacking" by Christopher Hadnagy
- "The Art of Deception" by Kevin Mitnick
- "Ghost in the Wires" by Kevin Mitnick

---

## Quick Command Reference

```bash
# START SEEKER (Docker)
docker exec -it whitehacking-vps bash -c "cd /opt/seeker && python3 seeker.py -p 9999"

# EXPOSE WITH NGROK
ngrok http 9999

# EXPOSE WITH CLOUDFLARE
cloudflared tunnel --url http://localhost:9999

# STOP SEEKER
# Press Ctrl+C in the Seeker terminal

# COPY RESULTS FROM DOCKER
docker cp whitehacking-vps:/home/vpsuser/results/ ./seeker-results/

# VIEW SEEKER LOGS
docker logs whitehacking-vps

# RESTART DOCKER VPS
docker-compose restart
```

---

**Remember**: This tool is a weapon. Use it responsibly, ethically, and legally. Always get written permission. Always educate victims after testing. Always delete collected data.

**Last Updated**: November 2024  
**Tool Version**: Seeker (thewhiteh4t)  
**Docker Image**: whitehacking-vps based on Ubuntu 22.04
