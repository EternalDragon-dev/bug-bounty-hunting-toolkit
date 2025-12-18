#!/usr/bin/env python3
"""
Advanced API Hunter with DataDome Bypass Integration
Discovers API endpoints using the DataDome bypass techniques
"""

import requests
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datadome_bypass import DataDomeBypass
import sys
import os

class AdvancedAPIHunter:
    def __init__(self, bypass_instance=None):
        self.bypass = bypass_instance or DataDomeBypass()
        self.discovered_endpoints = []
        self.data_exposures = []
        self.lock = threading.Lock()
        
        # High-value API paths that often leak data
        self.api_paths = [
            # GraphQL endpoints
            "/graphql", "/api/graphql", "/v1/graphql", "/v2/graphql",
            "/admin/graphql", "/internal/graphql",
            
            # REST API endpoints
            "/api", "/api/v1", "/api/v2", "/api/v3", "/v1", "/v2", "/v3",
            "/rest", "/rest/v1", "/rest/v2", "/webapi", "/services",
            
            # Admin/internal APIs
            "/admin/api", "/internal/api", "/private/api", "/staff/api",
            "/management/api", "/console/api", "/backend/api",
            
            # Mobile APIs
            "/mobile/api", "/app/api", "/ios/api", "/android/api",
            
            # Authentication APIs
            "/auth/api", "/oauth/api", "/sso/api", "/login/api",
            "/token", "/refresh", "/validate",
            
            # User/profile APIs
            "/users", "/user", "/profile", "/account", "/me",
            "/users/me", "/api/users", "/api/user", "/api/profile",
            
            # Data APIs
            "/data", "/export", "/dump", "/backup", "/download",
            "/reports", "/analytics", "/metrics", "/stats",
            
            # Config/settings APIs
            "/config", "/settings", "/configuration", "/env",
            "/status", "/health", "/info", "/version", "/debug",
            
            # Search APIs
            "/search", "/query", "/find", "/lookup", "/autocomplete",
            "/suggestions", "/api/search", "/elastic", "/solr",
            
            # File/upload APIs
            "/files", "/upload", "/download", "/documents", "/media",
            "/assets", "/storage", "/cdn", "/static",
            
            # Business logic APIs
            "/orders", "/payments", "/billing", "/invoices", "/transactions",
            "/products", "/catalog", "/inventory", "/bookings", "/reservations",
            
            # Communication APIs
            "/messages", "/notifications", "/emails", "/sms", "/chat",
            "/comments", "/reviews", "/feedback",
            
            # Third-party integration APIs
            "/stripe", "/paypal", "/aws", "/google", "/facebook",
            "/twitter", "/linkedin", "/github", "/slack", "/jira",
        ]
        
        # API methods to test
        self.methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        # Common API parameters that reveal data
        self.test_params = {
            "limit": ["999", "1000", "9999"],
            "page": ["1", "0"],
            "size": ["100", "1000"],
            "count": ["1000"],
            "debug": ["1", "true"],
            "verbose": ["1", "true"],
            "format": ["json", "xml", "csv"],
            "export": ["true", "1"],
            "raw": ["true", "1"],
            "admin": ["1", "true"],
            "internal": ["true"],
            "test": ["1", "true"],
            "dev": ["1", "true"],
        }

    def hunt_api_endpoints(self, domain, max_threads=10):
        """Hunt for API endpoints using DataDome bypass"""
        print(f"[+] Starting advanced API hunting on {domain}")
        
        # First test if we can bypass DataDome on a basic endpoint
        test_url = f"https://{domain}/"
        bypass_results = self.bypass.test_all_techniques(test_url)
        
        if not any(r.get("success") for r in bypass_results):
            print(f"[-] Failed to bypass DataDome protection on {domain}")
            print(f"[-] All bypass techniques failed - target is heavily protected")
            return {"endpoints": [], "data_exposures": []}
        
        working_session = self.bypass.get_working_session()
        if not working_session:
            print(f"[-] No working session available")
            return {"endpoints": [], "data_exposures": []}
        
        print(f"[+] DataDome bypass successful! Starting endpoint discovery...")
        
        # Generate URLs to test
        urls_to_test = []
        for path in self.api_paths:
            urls_to_test.append(f"https://{domain}{path}")
            # Also test with common API path variations
            if not path.startswith('/api'):
                urls_to_test.append(f"https://{domain}/api{path}")
        
        # Test endpoints with threading
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_url = {}
            
            for url in urls_to_test:
                future = executor.submit(self._test_endpoint, url, working_session)
                future_to_url[future] = url
            
            completed = 0
            for future in as_completed(future_to_url):
                completed += 1
                url = future_to_url[future]
                
                if completed % 10 == 0:
                    print(f"[+] Progress: {completed}/{len(urls_to_test)} endpoints tested")
                
                try:
                    result = future.get(timeout=30)
                    if result and result.get("accessible"):
                        with self.lock:
                            self.discovered_endpoints.append(result)
                            print(f"[!] FOUND: {result['url']} - {result['status_code']}")
                            
                        # Test for data exposure
                        data_result = self._test_data_exposure(result, working_session)
                        if data_result:
                            with self.lock:
                                self.data_exposures.append(data_result)
                                print(f"[!] DATA EXPOSURE: {data_result['url']} - {data_result['exposure_type']}")
                
                except Exception as e:
                    print(f"[!] Error testing {url}: {e}")
                
                # Rate limiting - respect the bypass session
                time.sleep(random.uniform(0.5, 1.5))
        
        return {
            "endpoints": self.discovered_endpoints,
            "data_exposures": self.data_exposures
        }

    def _test_endpoint(self, url, session):
        """Test a single endpoint for accessibility"""
        try:
            # Add human-like delay
            time.sleep(random.uniform(0.3, 0.8))
            
            response = session.get(url, timeout=10, allow_redirects=False)
            
            # Consider endpoint accessible if:
            # - 200 OK (success)
            # - 401/403 (exists but unauthorized)
            # - 405 Method Not Allowed (endpoint exists, wrong method)
            # - 400 Bad Request (endpoint exists, needs parameters)
            accessible_codes = [200, 400, 401, 403, 405, 422, 429]
            
            if response.status_code in accessible_codes:
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "accessible": True,
                    "headers": dict(response.headers),
                    "content_length": len(response.content),
                    "response_time": response.elapsed.total_seconds(),
                    "content_preview": response.text[:500] if len(response.text) < 500 else response.text[:500] + "..."
                }
            
            return {"url": url, "status_code": response.status_code, "accessible": False}
            
        except Exception as e:
            return {"url": url, "error": str(e), "accessible": False}

    def _test_data_exposure(self, endpoint_result, session):
        """Test an accessible endpoint for data exposure"""
        url = endpoint_result["url"]
        
        try:
            # Test different methods
            for method in ["GET", "POST", "OPTIONS"]:
                try:
                    time.sleep(random.uniform(0.2, 0.6))
                    
                    if method == "GET":
                        # Test with various parameters
                        for param_name, param_values in self.test_params.items():
                            for param_value in param_values:
                                test_url = f"{url}?{param_name}={param_value}"
                                
                                response = session.get(test_url, timeout=8)
                                
                                if self._is_data_exposure(response):
                                    return {
                                        "url": test_url,
                                        "method": method,
                                        "status_code": response.status_code,
                                        "exposure_type": self._classify_exposure(response),
                                        "data_preview": response.text[:1000] if len(response.text) < 1000 else response.text[:1000] + "...",
                                        "headers": dict(response.headers),
                                        "timestamp": datetime.now().isoformat()
                                    }
                                
                                time.sleep(random.uniform(0.1, 0.3))
                    
                    elif method == "POST":
                        # Test POST with common payloads
                        test_payloads = [
                            {},
                            {"limit": 1000},
                            {"debug": True},
                            {"export": True},
                            {"format": "json"}
                        ]
                        
                        for payload in test_payloads:
                            response = session.post(url, json=payload, timeout=8)
                            
                            if self._is_data_exposure(response):
                                return {
                                    "url": url,
                                    "method": method,
                                    "payload": payload,
                                    "status_code": response.status_code,
                                    "exposure_type": self._classify_exposure(response),
                                    "data_preview": response.text[:1000] if len(response.text) < 1000 else response.text[:1000] + "...",
                                    "headers": dict(response.headers),
                                    "timestamp": datetime.now().isoformat()
                                }
                            
                            time.sleep(random.uniform(0.1, 0.3))
                    
                    elif method == "OPTIONS":
                        response = session.options(url, timeout=8)
                        
                        # Check for verbose OPTIONS responses
                        if (response.status_code == 200 and 
                            len(response.text) > 100 and
                            any(keyword in response.text.lower() for keyword in ["endpoint", "api", "method", "parameter"])):
                            return {
                                "url": url,
                                "method": method,
                                "status_code": response.status_code,
                                "exposure_type": "API Documentation",
                                "data_preview": response.text[:1000] if len(response.text) < 1000 else response.text[:1000] + "...",
                                "headers": dict(response.headers),
                                "timestamp": datetime.now().isoformat()
                            }
                
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            return None

    def _is_data_exposure(self, response):
        """Determine if response contains data exposure"""
        if response.status_code != 200:
            return False
        
        content = response.text.lower()
        
        # Check for JSON/XML data
        if len(response.text) > 200 and (
            content.startswith('{') or content.startswith('[') or 
            content.startswith('<?xml') or '"id":' in content or
            '"user' in content or '"admin' in content or
            '"password' in content or '"email' in content or
            '"token' in content or '"key' in content
        ):
            return True
        
        # Check for sensitive keywords
        sensitive_keywords = [
            "password", "token", "key", "secret", "private",
            "admin", "internal", "database", "config", "env",
            "user_id", "username", "email", "phone", "address",
            "credit_card", "ssn", "api_key", "access_token",
            "session", "cookie", "auth", "oauth"
        ]
        
        if any(keyword in content for keyword in sensitive_keywords):
            return True
        
        return False

    def _classify_exposure(self, response):
        """Classify the type of data exposure"""
        content = response.text.lower()
        
        if '"password"' in content or 'password:' in content:
            return "Password Exposure"
        elif '"token"' in content or '"access_token"' in content:
            return "Token Exposure"
        elif '"api_key"' in content or '"key":' in content:
            return "API Key Exposure"
        elif '"email"' in content or '"phone"' in content:
            return "PII Exposure"
        elif '"user"' in content or '"admin"' in content:
            return "User Data Exposure"
        elif '"database"' in content or '"connection"' in content:
            return "Database Info Exposure"
        elif '"config"' in content or '"env"' in content:
            return "Configuration Exposure"
        elif content.startswith('[{') and content.endswith('}]'):
            return "Bulk Data Exposure"
        else:
            return "Sensitive Data Exposure"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced API Hunter with DataDome Bypass')
    parser.add_argument('domain', help='Target domain to hunt APIs on')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads')
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Remove protocol if provided
    domain = args.domain.replace('https://', '').replace('http://', '')
    
    hunter = AdvancedAPIHunter()
    results = hunter.hunt_api_endpoints(domain, max_threads=args.threads)
    
    print(f"\n{'='*60}")
    print("ADVANCED API HUNTING RESULTS")
    print(f"{'='*60}")
    
    print(f"\n[+] Discovered {len(results['endpoints'])} accessible API endpoints")
    print(f"[!] Found {len(results['data_exposures'])} data exposures")
    
    if results['data_exposures']:
        print(f"\n🚨 CRITICAL FINDINGS:")
        for exposure in results['data_exposures']:
            print(f"    - {exposure['url']}")
            print(f"      Type: {exposure['exposure_type']}")
            print(f"      Method: {exposure['method']}")
            print(f"      Status: {exposure['status_code']}")
            print()
    
    if results['endpoints']:
        print(f"\n📡 ACCESSIBLE ENDPOINTS:")
        for endpoint in results['endpoints']:
            print(f"    - {endpoint['url']} ({endpoint['status_code']})")
    
    # Save results
    if args.output:
        output_data = {
            'target_domain': domain,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_endpoints': len(results['endpoints']),
                'data_exposures': len(results['data_exposures'])
            },
            'endpoints': results['endpoints'],
            'data_exposures': results['data_exposures']
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n[+] Results saved to {args.output}")

if __name__ == '__main__':
    main()