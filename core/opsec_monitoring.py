#!/usr/bin/env python3
"""
Operational Security Monitoring System
=====================================

This module provides comprehensive OPSEC monitoring to detect potential security
failures, attribution risks, and operational compromises. It includes real-time
monitoring, automated alerts, and emergency shutdown procedures.

Features:
- IP leak detection and monitoring
- DNS leak detection
- Timing correlation analysis
- Behavioral pattern detection
- Network traffic analysis
- Process and system monitoring
- Automated emergency responses
- Real-time alerting system
- OPSEC violation logging
"""

import os
import sys
import json
import time
import socket
import psutil
import threading
import subprocess
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import queue
import hashlib
import requests
import dns.resolver
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class OpsecAlert:
    """Represents an OPSEC security alert"""
    alert_id: str
    severity: str  # critical, high, medium, low
    category: str  # ip_leak, dns_leak, timing, behavioral, network, system
    title: str
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    action_taken: Optional[str] = None


@dataclass
class NetworkSnapshot:
    """Represents a network state snapshot"""
    timestamp: datetime
    external_ip: str
    dns_servers: List[str]
    active_connections: List[Dict[str, Any]]
    routing_table: List[Dict[str, Any]]
    interfaces: Dict[str, Any]


@dataclass
class ProcessSnapshot:
    """Represents a process state snapshot"""
    timestamp: datetime
    running_processes: List[Dict[str, Any]]
    network_processes: List[Dict[str, Any]]
    suspicious_processes: List[Dict[str, Any]]


class OpsecMonitor:
    """Advanced operational security monitoring system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize OPSEC monitoring system"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'configs', 'opsec.json')
        self.config = self._load_config()
        
        # Core components
        self.alerts: List[OpsecAlert] = []
        self.alert_queue = queue.Queue()
        self.monitoring_active = False
        self.emergency_shutdown_triggered = False
        
        # Monitoring threads
        self.monitoring_threads: List[threading.Thread] = []
        self.shutdown_event = threading.Event()
        
        # State tracking
        self.baseline_state = None
        self.network_history: List[NetworkSnapshot] = []
        self.process_history: List[ProcessSnapshot] = []
        
        # Alert handlers
        self.alert_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "alerts_generated": 0,
            "critical_alerts": 0,
            "emergency_shutdowns": 0,
            "monitoring_uptime": 0,
            "last_check": None
        }
        
        # Initialize monitoring
        self._initialize_monitoring()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load OPSEC monitoring configuration"""
        default_config = {
            "monitoring": {
                "enabled": True,
                "check_interval": 30,  # seconds
                "baseline_samples": 5,
                "alert_threshold": 3
            },
            "ip_monitoring": {
                "enabled": True,
                "check_services": [
                    "https://api.ipify.org",
                    "https://icanhazip.com",
                    "https://ifconfig.me/ip"
                ],
                "expected_ranges": ["10.0.0.0/8"],  # Tor exit ranges
                "leak_tolerance": 0
            },
            "dns_monitoring": {
                "enabled": True,
                "expected_dns": ["127.0.0.1"],  # Tor DNS
                "leak_domains": ["google.com", "cloudflare.com"],
                "check_interval": 60
            },
            "timing_analysis": {
                "enabled": True,
                "correlation_threshold": 0.8,
                "pattern_window": 300,  # seconds
                "request_spacing_variance": 0.3
            },
            "behavioral_analysis": {
                "enabled": True,
                "user_agent_consistency": True,
                "request_pattern_analysis": True,
                "session_fingerprinting": True
            },
            "network_monitoring": {
                "enabled": True,
                "suspicious_ports": [22, 23, 3389, 5900],
                "connection_limits": {"per_host": 10, "total": 100},
                "bandwidth_monitoring": True
            },
            "process_monitoring": {
                "enabled": True,
                "whitelist": ["python", "tor", "proxychains"],
                "suspicious_keywords": ["keylog", "screen", "capture"],
                "memory_threshold": 1000000000  # 1GB
            },
            "emergency_response": {
                "enabled": True,
                "auto_shutdown": True,
                "network_kill": True,
                "process_termination": True,
                "file_cleanup": True
            },
            "alerting": {
                "log_alerts": True,
                "console_alerts": True,
                "file_alerts": True,
                "alert_file": "opsec_alerts.log"
            }
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
    
    def _initialize_monitoring(self):
        """Initialize monitoring components"""
        logger.info("Initializing OPSEC monitoring system...")
        
        # Set up alert handlers
        self._setup_alert_handlers()
        
        # Create baseline state
        self._create_baseline()
        
        # Set up signal handlers for emergency shutdown
        signal.signal(signal.SIGTERM, self._emergency_signal_handler)
        signal.signal(signal.SIGINT, self._emergency_signal_handler)
        
        logger.info("OPSEC monitoring system initialized")
    
    def _setup_alert_handlers(self):
        """Set up alert handling mechanisms"""
        self.alert_handlers = {
            "critical": self._handle_critical_alert,
            "high": self._handle_high_alert,
            "medium": self._handle_medium_alert,
            "low": self._handle_low_alert
        }
    
    def _create_baseline(self):
        """Create baseline security state"""
        logger.info("Creating OPSEC baseline state...")
        
        try:
            # Network baseline
            network_state = self._capture_network_state()
            self.network_history.append(network_state)
            
            # Process baseline
            process_state = self._capture_process_state()
            self.process_history.append(process_state)
            
            self.baseline_state = {
                "network": network_state,
                "processes": process_state,
                "timestamp": datetime.now()
            }
            
            logger.info("Baseline state created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create baseline state: {e}")
    
    def _capture_network_state(self) -> NetworkSnapshot:
        """Capture current network state"""
        try:
            # Get external IP
            external_ip = self._get_external_ip()
            
            # Get DNS servers
            dns_servers = self._get_dns_servers()
            
            # Get active connections
            connections = []
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "pid": conn.pid,
                        "status": conn.status
                    })
            
            # Get routing information
            routing = []
            try:
                result = subprocess.run(['netstat', '-rn'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    routing = [{"route_info": result.stdout}]
            except:
                pass
            
            # Get network interfaces
            interfaces = {}
            for interface, addrs in psutil.net_if_addrs().items():
                interfaces[interface] = [
                    {"family": addr.family, "address": addr.address, "netmask": addr.netmask}
                    for addr in addrs
                ]
            
            return NetworkSnapshot(
                timestamp=datetime.now(),
                external_ip=external_ip,
                dns_servers=dns_servers,
                active_connections=connections,
                routing_table=routing,
                interfaces=interfaces
            )
            
        except Exception as e:
            logger.error(f"Failed to capture network state: {e}")
            return NetworkSnapshot(
                timestamp=datetime.now(),
                external_ip="unknown",
                dns_servers=[],
                active_connections=[],
                routing_table=[],
                interfaces={}
            )
    
    def _capture_process_state(self) -> ProcessSnapshot:
        """Capture current process state"""
        try:
            running_processes = []
            network_processes = []
            suspicious_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'connections']):
                try:
                    proc_info = {
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else "",
                        "memory": proc.info['memory_info'].rss if proc.info['memory_info'] else 0
                    }
                    
                    running_processes.append(proc_info)
                    
                    # Check for network processes
                    if proc.info['connections']:
                        network_processes.append(proc_info)
                    
                    # Check for suspicious processes
                    if self._is_suspicious_process(proc_info):
                        suspicious_processes.append(proc_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ProcessSnapshot(
                timestamp=datetime.now(),
                running_processes=running_processes,
                network_processes=network_processes,
                suspicious_processes=suspicious_processes
            )
            
        except Exception as e:
            logger.error(f"Failed to capture process state: {e}")
            return ProcessSnapshot(
                timestamp=datetime.now(),
                running_processes=[],
                network_processes=[],
                suspicious_processes=[]
            )
    
    def _get_external_ip(self) -> str:
        """Get external IP address"""
        ip_services = self.config['ip_monitoring']['check_services']
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # Validate IP format
                    ipaddress.ip_address(ip)
                    return ip
            except Exception as e:
                logger.debug(f"Failed to get IP from {service}: {e}")
                continue
        
        return "unknown"
    
    def _get_dns_servers(self) -> List[str]:
        """Get current DNS servers"""
        dns_servers = []
        
        try:
            # Try to get from system resolver
            resolver = dns.resolver.Resolver()
            dns_servers = [str(ns) for ns in resolver.nameservers]
        except:
            pass
        
        # Fallback to reading resolv.conf on Unix systems
        if not dns_servers and os.path.exists('/etc/resolv.conf'):
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            parts = line.strip().split()
                            if len(parts) > 1:
                                dns_servers.append(parts[1])
            except:
                pass
        
        return dns_servers
    
    def _is_suspicious_process(self, proc_info: Dict[str, Any]) -> bool:
        """Check if process is suspicious"""
        suspicious_keywords = self.config['process_monitoring']['suspicious_keywords']
        memory_threshold = self.config['process_monitoring']['memory_threshold']
        
        # Check for suspicious keywords in command line
        cmdline = proc_info.get('cmdline', '').lower()
        for keyword in suspicious_keywords:
            if keyword.lower() in cmdline:
                return True
        
        # Check memory usage
        if proc_info.get('memory', 0) > memory_threshold:
            return True
        
        return False
    
    def start_monitoring(self):
        """Start OPSEC monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        logger.info("Starting OPSEC monitoring...")
        self.monitoring_active = True
        self.shutdown_event.clear()
        
        # Start monitoring threads
        if self.config['ip_monitoring']['enabled']:
            thread = threading.Thread(target=self._monitor_ip_leaks, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
        
        if self.config['dns_monitoring']['enabled']:
            thread = threading.Thread(target=self._monitor_dns_leaks, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
        
        if self.config['network_monitoring']['enabled']:
            thread = threading.Thread(target=self._monitor_network, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
        
        if self.config['process_monitoring']['enabled']:
            thread = threading.Thread(target=self._monitor_processes, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
        
        if self.config['timing_analysis']['enabled']:
            thread = threading.Thread(target=self._monitor_timing, daemon=True)
            thread.start()
            self.monitoring_threads.append(thread)
        
        # Start alert processing thread
        thread = threading.Thread(target=self._process_alerts, daemon=True)
        thread.start()
        self.monitoring_threads.append(thread)
        
        logger.info(f"Started {len(self.monitoring_threads)} monitoring threads")
    
    def stop_monitoring(self):
        """Stop OPSEC monitoring"""
        if not self.monitoring_active:
            return
        
        logger.info("Stopping OPSEC monitoring...")
        self.monitoring_active = False
        self.shutdown_event.set()
        
        # Wait for threads to finish
        for thread in self.monitoring_threads:
            thread.join(timeout=5)
        
        self.monitoring_threads.clear()
        logger.info("OPSEC monitoring stopped")
    
    def _monitor_ip_leaks(self):
        """Monitor for IP address leaks"""
        logger.info("Starting IP leak monitoring")
        check_interval = self.config['monitoring']['check_interval']
        
        while self.monitoring_active and not self.shutdown_event.wait(check_interval):
            try:
                current_ip = self._get_external_ip()
                
                if current_ip == "unknown":
                    continue
                
                # Check if IP is in expected ranges
                expected_ranges = self.config['ip_monitoring']['expected_ranges']
                ip_in_expected_range = False
                
                for range_str in expected_ranges:
                    try:
                        network = ipaddress.ip_network(range_str)
                        if ipaddress.ip_address(current_ip) in network:
                            ip_in_expected_range = True
                            break
                    except:
                        continue
                
                # Generate alert if IP leak detected
                if not ip_in_expected_range:
                    alert = OpsecAlert(
                        alert_id=f"ip_leak_{int(time.time())}",
                        severity="critical",
                        category="ip_leak",
                        title="IP Address Leak Detected",
                        description=f"Real IP address exposed: {current_ip}",
                        evidence={"leaked_ip": current_ip, "expected_ranges": expected_ranges}
                    )
                    self._generate_alert(alert)
                
            except Exception as e:
                logger.error(f"IP monitoring error: {e}")
    
    def _monitor_dns_leaks(self):
        """Monitor for DNS leaks"""
        logger.info("Starting DNS leak monitoring")
        check_interval = self.config['dns_monitoring']['check_interval']
        
        while self.monitoring_active and not self.shutdown_event.wait(check_interval):
            try:
                current_dns = self._get_dns_servers()
                expected_dns = self.config['dns_monitoring']['expected_dns']
                
                # Check for unexpected DNS servers
                leaked_dns = [dns for dns in current_dns if dns not in expected_dns]
                
                if leaked_dns:
                    alert = OpsecAlert(
                        alert_id=f"dns_leak_{int(time.time())}",
                        severity="high",
                        category="dns_leak",
                        title="DNS Leak Detected",
                        description=f"Unexpected DNS servers: {', '.join(leaked_dns)}",
                        evidence={"leaked_dns": leaked_dns, "expected_dns": expected_dns}
                    )
                    self._generate_alert(alert)
                
                # Test with leak domains
                leak_domains = self.config['dns_monitoring']['leak_domains']
                for domain in leak_domains:
                    try:
                        resolver = dns.resolver.Resolver()
                        answers = resolver.resolve(domain, 'A')
                        # Check if resolution went through expected DNS
                        if str(resolver.nameservers[0]) not in expected_dns:
                            alert = OpsecAlert(
                                alert_id=f"dns_resolution_leak_{int(time.time())}",
                                severity="medium",
                                category="dns_leak",
                                title="DNS Resolution Leak",
                                description=f"DNS query for {domain} leaked through {resolver.nameservers[0]}",
                                evidence={"domain": domain, "resolver": str(resolver.nameservers[0])}
                            )
                            self._generate_alert(alert)
                    except:
                        continue
                
            except Exception as e:
                logger.error(f"DNS monitoring error: {e}")
    
    def _monitor_network(self):
        """Monitor network activity"""
        logger.info("Starting network monitoring")
        check_interval = self.config['monitoring']['check_interval']
        
        while self.monitoring_active and not self.shutdown_event.wait(check_interval):
            try:
                network_state = self._capture_network_state()
                self.network_history.append(network_state)
                
                # Keep only recent history
                if len(self.network_history) > 100:
                    self.network_history = self.network_history[-50:]
                
                # Analyze for suspicious connections
                suspicious_ports = self.config['network_monitoring']['suspicious_ports']
                
                for conn in network_state.active_connections:
                    if conn['remote_addr']:
                        remote_port = int(conn['remote_addr'].split(':')[-1])
                        if remote_port in suspicious_ports:
                            alert = OpsecAlert(
                                alert_id=f"suspicious_connection_{int(time.time())}",
                                severity="medium",
                                category="network",
                                title="Suspicious Network Connection",
                                description=f"Connection to suspicious port {remote_port}: {conn['remote_addr']}",
                                evidence={"connection": conn}
                            )
                            self._generate_alert(alert)
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
    
    def _monitor_processes(self):
        """Monitor running processes"""
        logger.info("Starting process monitoring")
        check_interval = self.config['monitoring']['check_interval']
        
        while self.monitoring_active and not self.shutdown_event.wait(check_interval):
            try:
                process_state = self._capture_process_state()
                self.process_history.append(process_state)
                
                # Keep only recent history
                if len(self.process_history) > 100:
                    self.process_history = self.process_history[-50:]
                
                # Alert on suspicious processes
                for proc in process_state.suspicious_processes:
                    alert = OpsecAlert(
                        alert_id=f"suspicious_process_{proc['pid']}_{int(time.time())}",
                        severity="high",
                        category="system",
                        title="Suspicious Process Detected",
                        description=f"Process {proc['name']} (PID {proc['pid']}) flagged as suspicious",
                        evidence={"process": proc}
                    )
                    self._generate_alert(alert)
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
    
    def _monitor_timing(self):
        """Monitor for timing correlation attacks"""
        logger.info("Starting timing analysis monitoring")
        # This is a placeholder for timing analysis
        # In a real implementation, this would analyze request patterns
        pass
    
    def _process_alerts(self):
        """Process generated alerts"""
        logger.info("Starting alert processing")
        
        while self.monitoring_active and not self.shutdown_event.is_set():
            try:
                alert = self.alert_queue.get(timeout=1)
                self._handle_alert(alert)
                self.alert_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Alert processing error: {e}")
    
    def _generate_alert(self, alert: OpsecAlert):
        """Generate and queue an OPSEC alert"""
        self.alerts.append(alert)
        self.alert_queue.put(alert)
        self.stats["alerts_generated"] += 1
        
        if alert.severity == "critical":
            self.stats["critical_alerts"] += 1
    
    def _handle_alert(self, alert: OpsecAlert):
        """Handle an OPSEC alert"""
        logger.warning(f"OPSEC Alert [{alert.severity.upper()}]: {alert.title}")
        
        # Log to file if enabled
        if self.config['alerting']['log_alerts']:
            self._log_alert(alert)
        
        # Handle based on severity
        handler = self.alert_handlers.get(alert.severity)
        if handler:
            handler(alert)
    
    def _handle_critical_alert(self, alert: OpsecAlert):
        """Handle critical OPSEC alerts"""
        logger.critical(f"CRITICAL OPSEC VIOLATION: {alert.title}")
        
        if self.config['emergency_response']['auto_shutdown']:
            self._trigger_emergency_shutdown(f"Critical alert: {alert.title}")
    
    def _handle_high_alert(self, alert: OpsecAlert):
        """Handle high severity alerts"""
        logger.error(f"HIGH PRIORITY OPSEC ALERT: {alert.title}")
        # Could implement specific responses here
    
    def _handle_medium_alert(self, alert: OpsecAlert):
        """Handle medium severity alerts"""
        logger.warning(f"OPSEC WARNING: {alert.title}")
    
    def _handle_low_alert(self, alert: OpsecAlert):
        """Handle low severity alerts"""
        logger.info(f"OPSEC Notice: {alert.title}")
    
    def _log_alert(self, alert: OpsecAlert):
        """Log alert to file"""
        try:
            log_file = self.config['alerting']['alert_file']
            log_entry = {
                "timestamp": alert.timestamp.isoformat(),
                "alert_id": alert.alert_id,
                "severity": alert.severity,
                "category": alert.category,
                "title": alert.title,
                "description": alert.description,
                "evidence": alert.evidence
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def _trigger_emergency_shutdown(self, reason: str):
        """Trigger emergency shutdown procedures"""
        if self.emergency_shutdown_triggered:
            return
        
        logger.critical(f"TRIGGERING EMERGENCY SHUTDOWN: {reason}")
        self.emergency_shutdown_triggered = True
        self.stats["emergency_shutdowns"] += 1
        
        try:
            # Network kill switch
            if self.config['emergency_response']['network_kill']:
                self._kill_network()
            
            # Terminate suspicious processes
            if self.config['emergency_response']['process_termination']:
                self._terminate_processes()
            
            # File cleanup
            if self.config['emergency_response']['file_cleanup']:
                self._emergency_cleanup()
                
        except Exception as e:
            logger.error(f"Emergency shutdown error: {e}")
        
        # Stop monitoring
        self.stop_monitoring()
    
    def _kill_network(self):
        """Kill network connections"""
        try:
            # Kill Tor process
            subprocess.run(['pkill', '-f', 'tor'], timeout=10)
            
            # Kill proxy processes  
            subprocess.run(['pkill', '-f', 'proxychains'], timeout=10)
            
            logger.info("Network connections terminated")
            
        except Exception as e:
            logger.error(f"Failed to kill network: {e}")
    
    def _terminate_processes(self):
        """Terminate suspicious processes"""
        try:
            if self.process_history:
                latest_state = self.process_history[-1]
                for proc in latest_state.suspicious_processes:
                    try:
                        psutil.Process(proc['pid']).terminate()
                        logger.info(f"Terminated suspicious process {proc['name']} (PID {proc['pid']})")
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to terminate processes: {e}")
    
    def _emergency_cleanup(self):
        """Perform emergency file cleanup"""
        try:
            # Clean temp directories
            temp_patterns = ['/tmp/anon_*', '/tmp/toolkit_*', '/var/tmp/toolkit_*']
            for pattern in temp_patterns:
                subprocess.run(['rm', '-rf'] + [pattern], timeout=30)
            
            logger.info("Emergency cleanup completed")
            
        except Exception as e:
            logger.error(f"Emergency cleanup error: {e}")
    
    def _emergency_signal_handler(self, signum, frame):
        """Handle emergency shutdown signals"""
        logger.critical(f"Received signal {signum}, triggering emergency shutdown")
        self._trigger_emergency_shutdown(f"Signal {signum}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OPSEC monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "emergency_shutdown": self.emergency_shutdown_triggered,
            "active_threads": len(self.monitoring_threads),
            "total_alerts": len(self.alerts),
            "recent_alerts": len([a for a in self.alerts if (datetime.now() - a.timestamp).seconds < 3600]),
            "statistics": self.stats,
            "network_snapshots": len(self.network_history),
            "process_snapshots": len(self.process_history)
        }
    
    def get_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[OpsecAlert]:
        """Get recent alerts"""
        alerts = self.alerts[-limit:]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
    
    def cleanup(self):
        """Cleanup monitoring resources"""
        self.stop_monitoring()
        
        # Clear temp directory if exists
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except:
                pass
        
        logger.info("OPSEC monitoring cleanup completed")


def main():
    """Main function for testing"""
    print("🔒 OPSEC Monitoring System Test")
    print("=" * 50)
    
    try:
        monitor = OpsecMonitor()
        
        print("✅ OPSEC Monitor initialized")
        print(f"📊 Status: {monitor.get_status()}")
        
        # Test monitoring for a short period
        print("\n🔄 Starting monitoring test (10 seconds)...")
        monitor.start_monitoring()
        
        time.sleep(10)
        
        print("⏹️  Stopping monitoring...")
        monitor.stop_monitoring()
        
        print(f"📊 Final status: {monitor.get_status()}")
        print(f"🚨 Alerts generated: {len(monitor.get_alerts())}")
        
        monitor.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Monitoring failed: {e}")


if __name__ == "__main__":
    main()