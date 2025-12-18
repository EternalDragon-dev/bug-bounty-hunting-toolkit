#!/usr/bin/env python3
"""
Advanced OSINT Intelligence Scraper
===================================

A comprehensive data scraping tool for gathering intelligence on businesses and individuals
from publicly available sources. Designed for legitimate security research, client prospecting,
and safety verification purposes.

Features:
- Multi-source data aggregation (social media, business directories, public records)
- Business intelligence gathering (company info, employees, technologies)
- Personal background verification (social profiles, employment history)
- Risk assessment and red flag detection
- Professional report generation
- Ethical compliance and rate limiting

Author: Advanced Security Research Team
Version: 2.0
"""

import requests
import json
import time
import re
import csv
import sqlite3
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver
import whois
from bs4 import BeautifulSoup
import urllib.parse
import base64
import hashlib
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

@dataclass
class PersonProfile:
    """Data structure for individual profiles"""
    name: str
    location: str = ""
    email: str = ""
    phone: str = ""
    social_profiles: List[str] = None
    employment_history: List[str] = None
    education: List[str] = None
    risk_flags: List[str] = None
    verification_status: str = "unknown"
    last_updated: str = ""

@dataclass
class BusinessProfile:
    """Data structure for business profiles"""
    name: str
    location: str = ""
    industry: str = ""
    website: str = ""
    email: str = ""
    phone: str = ""
    employees: List[str] = None
    technologies: List[str] = None
    social_presence: List[str] = None
    financial_info: Dict = None
    risk_assessment: str = "unknown"
    prospect_score: int = 0
    last_updated: str = ""

class OSINTScraper:
    """Advanced OSINT Intelligence Gathering System"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit = 2  # seconds between requests
        self.results = {
            'persons': [],
            'businesses': [],
            'metadata': {
                'scan_date': datetime.now().isoformat(),
                'total_sources': 0,
                'confidence_score': 0
            }
        }
        self.db_path = "osint_intelligence.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create persons table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            email TEXT,
            phone TEXT,
            social_profiles TEXT,
            employment_history TEXT,
            education TEXT,
            risk_flags TEXT,
            verification_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create businesses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            industry TEXT,
            website TEXT,
            email TEXT,
            phone TEXT,
            employees TEXT,
            technologies TEXT,
            social_presence TEXT,
            financial_info TEXT,
            risk_assessment TEXT,
            prospect_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def rate_limit_request(self):
        """Implement rate limiting for ethical scraping"""
        time.sleep(self.rate_limit)
        
    def sanitize_input(self, data: str) -> str:
        """Sanitize input data for safe processing"""
        return re.sub(r'[<>"\';]', '', data.strip())
        
    def search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search Google for publicly available information
        Note: In production, use Google Custom Search API
        """
        self.rate_limit_request()
        results = []
        
        try:
            # Simulate Google search results (replace with actual API calls)
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Note: This is a placeholder - use proper search APIs in production
            results.append({
                'title': f"Search results for: {query}",
                'url': search_url,
                'snippet': f"Searching for information about {query}",
                'source': 'google_search'
            })
            
        except Exception as e:
            print(f"Google search error: {e}")
            
        return results
        
    def search_linkedin(self, name: str, location: str = "") -> Dict:
        """
        Gather LinkedIn professional information
        Note: Use LinkedIn API with proper authentication
        """
        self.rate_limit_request()
        profile_data = {
            'name': name,
            'location': location,
            'current_position': "",
            'company': "",
            'industry': "",
            'connections': 0,
            'skills': [],
            'experience': [],
            'education': []
        }
        
        try:
            # Placeholder for LinkedIn API integration
            search_query = f"{name} {location} site:linkedin.com"
            results = self.search_google(search_query, 5)
            
            for result in results:
                if 'linkedin.com/in/' in result.get('url', ''):
                    profile_data['linkedin_url'] = result['url']
                    # Extract additional info from snippet
                    if 'CEO' in result.get('snippet', ''):
                        profile_data['current_position'] = 'CEO'
                    
        except Exception as e:
            print(f"LinkedIn search error: {e}")
            
        return profile_data
        
    def search_social_media(self, name: str) -> List[Dict]:
        """Search various social media platforms for profiles"""
        self.rate_limit_request()
        platforms = ['twitter.com', 'facebook.com', 'instagram.com', 'tiktok.com']
        social_profiles = []
        
        for platform in platforms:
            try:
                search_query = f'"{name}" site:{platform}'
                results = self.search_google(search_query, 3)
                
                for result in results:
                    if platform in result.get('url', ''):
                        social_profiles.append({
                            'platform': platform.replace('.com', ''),
                            'url': result['url'],
                            'snippet': result.get('snippet', ''),
                            'confidence': self.calculate_name_match_confidence(name, result.get('snippet', ''))
                        })
                        
            except Exception as e:
                print(f"Social media search error for {platform}: {e}")
                
        return social_profiles
        
    def search_business_directories(self, business_name: str, location: str = "") -> Dict:
        """Search business directories for company information"""
        self.rate_limit_request()
        business_data = {
            'name': business_name,
            'location': location,
            'industry': "",
            'phone': "",
            'website': "",
            'employees': [],
            'annual_revenue': "",
            'founded': "",
            'directories': []
        }
        
        directories = [
            'yellowpages.com',
            'yelp.com', 
            'bbb.org',
            'crunchbase.com',
            'bloomberg.com'
        ]
        
        for directory in directories:
            try:
                search_query = f'"{business_name}" {location} site:{directory}'
                results = self.search_google(search_query, 2)
                
                for result in results:
                    if directory in result.get('url', ''):
                        business_data['directories'].append({
                            'source': directory,
                            'url': result['url'],
                            'snippet': result.get('snippet', '')
                        })
                        
                        # Extract phone numbers from snippets
                        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', result.get('snippet', ''))
                        if phone_match and not business_data['phone']:
                            business_data['phone'] = phone_match.group()
                            
            except Exception as e:
                print(f"Directory search error for {directory}: {e}")
                
        return business_data
        
    def check_domain_info(self, domain: str) -> Dict:
        """Gather domain and website information"""
        self.rate_limit_request()
        domain_data = {
            'domain': domain,
            'registrar': "",
            'creation_date': "",
            'expiration_date': "",
            'name_servers': [],
            'mx_records': [],
            'technologies': [],
            'ssl_info': {}
        }
        
        try:
            # WHOIS lookup
            w = whois.whois(domain)
            domain_data['registrar'] = str(w.registrar) if w.registrar else ""
            domain_data['creation_date'] = str(w.creation_date) if w.creation_date else ""
            domain_data['expiration_date'] = str(w.expiration_date) if w.expiration_date else ""
            
            # DNS records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                domain_data['mx_records'] = [str(mx) for mx in mx_records]
            except:
                pass
                
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                domain_data['name_servers'] = [str(ns) for ns in ns_records]
            except:
                pass
                
        except Exception as e:
            print(f"Domain info error: {e}")
            
        return domain_data
        
    def detect_technologies(self, url: str) -> List[str]:
        """Detect technologies used by a website"""
        self.rate_limit_request()
        technologies = []
        
        try:
            response = self.session.get(url, timeout=10)
            content = response.text.lower()
            headers = response.headers
            
            # Technology detection patterns
            tech_patterns = {
                'WordPress': ['wp-content', 'wordpress'],
                'React': ['react', '_react'],
                'Angular': ['angular', 'ng-'],
                'Vue.js': ['vue.js', '__vue__'],
                'jQuery': ['jquery'],
                'Bootstrap': ['bootstrap'],
                'Cloudflare': ['cloudflare'],
                'Google Analytics': ['google-analytics', 'gtag'],
                'Shopify': ['shopify', 'shop.js']
            }
            
            for tech, patterns in tech_patterns.items():
                if any(pattern in content for pattern in patterns):
                    technologies.append(tech)
                    
            # Check server headers
            server = headers.get('server', '').lower()
            if 'nginx' in server:
                technologies.append('Nginx')
            elif 'apache' in server:
                technologies.append('Apache')
                
        except Exception as e:
            print(f"Technology detection error: {e}")
            
        return technologies
        
    def assess_risk_flags(self, data: Dict, profile_type: str) -> List[str]:
        """Detect potential risk flags in gathered data"""
        risk_flags = []
        
        if profile_type == 'person':
            # Check for suspicious patterns
            social_profiles = data.get('social_profiles', [])
            if len(social_profiles) == 0:
                risk_flags.append('No social media presence found')
            elif len(social_profiles) > 10:
                risk_flags.append('Excessive social media presence')
                
            # Check employment gaps or inconsistencies
            employment = data.get('employment_history', [])
            if not employment:
                risk_flags.append('No employment history found')
                
        elif profile_type == 'business':
            # Check business legitimacy indicators
            directories = data.get('directories', [])
            if len(directories) < 2:
                risk_flags.append('Limited business directory presence')
                
            website = data.get('website', '')
            if not website:
                risk_flags.append('No official website found')
                
            # Check for recent domain registration
            domain_info = data.get('domain_info', {})
            creation_date = domain_info.get('creation_date', '')
            if creation_date:
                try:
                    created = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                    if (datetime.now() - created).days < 90:
                        risk_flags.append('Recently registered domain')
                except:
                    pass
                    
        return risk_flags
        
    def calculate_prospect_score(self, business_data: Dict) -> int:
        """Calculate business prospect scoring for potential clients"""
        score = 0
        
        # Website presence
        if business_data.get('website'):
            score += 20
            
        # Technology stack (indicates digital presence)
        technologies = business_data.get('technologies', [])
        if technologies:
            score += min(len(technologies) * 5, 25)
            
        # Directory listings (indicates established business)
        directories = business_data.get('directories', [])
        score += min(len(directories) * 10, 30)
        
        # Social media presence
        social_presence = business_data.get('social_presence', [])
        score += min(len(social_presence) * 5, 15)
        
        # Employee count (larger companies = better prospects)
        employees = business_data.get('employees', [])
        if len(employees) > 10:
            score += 10
            
        return min(score, 100)
        
    def calculate_name_match_confidence(self, target_name: str, content: str) -> float:
        """Calculate confidence score for name matches"""
        if not content:
            return 0.0
            
        target_words = target_name.lower().split()
        content_lower = content.lower()
        
        matches = sum(1 for word in target_words if word in content_lower)
        return matches / len(target_words) if target_words else 0.0
        
    def gather_person_intelligence(self, name: str, location: str = "", 
                                 email: str = "", phone: str = "") -> PersonProfile:
        """Comprehensive person intelligence gathering"""
        print(f"[*] Gathering intelligence on: {name}")
        
        # Initialize profile
        profile = PersonProfile(
            name=name,
            location=location,
            email=email,
            phone=phone,
            social_profiles=[],
            employment_history=[],
            education=[],
            risk_flags=[],
            last_updated=datetime.now().isoformat()
        )
        
        # LinkedIn search
        linkedin_data = self.search_linkedin(name, location)
        if linkedin_data.get('current_position'):
            profile.employment_history.append(linkedin_data['current_position'])
            
        # Social media search
        social_profiles = self.search_social_media(name)
        profile.social_profiles = [p['url'] for p in social_profiles if p['confidence'] > 0.5]
        
        # Risk assessment
        profile_data = asdict(profile)
        profile.risk_flags = self.assess_risk_flags(profile_data, 'person')
        
        # Verification status
        if len(profile.social_profiles) >= 2 and profile.employment_history:
            profile.verification_status = "verified"
        elif len(profile.social_profiles) >= 1:
            profile.verification_status = "partial"
        else:
            profile.verification_status = "unverified"
            
        return profile
        
    def gather_business_intelligence(self, business_name: str, location: str = "",
                                   website: str = "") -> BusinessProfile:
        """Comprehensive business intelligence gathering"""
        print(f"[*] Gathering intelligence on business: {business_name}")
        
        # Initialize profile
        profile = BusinessProfile(
            name=business_name,
            location=location,
            website=website,
            employees=[],
            technologies=[],
            social_presence=[],
            financial_info={},
            last_updated=datetime.now().isoformat()
        )
        
        # Business directory search
        directory_data = self.search_business_directories(business_name, location)
        profile.phone = directory_data.get('phone', '')
        profile.industry = directory_data.get('industry', '')
        if not profile.website and directory_data.get('website'):
            profile.website = directory_data['website']
            
        # Website analysis
        if profile.website:
            try:
                if not profile.website.startswith('http'):
                    profile.website = 'https://' + profile.website
                profile.technologies = self.detect_technologies(profile.website)
                
                # Domain information
                domain = profile.website.replace('https://', '').replace('http://', '').split('/')[0]
                domain_info = self.check_domain_info(domain)
                profile.financial_info['domain_info'] = domain_info
                
            except Exception as e:
                print(f"Website analysis error: {e}")
                
        # Social media presence
        social_profiles = self.search_social_media(business_name)
        profile.social_presence = [p['url'] for p in social_profiles if p['confidence'] > 0.3]
        
        # Risk assessment
        profile_data = asdict(profile)
        risk_flags = self.assess_risk_flags(profile_data, 'business')
        profile.risk_assessment = "high_risk" if len(risk_flags) > 3 else "low_risk"
        
        # Prospect scoring
        profile.prospect_score = self.calculate_prospect_score(asdict(profile))
        
        return profile
        
    def save_to_database(self, profile, profile_type: str):
        """Save profile to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if profile_type == 'person':
            cursor.execute('''
            INSERT INTO persons (name, location, email, phone, social_profiles, 
                               employment_history, education, risk_flags, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.name, profile.location, profile.email, profile.phone,
                json.dumps(profile.social_profiles), json.dumps(profile.employment_history),
                json.dumps(profile.education), json.dumps(profile.risk_flags),
                profile.verification_status
            ))
        elif profile_type == 'business':
            cursor.execute('''
            INSERT INTO businesses (name, location, industry, website, email, phone,
                                  employees, technologies, social_presence, financial_info,
                                  risk_assessment, prospect_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile.name, profile.location, profile.industry, profile.website,
                profile.email, profile.phone, json.dumps(profile.employees),
                json.dumps(profile.technologies), json.dumps(profile.social_presence),
                json.dumps(profile.financial_info), profile.risk_assessment,
                profile.prospect_score
            ))
            
        conn.commit()
        conn.close()
        
    def generate_report(self, output_file: str = "intelligence_report.json"):
        """Generate comprehensive intelligence report"""
        print(f"[*] Generating comprehensive report: {output_file}")
        
        # Compile results
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_persons': len(self.results['persons']),
                'total_businesses': len(self.results['businesses']),
                'scan_duration': 'N/A'
            },
            'executive_summary': {
                'high_risk_persons': len([p for p in self.results['persons'] 
                                        if len(p.risk_flags) > 2]),
                'verified_persons': len([p for p in self.results['persons'] 
                                       if p.verification_status == 'verified']),
                'high_prospect_businesses': len([b for b in self.results['businesses'] 
                                               if b.prospect_score > 70]),
                'total_risk_flags': sum(len(p.risk_flags) for p in self.results['persons'])
            },
            'persons': [asdict(p) for p in self.results['persons']],
            'businesses': [asdict(b) for b in self.results['businesses']],
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate CSV exports
        self.export_to_csv()
        
        print(f"[+] Report generated successfully: {output_file}")
        return report
        
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on findings"""
        recommendations = []
        
        # Business prospects
        high_prospects = [b for b in self.results['businesses'] if b.prospect_score > 70]
        if high_prospects:
            recommendations.append(f"Found {len(high_prospects)} high-value business prospects for pentesting/web development services")
            
        # Risk warnings
        high_risk_persons = [p for p in self.results['persons'] if len(p.risk_flags) > 2]
        if high_risk_persons:
            recommendations.append(f"CAUTION: {len(high_risk_persons)} persons flagged with multiple risk indicators")
            
        # Verification status
        unverified = [p for p in self.results['persons'] if p.verification_status == 'unverified']
        if unverified:
            recommendations.append(f"Additional verification needed for {len(unverified)} persons")
            
        return recommendations
        
    def export_to_csv(self):
        """Export results to CSV format"""
        # Export persons
        if self.results['persons']:
            with open('persons_intelligence.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results['persons'][0]).keys())
                writer.writeheader()
                for person in self.results['persons']:
                    row = asdict(person)
                    # Convert lists to strings for CSV
                    for key, value in row.items():
                        if isinstance(value, list):
                            row[key] = '; '.join(str(v) for v in value)
                    writer.writerow(row)
                    
        # Export businesses
        if self.results['businesses']:
            with open('businesses_intelligence.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.results['businesses'][0]).keys())
                writer.writeheader()
                for business in self.results['businesses']:
                    row = asdict(business)
                    # Convert lists and dicts to strings for CSV
                    for key, value in row.items():
                        if isinstance(value, (list, dict)):
                            row[key] = str(value)
                    writer.writerow(row)
                    
    def run_intelligence_scan(self, targets: Dict):
        """Main intelligence gathering orchestrator"""
        print("[*] Starting Advanced OSINT Intelligence Scan")
        print("="*60)
        
        start_time = datetime.now()
        
        # Process person targets
        if 'persons' in targets:
            print(f"[*] Processing {len(targets['persons'])} person targets...")
            for person_data in targets['persons']:
                try:
                    profile = self.gather_person_intelligence(**person_data)
                    self.results['persons'].append(profile)
                    self.save_to_database(profile, 'person')
                    print(f"[+] Completed: {profile.name} ({profile.verification_status})")
                except Exception as e:
                    print(f"[!] Error processing {person_data.get('name', 'Unknown')}: {e}")
                    
        # Process business targets
        if 'businesses' in targets:
            print(f"[*] Processing {len(targets['businesses'])} business targets...")
            for business_data in targets['businesses']:
                try:
                    # Map 'name' to 'business_name' if present for batch compatibility
                    if 'name' in business_data and 'business_name' not in business_data:
                        business_data['business_name'] = business_data.pop('name')
                    profile = self.gather_business_intelligence(**business_data)
                    self.results['businesses'].append(profile)
                    self.save_to_database(profile, 'business')
                    print(f"[+] Completed: {profile.name} (Score: {profile.prospect_score})")
                except Exception as e:
                    print(f"[!] Error processing {business_data.get('name', business_data.get('business_name', 'Unknown'))}: {e}")
                    
        # Generate final report
        scan_duration = datetime.now() - start_time
        self.results['metadata']['scan_duration'] = str(scan_duration)
        
        report = self.generate_report()
        
        print("\n" + "="*60)
        print(f"[+] Intelligence scan completed in {scan_duration}")
        print(f"[+] Persons processed: {len(self.results['persons'])}")
        print(f"[+] Businesses processed: {len(self.results['businesses'])}")
        print(f"[+] Reports generated: intelligence_report.json, *.csv")
        
        return report

def main():
    """Main execution function with example usage"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                 Advanced OSINT Intelligence Scraper         ║
    ║                                                              ║
    ║  Professional intelligence gathering for business prospects  ║
    ║  and personal safety verification through OSINT methods      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    scraper = OSINTScraper()
    
    # Example target configuration
    targets = {
        'persons': [
            {
                'name': 'John Smith',
                'location': 'San Francisco, CA',
                'email': 'john.smith@example.com'
            }
        ],
        'businesses': [
            {
                'business_name': 'TechStart Inc',
                'location': 'San Francisco, CA',
                'website': 'techstart.com'
            }
        ]
    }
    
    # Interactive mode
    print("\n[*] Interactive Intelligence Gathering Mode")
    print("Choose an option:")
    print("1. Person Intelligence Gathering")
    print("2. Business Intelligence Gathering") 
    print("3. Batch Processing from JSON")
    print("4. Database Query Mode")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        name = input("Enter person name: ").strip()
        location = input("Enter location (optional): ").strip()
        email = input("Enter email (optional): ").strip()
        phone = input("Enter phone (optional): ").strip()
        
        targets = {
            'persons': [{'name': name, 'location': location, 'email': email, 'phone': phone}]
        }
        
    elif choice == '2':
        business_name = input("Enter business name: ").strip()
        location = input("Enter location (optional): ").strip()
        website = input("Enter website (optional): ").strip()
        
        targets = {
            'businesses': [{'business_name': business_name, 'location': location, 'website': website}]
        }
        
    elif choice == '3':
        json_file = input("Enter JSON file path: ").strip()
        try:
            with open(json_file, 'r') as f:
                targets = json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return
            
    elif choice == '4':
        print("\nDatabase Query Mode - Feature coming soon!")
        return
        
    else:
        print("Invalid choice. Using example targets...")
        
    # Run intelligence scan
    scraper.run_intelligence_scan(targets)

if __name__ == "__main__":
    main()