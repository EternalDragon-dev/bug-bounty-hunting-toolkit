#!/usr/bin/env python3
"""
Advanced Traffic Analysis Protection Module
==========================================

This module provides sophisticated traffic analysis protection through:
- Traffic padding and timing obfuscation
- Decoy traffic generation 
- Connection multiplexing through different exit nodes
- Pattern disruption and correlation resistance
- Adaptive traffic shaping based on network conditions

Features:
- Multi-threaded decoy traffic generation
- Intelligent timing randomization
- Traffic flow padding and shaping
- Exit node rotation and multiplexing
- Behavioral pattern disruption
- Real-time traffic analysis countermeasures
"""

import os
import sys
import time
import random
import threading
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
import socket
import ssl
import requests
import concurrent.futures
from urllib.parse import urlparse
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TrafficFlow:
    """Represents a network traffic flow with metadata"""
    flow_id: str
    source_ip: str
    destination: str  
    protocol: str
    start_time: datetime
    duration: float = 0.0
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    obfuscated: bool = False
    decoy: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class DecoyProfile:
    """Configuration for decoy traffic generation"""
    name: str
    target_domains: List[str]
    request_patterns: List[str]
    timing_profile: Dict[str, Any]
    volume_profile: Dict[str, Any]
    user_agents: List[str]
    enabled: bool = True


class TrafficAnalysisProtection:
    """Advanced traffic analysis protection system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize traffic protection system"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'configs', 'traffic_protection.json')
        self.config = self._load_config()
        
        # Core components
        self.active_flows: Dict[str, TrafficFlow] = {}
        self.decoy_threads: List[threading.Thread] = []
        self.protection_active = False
        self.exit_nodes = []
        
        # Traffic analysis
        self.flow_patterns = {}
        self.timing_analyzer = TimingAnalyzer()
        self.padding_engine = TrafficPaddingEngine()
        self.decoy_generator = DecoyTrafficGenerator(self.config.get("decoy_profiles", []))
        
        # Statistics and monitoring
        self.stats = {
            "flows_protected": 0,
            "decoy_sessions": 0,
            "bytes_padded": 0,
            "timing_obfuscations": 0,
            "exit_node_switches": 0
        }
        
        # Load exit node configurations
        self._initialize_exit_nodes()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load traffic protection configuration"""
        default_config = {
            "protection_enabled": True,
            "timing_obfuscation": {
                "enabled": True,
                "min_delay": 0.1,
                "max_delay": 2.0,
                "jitter_factor": 0.3,
                "burst_protection": True
            },
            "traffic_padding": {
                "enabled": True,
                "min_padding": 64,
                "max_padding": 1024,
                "padding_frequency": 0.7,
                "adaptive_padding": True
            },
            "decoy_traffic": {
                "enabled": True,
                "concurrent_sessions": 3,
                "session_duration": [300, 1800],  # 5-30 minutes
                "request_frequency": [10, 60],    # 10-60 seconds
                "volume_ratio": 0.3               # 30% of real traffic volume
            },
            "exit_node_rotation": {
                "enabled": True,
                "rotation_interval": 1800,       # 30 minutes
                "max_concurrent_nodes": 3,
                "node_selection_strategy": "random"
            },
            "pattern_disruption": {
                "enabled": True,
                "flow_mixing": True,
                "timing_randomization": True,
                "size_normalization": True
            },
            "decoy_profiles": [
                {
                    "name": "web_browsing",
                    "target_domains": ["google.com", "wikipedia.org", "github.com", "stackoverflow.com"],
                    "request_patterns": ["search", "browse", "read"],
                    "timing_profile": {"min_interval": 5, "max_interval": 120},
                    "volume_profile": {"min_size": 1024, "max_size": 65536},
                    "user_agents": ["chrome", "firefox", "safari"]
                },
                {
                    "name": "social_media",
                    "target_domains": ["twitter.com", "reddit.com", "news.ycombinator.com"],
                    "request_patterns": ["timeline", "posts", "comments"],
                    "timing_profile": {"min_interval": 10, "max_interval": 300},
                    "volume_profile": {"min_size": 512, "max_size": 32768},
                    "user_agents": ["mobile_chrome", "mobile_firefox"]
                },
                {
                    "name": "development",
                    "target_domains": ["github.com", "gitlab.com", "bitbucket.org", "npmjs.com"],
                    "request_patterns": ["repos", "commits", "packages"],
                    "timing_profile": {"min_interval": 30, "max_interval": 600},
                    "volume_profile": {"min_size": 2048, "max_size": 131072},
                    "user_agents": ["developer_tools"]
                }
            ]
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")
                
        return default_config
    
    def _initialize_exit_nodes(self):
        """Initialize exit node configurations"""
        try:
            # In a real implementation, this would connect to Tor control port
            # or use other proxy networks to get available exit nodes
            self.exit_nodes = [
                {"id": "exit1", "ip": "127.0.0.1", "port": 9050, "country": "US"},
                {"id": "exit2", "ip": "127.0.0.1", "port": 9051, "country": "DE"}, 
                {"id": "exit3", "ip": "127.0.0.1", "port": 9052, "country": "NL"}
            ]
            logger.info(f"Initialized {len(self.exit_nodes)} exit nodes")
        except Exception as e:
            logger.error(f"Failed to initialize exit nodes: {e}")
            self.exit_nodes = []
    
    def start_protection(self) -> bool:
        """Start comprehensive traffic analysis protection"""
        try:
            if self.protection_active:
                logger.warning("Traffic protection already active")
                return True
                
            logger.info("Starting traffic analysis protection system")
            
            # Start core protection components
            if self.config.get("timing_obfuscation", {}).get("enabled", True):
                self.timing_analyzer.start()
                
            if self.config.get("traffic_padding", {}).get("enabled", True):
                self.padding_engine.start()
                
            if self.config.get("decoy_traffic", {}).get("enabled", True):
                self._start_decoy_traffic()
                
            if self.config.get("exit_node_rotation", {}).get("enabled", True):
                self._start_exit_node_rotation()
                
            self.protection_active = True
            logger.info("Traffic analysis protection system started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start traffic protection: {e}")
            return False
    
    def stop_protection(self) -> bool:
        """Stop all traffic analysis protection"""
        try:
            logger.info("Stopping traffic analysis protection system")
            
            # Stop all components
            self.protection_active = False
            
            self.timing_analyzer.stop()
            self.padding_engine.stop()
            self._stop_decoy_traffic()
            
            # Clear active flows
            self.active_flows.clear()
            
            logger.info("Traffic analysis protection system stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop traffic protection: {e}")
            return False
    
    def protect_request(self, request_func: Callable, *args, **kwargs) -> Any:
        """Wrap a network request with traffic analysis protection"""
        if not self.protection_active:
            logger.warning("Traffic protection not active, executing unprotected request")
            return request_func(*args, **kwargs)
            
        try:
            # Create flow tracking
            flow_id = self._generate_flow_id()
            flow = TrafficFlow(
                flow_id=flow_id,
                source_ip="127.0.0.1",  # Will be replaced with actual source
                destination=kwargs.get('url', str(args[0]) if args else 'unknown'),
                protocol="HTTPS",
                start_time=datetime.now()
            )
            
            self.active_flows[flow_id] = flow
            
            # Apply timing obfuscation
            if self.config.get("timing_obfuscation", {}).get("enabled", True):
                delay = self.timing_analyzer.calculate_obfuscation_delay(flow)
                if delay > 0:
                    time.sleep(delay)
                    self.stats["timing_obfuscations"] += 1
            
            # Apply traffic padding if applicable
            if self.config.get("traffic_padding", {}).get("enabled", True):
                padded_data = self.padding_engine.pad_request_data(kwargs)
                kwargs.update(padded_data)
            
            # Execute the actual request
            start_time = time.time()
            try:
                result = request_func(*args, **kwargs)
                flow.duration = time.time() - start_time
                flow.obfuscated = True
                self.stats["flows_protected"] += 1
                return result
                
            except Exception as e:
                flow.duration = time.time() - start_time
                logger.error(f"Protected request failed: {e}")
                raise
                
            finally:
                # Clean up flow tracking
                if flow_id in self.active_flows:
                    del self.active_flows[flow_id]
                    
        except Exception as e:
            logger.error(f"Failed to protect request: {e}")
            # Fallback to unprotected request
            return request_func(*args, **kwargs)
    
    def _generate_flow_id(self) -> str:
        """Generate unique flow identifier"""
        timestamp = str(int(time.time() * 1000000))
        random_bytes = os.urandom(8)
        return hashlib.sha256((timestamp + base64.b64encode(random_bytes).decode()).encode()).hexdigest()[:16]
    
    def _start_decoy_traffic(self):
        """Start decoy traffic generation"""
        try:
            concurrent_sessions = self.config.get("decoy_traffic", {}).get("concurrent_sessions", 3)
            
            for i in range(concurrent_sessions):
                thread = threading.Thread(
                    target=self._decoy_traffic_worker,
                    name=f"DecoyTraffic-{i+1}",
                    daemon=True
                )
                thread.start()
                self.decoy_threads.append(thread)
                
            logger.info(f"Started {concurrent_sessions} decoy traffic threads")
            
        except Exception as e:
            logger.error(f"Failed to start decoy traffic: {e}")
    
    def _stop_decoy_traffic(self):
        """Stop all decoy traffic generation"""
        try:
            # Signal threads to stop (they check protection_active)
            for thread in self.decoy_threads:
                if thread.is_alive():
                    thread.join(timeout=5.0)
                    
            self.decoy_threads.clear()
            logger.info("Stopped decoy traffic generation")
            
        except Exception as e:
            logger.error(f"Failed to stop decoy traffic: {e}")
    
    def _decoy_traffic_worker(self):
        """Worker thread for generating decoy traffic"""
        try:
            session = requests.Session()
            
            # Configure session for decoy traffic
            session.headers.update({
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            while self.protection_active:
                try:
                    # Select random decoy profile
                    profile = random.choice(self.decoy_generator.profiles)
                    
                    # Generate decoy request
                    target_domain = random.choice(profile.target_domains)
                    request_pattern = random.choice(profile.request_patterns)
                    
                    # Build decoy URL
                    url = self._build_decoy_url(target_domain, request_pattern)
                    
                    # Calculate timing for this request
                    timing = profile.timing_profile
                    delay = random.uniform(timing["min_interval"], timing["max_interval"])
                    
                    # Execute decoy request
                    try:
                        response = session.get(url, timeout=30, verify=False)
                        self.stats["decoy_sessions"] += 1
                        logger.debug(f"Decoy request: {url} -> {response.status_code}")
                        
                    except requests.RequestException as e:
                        logger.debug(f"Decoy request failed (expected): {e}")
                    
                    # Wait before next request
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.debug(f"Decoy worker error: {e}")
                    time.sleep(60)  # Back off on errors
                    
        except Exception as e:
            logger.error(f"Decoy traffic worker fatal error: {e}")
    
    def _build_decoy_url(self, domain: str, pattern: str) -> str:
        """Build realistic decoy URL based on domain and pattern"""
        schemes = ["https://", "http://"]
        scheme = random.choice(schemes)
        
        paths = {
            "search": ["/search?q=", "/s?q=", "/query?search="],
            "browse": ["/", "/home", "/index", "/main"],
            "read": ["/article/", "/post/", "/page/", "/docs/"],
            "timeline": ["/", "/home", "/feed", "/timeline"],
            "posts": ["/posts", "/articles", "/news"],
            "comments": ["/comments", "/discussions", "/forum"],
            "repos": ["/repositories", "/projects", "/code"],
            "commits": ["/commits", "/changes", "/history"],
            "packages": ["/packages", "/libraries", "/modules"]
        }
        
        if pattern in paths:
            path = random.choice(paths[pattern])
        else:
            path = "/"
            
        # Add random parameters for search patterns
        if "search" in pattern:
            queries = ["tutorial", "documentation", "guide", "example", "reference", "api"]
            path += random.choice(queries)
            
        return f"{scheme}{domain}{path}"
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for decoy traffic"""
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        return random.choice(user_agents)
    
    def _start_exit_node_rotation(self):
        """Start automatic exit node rotation"""
        def rotation_worker():
            while self.protection_active:
                try:
                    if self.exit_nodes:
                        # Rotate to a different exit node
                        current_node = random.choice(self.exit_nodes)
                        logger.debug(f"Rotating to exit node: {current_node['id']} ({current_node['country']})")
                        self.stats["exit_node_switches"] += 1
                        
                        # In a real implementation, this would reconfigure proxy settings
                        # self._configure_exit_node(current_node)
                        
                    # Wait for next rotation interval
                    interval = self.config.get("exit_node_rotation", {}).get("rotation_interval", 1800)
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Exit node rotation error: {e}")
                    time.sleep(300)  # Back off on errors
        
        thread = threading.Thread(target=rotation_worker, name="ExitNodeRotation", daemon=True)
        thread.start()
        logger.info("Started exit node rotation")
    
    def get_protection_status(self) -> Dict[str, Any]:
        """Get current protection status and statistics"""
        return {
            "protection_active": self.protection_active,
            "active_flows": len(self.active_flows),
            "decoy_threads": len([t for t in self.decoy_threads if t.is_alive()]),
            "exit_nodes_available": len(self.exit_nodes),
            "statistics": self.stats.copy(),
            "configuration": {
                "timing_obfuscation": self.config.get("timing_obfuscation", {}).get("enabled", False),
                "traffic_padding": self.config.get("traffic_padding", {}).get("enabled", False),
                "decoy_traffic": self.config.get("decoy_traffic", {}).get("enabled", False),
                "exit_node_rotation": self.config.get("exit_node_rotation", {}).get("enabled", False)
            }
        }
    
    def emergency_stop(self) -> bool:
        """Emergency stop all traffic analysis protection"""
        try:
            logger.warning("EMERGENCY STOP: Shutting down traffic protection immediately")
            
            self.protection_active = False
            
            # Force stop all threads
            for thread in self.decoy_threads:
                if thread.is_alive():
                    # Note: Python doesn't have thread.stop(), so we rely on daemon threads
                    pass
                    
            # Clear all state
            self.active_flows.clear()
            self.decoy_threads.clear()
            
            # Reset statistics
            self.stats = {
                "flows_protected": 0,
                "decoy_sessions": 0, 
                "bytes_padded": 0,
                "timing_obfuscations": 0,
                "exit_node_switches": 0
            }
            
            logger.info("Emergency stop completed")
            return True
            
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            return False


class TimingAnalyzer:
    """Analyzes and obfuscates network timing patterns"""
    
    def __init__(self):
        self.active = False
        self.request_history = []
        self.timing_profiles = {
            "stealth": {"min_delay": 0.5, "max_delay": 3.0, "jitter": 0.4},
            "balanced": {"min_delay": 0.1, "max_delay": 1.5, "jitter": 0.3},
            "aggressive": {"min_delay": 0.05, "max_delay": 0.5, "jitter": 0.2}
        }
        self.current_profile = "balanced"
    
    def start(self):
        """Start timing analysis and obfuscation"""
        self.active = True
        logger.info("Timing analyzer started")
    
    def stop(self):
        """Stop timing analysis"""
        self.active = False
        self.request_history.clear()
        logger.info("Timing analyzer stopped")
    
    def calculate_obfuscation_delay(self, flow: TrafficFlow) -> float:
        """Calculate timing delay to obfuscate traffic patterns"""
        if not self.active:
            return 0.0
            
        try:
            profile = self.timing_profiles[self.current_profile]
            
            # Base delay from profile
            base_delay = random.uniform(profile["min_delay"], profile["max_delay"])
            
            # Add jitter to prevent regularity
            jitter = random.uniform(-profile["jitter"], profile["jitter"])
            
            # Consider recent request history for burst protection
            recent_requests = [r for r in self.request_history 
                             if (datetime.now() - r).total_seconds() < 60]
            
            if len(recent_requests) > 5:  # Burst detected
                base_delay *= 1.5  # Increase delay during bursts
                
            delay = max(0.0, base_delay + jitter)
            
            # Record this request
            self.request_history.append(datetime.now())
            
            # Keep only recent history
            cutoff = datetime.now() - timedelta(minutes=5)
            self.request_history = [r for r in self.request_history if r > cutoff]
            
            return delay
            
        except Exception as e:
            logger.error(f"Failed to calculate timing delay: {e}")
            return 0.0


class TrafficPaddingEngine:
    """Handles traffic padding and size obfuscation"""
    
    def __init__(self):
        self.active = False
        self.padding_stats = {"requests_padded": 0, "bytes_added": 0}
    
    def start(self):
        """Start traffic padding engine"""
        self.active = True
        logger.info("Traffic padding engine started")
    
    def stop(self):
        """Stop traffic padding engine"""
        self.active = False
        logger.info("Traffic padding engine stopped")
    
    def pad_request_data(self, request_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Add padding to request data to obfuscate size patterns"""
        if not self.active:
            return {}
            
        try:
            padding_size = random.randint(64, 1024)
            padding_data = os.urandom(padding_size)
            
            # Add padding as custom header (will be ignored by most servers)
            padded_kwargs = {}
            if 'headers' not in request_kwargs:
                padded_kwargs['headers'] = {}
            else:
                padded_kwargs['headers'] = request_kwargs['headers'].copy()
                
            # Add padding header
            padded_kwargs['headers']['X-Padding'] = base64.b64encode(padding_data).decode()
            
            self.padding_stats["requests_padded"] += 1
            self.padding_stats["bytes_added"] += padding_size
            
            return padded_kwargs
            
        except Exception as e:
            logger.error(f"Failed to pad request data: {e}")
            return {}


class DecoyTrafficGenerator:
    """Generates realistic decoy traffic to mask real requests"""
    
    def __init__(self, decoy_configs: List[Dict[str, Any]]):
        self.profiles = []
        
        for config in decoy_configs:
            profile = DecoyProfile(
                name=config["name"],
                target_domains=config["target_domains"],
                request_patterns=config["request_patterns"],
                timing_profile=config["timing_profile"],
                volume_profile=config["volume_profile"],
                user_agents=config["user_agents"]
            )
            self.profiles.append(profile)
            
        logger.info(f"Initialized {len(self.profiles)} decoy traffic profiles")


def create_protected_session() -> requests.Session:
    """Create a requests session with traffic analysis protection"""
    # Initialize protection system
    protection = TrafficAnalysisProtection()
    
    # Create session
    session = requests.Session()
    
    # Wrap session methods with protection
    original_get = session.get
    original_post = session.post
    original_put = session.put
    original_delete = session.delete
    
    session.get = lambda *args, **kwargs: protection.protect_request(original_get, *args, **kwargs)
    session.post = lambda *args, **kwargs: protection.protect_request(original_post, *args, **kwargs)
    session.put = lambda *args, **kwargs: protection.protect_request(original_put, *args, **kwargs)
    session.delete = lambda *args, **kwargs: protection.protect_request(original_delete, *args, **kwargs)
    
    # Store protection instance for later access
    session._traffic_protection = protection
    
    return session


def main():
    """CLI interface for traffic analysis protection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Traffic Analysis Protection System")
    parser.add_argument('action', choices=['start', 'stop', 'status', 'emergency', 'test'], help='Action to perform')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--profile', '-p', choices=['stealth', 'balanced', 'aggressive'], default='balanced', help='Timing profile')
    parser.add_argument('--duration', '-d', type=int, default=300, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    # Initialize protection system
    protection = TrafficAnalysisProtection(args.config)
    
    try:
        if args.action == 'start':
            if protection.start_protection():
                print("✅ Traffic analysis protection started successfully")
                print(f"🔹 Active protection features:")
                status = protection.get_protection_status()
                config = status['configuration']
                for feature, enabled in config.items():
                    status_icon = "✅" if enabled else "❌"
                    print(f"   {status_icon} {feature.replace('_', ' ').title()}")
            else:
                print("❌ Failed to start traffic analysis protection")
                return 1
                
        elif args.action == 'stop':
            if protection.stop_protection():
                print("✅ Traffic analysis protection stopped successfully")
            else:
                print("❌ Failed to stop traffic analysis protection")
                return 1
                
        elif args.action == 'status':
            status = protection.get_protection_status()
            print(json.dumps(status, indent=2))
            
        elif args.action == 'emergency':
            if protection.emergency_stop():
                print("✅ Emergency stop completed successfully")
            else:
                print("⚠️ Emergency stop completed with warnings")
                
        elif args.action == 'test':
            print(f"🧪 Testing traffic protection for {args.duration} seconds...")
            
            # Start protection
            if not protection.start_protection():
                print("❌ Failed to start protection for testing")
                return 1
            
            try:
                # Create protected session
                session = create_protected_session()
                
                # Run test requests
                test_urls = [
                    "https://httpbin.org/get",
                    "https://httpbin.org/user-agent", 
                    "https://httpbin.org/headers",
                    "https://httpbin.org/ip"
                ]
                
                start_time = time.time()
                test_count = 0
                
                while (time.time() - start_time) < args.duration:
                    try:
                        url = random.choice(test_urls)
                        response = session.get(url, timeout=10)
                        test_count += 1
                        print(f"✅ Test request {test_count}: {url} -> {response.status_code}")
                        
                        # Wait before next test
                        time.sleep(random.uniform(5, 15))
                        
                    except Exception as e:
                        print(f"⚠️ Test request failed: {e}")
                        
                # Show final statistics
                final_status = protection.get_protection_status()
                print(f"\n📊 Test Results:")
                print(f"   Test requests: {test_count}")
                print(f"   Protected flows: {final_status['statistics']['flows_protected']}")
                print(f"   Decoy sessions: {final_status['statistics']['decoy_sessions']}")
                print(f"   Timing obfuscations: {final_status['statistics']['timing_obfuscations']}")
                
            finally:
                protection.stop_protection()
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        protection.emergency_stop()
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        protection.emergency_stop()
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())