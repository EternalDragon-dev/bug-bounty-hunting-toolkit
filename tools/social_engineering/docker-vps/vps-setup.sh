#!/bin/bash

echo "🔒 White Hat Hacking VPS - Tool Setup"
echo "====================================="

# Create aliases for common tools
cat >> /home/vpsuser/.bashrc << 'EOF'

# White Hat Hacking Tool Aliases
alias seeker='cd /opt/seeker && python3 seeker.py'
alias tools='echo "Available tools: seeker, nmap, nikto, sqlmap, gobuster, dirb, hydra, john, hashcat"'
alias hackhelp='echo "
🔒 White Hat Hacking VPS Tools:

OSINT & Reconnaissance:
  seeker         - Social engineering tool for geolocation tracking
  nmap           - Network discovery and security auditing
  nikto          - Web vulnerability scanner
  gobuster       - Directory/file & DNS brute-forcer
  dirb           - Web content scanner

Web Application Testing:
  sqlmap         - SQL injection testing
  curl           - HTTP client for API testing
  
Password Attacks:
  hydra          - Login brute-forcer
  john           - Password hash cracker
  hashcat        - Advanced password recovery

Network Analysis:
  tcpdump        - Network packet analyzer
  netcat         - Network utility
  traceroute     - Network path tracing
  whois          - Domain information lookup

Usage Examples:
  seeker                    # Start Seeker social engineering tool
  nmap -sV target.com       # Version scan
  nikto -h https://target.com
  gobuster dir -u https://target.com -w /usr/share/wordlists/dirb/common.txt
  sqlmap -u \"http://target.com/page?id=1\" --dbs
"'

EOF

# Create tools directory for user
mkdir -p /home/vpsuser/tools
chown vpsuser:vpsuser /home/vpsuser/tools

# Download common wordlists
mkdir -p /usr/share/wordlists
cd /usr/share/wordlists
wget -q https://github.com/danielmiessler/SecLists/archive/master.zip -O seclists.zip
unzip -q seclists.zip
rm seclists.zip
mv SecLists-master seclists

echo "✅ VPS setup complete!"
echo "Run 'hackhelp' for available tools and usage examples"