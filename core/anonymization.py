#!/usr/bin/env python3
"""
Advanced Anonymization Module for Bug Bounty Toolkit
Provides centralized anonymous networking with toggle control
"""

import os
import sys
import time
import random
import socket
import requests
import subprocess
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import json
import logging
from datetime import datetime

# Import advanced user agent system
try:
    from .user_agents import user_agent_rotator, get_random_headers, get_desktop_headers, get_mobile_headers
    USER_AGENT_SYSTEM_AVAILABLE = True
except ImportError:
    USER_AGENT_SYSTEM_AVAILABLE = False
    print("[!] Advanced user agent system not available")

# Import advanced timing system
try:
    from .timing import timing_system, wait_before_request, record_request_response
    TIMING_SYSTEM_AVAILABLE = True
except ImportError:
    TIMING_SYSTEM_AVAILABLE = False
    print("[!] Advanced timing system not available")

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False
    print("[!] Warning: PySocks not installed. Install with: pip install PySocks")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnonymousNetworking:
    """Centralized anonymous networking with toggle control"""
    
    def __init__(self):
        self.anonymous_mode = self._check_anonymous_mode()
        self.tor_enabled = False
        self.proxy_chain_enabled = False
        self.user_agents = self._load_user_agents()
        self.current_user_agent = None
        self.session = None
        self._initialize_session()
        
        if self.anonymous_mode:
            self._setup_anonymization()
    
    def _check_anonymous_mode(self) -> bool:
        """Check if anonymous mode is enabled via environment variable"""
        env_var = os.getenv('TOOLKIT_ANONYMOUS', '').lower()
        return env_var in ['true', '1', 'yes', 'on', 'enabled']
    
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent strings (fallback if advanced system unavailable)"""
        return [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            # Mobile Chrome on Android
            'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            # Mobile Safari on iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            # Security scanner user agents (for legitimate testing)
            'Mozilla/5.0 (compatible; SecurityScanner/1.0; +https://example.com/bot)',
            'Mozilla/5.0 (compatible; VulnScanner/2.0)',
        ]
    
    def _initialize_session(self):
        """Initialize requests session with security headers"""
        self.session = requests.Session()
        
        # Set secure defaults
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Set random user agent
        self.rotate_user_agent()
        
        # Disable SSL warnings for testing environments
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _setup_anonymization(self):
        """Setup Tor and proxy chain routing"""
        print("[+] Anonymous mode enabled - Setting up anonymization...")
        
        # Check if Tor is running
        if self._check_tor_running():
            self.tor_enabled = True
            self._setup_tor_routing()
            print("[+] Tor routing enabled")
        else:
            print("[!] Tor not running - attempting to start...")
            if self._start_tor():
                self.tor_enabled = True
                self._setup_tor_routing()
                print("[+] Tor started and routing enabled")
            else:
                print("[!] Failed to start Tor - continuing without Tor")
        
        # Check proxychains
        if self._check_proxychains_available():
            self.proxy_chain_enabled = True
            print("[+] Proxychains available")
        
        self._setup_anonymous_headers()
    
    def _check_tor_running(self) -> bool:
        """Check if Tor is running on default port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            return result == 0
        except:
            return False
    
    def _start_tor(self) -> bool:
        """Attempt to start Tor service"""
        try:
            # Try systemctl (Linux)
            subprocess.run(['sudo', 'systemctl', 'start', 'tor'], 
                         capture_output=True, check=True)
            time.sleep(3)
            return self._check_tor_running()
        except:
            try:
                # Try brew services (macOS)
                subprocess.run(['brew', 'services', 'start', 'tor'], 
                             capture_output=True, check=True)
                time.sleep(3)
                return self._check_tor_running()
            except:
                return False
    
    def _setup_tor_routing(self):
        """Configure SOCKS5 proxy through Tor"""
        if not SOCKS_AVAILABLE:
            print("[!] PySocks not available - install with: pip install PySocks")
            return
            
        # Set up SOCKS proxy for all socket connections
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        
        # Configure requests session to use Tor
        self.session.proxies = {
            'http': 'socks5://127.0.0.1:9050',
            'https': 'socks5://127.0.0.1:9050'
        }
    
    def _check_proxychains_available(self) -> bool:
        """Check if proxychains is available"""
        try:
            result = subprocess.run(['which', 'proxychains4'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _setup_anonymous_headers(self):
        """Configure headers for maximum anonymity"""
        # Remove potentially identifying headers
        self.session.headers.pop('User-Agent', None)
        
        # Add anonymity-focused headers
        self.session.headers.update({
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'close'
        })
    
    def rotate_user_agent(self):
        """Rotate to a random user agent using advanced system if available"""
        if USER_AGENT_SYSTEM_AVAILABLE:
            # Use advanced user agent rotation with complete headers
            headers = get_random_headers()
            self.current_user_agent = headers['User-Agent']
            
            # Update session headers with realistic browser headers
            self.session.headers.update(headers)
        else:
            # Fallback to simple rotation
            self.current_user_agent = random.choice(self.user_agents)
            self.session.headers['User-Agent'] = self.current_user_agent
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an anonymized HTTP request with advanced timing"""
        
        parsed_url = urlparse(url)
        target_host = parsed_url.netloc
        
        # Advanced timing and delays if in anonymous mode
        if self.anonymous_mode:
            if TIMING_SYSTEM_AVAILABLE:
                # Use advanced timing system
                delay_used = wait_before_request(target_host, method)
            else:
                # Fallback to simple random delay
                delay = random.uniform(0.5, 3.0)
                time.sleep(delay)
                delay_used = delay
            
            # Rotate user agent occasionally
            if random.random() < 0.3:  # 30% chance
                self.rotate_user_agent()
        
        # Add timeout if not specified
        kwargs.setdefault('timeout', 30)
        
        # Disable SSL verification for testing (enable in production)
        kwargs.setdefault('verify', False)
        
        request_start = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Record timing metrics if available
            if self.anonymous_mode and TIMING_SYSTEM_AVAILABLE:
                response_time = time.time() - request_start
                success = 200 <= response.status_code < 400
                record_request_response(target_host, response_time, response.status_code, success)
            
            if self.anonymous_mode:
                logger.info(f"Anonymous request: {method} {url} -> {response.status_code}")
            
            return response
            
        except Exception as e:
            # Record failed request if timing system available
            if self.anonymous_mode and TIMING_SYSTEM_AVAILABLE:
                response_time = time.time() - request_start
                record_request_response(target_host, response_time, 0, False)
            
            logger.error(f"Request failed: {method} {url} -> {str(e)}")
            raise
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make anonymous GET request"""
        return self.make_request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make anonymous POST request"""
        return self.make_request('POST', url, **kwargs)
    
    def execute_command_anonymously(self, command: List[str]) -> subprocess.CompletedProcess:
        """Execute command through proxychains if available and anonymous mode is on"""
        
        if self.anonymous_mode and self.proxy_chain_enabled:
            # Prepend proxychains4 to the command
            command = ['proxychains4', '-q'] + command
            print(f"[+] Executing anonymously: {' '.join(command[2:])}")  # Hide proxychains from output
        
        return subprocess.run(command, capture_output=True, text=True)
    
    def check_anonymity(self) -> Dict[str, Any]:
        """Check current IP and anonymity status"""
        results = {
            'anonymous_mode': self.anonymous_mode,
            'tor_enabled': self.tor_enabled,
            'proxy_chain_enabled': self.proxy_chain_enabled,
            'current_ip': None,
            'tor_status': None,
            'user_agent': self.current_user_agent
        }
        
        try:
            # Check current IP
            response = self.get('https://ipinfo.io/json', timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                results['current_ip'] = ip_info.get('ip')
                results['location'] = ip_info.get('city', '') + ', ' + ip_info.get('country', '')
        except:
            results['current_ip'] = 'Unknown'
        
        try:
            # Check Tor status
            if self.tor_enabled:
                response = self.get('https://check.torproject.org/api/ip', timeout=10)
                if response.status_code == 200:
                    tor_check = response.json()
                    results['tor_status'] = tor_check.get('IsTor', False)
        except:
            results['tor_status'] = 'Unknown'
        
        return results
    
    def generate_report(self) -> str:
        """Generate anonymity status report"""
        status = self.check_anonymity()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    ANONYMIZATION STATUS                      ║
╚══════════════════════════════════════════════════════════════╝

Anonymous Mode: {'✅ ENABLED' if status['anonymous_mode'] else '❌ DISABLED'}
Tor Routing: {'✅ ACTIVE' if status['tor_enabled'] else '❌ INACTIVE'}
Proxy Chains: {'✅ AVAILABLE' if status['proxy_chain_enabled'] else '❌ UNAVAILABLE'}

Current IP: {status.get('current_ip', 'Unknown')}
Location: {status.get('location', 'Unknown')}
Tor Status: {'✅ USING TOR' if status.get('tor_status') else '❌ NOT USING TOR' if status.get('tor_status') is False else '❓ UNKNOWN'}
User Agent: {status.get('user_agent', 'None')[:80]}...

Environment Variable: TOOLKIT_ANONYMOUS={os.getenv('TOOLKIT_ANONYMOUS', 'not set')}
"""
        return report

# Global instance for toolkit-wide use
anon_net = AnonymousNetworking()

# Convenience functions for easy toolkit integration
def get(url: str, **kwargs) -> requests.Response:
    """Make anonymous GET request"""
    return anon_net.get(url, **kwargs)

def post(url: str, **kwargs) -> requests.Response:
    """Make anonymous POST request"""
    return anon_net.post(url, **kwargs)

def execute_anonymously(command: List[str]) -> subprocess.CompletedProcess:
    """Execute command anonymously"""
    return anon_net.execute_command_anonymously(command)

def check_anonymity() -> Dict[str, Any]:
    """Check current anonymity status"""
    return anon_net.check_anonymity()

def generate_anonymity_report() -> str:
    """Generate anonymity status report"""
    return anon_net.generate_report()

def is_anonymous_mode() -> bool:
    """Check if anonymous mode is enabled"""
    return anon_net.anonymous_mode

if __name__ == "__main__":
    # Test the anonymization system
    print(generate_anonymity_report())
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"\n[+] Testing anonymized request to: {test_url}")
        try:
            response = get(test_url)
            print(f"[+] Response: {response.status_code}")
            print(f"[+] Headers: {dict(list(response.headers.items())[:5])}")
        except Exception as e:
            print(f"[!] Test failed: {e}")