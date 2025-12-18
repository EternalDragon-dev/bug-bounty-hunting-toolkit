#!/usr/bin/env python3
"""
DataDome Bypass Hunter - Advanced Evasion Techniques
Bypasses DataDome bot protection for legitimate security research
"""

import requests
import random
import time
import json
from datetime import datetime
import base64
import hashlib
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import threading

class DataDomeBypass:
    def __init__(self):
        self.session = requests.Session()
        self.bypass_techniques = []
        self.success_headers = None
        self.success_rate = 0
        
        # Real browser User-Agents from different browsers/devices
        self.user_agents = [
            # Chrome Desktop
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            # Firefox Desktop
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
            # Safari Desktop
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            # Mobile browsers
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            # Custom bugcrowd compliance
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 bugcrowd-research",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 bugcrowd-security-research Chrome/119.0.0.0 Safari/537.36"
        ]
        
        # Real Accept-Language headers from different regions
        self.accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9,fr;q=0.8",
            "fr-FR,fr;q=0.9,en;q=0.8",
            "es-ES,es;q=0.9,en;q=0.8",
            "de-DE,de;q=0.9,en;q=0.8",
            "it-IT,it;q=0.9,en;q=0.8",
            "nl-NL,nl;q=0.9,en;q=0.8",
            "pt-BR,pt;q=0.9,en;q=0.8"
        ]
        
        # Real viewport sizes
        self.viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
            {"width": 375, "height": 667},   # iPhone
            {"width": 414, "height": 896},   # iPhone Pro
            {"width": 360, "height": 640},   # Android
        ]

    def generate_realistic_headers(self, target_domain):
        """Generate realistic browser headers to evade detection"""
        ua = random.choice(self.user_agents)
        viewport = random.choice(self.viewports)
        
        # Determine browser from UA
        is_chrome = "Chrome" in ua and "Edg" not in ua
        is_firefox = "Firefox" in ua
        is_safari = "Safari" in ua and "Chrome" not in ua
        is_mobile = "Mobile" in ua or "Android" in ua
        
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice(self.accept_languages),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        # Chrome-specific headers
        if is_chrome:
            headers.update({
                "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                "sec-ch-ua-mobile": "?1" if is_mobile else "?0",
                "sec-ch-ua-platform": '"Android"' if is_mobile else '"macOS"',
                "sec-ch-ua-arch": '"arm"' if is_mobile else '"x86"',
                "sec-ch-ua-bitness": '"64"',
                "sec-ch-ua-full-version-list": '"Google Chrome";v="119.0.6045.199", "Chromium";v="119.0.6045.199", "Not?A_Brand";v="24.0.0.0"',
                "sec-ch-viewport-width": str(viewport["width"]),
                "sec-ch-viewport-height": str(viewport["height"]),
                "sec-ch-device-memory": str(random.choice([2, 4, 8])),
            })
        
        # Add referer from legitimate sources
        referers = [
            f"https://www.google.com/",
            f"https://www.bing.com/",
            f"https://duckduckgo.com/",
            f"https://{target_domain}/",
            None  # Direct navigation
        ]
        
        referer = random.choice(referers)
        if referer:
            headers["Referer"] = referer
        
        return headers

    def technique_1_basic_rotation(self, url):
        """Technique 1: Basic header rotation with realistic timing"""
        try:
            headers = self.generate_realistic_headers(urllib.parse.urlparse(url).netloc)
            
            # Add random delay to simulate human behavior
            time.sleep(random.uniform(1.0, 3.5))
            
            response = self.session.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            return self._analyze_response(response, "Basic Rotation")
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_2_cookie_manipulation(self, url):
        """Technique 2: Cookie manipulation and session handling"""
        try:
            headers = self.generate_realistic_headers(urllib.parse.urlparse(url).netloc)
            
            # Clear existing cookies
            self.session.cookies.clear()
            
            # Sometimes add legitimate tracking cookies
            if random.random() > 0.3:
                tracking_cookies = {
                    "_ga": f"GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}",
                    "_gid": f"GA1.2.{random.randint(100000000, 999999999)}",
                    "_fbp": f"fb.1.{int(time.time() * 1000)}.{random.randint(100000000, 999999999)}",
                }
                
                for name, value in tracking_cookies.items():
                    self.session.cookies.set(name, value, domain=urllib.parse.urlparse(url).netloc)
            
            # Human-like delay
            time.sleep(random.uniform(0.8, 2.2))
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            return self._analyze_response(response, "Cookie Manipulation")
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_3_javascript_fingerprint_evasion(self, url):
        """Technique 3: Emulate JavaScript fingerprinting values"""
        try:
            headers = self.generate_realistic_headers(urllib.parse.urlparse(url).netloc)
            viewport = random.choice(self.viewports)
            
            # Add headers that JavaScript would typically send
            headers.update({
                "X-Requested-With": "XMLHttpRequest",
                "X-Viewport-Width": str(viewport["width"]),
                "X-Viewport-Height": str(viewport["height"]),
                "X-Screen-Resolution": f"{viewport['width']}x{viewport['height']}",
                "X-Timezone-Offset": str(random.choice([-480, -420, -360, -300, -240, -180, 0, 60, 120, 180])),
                "X-Language": random.choice(["en-US", "en-GB", "fr-FR", "es-ES", "de-DE"]),
                "X-Platform": random.choice(["MacIntel", "Win32", "Linux x86_64"]),
                "X-Touch-Support": "0" if not "Mobile" in headers["User-Agent"] else "1",
            })
            
            time.sleep(random.uniform(1.2, 2.8))
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            return self._analyze_response(response, "JS Fingerprint Evasion")
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_4_legitimate_workflow_simulation(self, url):
        """Technique 4: Simulate legitimate user workflow"""
        try:
            domain = urllib.parse.urlparse(url).netloc
            
            # Step 1: Visit homepage first (common user behavior)
            headers = self.generate_realistic_headers(domain)
            home_url = f"https://{domain}/"
            
            time.sleep(random.uniform(0.5, 1.5))
            home_response = self.session.get(home_url, headers=headers, timeout=10)
            
            if "datadome" in home_response.text.lower() or home_response.status_code == 403:
                # Step 2: Try with search engine referer
                headers["Referer"] = f"https://www.google.com/search?q=site:{domain}"
                time.sleep(random.uniform(1.0, 2.0))
                home_response = self.session.get(home_url, headers=headers, timeout=10)
            
            # Step 3: Now try target URL as if navigating from homepage
            if home_response.status_code == 200:
                headers["Referer"] = home_url
                time.sleep(random.uniform(1.5, 3.0))
                
                response = self.session.get(url, headers=headers, timeout=10)
                return self._analyze_response(response, "Legitimate Workflow")
            
            return {"success": False, "error": "Homepage blocked"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_5_http2_downgrade(self, url):
        """Technique 5: Force HTTP/1.1 to evade HTTP/2 fingerprinting"""
        try:
            headers = self.generate_realistic_headers(urllib.parse.urlparse(url).netloc)
            
            # Force HTTP/1.1
            adapter = requests.adapters.HTTPAdapter()
            self.session.mount('https://', adapter)
            self.session.mount('http://', adapter)
            
            time.sleep(random.uniform(1.0, 2.5))
            
            response = self.session.get(url, headers=headers, timeout=10, 
                                      stream=False)  # Disable streaming
            
            return self._analyze_response(response, "HTTP/1.1 Downgrade")
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def technique_6_request_spacing(self, url):
        """Technique 6: Human-like request spacing with multiple attempts"""
        try:
            success_count = 0
            attempts = 3
            
            for attempt in range(attempts):
                headers = self.generate_realistic_headers(urllib.parse.urlparse(url).netloc)
                
                # Vary delay based on attempt
                delays = [2.5, 4.2, 6.8]
                time.sleep(delays[attempt] + random.uniform(-0.5, 0.5))
                
                response = self.session.get(url, headers=headers, timeout=10)
                
                if response.status_code != 403 and "datadome" not in response.text.lower():
                    success_count += 1
                    if success_count == 1:  # Return on first success
                        return self._analyze_response(response, f"Request Spacing (Attempt {attempt + 1})")
            
            return {"success": False, "error": f"All {attempts} attempts failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_response(self, response, technique_name):
        """Analyze response to determine if bypass was successful"""
        is_blocked = (
            response.status_code == 403 or 
            "datadome" in response.text.lower() or
            "x-datadome" in [h.lower() for h in response.headers.keys()]
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
            result["success_headers"] = dict(response.request.headers)
            result["cookies"] = dict(response.cookies)
            
        return result

    def test_all_techniques(self, url):
        """Test all bypass techniques against a URL"""
        print(f"[+] Testing DataDome bypass techniques against: {url}")
        
        techniques = [
            self.technique_1_basic_rotation,
            self.technique_2_cookie_manipulation,
            self.technique_3_javascript_fingerprint_evasion,
            self.technique_4_legitimate_workflow_simulation,
            self.technique_5_http2_downgrade,
            self.technique_6_request_spacing,
        ]
        
        results = []
        
        for i, technique in enumerate(techniques, 1):
            print(f"[+] Testing technique {i}: {technique.__doc__.split(':')[1].split('Technique')[0].strip()}")
            
            try:
                result = technique(url)
                results.append(result)
                
                if result.get("success"):
                    print(f"[!] SUCCESS: {result['technique']} bypassed DataDome!")
                    print(f"    Status: {result['status_code']}")
                    print(f"    Response time: {result['response_time']:.2f}s")
                    self.success_headers = result.get("success_headers")
                    break
                else:
                    print(f"[-] FAILED: {result['technique']} - {result.get('error', 'Blocked')}")
                    
            except Exception as e:
                print(f"[!] ERROR in {technique.__name__}: {e}")
                results.append({"technique": technique.__name__, "success": False, "error": str(e)})
            
            # Cool-down between techniques
            time.sleep(random.uniform(2.0, 4.0))
        
        return results

    def get_working_session(self):
        """Return a working session with successful headers"""
        if self.success_headers:
            working_session = requests.Session()
            working_session.headers.update(self.success_headers)
            return working_session
        return None

    def bypass_request(self, url, method="GET", data=None, json_data=None):
        """Make a request using successful bypass technique"""
        if not self.success_headers:
            # Try to find working technique first
            results = self.test_all_techniques(url)
            if not any(r.get("success") for r in results):
                raise Exception("No working bypass technique found")
        
        # Use working headers
        session = self.get_working_session()
        
        # Add human-like delay
        time.sleep(random.uniform(1.0, 2.5))
        
        if method.upper() == "GET":
            return session.get(url, timeout=10)
        elif method.upper() == "POST":
            if json_data:
                return session.post(url, json=json_data, timeout=10)
            else:
                return session.post(url, data=data, timeout=10)
        else:
            return session.request(method, url, data=data, json=json_data, timeout=10)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DataDome Bypass Tester')
    parser.add_argument('url', help='Target URL to test bypass techniques against')
    parser.add_argument('-o', '--output', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    bypass = DataDomeBypass()
    results = bypass.test_all_techniques(args.url)
    
    print(f"\n{'='*60}")
    print("DATADOME BYPASS RESULTS")
    print(f"{'='*60}")
    
    successful_techniques = [r for r in results if r.get("success")]
    
    if successful_techniques:
        print(f"\n[+] SUCCESS! Found {len(successful_techniques)} working bypass technique(s):")
        for result in successful_techniques:
            print(f"    - {result['technique']}")
            print(f"      Status: {result['status_code']}")
            print(f"      Response time: {result['response_time']:.2f}s")
            
        print(f"\n[+] You can now use bypass.get_working_session() to make requests")
        
    else:
        print(f"\n[-] All bypass techniques failed against this target")
        print(f"[-] This target has very strong DataDome protection")
        
    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                'target': args.url,
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'successful_techniques': len(successful_techniques)
            }, f, indent=2)
        print(f"\n[+] Results saved to {args.output}")

if __name__ == '__main__':
    main()