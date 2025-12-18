#!/usr/bin/env python3
"""
Advanced User Agent Database and Rotation System
Provides comprehensive browser fingerprinting resistance
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class UserAgentProfile:
    """Complete user agent profile with associated headers"""
    user_agent: str
    platform: str  # windows, macos, linux, android, ios
    browser: str   # chrome, firefox, safari, edge
    device_type: str  # desktop, mobile, tablet
    headers: Dict[str, str]
    screen_resolution: str
    timezone: str
    language: str
    characteristics: List[str]  # Features like "webgl", "touch", etc.

class AdvancedUserAgentRotator:
    """Advanced user agent rotation with complete browser fingerprinting"""
    
    def __init__(self):
        self.profiles = self._load_user_agent_profiles()
        self.current_profile = None
        self.session_profiles = []  # Track profiles used in current session
        
    def _load_user_agent_profiles(self) -> List[UserAgentProfile]:
        """Load comprehensive user agent profiles"""
        
        # Chrome profiles (most common)
        chrome_profiles = [
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="windows",
                browser="chrome",
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="1920x1080",
                timezone="America/New_York",
                language="en-US",
                characteristics=["webgl", "canvas", "webrtc", "geolocation"]
            ),
            
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="macos",
                browser="chrome",
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"macOS"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="2560x1600",
                timezone="America/Los_Angeles", 
                language="en-US",
                characteristics=["webgl", "canvas", "webrtc", "geolocation"]
            ),
            
            UserAgentProfile(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                platform="linux",
                browser="chrome",
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Linux"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="1920x1080",
                timezone="UTC",
                language="en-US",
                characteristics=["webgl", "canvas", "webrtc"]
            ),
        ]
        
        # Firefox profiles
        firefox_profiles = [
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                platform="windows",
                browser="firefox",
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                },
                screen_resolution="1920x1080",
                timezone="America/New_York",
                language="en-US",
                characteristics=["webgl", "canvas", "indexeddb"]
            ),
            
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                platform="macos",
                browser="firefox", 
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1"
                },
                screen_resolution="2560x1600",
                timezone="America/Los_Angeles",
                language="en-US",
                characteristics=["webgl", "canvas", "indexeddb"]
            ),
        ]
        
        # Safari profiles
        safari_profiles = [
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
                platform="macos",
                browser="safari",
                device_type="desktop",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="2560x1600",
                timezone="America/Los_Angeles",
                language="en-US",
                characteristics=["webgl", "canvas", "geolocation"]
            ),
        ]
        
        # Mobile profiles
        mobile_profiles = [
            UserAgentProfile(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                platform="ios",
                browser="safari",
                device_type="mobile",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="393x852",
                timezone="America/New_York",
                language="en-US",
                characteristics=["touch", "geolocation", "accelerometer"]
            ),
            
            UserAgentProfile(
                user_agent="Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                platform="android",
                browser="chrome",
                device_type="mobile",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?1",
                    "Sec-Ch-Ua-Platform": '"Android"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                },
                screen_resolution="412x915",
                timezone="America/New_York",
                language="en-US",
                characteristics=["touch", "geolocation", "accelerometer", "webgl"]
            ),
        ]
        
        # Security scanner profiles (for legitimate testing)
        scanner_profiles = [
            UserAgentProfile(
                user_agent="Mozilla/5.0 (compatible; SecurityScanner/1.0; +https://example.com/security-research)",
                platform="linux",
                browser="scanner",
                device_type="server",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1"
                },
                screen_resolution="1920x1080",
                timezone="UTC",
                language="en-US",
                characteristics=["automated"]
            ),
            
            UserAgentProfile(
                user_agent="Mozilla/5.0 (compatible; VulnScanner/2.0; Security Research)",
                platform="linux", 
                browser="scanner",
                device_type="server",
                headers={
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1"
                },
                screen_resolution="1920x1080",
                timezone="UTC",
                language="en-US",
                characteristics=["automated", "security"]
            ),
        ]
        
        return chrome_profiles + firefox_profiles + safari_profiles + mobile_profiles + scanner_profiles
    
    def get_random_profile(self, device_type: Optional[str] = None, platform: Optional[str] = None) -> UserAgentProfile:
        """Get a random user agent profile with optional filtering"""
        
        available_profiles = self.profiles
        
        # Filter by device type if specified
        if device_type:
            available_profiles = [p for p in available_profiles if p.device_type == device_type]
            
        # Filter by platform if specified  
        if platform:
            available_profiles = [p for p in available_profiles if p.platform == platform]
        
        if not available_profiles:
            # Fallback to all profiles if filters are too restrictive
            available_profiles = self.profiles
            
        profile = random.choice(available_profiles)
        self.current_profile = profile
        self.session_profiles.append(profile)
        
        return profile
    
    def get_desktop_profile(self) -> UserAgentProfile:
        """Get a random desktop profile"""
        return self.get_random_profile(device_type="desktop")
    
    def get_mobile_profile(self) -> UserAgentProfile:
        """Get a random mobile profile"""
        return self.get_random_profile(device_type="mobile")
    
    def get_scanner_profile(self) -> UserAgentProfile:
        """Get a security scanner profile"""
        scanner_profiles = [p for p in self.profiles if p.browser == "scanner"]
        profile = random.choice(scanner_profiles)
        self.current_profile = profile
        return profile
    
    def rotate_profile(self, avoid_recent: bool = True) -> UserAgentProfile:
        """Rotate to a new profile, optionally avoiding recently used ones"""
        
        if avoid_recent and len(self.session_profiles) > 0:
            # Avoid profiles used in last 5 requests
            recent_profiles = self.session_profiles[-5:]
            available = [p for p in self.profiles if p not in recent_profiles]
            
            if available:
                profile = random.choice(available)
            else:
                # If all profiles were recently used, just pick randomly
                profile = random.choice(self.profiles)
        else:
            profile = random.choice(self.profiles)
            
        self.current_profile = profile
        self.session_profiles.append(profile)
        
        return profile
    
    def get_matching_headers(self, profile: Optional[UserAgentProfile] = None) -> Dict[str, str]:
        """Get headers that match the current or specified profile"""
        
        if profile is None:
            profile = self.current_profile
            
        if profile is None:
            # No profile set, get a random one
            profile = self.get_random_profile()
            
        headers = profile.headers.copy()
        headers["User-Agent"] = profile.user_agent
        
        # Add some random variance to avoid exact fingerprint matching
        if random.random() < 0.3:  # 30% chance
            headers["Cache-Control"] = random.choice(["max-age=0", "no-cache", "no-store"])
            
        if random.random() < 0.2:  # 20% chance
            headers["Connection"] = random.choice(["keep-alive", "close"])
        
        return headers
    
    def get_fingerprint_data(self, profile: Optional[UserAgentProfile] = None) -> Dict[str, str]:
        """Get browser fingerprint data for the profile"""
        
        if profile is None:
            profile = self.current_profile
            
        if profile is None:
            profile = self.get_random_profile()
            
        return {
            "user_agent": profile.user_agent,
            "platform": profile.platform,
            "browser": profile.browser,
            "device_type": profile.device_type,
            "screen_resolution": profile.screen_resolution,
            "timezone": profile.timezone,
            "language": profile.language,
            "characteristics": profile.characteristics
        }
    
    def generate_session_report(self) -> Dict:
        """Generate report of user agents used in current session"""
        
        profile_counts = {}
        browser_counts = {}
        platform_counts = {}
        
        for profile in self.session_profiles:
            # Count profiles
            profile_key = f"{profile.browser}-{profile.platform}-{profile.device_type}"
            profile_counts[profile_key] = profile_counts.get(profile_key, 0) + 1
            
            # Count browsers
            browser_counts[profile.browser] = browser_counts.get(profile.browser, 0) + 1
            
            # Count platforms
            platform_counts[profile.platform] = platform_counts.get(profile.platform, 0) + 1
        
        return {
            "total_requests": len(self.session_profiles),
            "unique_profiles": len(set(p.user_agent for p in self.session_profiles)),
            "profile_distribution": profile_counts,
            "browser_distribution": browser_counts,
            "platform_distribution": platform_counts,
            "session_start": self.session_profiles[0].user_agent if self.session_profiles else None,
            "current_profile": self.current_profile.user_agent if self.current_profile else None
        }
    
    def clear_session(self):
        """Clear session history"""
        self.session_profiles = []
        self.current_profile = None

# Global instance for easy access
user_agent_rotator = AdvancedUserAgentRotator()

# Convenience functions
def get_random_user_agent() -> str:
    """Get a random user agent string"""
    profile = user_agent_rotator.get_random_profile()
    return profile.user_agent

def get_random_headers() -> Dict[str, str]:
    """Get random headers with matching user agent"""
    profile = user_agent_rotator.get_random_profile()
    return user_agent_rotator.get_matching_headers(profile)

def get_desktop_headers() -> Dict[str, str]:
    """Get desktop browser headers"""
    profile = user_agent_rotator.get_desktop_profile()
    return user_agent_rotator.get_matching_headers(profile)

def get_mobile_headers() -> Dict[str, str]:
    """Get mobile browser headers"""
    profile = user_agent_rotator.get_mobile_profile()
    return user_agent_rotator.get_matching_headers(profile)

def get_scanner_headers() -> Dict[str, str]:
    """Get security scanner headers"""
    profile = user_agent_rotator.get_scanner_profile()
    return user_agent_rotator.get_matching_headers(profile)

def rotate_user_agent() -> str:
    """Rotate to a new user agent"""
    profile = user_agent_rotator.rotate_profile()
    return profile.user_agent

if __name__ == "__main__":
    # Test the user agent rotation system
    print("🎭 Advanced User Agent Rotation System Test")
    print("=" * 50)
    
    # Test different profile types
    print("\\n📱 Mobile Profile:")
    mobile = user_agent_rotator.get_mobile_profile()
    print(f"User Agent: {mobile.user_agent}")
    print(f"Platform: {mobile.platform}, Browser: {mobile.browser}")
    
    print("\\n🖥️  Desktop Profile:")
    desktop = user_agent_rotator.get_desktop_profile()
    print(f"User Agent: {desktop.user_agent}")
    print(f"Platform: {desktop.platform}, Browser: {desktop.browser}")
    
    print("\\n🔍 Scanner Profile:")
    scanner = user_agent_rotator.get_scanner_profile()
    print(f"User Agent: {scanner.user_agent}")
    print(f"Type: {scanner.device_type}")
    
    # Test rotation
    print("\\n🔄 Rotation Test:")
    for i in range(3):
        profile = user_agent_rotator.rotate_profile()
        print(f"{i+1}. {profile.browser.upper()} on {profile.platform.upper()}")
    
    # Session report
    print("\\n📊 Session Report:")
    report = user_agent_rotator.generate_session_report()
    print(f"Total requests: {report['total_requests']}")
    print(f"Unique profiles: {report['unique_profiles']}")
    print(f"Browser distribution: {report['browser_distribution']}")