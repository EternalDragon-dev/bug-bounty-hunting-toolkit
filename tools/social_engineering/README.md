# Social Engineering Tools Directory

This directory contains professional OSINT and social engineering tools for bug bounty hunting and security assessments.

## 📁 Directory Structure

```
social_engineering/
├── sherlock/                    # Username search across 300+ sites
├── spiderfoot/                  # Automated OSINT framework (200+ modules)
├── recon-ng/                    # Modular reconnaissance framework
├── social_mapper/               # Facial recognition profile correlator
├── theHarvester/                # Email and domain information gatherer
├── WhatsMyName/                 # Username enumeration database
├── maigret/                     # Advanced username OSINT (3000+ sites)
├── docker-vps/                  # Docker container with Seeker + pentesting tools
├── COMPLETE_OSINT_TOOLKIT.md    # Comprehensive guide for all OSINT tools
└── README.md                    # This file
```

## 🔧 Installed Tools

### Username & Social Media
- ⭐ **Sherlock** - Fast username search (300+ platforms)
- ⭐ **Maigret** - Advanced username OSINT with reports (3000+ sites)
- ⭐ **WhatsMyName** - Username database for integration

### Email & Domain
- ⭐ **theHarvester** - Email addresses, subdomains, IPs from public sources
- ⭐ **Holehe** (global pip) - Check email registrations (120+ sites)

### Automation Frameworks
- ⭐ **SpiderFoot** - Automated OSINT with 200+ modules
- ⭐ **Recon-ng** - Modular reconnaissance framework

### Social Engineering
- ⭐ **Social Mapper** - Facial recognition across social media platforms
- ⭐ **Seeker** (in docker-vps) - Geolocation social engineering tool
- ⭐ **Twint** (global pip) - Twitter intelligence gathering

## 📖 Quick Start Guides

### For Username Reconnaissance:
```bash
# Quick search
sherlock username

# Detailed report
maigret username --html --pdf
```

### For Email Investigation:
```bash
# Check where email is registered
holehe email@example.com

# Harvest emails from domain
cd theHarvester
python3 theHarvester.py -d company.com -b all
```

### For Automated Scanning:
```bash
# Start SpiderFoot web interface
cd spiderfoot
python3 sf.py -l 127.0.0.1:5001
# Visit http://127.0.0.1:5001

# Use Recon-ng framework
cd recon-ng
python3 recon-ng
```

### For Social Engineering Testing:
```bash
# Facial recognition across platforms
cd social_mapper
python3 social_mapper.py -f imagefolder -i ./photos/ -m fast -fb -tw

# Geolocation tracking (Docker)
cd docker-vps
./demo-seeker.sh
```

## 📚 Documentation

### Main Guides:
- **[COMPLETE_OSINT_TOOLKIT.md](COMPLETE_OSINT_TOOLKIT.md)** - Comprehensive guide for all OSINT tools
- **[docker-vps/SEEKER_GUIDE.md](docker-vps/SEEKER_GUIDE.md)** - Complete Seeker usage with Docker and hosting
- **[social_mapper/WARP.md](social_mapper/WARP.md)** - Social Mapper architecture and development guide

### Tool-Specific Docs:
Each tool directory contains its own README with detailed usage instructions.

## 🛠️ Docker VPS

The `docker-vps/` directory contains a complete penetration testing environment with:

**Installed Tools:**
- Seeker (geolocation social engineering)
- Nmap, Nikto, Gobuster, Dirb
- SQLMap, Hydra, John the Ripper, Hashcat
- Network tools (tcpdump, netcat, whois)

**Quick Start:**
```bash
cd docker-vps

# Start VPS
docker-compose up -d

# Access shell
docker exec -it whitehacking-vps bash

# Run Seeker
cd /opt/seeker && python3 seeker.py -p 9999
```

**Documentation:**
- `docker-vps/README.md` - VPS overview
- `docker-vps/SEEKER_GUIDE.md` - Complete Seeker guide with ngrok/cloudflare setup
- `docker-vps/HOW_IT_WORKS.md` - Technical details and protection strategies
- `docker-vps/EXPOSE_TO_INTERNET.md` - ngrok/cloudflare/port forwarding setup

## ⚡ Common Workflows

### Workflow 1: Complete Person Investigation
```bash
# 1. Username search
sherlock target_username
maigret target_username --html

# 2. If you find email
holehe found@email.com

# 3. Domain research
cd theHarvester
python3 theHarvester.py -d company.com -b all

# 4. Automated deep dive
cd ../spiderfoot
python3 sf.py -l 127.0.0.1:5001
# Scan email via web interface

# 5. Twitter investigation
twint -u username --user-full
```

### Workflow 2: Company Assessment
```bash
# 1. Recon-ng for structured data
cd recon-ng
python3 recon-ng
# workspaces create company_name
# db insert domains company.com
# marketplace install all
# modules load recon/domains-hosts/hackertarget
# run

# 2. SpiderFoot automated scan
cd ../spiderfoot
python3 sf.py -s company.com -o json

# 3. Harvest employee emails
cd ../theHarvester
python3 theHarvester.py -d company.com -b linkedin,google,bing
```

### Workflow 3: Social Engineering Assessment
```bash
# 1. Collect employee photos from company website/LinkedIn
# Save to folder: /path/to/photos/

# 2. Find social media profiles
cd social_mapper
python3 social_mapper.py -f imagefolder -i /path/to/photos/ -m accurate -a

# 3. Test location tracking awareness (with permission!)
cd ../docker-vps
docker-compose up -d
./demo-seeker.sh
# Or follow SEEKER_GUIDE.md for full setup with ngrok
```

## 🔒 Security & Ethics

### ✅ Authorized Use Cases:
- Personal privacy audits (test yourself)
- Bug bounty programs (within scope)
- Security assessments (with signed contracts)
- Employee training (with management approval)
- Academic research (with IRB approval)

### ❌ Prohibited Activities:
- Stalking or harassment
- Unauthorized targeting
- Identity theft or fraud
- Corporate espionage
- Doxxing or public exposure

### 📋 Best Practices:
1. **Get Written Permission** - Always have documentation
2. **Test on Yourself First** - Understand what you're collecting
3. **Use VPN/Tor** - Protect your identity during investigations
4. **Document Everything** - Keep detailed notes and logs
5. **Delete Data After Testing** - Don't retain unnecessary information
6. **Educate Targets** - Explain findings and protection strategies

## 🆘 Troubleshooting

### Tools Not Found:
```bash
# Reinstall pip-installed tools
pip3 install --upgrade sherlock-project maigret holehe twint

# Check installation
which sherlock maigret holehe twint
```

### Docker VPS Issues:
```bash
# Rebuild VPS
cd docker-vps
docker-compose down
docker-compose up -d --build

# Check container status
docker ps | grep whitehacking-vps

# View logs
docker logs whitehacking-vps
```

### Permission Errors:
```bash
# Some tools require elevated permissions
# For nmap scans in Docker:
docker exec -it --privileged whitehacking-vps bash
```

## 📦 Adding New Tools

To add a new tool to this directory:

1. **Clone/install the tool:**
   ```bash
   cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering
   git clone https://github.com/tool/repo
   ```

2. **Update this README** with the tool description

3. **Update COMPLETE_OSINT_TOOLKIT.md** if it's an OSINT tool

4. **Add to .gitignore** any results/logs folders

## 📊 Tool Comparison

| Tool | Type | Focus | Speed | Difficulty |
|------|------|-------|-------|------------|
| Sherlock | CLI | Usernames | ⚡⚡⚡ | Easy |
| Maigret | CLI | Usernames | ⚡⚡ | Easy |
| Holehe | CLI | Emails | ⚡⚡⚡ | Easy |
| theHarvester | CLI | Emails/Domains | ⚡⚡ | Easy |
| SpiderFoot | Web | Automated | ⚡⚡ | Medium |
| Recon-ng | Framework | Modular | ⚡⚡ | Medium-Hard |
| Social Mapper | CLI | Facial Recog | ⚡ | Hard |
| Seeker | Web/Docker | Geolocation | ⚡⚡ | Medium |
| Twint | CLI | Twitter | ⚡⚡ | Medium |

## 🔄 Updates

To update all tools:
```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering

# Update git-based tools
for dir in sherlock spiderfoot recon-ng social_mapper theHarvester WhatsMyName; do
    cd $dir && git pull && cd ..
done

# Update pip-installed tools
pip3 install --upgrade sherlock-project maigret holehe twint

# Update Docker VPS
cd docker-vps
docker-compose pull
docker-compose up -d --build
```

## 📞 Support

For issues with specific tools, check their README files in respective directories or visit:
- SpiderFoot: https://github.com/smicallef/spiderfoot
- Recon-ng: https://github.com/lanmaster53/recon-ng
- Sherlock: https://github.com/sherlock-project/sherlock
- Social Mapper: https://github.com/Greenwolf/social_mapper
- Seeker: https://github.com/thewhiteh4t/seeker

## 📄 License

Each tool in this directory has its own license. Check individual tool directories for license information.

---

**Last Updated**: November 2024  
**Maintained by**: Bug Bounty Hunting Toolkit
