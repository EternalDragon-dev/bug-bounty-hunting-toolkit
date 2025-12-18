# Complete OSINT Toolkit - Installation Guide

## 📋 Table of Contents
1. [Username & Social Media Tools](#username--social-media-tools)
2. [Automation & Frameworks](#automation--frameworks)
3. [Specialized Tools](#specialized-tools)
4. [GUI Tools](#gui-tools)
5. [Quick Start Guide](#quick-start-guide)
6. [Best Practices](#best-practices)

---

## Username & Social Media Tools

### 1. 🔍 **Sherlock** ⭐ INSTALLED
**Location:** `~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/sherlock`

**Purpose:** Find usernames across 300+ social networks

**Why it's useful:**
Sherlock rapidly checks if a specific username exists on hundreds of platforms simultaneously. This is invaluable for bug bounty hunters and penetration testers who need to:
- Discover a target's complete digital footprint across multiple platforms
- Find forgotten or secondary accounts that may have weaker security
- Identify where a target is most active online for social engineering vectors
- Map out an organization's employees' public profiles for phishing campaigns
- Verify if a username is being impersonated across different sites

**Real-world scenario:** You've identified a target employee's username on LinkedIn. Running Sherlock reveals they use the same username on GitHub (code repositories with API keys), Twitter (personal opinions), and Reddit (technical discussions) - all potentially valuable intelligence sources.

**Usage:**
```bash
# Basic search
sherlock username

# Save to file
sherlock username -o results.txt

# Search specific platforms
sherlock username --site Instagram --site Twitter --site GitHub

# Export as CSV
sherlock username --csv

# Verbose output
sherlock username --verbose
```

**Best for:** Quick username reconnaissance

---

### 2. 🎯 **Maigret** ⭐ INSTALLED
**Location:** Installed globally via pip

**Purpose:** Advanced username OSINT with 3000+ sites and beautiful reports

**Why it's useful:**
Maigret is Sherlock on steroids - it checks 10x more sites and generates professional HTML/PDF reports suitable for client deliverables. Key advantages:
- **Extended coverage**: 3000+ sites including regional platforms (Russian VK, Chinese Weibo, Japanese LINE)
- **Professional reporting**: HTML reports with screenshots, timestamps, and categorized findings
- **Tor integration**: Built-in anonymity for sensitive investigations
- **Deep analysis**: Extracts profile metadata (join dates, bio, followers) when available
- **Client-ready output**: PDF reports you can include in penetration testing deliverables

**Real-world scenario:** During a red team engagement, you need to present findings to executives. Maigret generates a visual HTML report showing 47 discovered profiles of the target employee, complete with profile pictures and activity timelines - far more convincing than a text file.

**Usage:**
```bash
# Basic search
maigret username

# Generate HTML report
maigret username --html

# Generate PDF report
maigret username --pdf

# Search top 100 sites (faster)
maigret username --top-sites 100

# Generate all report formats
maigret username -T -C -H -P -J

# Use with Tor for anonymity
maigret username --tor-proxy
```

**Best for:** Detailed investigations with professional reports

---

### 3. 📧 **Holehe** ⭐ INSTALLED
**Location:** Installed globally via pip

**Purpose:** Check which websites an email address is registered on (120+ sites)

**Why it's useful:**
Holehe performs email enumeration without triggering password reset emails or alerts. It exploits subtle differences in website responses (login errors, account recovery flows) to detect if an email is registered. Critical for:
- **Credential stuffing assessment**: Identify where leaked credentials might work
- **Attack surface mapping**: Find all platforms where a target has accounts
- **Phishing vector identification**: Discover which platforms to impersonate for maximum credibility
- **Data breach correlation**: Cross-reference emails from breach databases with active accounts
- **Account takeover opportunities**: Identify platforms with weak password reset mechanisms

**How it works:** When you check "target@company.com", Holehe simulates login attempts and analyzes HTTP responses. A "user not found" vs "incorrect password" message reveals registration status without actually logging in.

**Real-world scenario:** You find "admin@targetcorp.com" in an old data breach (password: "Summer2018!"). Holehe reveals this email is registered on AWS, Azure, GitHub, DockerHub, and NPM - each a potential entry point if the password was reused.

**Usage:**
```bash
# Check email registrations
holehe email@example.com

# Check your own email (for testing)
holehe your.email@gmail.com
```

**Sites it checks:**
- Social media (Twitter, Instagram, Facebook)
- Dating apps (Tinder, Bumble, OkCupid)
- Gaming platforms (Xbox, PlayStation, Steam)
- E-commerce (Amazon, eBay, Etsy)
- Professional networks (LinkedIn, GitHub)

**Best for:** Email-based reconnaissance

---

### 4. 🐦 **Twint** ⭐ INSTALLED
**Location:** Installed globally via pip

**Purpose:** Twitter intelligence gathering without API limits (bypass Twitter/X API restrictions)

**Why it's useful:**
Twint scrapes Twitter/X data without requiring API keys, avoiding rate limits and $100/month API fees. Essential for:
- **Historical timeline analysis**: Scrape ALL tweets from a target (Twitter API limits to 3,200)
- **Geolocation tracking**: Identify tweets from specific locations ("check-ins" at office/home)
- **Relationship mapping**: Extract follower/following networks to identify associates
- **Content analysis**: Search for keywords like "password", "VPN", "working from", "on vacation"
- **Metadata extraction**: Capture tweet timestamps, devices used, and deleted tweets (if cached)
- **Sentiment analysis**: Bulk export tweets for AI-powered sentiment/topic modeling

**How it works:** Twint bypasses the API by mimicking browser requests to Twitter's search and profile pages, then parsing the HTML - no authentication required.

**Real-world scenario:** A target employee tweets "Excited for our AWS migration next week!" in 2021. Twint retrieves this old tweet (beyond API limits) revealing infrastructure details. You also discover they tweet from "Twitter for iPhone" between 8am-5pm (working hours) and their location history shows regular check-ins near a specific office building.

**Usage:**
```bash
# Search tweets by username
twint -u username

# Search tweets by keyword
twint -s "keyword"

# Get user info
twint -u username --user-full

# Search by location
twint -g "40.7127,-74.0059,10km"

# Export to CSV
twint -u username -o output.csv --csv

# Get followers
twint -u username --followers

# Search by date range
twint -u username --since "2023-01-01" --until "2023-12-31"
```

**Note:** Twitter/X has made scraping harder. Twint may have limitations.

**Best for:** Twitter-specific investigations

---

## Automation & Frameworks

### 5. 🕷️ **SpiderFoot** ⭐ INSTALLED
**Location:** `~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/spiderfoot`

**Purpose:** Automated OSINT reconnaissance with 200+ modules (OSINT automation framework)

**Why it's useful:**
SpiderFoot is a one-stop automated reconnaissance platform that correlates data from 200+ sources. Think of it as "set it and forget it" OSINT:
- **Passive reconnaissance**: Gather intelligence without touching target systems
- **Correlation engine**: Automatically discovers relationships (domain → emails → social profiles → phone numbers)
- **Web-based interface**: User-friendly dashboard with interactive graphs
- **API integrations**: Queries Shodan, VirusTotal, HaveIBeenPwned, Certificate Transparency logs, and more
- **Continuous monitoring**: Schedule scans to detect new exposed data
- **Export flexibility**: Generate reports in JSON, CSV, HTML for further analysis

**What it discovers:**
- Subdomains, IP addresses, open ports
- Email addresses and format patterns (firstname.lastname@company.com)
- Employee names from LinkedIn, social media
- Leaked credentials from breach databases
- SSL certificates and historical DNS records
- Technologies used (web servers, frameworks, CDNs)
- Cloud storage buckets (S3, Azure Blob)
- Related domains and acquisitions

**Real-world scenario:** You input "targetcorp.com" into SpiderFoot. Within 30 minutes, it returns: 47 subdomains, 12 employee email addresses, 3 exposed S3 buckets, 2 LinkedIn employee profiles, 5 historical data breaches containing company emails, and identifies they use Cloudflare and AWS. All from a single scan.

**Usage:**
```bash
# Start web interface
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/spiderfoot
python3 sf.py -l 127.0.0.1:5001

# Then open browser to: http://127.0.0.1:5001
```

**CLI Usage:**
```bash
# Scan a domain
python3 sf.py -s example.com -o json

# List available modules
python3 sf.py -M

# Use specific modules
python3 sf.py -s example.com -m sfp_dnsresolve,sfp_emailformat
```

**Modules include:**
- DNS records
- WHOIS information
- Email addresses
- Social media profiles
- Leaked credentials
- Subdomains
- SSL certificates
- IP geolocation

**Best for:** Comprehensive automated scans

---

### 6. 🔧 **Recon-ng** ⭐ INSTALLED
**Location:** `~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/recon-ng`

**Purpose:** Full-featured reconnaissance framework (the Metasploit of OSINT - modular, scriptable, database-driven)

**Why it's useful:**
Recon-ng is for structured, methodical investigations where you need granular control. Unlike automated tools, you manually select and chain modules:
- **Modular architecture**: 100+ modules for specific tasks (DNS brute-force, email harvesting, contact discovery)
- **Workspace isolation**: Separate databases for different targets/engagements
- **API key management**: Centralized storage for Shodan, Censys, Hunter.io keys
- **Database-driven**: All findings stored in SQLite - query with SQL for complex analysis
- **Chaining modules**: Output of one module becomes input for another (domains → IPs → Shodan → vulnerabilities)
- **Repeatable**: Save module configurations for consistent assessments

**Module categories explained:**
- **Discovery**: Find subdomains, hosts, IPs (google_site_web, bing_domain_web, hackertarget)
- **Recon**: Gather contacts, profiles, employees (whois_pocs, hibp_breach, linkedin_contacts)
- **Import**: Load data from other tools (CSVs, Masscan, Nmap)
- **Reporting**: Generate formatted output (HTML, CSV, JSON, Excel)

**Real-world scenario:** During a phishing simulation, you:
1. Use `google_site_web` module to find 20 subdomains
2. Run `bing_linkedin_cache` to extract 50 employee names from LinkedIn
3. Apply `hibp_breach` to check if any employee emails appear in breaches
4. Use `email_validator` to verify email format (firstname.lastname@company.com)
5. Export to CSV → feed into Gophish phishing framework
All findings are in the Recon-ng database for future reference.

**Usage:**
```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/recon-ng
python3 recon-ng

# Inside recon-ng:
# Create workspace
workspaces create my_investigation

# Install modules
marketplace install all

# Search for modules
marketplace search

# Use a module
modules load recon/domains-hosts/google_site_web
options set SOURCE example.com
run

# Add domains/hosts
db insert domains example.com

# Show results
show hosts
show contacts
```

**Module categories:**
- Discovery (subdomains, hosts)
- Import/Export
- Recon (contacts, profiles)
- Reporting

**Best for:** Structured, modular investigations

---

## Specialized Tools

### 7. 👤 **Social-Mapper** ⭐ INSTALLED
**Location:** `~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/social_mapper`

**Purpose:** Facial recognition to correlate social media profiles across platforms (eliminate false positives in name searches)

**Why it's useful:**
When searching for "John Smith", you get thousands of results. Social Mapper uses facial recognition to identify THE correct John Smith:
- **Facial matching**: Upload target photos → tool finds matching faces on social media
- **Cross-platform correlation**: Link LinkedIn profile → Facebook → Twitter → Instagram as the same person
- **Bulk processing**: Process 100+ employees from a company org chart simultaneously
- **False positive elimination**: Name searches return 500 "Michael Johnson" profiles; facial recognition narrows to 1
- **HTML reports**: Visual reports with side-by-side photo comparisons for human verification
- **Reconnaissance at scale**: Map entire company employee social media presence automatically

**How it works:**
1. You provide photos (from company website, LinkedIn, or physical surveillance)
2. Social Mapper searches LinkedIn/Facebook/Twitter/Instagram/VK for the person's name
3. Face recognition compares target photo with profile pictures from search results
4. Matches above threshold (configurable) are flagged as positive identifications
5. Generates HTML report with profile links and photos

**Platforms supported:** LinkedIn, Facebook, Twitter, Instagram, Pinterest, VKontakte (VK), Weibo, Douban

**Real-world scenario:** Your client provides employee photos from their company website. You feed 50 faces into Social Mapper. It returns:
- 47 LinkedIn profiles (3 employees have no LinkedIn)
- 32 Facebook accounts (15 using privacy settings)
- 28 Instagram profiles
- 41 Twitter accounts

You now have a complete social media map of the organization for targeted phishing or social engineering assessment.

**⚠️ WARNING:** Facebook detection kicks in after ~100 searches. Use disposable accounts.

**Usage:**
```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/social_mapper

# Search with photos
python3 social_mapper.py -f path/to/photos/ -m all -o results

# Search specific platforms
python3 social_mapper.py -f photos/ -m linkedin,facebook,twitter

# Use with names file
python3 social_mapper.py -f photos/ -i names.txt -m all
```

**Platforms supported:**
- LinkedIn
- Facebook
- Twitter
- Instagram
- VKontakte (VK)
- Weibo
- Douban

**Requirements:**
- Photos of target individuals
- Valid social media credentials (for scraping)

**Best for:** Matching faces across platforms

---

### 8. 📝 **WhatsMyName** ⭐ INSTALLED
**Location:** `~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/WhatsMyName`

**Purpose:** Username enumeration with curated database (alternative to Sherlock with focus on accuracy)

**Why it's useful:**
WhatsMyName provides a constantly-updated database of 500+ sites with detection rules optimized to minimize false positives:
- **JSON database**: `wmn-data.json` contains site-specific detection logic (response codes, page content, error messages)
- **Integration-friendly**: Designed to be embedded in other tools (Python scripts, web apps, automation frameworks)
- **Community-maintained**: Database updated weekly with new sites and fixed detection rules
- **Custom searches**: Write your own scripts using the JSON database for specialized workflows
- **Lower false positives**: Each site has multiple confirmation methods (not just HTTP 200)

**How it differs from Sherlock:**
- **Sherlock**: Fast, CLI-focused, good for quick checks
- **WhatsMyName**: Curated database for integration, more accurate detections, better for custom tooling

**Use cases:**
- Build custom OSINT dashboards that query the WhatsMyName database
- Integrate username checking into CI/CD pipelines for monitoring brand impersonation
- Create automated alerts when target usernames appear on new platforms
- Combine with API integrations for enriched profile data

**Best for:** Developers building custom OSINT tools or automated monitoring systems

---

## GUI Tools

### 9. 🌐 **Maltego** 📥 DOWNLOAD REQUIRED
**Website:** https://www.maltego.com/downloads/

**Purpose:** Visual link analysis and relationship mapping (see connections between people, companies, domains, IPs)

**Why it's useful:**
Maltego transforms raw OSINT data into interactive visual graphs showing relationships. It's THE tool for understanding complex connections:
- **Visual intelligence**: See how domains → IPs → owners → companies → employees → social profiles connect
- **Transforms**: Automated queries to 100+ data sources (DNS, WHOIS, social media, threat intel)
- **Pattern recognition**: Spot hidden relationships humans miss in spreadsheet data
- **Pivot analysis**: Click any entity → run transforms → discover new connected entities
- **Collaborative investigations**: Share graphs with team members
- **Presentation-ready**: Export graphs for client reports or executive briefings

**What you can map:**
- **Infrastructure**: domain.com → DNS records → IP addresses → hosting provider → other domains on same server
- **People**: employee name → email → social profiles → phone number → physical address → associates
- **Organizations**: company.com → acquired companies → subsidiaries → key employees → investors
- **Threat intelligence**: malware hash → C2 domains → IP addresses → related campaigns → threat actor attribution

**Transforms explained:**
- **Built-in transforms**: DNS lookups, WHOIS, email pattern generation
- **Transform Hub**: Free/paid transform packs (Shodan, VirusTotal, Farsight DNSDB, Censys, PassiveTotal)
- **Custom transforms**: Write your own in Python to query proprietary databases

**Real-world scenario:** 
You start with "targetcorp.com" domain. Run transforms and the graph reveals:
- 15 subdomains all resolve to AWS IPs in us-east-1
- One subdomain (vpn.targetcorp.com) resolves to an on-premise IP
- WHOIS shows domain registered by "John Doe (jdoe@targetcorp.com)"
- LinkedIn transform finds John Doe is the IT Director
- His Twitter account mentions attending "DefCon 2022"
- Twitter followers include employees from partner companies
- A data breach transform shows jdoe@targetcorp.com in a 2019 breach

This visual map gives you attack vectors (on-premise VPN), key personnel (IT Director), and potential credential reuse (2019 breach).

**Installation:**
1. Download Maltego CE (Community Edition) - FREE
2. Install the `.dmg` file for macOS
3. Create a free account on first launch
4. Run transforms to gather intelligence

**Features:**
- Visual graphs of relationships
- Transforms for data gathering
- Link analysis
- Report generation
- Export to various formats

**Transforms available:**
- Social media profiles
- Domain/IP information
- Email addresses
- Phone numbers
- Company data
- Person information

**Usage:**
1. Create a new graph
2. Add entities (person, email, domain, etc.)
3. Run transforms to gather data
4. Visualize connections
5. Export results

**Best for:** Visualizing complex relationships and connections

---

## Quick Start Guide

### 🎯 Scenario 1: Username Investigation (Your own profile)
```bash
# Step 1: Quick check with Sherlock
sherlock your_username

# Step 2: Detailed report with Maigret
maigret your_username --html --pdf

# Step 3: Check reports
open reports/your_username.html
```

---

### 🎯 Scenario 2: Email Investigation (Your own email)
```bash
# Check where your email is registered
holehe your.email@example.com

# Use in SpiderFoot for deeper analysis
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/spiderfoot
python3 sf.py -l 127.0.0.1:5001
# Then scan your email via web interface
```

---

### 🎯 Scenario 3: Domain Investigation
```bash
# Use Recon-ng
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/recon-ng
python3 recon-ng

# Inside recon-ng:
workspaces create domain_investigation
db insert domains example.com
marketplace install recon/domains-hosts/hackertarget
modules load recon/domains-hosts/hackertarget
run
show hosts

# Or use SpiderFoot web interface
```

---

### 🎯 Scenario 4: Twitter Investigation
```bash
# Search user tweets
twint -u username --limit 100

# Search by keyword
twint -s "cybersecurity" --limit 50

# Get user followers
twint -u username --followers

# Export to CSV
twint -u username -o results.csv --csv
```

---

## Best Practices

### ✅ DO:
1. **Test on yourself first** - Always start with your own profiles
2. **Use VPN/Tor** - Protect your identity during investigations
3. **Document everything** - Keep detailed notes of findings
4. **Respect rate limits** - Don't overwhelm servers
5. **Verify information** - Cross-reference from multiple sources
6. **Get authorization** - Only investigate with proper permission
7. **Save reports** - Generate and archive reports for reference
8. **Update tools regularly** - Keep tools up-to-date

### ❌ DON'T:
1. **Target individuals without permission** - Always get authorization
2. **Use for harassment** - Never use for malicious purposes
3. **Share sensitive data** - Respect privacy
4. **Violate ToS** - Follow platform terms of service
5. **Use real credentials for automation** - Use test accounts
6. **Assume accuracy** - Verify before acting on information
7. **Forget OPSEC** - Protect your own identity

---

## Tool Comparison Matrix

| Tool | Type | Sites | Speed | Reports | Difficulty | Best Use Case |
|------|------|-------|-------|---------|------------|---------------|
| **Sherlock** | CLI | 300+ | ⚡⚡⚡ | TXT, CSV | Easy | Quick username checks |
| **Maigret** | CLI | 3000+ | ⚡⚡ | HTML, PDF, CSV | Easy | Detailed username reports |
| **Holehe** | CLI | 120+ | ⚡⚡⚡ | Terminal | Easy | Email investigations |
| **SpiderFoot** | Web/CLI | 200+ modules | ⚡⚡ | HTML, CSV, JSON | Medium | Automated full scans |
| **Recon-ng** | Framework | Many modules | ⚡⚡ | Various | Medium-Hard | Structured investigations |
| **Social-Mapper** | CLI | 7 platforms | ⚡ | HTML | Hard | Facial recognition |
| **Twint** | CLI | Twitter only | ⚡⚡ | CSV, JSON | Medium | Twitter-specific |
| **Maltego** | GUI | Many transforms | ⚡ | Graphs, Reports | Medium | Visual analysis |

---

## Advanced Workflows

### 🔥 Full OSINT Investigation Workflow

```bash
# 1. Start with username
sherlock target_username -o sherlock_results.txt

# 2. Deep dive
maigret target_username --html --pdf

# 3. If you find an email
holehe found_email@example.com

# 4. Full automated scan
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/spiderfoot
python3 sf.py -l 127.0.0.1:5001
# Scan via web interface

# 5. Structured investigation
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/recon-ng
python3 recon-ng
# Use modules for specific data

# 6. Twitter investigation
twint -u username --user-full -o twitter_results.csv --csv

# 7. Visualize in Maltego
# Import findings and create relationship graph
```

---

## Output Management

### Directory Structure
```
social_engineering/
├── sherlock/
├── spiderfoot/
├── recon-ng/
├── social_mapper/
├── maigret/
├── WhatsMyName/
├── OSINT_TOOLS_GUIDE.md
└── COMPLETE_OSINT_TOOLKIT.md (this file)

# Store your results:
results/
├── username_investigations/
├── email_investigations/
├── domain_investigations/
└── reports/
```

### Recommended Results Structure
```bash
mkdir -p ~/Documents/bug-bounty-hunting-toolkit/results/{username,email,domain,twitter,reports}
```

---

## Troubleshooting

### Common Issues

**1. "Command not found" errors:**
```bash
# Reinstall the tool
pip3 install --upgrade tool-name

# Check if it's in PATH
which sherlock
```

**2. Rate limiting / IP bans:**
```bash
# Use Tor with Maigret
maigret username --tor-proxy

# Add delays
sherlock username --timeout 10
```

**3. SpiderFoot won't start:**
```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering/spiderfoot
pip3 install -r requirements.txt
python3 sf.py -l 127.0.0.1:5001
```

**4. Recon-ng module errors:**
```bash
# Inside recon-ng
marketplace refresh
marketplace install all
```

---

## Updates & Maintenance

### Update all tools:
```bash
cd ~/Documents/bug-bounty-hunting-toolkit/tools/social_engineering

# Update Sherlock
cd sherlock && git pull && cd ..

# Update SpiderFoot
cd spiderfoot && git pull && pip3 install -r requirements.txt && cd ..

# Update Recon-ng
cd recon-ng && git pull && pip3 install -r REQUIREMENTS && cd ..

# Update pip tools
pip3 install --upgrade sherlock-project maigret holehe twint

# Update Maltego
# Download latest version from website
```

---

## Legal & Ethical Guidelines

### 🚨 IMPORTANT REMINDERS:

1. **Authorization Required**
   - Get written permission for investigations
   - Only test on your own accounts without permission
   - Respect privacy laws in your jurisdiction

2. **Ethical Use Only**
   - Security research
   - Authorized penetration testing
   - Educational purposes
   - Personal privacy audits

3. **Illegal Uses** ❌
   - Stalking or harassment
   - Identity theft
   - Unauthorized access
   - Doxxing
   - Corporate espionage

4. **Data Handling**
   - Encrypt sensitive findings
   - Secure storage of results
   - Proper data disposal
   - Respect data protection laws (GDPR, CCPA, etc.)

---

## Additional Resources

### 📚 Learning Resources:
- **OSINT Framework:** https://osintframework.com/
- **Awesome OSINT:** https://github.com/jivoi/awesome-osint
- **Intel Techniques:** https://inteltechniques.com/
- **OSINT Curious:** https://osintcurio.us/

### 🛠️ More Tools to Explore:
- **theHarvester** - Email/subdomain discovery
- **Metagoofil** - Metadata extraction
- **Sublist3r** - Subdomain enumeration
- **Photon** - Web crawler for OSINT
- **Gobuster** - Directory/DNS busting

### 📖 Books:
- "Open Source Intelligence Techniques" by Michael Bazzell
- "OSINT Handbook" by i-intelligence
- "Social Engineering: The Art of Human Hacking" by Christopher Hadnagy

---

## Quick Reference Commands

```bash
# USERNAME SEARCHES
sherlock username
maigret username --html

# EMAIL SEARCHES  
holehe email@example.com

# TWITTER
twint -u username

# AUTOMATED SCANS
cd spiderfoot && python3 sf.py -l 127.0.0.1:5001

# FRAMEWORK
cd recon-ng && python3 recon-ng

# REPORTS
maigret username -T -C -H -P
```

---

## Summary

You now have a **complete OSINT toolkit** with:
- ✅ 8 CLI/framework tools installed
- ✅ 1 GUI tool (Maltego - requires download)
- ✅ 300+ to 3000+ sites coverage
- ✅ Email, username, domain, and Twitter investigation capabilities
- ✅ Automated and manual investigation options
- ✅ Multiple report formats (HTML, PDF, CSV, JSON)
- ✅ Facial recognition capabilities
- ✅ Visual link analysis (Maltego)

**Start with:** Test all tools on your own information to understand what data is publicly available about you!

---

**Last Updated:** November 2025
**Toolkit Version:** 1.0
**Maintained by:** Your Bug Bounty Toolkit
