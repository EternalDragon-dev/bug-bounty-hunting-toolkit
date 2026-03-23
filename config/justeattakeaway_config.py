#!/usr/bin/env python3
"""
Just Eat Takeaway.com Bug Bounty Configuration
Setup for testing environment and target configuration
"""

import os
import json
import requests
from datetime import datetime

class JustEatTakeawayConfig:
    def __init__(self):
        self.bugcrowd_username = "hiddenghost404"
        self.test_email = "hiddenghost404@bugcrowdninja.com"
        self.headers = {
            "X-Bug-Bounty": self.bugcrowd_username,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Priority targets organized by payout potential
        self.p1_targets = {
            "payment_systems": [
                "https://api-payments-secure-prod.skippayments.com",
                "https://takeawaypay.azurefd.net/en/takeawaypay/",
                "https://takeaway.pay-creditcard.takeaway.com",
                "https://global-payments-web.payments.pmt-1.eu-west-1.production.jet-external.com"
            ],
            "critical_apis": [
                "https://rest.api.eu-central-1.production.jet-external.com",
                "https://uk.api.just-eat.io",
                "https://aus.api.just-eat.io",
                "https://api-skipthedishes.skipthedishes.com",
                "https://i18n.api.just-eat.io",
                "https://cw-api.takeaway.com"
            ]
        }
        
        self.p2_targets = {
            "business_assets": [
                "https://thuisbezorgd.nl",
                "https://takeaway.com",
                "https://skipthedishes.com",
                "https://just-eat.dk",
                "https://lieferando.de",
                "https://pyszne.pl",
                "https://bistro.sk",
                "https://just-eat.es",
                "https://just-eat.co.uk",
                "https://just-eat.ch",
                "https://10bis.co.il",
                "https://scoober.com",
                "https://just-eat.com",
                "https://skippayments.com"
            ]
        }
        
        self.p3_targets = {
            "other_assets": [
                "https://justeattakeaway.com",
                "https://just-eat.io",
                "https://justeat-int.com",
                "https://yourdelivery.de",
                "https://just-data.io",
                "https://jet-external.com"
            ]
        }
        
        # Focus areas as per program requirements
        self.focus_areas = [
            "Authorization bypasses",
            "IDORs",
            "PII disclosure",
            "Business logic abuse"
        ]
        
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "justeattakeaway")
        self.create_output_structure()
    
    def create_output_structure(self):
        """Create directory structure for results"""
        dirs = [
            f"{self.output_dir}",
            f"{self.output_dir}/reconnaissance",
            f"{self.output_dir}/vulnerabilities",
            f"{self.output_dir}/poc_reports",
            f"{self.output_dir}/exploit_chains",
            f"{self.output_dir}/screenshots"
        ]
        
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    def get_session_with_headers(self):
        """Get requests session with proper headers"""
        session = requests.Session()
        session.headers.update(self.headers)
        return session
    
    def log_activity(self, message, level="INFO"):
        """Log testing activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        log_file = f"{self.output_dir}/testing_log.txt"
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
    
    def save_vulnerability(self, vuln_data):
        """Save vulnerability data"""
        vuln_id = f"JET_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        vuln_file = f"{self.output_dir}/vulnerabilities/{vuln_id}.json"
        
        vuln_data['id'] = vuln_id
        vuln_data['discovered_at'] = datetime.now().isoformat()
        
        with open(vuln_file, 'w') as f:
            json.dump(vuln_data, f, indent=2)
        
        return vuln_id
    
    def get_high_priority_targets(self):
        """Get targets sorted by priority (P1 first)"""
        targets = []
        
        # P1 targets first (highest payout)
        for category, urls in self.p1_targets.items():
            for url in urls:
                targets.append({
                    "url": url,
                    "priority": "P1",
                    "category": category,
                    "payout_range": "$3500-$4500"
                })
        
        # P2 targets
        for category, urls in self.p2_targets.items():
            for url in urls:
                targets.append({
                    "url": url,
                    "priority": "P2", 
                    "category": category,
                    "payout_range": "$1500-$2500"
                })
        
        # P3 targets
        for category, urls in self.p3_targets.items():
            for url in urls:
                targets.append({
                    "url": url,
                    "priority": "P3",
                    "category": category,
                    "payout_range": "$500-$750"
                })
        
        return targets

if __name__ == "__main__":
    config = JustEatTakeawayConfig()
    config.log_activity("Just Eat Takeaway.com testing environment initialized")
    
    targets = config.get_high_priority_targets()
    config.log_activity(f"Loaded {len(targets)} targets for testing")
    
    # Save configuration
    config_data = {
        "program": "Just Eat Takeaway.com",
        "platform": "Bugcrowd",
        "username": config.bugcrowd_username,
        "email": config.test_email,
        "targets": targets,
        "focus_areas": config.focus_areas
    }
    
    with open(f"{config.output_dir}/config.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    print("\n=== JUST EAT TAKEAWAY.COM TESTING SETUP COMPLETE ===")
    print(f"Output directory: {config.output_dir}")
    print(f"Total targets: {len(targets)}")
    print(f"P1 targets (highest priority): {len([t for t in targets if t['priority'] == 'P1'])}")
    print("Ready for vulnerability testing!")