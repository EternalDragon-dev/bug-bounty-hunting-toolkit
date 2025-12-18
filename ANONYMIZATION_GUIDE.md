# 🎭 ANONYMIZATION TOGGLE SYSTEM - USAGE GUIDE

**Status:** ✅ **IMPLEMENTED** - Ready for use!

---

## 🚀 QUICK START

### Enable Anonymous Mode
```bash
# Enable anonymization for all toolkit operations
python3 toolkit_controller.py --enable-anon

# Or set manually
export TOOLKIT_ANONYMOUS=true
```

### Check Status
```bash
# View detailed anonymization status
python3 toolkit_controller.py --status
```

### Test Anonymization
```bash
# Quick IP check test
python3 toolkit_controller.py --test

# Test with specific URL
python3 toolkit_controller.py --test https://httpbin.org/ip
```

### Disable Anonymous Mode
```bash
python3 toolkit_controller.py --disable-anon
```

---

## 🛠️ INSTALLATION & SETUP

### Install Dependencies
```bash
# Install required Python packages
python3 toolkit_controller.py --install-deps

# Install system tools (macOS)
brew install tor proxychains-ng

# Install system tools (Linux)
sudo apt install tor proxychains4
```

### Start Tor (if needed)
```bash
# macOS
brew services start tor

# Linux
sudo systemctl start tor
```

---

## 💻 USAGE EXAMPLES

### List Available Tools
```bash
python3 toolkit_controller.py --list-tools
```

### Run Tools in Anonymous Mode
```bash
# Enable anonymous mode first
export TOOLKIT_ANONYMOUS=true

# All tools now run anonymously by default
python3 toolkit_controller.py --run subdomain_exposure_hunter fastcryptopump.com
python3 toolkit_controller.py --run advanced_api_hunter example.com
```

### Run Tools in Direct Mode
```bash
# Disable anonymous mode
unset TOOLKIT_ANONYMOUS

# Tools run in direct mode
python3 toolkit_controller.py --run osint_intelligence_scraper
```

### Mixed Usage
```bash
# Quick toggle for single command
TOOLKIT_ANONYMOUS=true python3 tools/web_applications/subdomain_exposure_hunter.py target.com

# Normal usage (direct)
python3 tools/web_applications/advanced_api_hunter.py target.com
```

---

## 🔄 HOW IT WORKS

### Environment Variable Control
- **`TOOLKIT_ANONYMOUS=true`** → All traffic routed through Tor/proxychains
- **`TOOLKIT_ANONYMOUS=false`** or unset → Direct connections

### Automatic Features When Anonymous Mode is ON:
✅ **Tor SOCKS5 routing** (if Tor is running)  
✅ **Proxychains integration** (if available)  
✅ **User agent rotation** (10 realistic user agents)  
✅ **Request timing randomization** (0.5-3.0 second delays)  
✅ **Anonymous headers** (removes identifying information)  
✅ **SSL verification disabled** (for testing environments)  

### Status Indicators:
```
✅ ENABLED  - Feature active
❌ DISABLED - Feature inactive  
❓ UNKNOWN  - Status cannot be determined
```

---

## 📊 ANONYMIZATION FEATURES

### Network Anonymization
- **Tor Integration:** Automatic SOCKS5 proxy through port 9050
- **Proxychains Support:** Routes external tools through proxy chains
- **Connection Pooling:** Manages persistent connections efficiently

### Request Obfuscation
- **User Agent Rotation:** 10 realistic browser user agents
- **Header Randomization:** Removes/modifies identifying headers
- **Timing Randomization:** Random delays between requests (0.5-3.0s)
- **SSL Fingerprint Masking:** Disables SSL verification for testing

### Tool Integration
- **Transparent Integration:** Works with all existing tools
- **Command Wrapper:** Automatically routes external commands
- **Session Management:** Maintains anonymity across tool sessions

---

## 🔍 STATUS MONITORING

### Check Your Anonymization Status
```bash
python3 toolkit_controller.py --status
```

**Sample Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                    ANONYMIZATION STATUS                      ║
╚══════════════════════════════════════════════════════════════╝

Anonymous Mode: ✅ ENABLED
Tor Routing: ✅ ACTIVE
Proxy Chains: ✅ AVAILABLE

Current IP: 185.220.101.32
Location: , 
Tor Status: ✅ USING TOR
User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...

Environment Variable: TOOLKIT_ANONYMOUS=true
```

---

## 🚨 TROUBLESHOOTING

### Tor Not Working
```bash
# Check if Tor is running
lsof -i :9050

# Start Tor service
brew services start tor          # macOS
sudo systemctl start tor         # Linux
```

### PySocks Missing
```bash
pip install PySocks requests[socks]
```

### Proxychains Not Available
```bash
# macOS
brew install proxychains-ng

# Linux
sudo apt install proxychains4
```

### IP Not Changing
1. Verify Tor is running: `curl -x socks5://127.0.0.1:9050 https://httpbin.org/ip`
2. Check environment variable: `echo $TOOLKIT_ANONYMOUS`
3. Restart your terminal session
4. Test with: `python3 toolkit_controller.py --test`

---

## 🎯 BEST PRACTICES

### When to Use Anonymous Mode
✅ **Target testing without permission**  
✅ **Reconnaissance on sensitive targets**  
✅ **Avoiding rate limiting/blocking**  
✅ **Testing from different geographic locations**  
✅ **Protecting your identity during research**

### When to Use Direct Mode  
✅ **Authorized penetration tests**  
✅ **Internal network testing**  
✅ **Local development/testing**  
✅ **When speed is more important than anonymity**  
✅ **Bug bounty programs that require identification**

### Security Tips
- 🔄 **Change circuits regularly** - Restart Tor periodically
- 🕐 **Randomize timing** - Don't follow predictable patterns  
- 🎭 **Use different personas** - Vary your testing approach
- 📱 **Test from mobile** - Mix desktop/mobile user agents
- 🔍 **Monitor for leaks** - Regular IP/DNS leak checks

---

## 🔧 INTEGRATION EXAMPLES

### Update Existing Tools
```python
# Before (direct connection)
import requests
response = requests.get(url)

# After (automatic anonymization)
from core.anonymization import get
response = get(url)  # Automatically anonymous if TOOLKIT_ANONYMOUS=true
```

### Command Line Tools
```python
# Before
subprocess.run(['nmap', target])

# After
from core.anonymization import execute_anonymously
execute_anonymously(['nmap', target])  # Routes through proxychains if enabled
```

---

## 📈 NEXT STEPS

The anonymization toggle system is fully functional! Here's what's coming next:

1. ✅ **Toggle System** - COMPLETED
2. 🔄 **Advanced Network Module** - In progress  
3. 📱 **User Agent Database** - Planned
4. ⏱️ **Timing Randomization** - Planned
5. 🖥️ **VM Integration** - Planned

---

**🎉 Ready to hack anonymously! Use `python3 toolkit_controller.py --enable-anon` to get started.**