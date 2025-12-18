#!/usr/bin/env python3
"""
Advanced S3 Bucket Hunter - Data Exposure Discovery Tool
Discovers misconfigured AWS S3 buckets and tests for sensitive data exposure
"""

import boto3
import requests
import threading
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from botocore.exceptions import NoCredentialsError, ClientError
import os
from datetime import datetime

class S3Hunter:
    def __init__(self, target_domain, wordlist_file=None, threads=20):
        self.target_domain = target_domain
        self.threads = threads
        self.found_buckets = []
        self.sensitive_files = []
        self.business_impact = []
        self.wordlist = self._load_wordlist(wordlist_file)
        
        # Common S3 bucket naming patterns
        self.bucket_patterns = [
            "{domain}",
            "{domain}-backup",
            "{domain}-backups",
            "{domain}-data",
            "{domain}-db",
            "{domain}-database",
            "{domain}-logs",
            "{domain}-uploads",
            "{domain}-assets",
            "{domain}-static",
            "{domain}-media",
            "{domain}-files",
            "{domain}-documents",
            "{domain}-private",
            "{domain}-internal",
            "{domain}-staging",
            "{domain}-dev",
            "{domain}-development",
            "{domain}-test",
            "{domain}-testing",
            "{domain}-prod",
            "{domain}-production",
            "backup-{domain}",
            "backups-{domain}",
            "data-{domain}",
            "logs-{domain}",
            "files-{domain}",
            "{company}",
            "{company}-backup",
            "{company}-data",
            "{company}-files"
        ]
        
        # Sensitive file patterns to look for
        self.sensitive_patterns = {
            'Database Dumps': [r'\.sql$', r'\.db$', r'\.sqlite$', r'dump\.'],
            'Configuration Files': [r'\.env$', r'config\.', r'\.conf$', r'\.ini$', r'\.yaml$', r'\.yml$'],
            'Private Keys': [r'\.pem$', r'\.key$', r'private', r'id_rsa', r'\.p12$'],
            'Log Files': [r'\.log$', r'access\.log', r'error\.log', r'debug\.'],
            'Backup Files': [r'\.bak$', r'\.backup$', r'\.tar', r'\.zip$', r'\.gz$'],
            'Source Code': [r'\.git/', r'\.svn/', r'source', r'src/'],
            'User Data': [r'users?\.', r'customers?\.', r'accounts?\.', r'profiles?\.'],
            'Financial Data': [r'payment', r'transaction', r'invoice', r'billing', r'financial']
        }

    def _load_wordlist(self, wordlist_file):
        """Load custom wordlist or use default"""
        if wordlist_file and os.path.exists(wordlist_file):
            with open(wordlist_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        
        # Default wordlist
        return [
            'www', 'api', 'app', 'mobile', 'admin', 'test', 'dev', 'staging',
            'prod', 'production', 'backup', 'data', 'files', 'uploads', 'assets',
            'static', 'media', 'logs', 'documents', 'private', 'internal'
        ]

    def generate_bucket_names(self):
        """Generate potential bucket names"""
        domain_parts = self.target_domain.replace('www.', '').split('.')
        company = domain_parts[0]
        
        bucket_names = set()
        
        # Generate from patterns
        for pattern in self.bucket_patterns:
            bucket_names.add(pattern.format(domain=company, company=company))
            
        # Add wordlist combinations
        for word in self.wordlist:
            bucket_names.add(f"{company}-{word}")
            bucket_names.add(f"{word}-{company}")
            bucket_names.add(f"{company}{word}")
            
        return list(bucket_names)

    def check_bucket_exists(self, bucket_name):
        """Check if S3 bucket exists and is accessible"""
        try:
            # Try HTTP HEAD request first (faster)
            url = f"https://{bucket_name}.s3.amazonaws.com"
            response = requests.head(url, timeout=5)
            
            if response.status_code == 200:
                return {'name': bucket_name, 'url': url, 'accessible': True, 'method': 'http'}
            elif response.status_code == 403:
                return {'name': bucket_name, 'url': url, 'accessible': False, 'method': 'http', 'exists': True}
                
        except Exception:
            pass
            
        try:
            # Try with different regions
            regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
            for region in regions:
                url = f"https://s3-{region}.amazonaws.com/{bucket_name}"
                response = requests.head(url, timeout=5)
                if response.status_code in [200, 403]:
                    return {
                        'name': bucket_name, 
                        'url': url, 
                        'accessible': response.status_code == 200,
                        'method': 'regional',
                        'region': region,
                        'exists': True
                    }
        except Exception:
            pass
            
        return None

    def analyze_bucket_contents(self, bucket_info):
        """Analyze bucket contents for sensitive data"""
        if not bucket_info.get('accessible'):
            return bucket_info
            
        try:
            url = bucket_info['url']
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response to get file list
                content = response.text
                files = re.findall(r'<Key>(.*?)</Key>', content)
                
                bucket_info['files'] = files[:50]  # Limit to first 50 files
                bucket_info['total_files'] = len(re.findall(r'<Key>', content))
                
                # Check for sensitive files
                sensitive_found = {}
                high_value_files = []
                
                for file_path in files:
                    for category, patterns in self.sensitive_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, file_path, re.IGNORECASE):
                                if category not in sensitive_found:
                                    sensitive_found[category] = []
                                sensitive_found[category].append(file_path)
                                high_value_files.append({
                                    'file': file_path,
                                    'category': category,
                                    'url': f"{url}/{file_path}"
                                })
                
                bucket_info['sensitive_files'] = sensitive_found
                bucket_info['high_value_files'] = high_value_files
                
                # Test write permissions
                bucket_info['writable'] = self.test_write_permissions(bucket_info['name'])
                
        except Exception as e:
            bucket_info['error'] = str(e)
            
        return bucket_info

    def test_write_permissions(self, bucket_name):
        """Test if bucket has write permissions"""
        try:
            # Try to upload a test file
            test_content = "test-file-for-security-research"
            test_key = f"security-test-{int(time.time())}.txt"
            
            # Try using requests for simple PUT
            url = f"https://{bucket_name}.s3.amazonaws.com/{test_key}"
            response = requests.put(url, data=test_content, timeout=5)
            
            if response.status_code in [200, 201]:
                # Try to delete the test file
                requests.delete(url, timeout=5)
                return True
                
        except Exception:
            pass
            
        return False

    def assess_business_impact(self, bucket_info):
        """Assess business impact of exposed bucket"""
        impact = {
            'severity': 'Low',
            'impact_score': 0,
            'findings': [],
            'potential_damage': []
        }
        
        if not bucket_info.get('accessible'):
            if bucket_info.get('exists'):
                impact['findings'].append("Bucket exists but not publicly readable")
                impact['impact_score'] += 1
            return impact
            
        # Check for sensitive files
        sensitive_files = bucket_info.get('sensitive_files', {})
        
        if 'Database Dumps' in sensitive_files:
            impact['severity'] = 'Critical'
            impact['impact_score'] += 50
            impact['findings'].append(f"Database dumps exposed: {len(sensitive_files['Database Dumps'])} files")
            impact['potential_damage'].append("Complete database compromise")
            
        if 'Private Keys' in sensitive_files:
            impact['severity'] = 'Critical' 
            impact['impact_score'] += 40
            impact['findings'].append(f"Private keys exposed: {len(sensitive_files['Private Keys'])} files")
            impact['potential_damage'].append("Infrastructure compromise")
            
        if 'Configuration Files' in sensitive_files:
            impact['impact_score'] += 30
            if impact['severity'] != 'Critical':
                impact['severity'] = 'High'
            impact['findings'].append(f"Configuration files exposed: {len(sensitive_files['Configuration Files'])} files")
            impact['potential_damage'].append("Application secrets exposed")
            
        if 'User Data' in sensitive_files or 'Financial Data' in sensitive_files:
            impact['impact_score'] += 35
            if impact['severity'] not in ['Critical', 'High']:
                impact['severity'] = 'High'
            impact['findings'].append("Sensitive user/financial data exposed")
            impact['potential_damage'].append("Privacy violation, regulatory compliance issues")
            
        # Check write permissions
        if bucket_info.get('writable'):
            impact['impact_score'] += 25
            if impact['severity'] == 'Low':
                impact['severity'] = 'Medium'
            impact['findings'].append("Bucket has public write permissions")
            impact['potential_damage'].append("Data tampering, malware hosting")
            
        # File count impact
        total_files = bucket_info.get('total_files', 0)
        if total_files > 1000:
            impact['impact_score'] += 15
            impact['findings'].append(f"Large number of files exposed: {total_files}")
            
        # Set final severity based on score
        if impact['impact_score'] >= 40 and impact['severity'] != 'Critical':
            impact['severity'] = 'High'
        elif impact['impact_score'] >= 20 and impact['severity'] not in ['Critical', 'High']:
            impact['severity'] = 'Medium'
            
        return impact

    def hunt_buckets(self):
        """Main hunting function"""
        print(f"[+] Starting S3 bucket hunt for {self.target_domain}")
        bucket_names = self.generate_bucket_names()
        print(f"[+] Generated {len(bucket_names)} potential bucket names")
        
        found_buckets = []
        
        # Multi-threaded bucket discovery
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_bucket = {
                executor.submit(self.check_bucket_exists, name): name 
                for name in bucket_names
            }
            
            for future in as_completed(future_to_bucket):
                bucket_name = future_to_bucket[future]
                try:
                    result = future.result()
                    if result:
                        print(f"[!] Found bucket: {result['name']}")
                        found_buckets.append(result)
                except Exception as e:
                    print(f"[!] Error checking {bucket_name}: {e}")
        
        # Analyze found buckets
        print(f"\n[+] Analyzing {len(found_buckets)} discovered buckets...")
        
        for bucket in found_buckets:
            bucket = self.analyze_bucket_contents(bucket)
            bucket['business_impact'] = self.assess_business_impact(bucket)
            self.found_buckets.append(bucket)
            
        return self.found_buckets

    def generate_report(self):
        """Generate comprehensive report"""
        report = {
            'target': self.target_domain,
            'scan_time': datetime.now().isoformat(),
            'summary': {
                'total_buckets_found': len(self.found_buckets),
                'accessible_buckets': len([b for b in self.found_buckets if b.get('accessible')]),
                'writable_buckets': len([b for b in self.found_buckets if b.get('writable')]),
                'critical_findings': len([b for b in self.found_buckets if b.get('business_impact', {}).get('severity') == 'Critical']),
                'high_findings': len([b for b in self.found_buckets if b.get('business_impact', {}).get('severity') == 'High'])
            },
            'buckets': self.found_buckets
        }
        
        # Calculate total business impact
        total_impact = sum(b.get('business_impact', {}).get('impact_score', 0) for b in self.found_buckets)
        report['total_business_impact'] = total_impact
        
        if total_impact >= 100:
            report['overall_severity'] = 'Critical'
        elif total_impact >= 50:
            report['overall_severity'] = 'High'
        elif total_impact >= 20:
            report['overall_severity'] = 'Medium'
        else:
            report['overall_severity'] = 'Low'
            
        return report

    def save_report(self, filename=None):
        """Save detailed report"""
        if not filename:
            filename = f"s3_hunt_{self.target_domain.replace('.', '_')}_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced S3 Bucket Hunter')
    parser.add_argument('domain', help='Target domain to hunt S3 buckets for')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=20, help='Number of threads')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = S3Hunter(args.domain, args.wordlist, args.threads)
    buckets = hunter.hunt_buckets()
    
    print(f"\n{'='*60}")
    print("S3 BUCKET HUNTING RESULTS")
    print(f"{'='*60}")
    
    if not buckets:
        print("[-] No S3 buckets found")
        return
        
    for bucket in buckets:
        print(f"\n[!] Bucket: {bucket['name']}")
        print(f"    URL: {bucket['url']}")
        print(f"    Accessible: {bucket.get('accessible', False)}")
        print(f"    Writable: {bucket.get('writable', False)}")
        print(f"    Files: {bucket.get('total_files', 0)}")
        
        impact = bucket.get('business_impact', {})
        print(f"    Severity: {impact.get('severity', 'Unknown')}")
        print(f"    Impact Score: {impact.get('impact_score', 0)}")
        
        if bucket.get('sensitive_files'):
            print(f"    Sensitive Files:")
            for category, files in bucket['sensitive_files'].items():
                print(f"      - {category}: {len(files)} files")
                
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Total Business Impact Score: {report['total_business_impact']}")
    print(f"[+] Overall Severity: {report['overall_severity']}")

if __name__ == '__main__':
    main()