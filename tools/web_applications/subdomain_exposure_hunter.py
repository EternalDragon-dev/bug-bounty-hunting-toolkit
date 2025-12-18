#!/usr/bin/env python3
"""
Subdomain Data Exposure Hunter - Data Exposure Discovery Tool
Automatically scans discovered subdomains for exposed data, staging environments, and development instances
"""

import requests
import dns.resolver
import threading
import time
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from datetime import datetime
import socket
import ssl
import random

class SubdomainExposureHunter:
    def __init__(self, domain, threads=50, timeout=10):
        self.domain = domain.lower().strip()
        self.threads = threads
        self.timeout = timeout
        self.findings = []
        self.discovered_subdomains = []
        self.live_subdomains = []
        
        # Subdomain discovery wordlists
        self.subdomain_wordlist = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'ns3', 'test', 'staging',
            'dev', 'development', 'admin', 'administrator', 'demo', 'stage', 'beta',
            'alpha', 'preview', 'pre', 'uat', 'qa', 'testing', 'internal', 'private',
            'secure', 'vpn', 'ssh', 'remote', 'git', 'svn', 'repo', 'repository',
            'jenkins', 'ci', 'cd', 'build', 'deploy', 'deployment', 'docker', 'k8s',
            'kubernetes', 'master', 'slave', 'worker', 'node', 'cluster', 'db', 'database',
            'sql', 'mysql', 'postgres', 'mongodb', 'redis', 'elastic', 'elasticsearch',
            'kibana', 'grafana', 'prometheus', 'monitor', 'monitoring', 'metrics',
            'logs', 'log', 'syslog', 'splunk', 'elk', 'backup', 'backups', 'archive',
            'old', 'legacy', 'retired', 'deprecated', 'temp', 'tmp', 'temporary',
            'cache', 'cdn', 'static', 'assets', 'media', 'images', 'img', 'files',
            'docs', 'doc', 'documentation', 'wiki', 'help', 'support', 'ticket',
            'api', 'rest', 'graphql', 'ws', 'websocket', 'mobile', 'app', 'apps',
            'service', 'services', 'microservice', 'ms', 'gateway', 'proxy', 'load',
            'balance', 'lb', 'nat', 'firewall', 'fw', 'router', 'switch', 'network',
            'lan', 'wan', 'dmz', 'office', 'corp', 'corporate', 'intranet', 'extranet',
            'partner', 'vendor', 'client', 'customer', 'user', 'member', 'guest',
            'public', 'private', 'internal', 'external', 'front', 'backend', 'middle',
            'edge', 'core', 'hub', 'node', 'endpoint', 'interface', 'portal', 'dashboard',
            'console', 'control', 'manage', 'management', 'config', 'configuration',
            'settings', 'preference', 'profile', 'account', 'billing', 'payment',
            'shop', 'store', 'cart', 'checkout', 'order', 'invoice', 'receipt',
            'report', 'analytics', 'stats', 'statistics', 'data', 'warehouse',
            'lake', 'stream', 'flow', 'pipeline', 'etl', 'batch', 'queue', 'job',
            'task', 'scheduler', 'cron', 'timer', 'event', 'trigger', 'hook',
            'webhook', 'callback', 'notification', 'alert', 'alarm', 'warning',
            'error', 'exception', 'debug', 'trace', 'audit', 'security', 'auth',
            'authentication', 'authorization', 'oauth', 'saml', 'sso', 'ldap',
            'ad', 'directory', 'identity', 'iam', 'rbac', 'acl', 'permission',
            'role', 'group', 'team', 'department', 'division', 'branch', 'region'
        ]
        
        # Development/staging indicators
        self.dev_indicators = [
            'dev', 'develop', 'development', 'test', 'testing', 'stage', 'staging',
            'uat', 'qa', 'demo', 'beta', 'alpha', 'preview', 'pre', 'temp', 'tmp',
            'sandbox', 'lab', 'experimental', 'canary', 'pilot', 'trial'
        ]
        
        # Sensitive endpoints to test on each subdomain
        self.test_endpoints = [
            '/', '/.env', '/config.php', '/wp-config.php', '/database.php',
            '/admin', '/admin.php', '/administrator', '/phpmyadmin',
            '/debug', '/test', '/staging', '/dev', '/.git', '/.svn',
            '/backup', '/backups', '/.backup', '/db', '/database',
            '/api', '/api/v1', '/api/debug', '/api/config',
            '/console', '/dashboard', '/panel', '/control',
            '/logs', '/log', '/.log', '/error.log', '/access.log',
            '/info.php', '/phpinfo.php', '/test.php', '/debug.php',
            '/robots.txt', '/sitemap.xml', '/.htaccess', '/web.config',
            '/crossdomain.xml', '/clientaccesspolicy.xml'
        ]
        
        # Sensitive patterns to look for
        self.sensitive_patterns = {
            'Database Credentials': [
                r'(?i)(database|db|mysql|postgres)[_\s]*(?:host|server|hostname|user|username|pass|password)["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)',
                r'(?i)connection[_\s]*string["\'\s]*[:=]["\'\s]*([^\s"\'<>]+)'
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
            'JWT Tokens': [
                r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
            ],
            'Email Addresses': [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ],
            'Private Keys': [
                r'-----BEGIN [A-Z]+ PRIVATE KEY-----'
            ],
            'Passwords': [
                r'(?i)password["\'\s]*[:=]["\'\s]*([^\s"\'<>]{6,})'
            ],
            'Internal IPs': [
                r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)\d{1,3}\.\d{1,3}\b'
            ]
        }
        
        # Development/debug content indicators
        self.debug_indicators = [
            'debug', 'trace', 'stack trace', 'error', 'exception', 'warning',
            'var_dump', 'print_r', 'console.log', 'development', 'staging',
            'test mode', 'debug mode', 'verbose', 'phpinfo', 'server info'
        ]

    def discover_subdomains_dns(self):
        """Discover subdomains using DNS brute force"""
        discovered = []
        
        print(f"[+] DNS brute forcing subdomains for {self.domain}")
        
        def test_subdomain(subdomain):
            full_domain = f"{subdomain}.{self.domain}"
            try:
                # Try A record
                dns.resolver.resolve(full_domain, 'A')
                discovered.append(full_domain)
                return full_domain
            except:
                try:
                    # Try CNAME record
                    dns.resolver.resolve(full_domain, 'CNAME')
                    discovered.append(full_domain)
                    return full_domain
                except:
                    pass
            return None
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(test_subdomain, sub): sub for sub in self.subdomain_wordlist}
            
            for future in as_completed(futures):
                subdomain = futures[future]
                try:
                    result = future.result()
                    if result:
                        print(f"[+] Found subdomain: {result}")
                except Exception:
                    pass
        
        return discovered

    def discover_subdomains_certificate(self):
        """Discover subdomains from SSL certificate transparency logs"""
        discovered = []
        
        try:
            # Try crt.sh API
            print(f"[+] Checking certificate transparency logs for {self.domain}")
            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name_value = entry.get('name_value', '')
                    for name in name_value.split('\n'):
                        name = name.strip().lower()
                        if name.endswith(self.domain) and name != self.domain:
                            # Remove wildcard prefix
                            if name.startswith('*.'):
                                name = name[2:]
                            if name not in discovered and '.' in name:
                                discovered.append(name)
                                print(f"[+] Found subdomain from CT logs: {name}")
        except Exception as e:
            print(f"[!] Error checking certificate transparency: {e}")
        
        return discovered

    def test_subdomain_alive(self, subdomain):
        """Test if a subdomain is responding to HTTP/HTTPS"""
        alive_info = {}
        
        for scheme in ['https', 'http']:
            try:
                url = f"{scheme}://{subdomain}"
                response = requests.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
                
                if response.status_code in range(200, 500):  # Any meaningful response
                    alive_info = {
                        'subdomain': subdomain,
                        'url': url,
                        'status_code': response.status_code,
                        'title': self._extract_title(response.text),
                        'server': response.headers.get('Server', 'Unknown'),
                        'content_length': len(response.content),
                        'response_headers': dict(response.headers),
                        'is_dev': any(indicator in subdomain.lower() for indicator in self.dev_indicators),
                        'scheme': scheme
                    }
                    break
                    
            except Exception:
                pass
        
        return alive_info if alive_info else None

    def _extract_title(self, html_content):
        """Extract title from HTML content"""
        try:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                return title_match.group(1).strip()[:100]  # Limit to 100 chars
        except Exception:
            pass
        return 'No Title'

    def test_subdomain_endpoints(self, subdomain_info):
        """Test various endpoints on a live subdomain for data exposure"""
        findings = []
        base_url = subdomain_info['url']
        
        for endpoint in self.test_endpoints:
            try:
                test_url = urljoin(base_url, endpoint)
                response = requests.get(test_url, timeout=self.timeout, verify=False, allow_redirects=False)
                
                if response.status_code == 200:
                    finding = self._analyze_endpoint_response(test_url, response, subdomain_info)
                    if finding:
                        findings.append(finding)
                        
            except Exception:
                pass
        
        return findings

    def _analyze_endpoint_response(self, url, response, subdomain_info):
        """Analyze endpoint response for sensitive data exposure"""
        content = response.text
        content_lower = content.lower()
        
        # Skip very small responses
        if len(content.strip()) < 50:
            return None
        
        # Extract sensitive data
        sensitive_data = {}
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    clean_matches = []
                    for match in matches:
                        if isinstance(match, tuple):
                            match = next((m for m in match if m), str(match))
                        clean_matches.append(str(match).strip())
                    
                    if clean_matches:
                        if category not in sensitive_data:
                            sensitive_data[category] = {'count': 0, 'samples': []}
                        sensitive_data[category]['count'] += len(clean_matches)
                        sensitive_data[category]['samples'].extend(clean_matches[:3])
        
        # Check for debug/development content
        debug_content = any(indicator in content_lower for indicator in self.debug_indicators)
        
        # Check for common sensitive files
        endpoint_path = urlparse(url).path
        is_sensitive_file = any(sensitive_file in endpoint_path.lower() 
                              for sensitive_file in ['.env', 'config', 'database', 'backup', '.git', 'admin'])
        
        # Check for directory listings
        is_directory_listing = ('index of' in content_lower or 
                              'directory listing' in content_lower or 
                              'parent directory' in content_lower)
        
        # Check for error pages with stack traces
        has_stack_trace = any(trace_indicator in content_lower 
                            for trace_indicator in ['stack trace', 'traceback', 'exception', 'error'])
        
        # Determine severity and business impact
        severity = 'Low'
        business_impact = 'Information disclosure'
        exposure_type = 'General Information Disclosure'
        
        if sensitive_data:
            severity = 'High'
            exposure_type = 'Sensitive Data Exposure'
            business_impact = f'Sensitive data exposed: {", ".join(sensitive_data.keys())}'
            
            # Critical if credentials or keys are exposed
            if any(category in sensitive_data for category in ['Database Credentials', 'AWS Credentials', 'Private Keys']):
                severity = 'Critical'
                business_impact = 'Critical credentials exposed'
                
        elif is_sensitive_file:
            severity = 'High'
            exposure_type = 'Configuration File Exposure'
            business_impact = f'Sensitive configuration file exposed: {endpoint_path}'
            
        elif is_directory_listing:
            severity = 'Medium'
            exposure_type = 'Directory Listing'
            business_impact = 'Directory structure exposed via directory listing'
            
        elif debug_content or has_stack_trace:
            severity = 'Medium'
            exposure_type = 'Debug Information Disclosure'
            business_impact = 'Debug information and potentially sensitive data exposed'
            
        elif subdomain_info['is_dev']:
            severity = 'Medium'
            exposure_type = 'Development Environment Exposure'
            business_impact = 'Development/staging environment accessible from internet'
            
        # Only report if there's actual exposure
        if (sensitive_data or is_sensitive_file or is_directory_listing or 
            debug_content or has_stack_trace or 
            (subdomain_info['is_dev'] and len(content) > 500)):
            
            return {
                'type': exposure_type,
                'url': url,
                'subdomain': subdomain_info['subdomain'],
                'method': 'GET',
                'status_code': response.status_code,
                'severity': severity,
                'is_development': subdomain_info['is_dev'],
                'sensitive_data': sensitive_data,
                'has_debug_content': debug_content,
                'has_stack_trace': has_stack_trace,
                'is_directory_listing': is_directory_listing,
                'is_sensitive_file': is_sensitive_file,
                'response_size': len(content),
                'response_sample': content[:1000],  # First 1000 chars
                'business_impact': business_impact,
                'details': f'Subdomain {subdomain_info["subdomain"]} exposes sensitive information'
            }
        
        return None

    def check_subdomain_security(self, subdomain_info):
        """Check subdomain for common security misconfigurations"""
        findings = []
        
        # Check for missing security headers
        headers = subdomain_info.get('response_headers', {})
        missing_headers = []
        
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1',
            'Strict-Transport-Security': 'max-age',
            'Content-Security-Policy': 'policy'
        }
        
        for header, expected in security_headers.items():
            if header not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            findings.append({
                'type': 'Missing Security Headers',
                'url': subdomain_info['url'],
                'subdomain': subdomain_info['subdomain'],
                'severity': 'Medium',
                'missing_headers': missing_headers,
                'business_impact': 'Missing security headers may lead to various client-side attacks',
                'details': f'Security headers missing: {", ".join(missing_headers)}'
            })
        
        # Check for server information disclosure
        server_header = headers.get('Server', '')
        if server_header and any(version_info in server_header.lower() 
                               for version_info in ['/', 'apache', 'nginx', 'iis']):
            findings.append({
                'type': 'Server Information Disclosure',
                'url': subdomain_info['url'],
                'subdomain': subdomain_info['subdomain'],
                'severity': 'Low',
                'server_info': server_header,
                'business_impact': 'Server version information disclosure aids attackers',
                'details': f'Server header reveals: {server_header}'
            })
        
        return findings

    def hunt_subdomain_exposure(self):
        """Main function to hunt for subdomain data exposure"""
        print(f"[+] Starting subdomain data exposure hunt for {self.domain}")
        
        # Phase 1: Discover subdomains
        print(f"[+] Phase 1: Subdomain Discovery")
        dns_subdomains = self.discover_subdomains_dns()
        cert_subdomains = self.discover_subdomains_certificate()
        
        # Combine and deduplicate
        all_subdomains = list(set(dns_subdomains + cert_subdomains))
        self.discovered_subdomains = all_subdomains
        
        print(f"[+] Total subdomains discovered: {len(all_subdomains)}")
        
        if not all_subdomains:
            print("[-] No subdomains discovered")
            return []
        
        # Phase 2: Test subdomain liveness
        print(f"[+] Phase 2: Testing subdomain liveness")
        live_subdomains = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            alive_futures = {
                executor.submit(self.test_subdomain_alive, subdomain): subdomain
                for subdomain in all_subdomains
            }
            
            for future in as_completed(alive_futures):
                subdomain = alive_futures[future]
                try:
                    result = future.result()
                    if result:
                        live_subdomains.append(result)
                        print(f"[+] Live subdomain: {result['subdomain']} ({result['status_code']})")
                except Exception:
                    pass
        
        self.live_subdomains = live_subdomains
        print(f"[+] Live subdomains found: {len(live_subdomains)}")
        
        if not live_subdomains:
            print("[-] No live subdomains found")
            return []
        
        # Phase 3: Test for data exposure
        print(f"[+] Phase 3: Testing for data exposure")
        all_findings = []
        
        with ThreadPoolExecutor(max_workers=min(self.threads, 20)) as executor:  # Limit for endpoint testing
            endpoint_futures = {
                executor.submit(self.test_subdomain_endpoints, subdomain_info): subdomain_info
                for subdomain_info in live_subdomains
            }
            
            security_futures = {
                executor.submit(self.check_subdomain_security, subdomain_info): subdomain_info
                for subdomain_info in live_subdomains
            }
            
            # Collect endpoint findings
            for future in as_completed(endpoint_futures):
                subdomain_info = endpoint_futures[future]
                try:
                    findings = future.result()
                    if findings:
                        all_findings.extend(findings)
                        print(f"[!] Found {len(findings)} exposures on {subdomain_info['subdomain']}")
                except Exception as e:
                    pass
            
            # Collect security findings
            for future in as_completed(security_futures):
                subdomain_info = security_futures[future]
                try:
                    findings = future.result()
                    if findings:
                        all_findings.extend(findings)
                except Exception:
                    pass
        
        self.findings = all_findings
        print(f"[+] Subdomain exposure hunting completed. Found {len(all_findings)} total issues.")
        return all_findings

    def generate_report(self):
        """Generate comprehensive subdomain exposure report"""
        report = {
            'domain': self.domain,
            'scan_time': datetime.now().isoformat(),
            'discovery_summary': {
                'total_subdomains_discovered': len(self.discovered_subdomains),
                'live_subdomains': len(self.live_subdomains),
                'development_subdomains': len([s for s in self.live_subdomains if s['is_dev']])
            },
            'vulnerability_summary': {
                'total_findings': len(self.findings),
                'critical_findings': len([f for f in self.findings if f.get('severity') == 'Critical']),
                'high_findings': len([f for f in self.findings if f.get('severity') == 'High']),
                'medium_findings': len([f for f in self.findings if f.get('severity') == 'Medium']),
                'low_findings': len([f for f in self.findings if f.get('severity') == 'Low'])
            },
            'subdomains_discovered': self.discovered_subdomains,
            'live_subdomains': self.live_subdomains,
            'findings': self.findings
        }
        
        # Vulnerability type breakdown
        vuln_types = {}
        for finding in self.findings:
            vuln_type = finding.get('type', 'Unknown')
            vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
        
        report['vulnerability_types'] = vuln_types
        
        # Subdomain risk assessment
        high_risk_subdomains = []
        for subdomain in self.live_subdomains:
            subdomain_findings = [f for f in self.findings if f.get('subdomain') == subdomain['subdomain']]
            if any(f.get('severity') in ['Critical', 'High'] for f in subdomain_findings):
                high_risk_subdomains.append({
                    'subdomain': subdomain['subdomain'],
                    'findings': len(subdomain_findings),
                    'max_severity': max([f.get('severity', 'Low') for f in subdomain_findings], 
                                      key=lambda x: ['Low', 'Medium', 'High', 'Critical'].index(x))
                })
        
        report['high_risk_subdomains'] = high_risk_subdomains
        
        # Overall risk assessment
        severities = [f.get('severity', 'Low') for f in self.findings]
        if 'Critical' in severities:
            report['overall_risk'] = 'Critical'
        elif 'High' in severities:
            report['overall_risk'] = 'High'
        elif 'Medium' in severities:
            report['overall_risk'] = 'Medium'
        else:
            report['overall_risk'] = 'Low'
            
        return report

    def save_report(self, filename=None):
        """Save detailed report"""
        if not filename:
            filename = f"subdomain_exposure_hunt_{self.domain.replace('.', '_')}_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Subdomain Data Exposure Hunter')
    parser.add_argument('domain', help='Target domain to hunt subdomains for')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = SubdomainExposureHunter(args.domain, args.threads, args.timeout)
    findings = hunter.hunt_subdomain_exposure()
    
    print(f"\n{'='*60}")
    print("SUBDOMAIN EXPOSURE HUNTING RESULTS")
    print(f"{'='*60}")
    
    # Display discovery summary
    print(f"\nDISCOVERY SUMMARY:")
    print(f"-----------------")
    print(f"Subdomains Discovered: {len(hunter.discovered_subdomains)}")
    print(f"Live Subdomains: {len(hunter.live_subdomains)}")
    print(f"Development Subdomains: {len([s for s in hunter.live_subdomains if s['is_dev']])}")
    
    if not findings:
        print("\n[-] No subdomain exposure vulnerabilities found")
        return
        
    print(f"Vulnerabilities Found: {len(findings)}")
    
    # Group findings by severity and subdomain
    severity_groups = {}
    subdomain_stats = {}
    
    for finding in findings:
        severity = finding.get('severity', 'Low')
        subdomain = finding.get('subdomain', 'Unknown')
        
        if severity not in severity_groups:
            severity_groups[severity] = []
        severity_groups[severity].append(finding)
        
        subdomain_stats[subdomain] = subdomain_stats.get(subdomain, 0) + 1
    
    # Display findings by severity
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity in severity_groups:
            print(f"\n{severity.upper()} SEVERITY FINDINGS:")
            print("-" * 40)
            
            for finding in severity_groups[severity][:5]:  # Show first 5 per severity
                print(f"\n[!] {finding['type']}")
                print(f"    Subdomain: {finding['subdomain']}")
                print(f"    URL: {finding['url']}")
                print(f"    Impact: {finding['business_impact']}")
                
                if finding.get('sensitive_data'):
                    print(f"    Sensitive Data Types:")
                    for data_type, info in finding['sensitive_data'].items():
                        print(f"      - {data_type}: {info['count']} instances")
                
                if finding.get('is_development'):
                    print(f"    Development Environment: Yes")
                    
            if len(severity_groups[severity]) > 5:
                print(f"\n    ... and {len(severity_groups[severity]) - 5} more {severity.lower()} findings")
    
    # Display top risky subdomains
    print(f"\nTOP RISKY SUBDOMAINS:")
    print("-" * 25)
    sorted_subdomains = sorted(subdomain_stats.items(), key=lambda x: x[1], reverse=True)
    for subdomain, count in sorted_subdomains[:10]:
        dev_indicator = " (DEV)" if any(s['subdomain'] == subdomain and s['is_dev'] 
                                      for s in hunter.live_subdomains) else ""
        print(f"{subdomain}: {count} issues{dev_indicator}")
    
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Overall Risk Level: {report['overall_risk']}")
    print(f"[+] High-Risk Subdomains: {len(report['high_risk_subdomains'])}")
    print(f"[+] Total Findings: {report['vulnerability_summary']['total_findings']}")

if __name__ == '__main__':
    main()