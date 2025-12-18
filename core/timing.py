#!/usr/bin/env python3
"""
Advanced Request Timing and Rate Limiting System
Implements intelligent delays and burst protection for stealth operations
"""

import time
import random
import math
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

@dataclass
class TimingProfile:
    """Timing profile for different operational scenarios"""
    name: str
    base_delay: float  # Base delay between requests (seconds)
    jitter_range: tuple  # (min_jitter, max_jitter) as multipliers
    burst_size: int  # Maximum requests in burst
    burst_delay: float  # Additional delay after burst
    adaptive: bool  # Whether to adapt timing based on responses
    human_like: bool  # Whether to simulate human-like patterns
    max_requests_per_minute: int  # Rate limit
    
@dataclass 
class RequestMetrics:
    """Track request metrics for adaptive timing"""
    timestamp: datetime
    response_time: float
    status_code: int
    target_host: str
    success: bool = True
    rate_limited: bool = False
    
class AdaptiveTimingSystem:
    """Advanced request timing system with adaptive capabilities"""
    
    def __init__(self):
        self.profiles = self._load_timing_profiles()
        self.current_profile = self.profiles["balanced"]
        self.request_history: deque = deque(maxlen=1000)
        self.host_metrics: Dict[str, List[RequestMetrics]] = defaultdict(list)
        self.burst_counters: Dict[str, int] = defaultdict(int)
        self.last_request_times: Dict[str, datetime] = {}
        self.adaptive_delays: Dict[str, float] = defaultdict(lambda: 0.0)
        self.lock = threading.Lock()
        
    def _load_timing_profiles(self) -> Dict[str, TimingProfile]:
        """Load predefined timing profiles for different scenarios"""
        return {
            "stealth": TimingProfile(
                name="stealth",
                base_delay=5.0,
                jitter_range=(0.8, 1.5),
                burst_size=3,
                burst_delay=15.0,
                adaptive=True,
                human_like=True,
                max_requests_per_minute=8
            ),
            
            "balanced": TimingProfile(
                name="balanced",
                base_delay=2.0,
                jitter_range=(0.5, 2.0),
                burst_size=5,
                burst_delay=8.0,
                adaptive=True,
                human_like=True,
                max_requests_per_minute=15
            ),
            
            "aggressive": TimingProfile(
                name="aggressive",
                base_delay=0.5,
                jitter_range=(0.1, 1.0),
                burst_size=10,
                burst_delay=3.0,
                adaptive=True,
                human_like=False,
                max_requests_per_minute=40
            ),
            
            "crawl": TimingProfile(
                name="crawl",
                base_delay=1.0,
                jitter_range=(0.3, 1.8),
                burst_size=8,
                burst_delay=5.0,
                adaptive=True,
                human_like=True,
                max_requests_per_minute=25
            ),
            
            "human": TimingProfile(
                name="human",
                base_delay=8.0,
                jitter_range=(0.6, 2.5),
                burst_size=2,
                burst_delay=30.0,
                adaptive=True,
                human_like=True,
                max_requests_per_minute=5
            ),
            
            "scanner": TimingProfile(
                name="scanner",
                base_delay=0.1,
                jitter_range=(0.05, 0.3),
                burst_size=20,
                burst_delay=1.0,
                adaptive=False,
                human_like=False,
                max_requests_per_minute=100
            )
        }
    
    def set_profile(self, profile_name: str):
        """Set the current timing profile"""
        if profile_name in self.profiles:
            self.current_profile = self.profiles[profile_name]
            print(f"[+] Timing profile set to: {profile_name}")
        else:
            print(f"[!] Unknown timing profile: {profile_name}")
            print(f"[+] Available profiles: {list(self.profiles.keys())}")
    
    def calculate_delay(self, target_host: str, request_type: str = "GET") -> float:
        """Calculate appropriate delay before next request"""
        
        with self.lock:
            profile = self.current_profile
            
            # Base delay with jitter
            jitter_min, jitter_max = profile.jitter_range
            jitter = random.uniform(jitter_min, jitter_max)
            base_delay = profile.base_delay * jitter
            
            # Human-like timing patterns
            if profile.human_like:
                base_delay = self._apply_human_patterns(base_delay)
            
            # Adaptive delay based on past responses
            if profile.adaptive:
                adaptive_delay = self.adaptive_delays.get(target_host, 0.0)
                base_delay += adaptive_delay
            
            # Burst protection
            burst_delay = self._calculate_burst_delay(target_host)
            
            # Rate limiting check
            rate_delay = self._calculate_rate_limit_delay(target_host)
            
            # Take the maximum of all delays
            total_delay = max(base_delay, burst_delay, rate_delay)
            
            return total_delay
    
    def _apply_human_patterns(self, base_delay: float) -> float:
        """Apply human-like timing patterns"""
        
        current_time = datetime.now()
        hour = current_time.hour
        
        # Slower during "break times" (lunch, evening)
        if hour in [12, 13, 17, 18, 19]:
            base_delay *= random.uniform(1.2, 1.8)
        
        # Faster during "work hours"
        elif hour in [9, 10, 14, 15, 16]:
            base_delay *= random.uniform(0.8, 1.2)
        
        # Add occasional longer pauses (human takes a break)
        if random.random() < 0.05:  # 5% chance
            base_delay += random.uniform(10.0, 30.0)
            
        # Add micro-pauses that humans have
        if random.random() < 0.3:  # 30% chance
            base_delay += random.uniform(0.1, 0.5)
            
        return base_delay
    
    def _calculate_burst_delay(self, target_host: str) -> float:
        """Calculate delay needed for burst protection"""
        
        profile = self.current_profile
        burst_count = self.burst_counters.get(target_host, 0)
        
        # If we've hit the burst limit, add burst delay
        if burst_count >= profile.burst_size:
            self.burst_counters[target_host] = 0  # Reset counter
            return profile.burst_delay
        
        return 0.0
    
    def _calculate_rate_limit_delay(self, target_host: str) -> float:
        """Calculate delay to stay within rate limits"""
        
        profile = self.current_profile
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)
        
        # Count requests in last minute
        if target_host in self.host_metrics:
            recent_requests = [
                req for req in self.host_metrics[target_host]
                if req.timestamp > minute_ago
            ]
            
            if len(recent_requests) >= profile.max_requests_per_minute:
                # Calculate delay needed to respect rate limit
                oldest_request = min(recent_requests, key=lambda x: x.timestamp)
                time_until_oldest_expires = 60 - (current_time - oldest_request.timestamp).total_seconds()
                return max(0, time_until_oldest_expires)
        
        return 0.0
    
    def wait_for_next_request(self, target_host: str, request_type: str = "GET") -> float:
        """Wait appropriate time before next request and return delay used"""
        
        delay = self.calculate_delay(target_host, request_type)
        
        if delay > 0:
            if delay > 10:
                print(f"[⏸️ ] Sleeping for {delay:.1f}s ({self.current_profile.name} profile)")
            time.sleep(delay)
        
        # Increment burst counter
        self.burst_counters[target_host] += 1
        self.last_request_times[target_host] = datetime.now()
        
        return delay
    
    def record_response(self, target_host: str, response_time: float, status_code: int, success: bool = True):
        """Record response metrics for adaptive timing"""
        
        metrics = RequestMetrics(
            timestamp=datetime.now(),
            response_time=response_time,
            status_code=status_code,
            target_host=target_host,
            success=success,
            rate_limited=(status_code in [429, 503, 509])
        )
        
        with self.lock:
            self.host_metrics[target_host].append(metrics)
            self.request_history.append(metrics)
            
            # Adaptive learning
            if self.current_profile.adaptive:
                self._update_adaptive_delay(target_host, metrics)
    
    def _update_adaptive_delay(self, target_host: str, metrics: RequestMetrics):
        """Update adaptive delay based on response metrics"""
        
        current_adaptive_delay = self.adaptive_delays[target_host]
        
        # If we got rate limited, increase delay significantly
        if metrics.rate_limited:
            self.adaptive_delays[target_host] = current_adaptive_delay + 5.0
            print(f"[⚠️ ] Rate limited by {target_host}, increasing delay to {self.adaptive_delays[target_host]:.1f}s")
        
        # If request failed, increase delay slightly
        elif not metrics.success:
            self.adaptive_delays[target_host] = current_adaptive_delay + 1.0
            
        # If request was very slow, increase delay
        elif metrics.response_time > 10.0:
            self.adaptive_delays[target_host] = current_adaptive_delay + 0.5
            
        # If everything is good, gradually decrease adaptive delay
        elif metrics.success and metrics.response_time < 2.0:
            self.adaptive_delays[target_host] = max(0, current_adaptive_delay - 0.1)
        
        # Cap adaptive delay at reasonable maximum
        self.adaptive_delays[target_host] = min(30.0, self.adaptive_delays[target_host])
    
    def get_timing_stats(self, target_host: Optional[str] = None) -> Dict[str, Any]:
        """Get timing statistics"""
        
        with self.lock:
            stats = {
                "current_profile": self.current_profile.name,
                "total_requests": len(self.request_history),
                "hosts_contacted": len(self.host_metrics),
                "adaptive_delays": dict(self.adaptive_delays),
                "burst_counters": dict(self.burst_counters)
            }
            
            if target_host and target_host in self.host_metrics:
                host_requests = self.host_metrics[target_host]
                stats["host_stats"] = {
                    "total_requests": len(host_requests),
                    "success_rate": sum(1 for r in host_requests if r.success) / len(host_requests) * 100,
                    "avg_response_time": sum(r.response_time for r in host_requests) / len(host_requests),
                    "rate_limited_count": sum(1 for r in host_requests if r.rate_limited),
                    "current_adaptive_delay": self.adaptive_delays.get(target_host, 0.0)
                }
            
            return stats
    
    def reset_host_metrics(self, target_host: str):
        """Reset metrics for a specific host"""
        with self.lock:
            if target_host in self.host_metrics:
                del self.host_metrics[target_host]
            if target_host in self.adaptive_delays:
                del self.adaptive_delays[target_host]
            if target_host in self.burst_counters:
                del self.burst_counters[target_host]
            if target_host in self.last_request_times:
                del self.last_request_times[target_host]
            print(f"[+] Reset timing metrics for {target_host}")
    
    def clear_all_metrics(self):
        """Clear all timing metrics"""
        with self.lock:
            self.request_history.clear()
            self.host_metrics.clear()
            self.adaptive_delays.clear()
            self.burst_counters.clear()
            self.last_request_times.clear()
            print("[+] All timing metrics cleared")
    
    def export_metrics(self, filename: str):
        """Export timing metrics to JSON file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "current_profile": self.current_profile.name,
            "request_history": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "target_host": r.target_host,
                    "success": r.success,
                    "rate_limited": r.rate_limited
                }
                for r in self.request_history
            ],
            "adaptive_delays": dict(self.adaptive_delays),
            "timing_stats": self.get_timing_stats()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[+] Timing metrics exported to {filename}")

# Global timing system instance
timing_system = AdaptiveTimingSystem()

# Convenience functions
def set_timing_profile(profile_name: str):
    """Set the current timing profile"""
    timing_system.set_profile(profile_name)

def wait_before_request(target_host: str, request_type: str = "GET") -> float:
    """Wait appropriate time before making a request"""
    return timing_system.wait_for_next_request(target_host, request_type)

def record_request_response(target_host: str, response_time: float, status_code: int, success: bool = True):
    """Record response for adaptive timing"""
    timing_system.record_response(target_host, response_time, status_code, success)

def get_current_profile() -> str:
    """Get current timing profile name"""
    return timing_system.current_profile.name

def get_timing_statistics(target_host: Optional[str] = None) -> Dict[str, Any]:
    """Get timing statistics"""
    return timing_system.get_timing_stats(target_host)

if __name__ == "__main__":
    # Test the timing system
    print("⏱️  Advanced Request Timing System Test")
    print("=" * 50)
    
    test_host = "example.com"
    
    # Test different profiles
    for profile in ["stealth", "balanced", "aggressive", "human"]:
        print(f"\\nTesting {profile} profile:")
        set_timing_profile(profile)
        
        for i in range(3):
            delay = wait_before_request(test_host)
            record_request_response(test_host, random.uniform(0.5, 3.0), 200, True)
            print(f"  Request {i+1}: {delay:.2f}s delay")
    
    # Show statistics
    print("\\n📊 Final Statistics:")
    stats = get_timing_statistics(test_host)
    print(f"Total requests: {stats['total_requests']}")
    print(f"Host stats: {stats.get('host_stats', {})}")
    
    # Test adaptive delay (simulate rate limiting)
    print("\\nTesting adaptive delay (simulating rate limit):")
    record_request_response(test_host, 1.0, 429, False)  # Rate limited
    delay = wait_before_request(test_host)
    print(f"Adaptive delay after rate limit: {delay:.2f}s")