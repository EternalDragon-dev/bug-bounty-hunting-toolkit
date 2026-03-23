# White Hat Hacking VPS

This Docker-based VPS is equipped with essential tools for ethical hacking and bug bounty hunting.

## 🚀 Quick Start

### Access VPS
```bash
# Direct shell access (recommended)
docker exec -it whitehacking-vps bash

# SSH access
ssh vpsuser@localhost -p 2222
# Password: password123
```

### Management Commands
```bash
# Start VPS
docker-compose up -d

# Stop VPS
docker-compose down

# Restart VPS
docker-compose restart

# View logs
docker logs whitehacking-vps

# Rebuild VPS (after changes)
docker-compose up -d --build
```

## 🔧 Installed Tools

### OSINT & Reconnaissance
- **Seeker** - Social engineering geolocation tool
  ```bash
  cd /opt/seeker && python3 seeker.py
  ```
- **Nmap** - Network discovery and security auditing
- **Nikto** - Web vulnerability scanner
- **Gobuster** - Directory/file & DNS brute-forcer
- **Dirb** - Web content scanner

### Web Application Testing
- **SQLMap** - SQL injection testing
- **curl** - HTTP client for API testing

### Password Attacks
- **Hydra** - Login brute-forcer
- **John the Ripper** - Password hash cracker
- **Hashcat** - Advanced password recovery

### Network Analysis
- **tcpdump** - Network packet analyzer
- **netcat** - Network utility
- **traceroute** - Network path tracing
- **whois** - Domain information lookup

## 📁 Directory Structure

```
/home/vpsuser/
├── data/      # Persistent data storage
├── tools/     # Custom tools
└── results/   # Scan results and outputs
```

## 🌐 Port Mappings

- **2222** → SSH (port 22)
- **8080** → Web server
- **3000** → Development server
- **4444** → Reverse shell listener
- **5555** → Custom tool port

## ⚡ Quick Examples

### Seeker (Geolocation Social Engineering)
```bash
cd /opt/seeker
python3 seeker.py -p 8080
```

### Network Reconnaissance
```bash
nmap -sV target.com
nikto -h https://target.com
gobuster dir -u https://target.com -w /usr/share/dirb/wordlists/common.txt
```

### Web Application Testing
```bash
sqlmap -u "http://target.com/page?id=1" --dbs
```

### Password Attacks
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-post-form "/login:username=^USER^&password=^PASS^:Login failed"
```

## 🔒 Security Notes

- **For White Hat/Ethical Hacking Only** - Only use these tools on systems you own or have explicit permission to test
- Change the default password: `passwd vpsuser`
- The VPS runs in privileged mode for certain security tools
- All data in `./data`, `./tools`, and `./results` folders persists between container restarts

## 🛠 Customization

To add more tools or modify the setup:
1. Edit `Dockerfile` to add packages
2. Modify `vps-setup.sh` for custom configurations
3. Rebuild with `docker-compose up -d --build`

---

**Location**: `bug-bounty-hunting-toolkit/tools/docker-vps/`
