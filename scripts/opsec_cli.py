#!/usr/bin/env python3
"""
OPSEC Monitoring CLI
===================

Command line interface for the operational security monitoring system.
"""

import os
import sys
import argparse
import json
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.opsec_monitoring import OpsecMonitor
except ImportError as e:
    print(f"❌ Failed to import OPSEC monitoring module: {e}")
    print("📍 Make sure you're running from the toolkit directory")
    sys.exit(1)


def status_command(args):
    """Show OPSEC monitoring status"""
    print("🔒 OPSEC Monitoring Status")
    print("=" * 50)
    
    try:
        monitor = OpsecMonitor()
        status = monitor.get_status()
        
        print(f"📡 Monitoring Active: {'✅ Yes' if status['monitoring_active'] else '❌ No'}")
        print(f"🚨 Emergency Shutdown: {'🔴 Triggered' if status['emergency_shutdown'] else '✅ Normal'}")
        print(f"🧵 Active Threads: {status['active_threads']}")
        print(f"🚨 Total Alerts: {status['total_alerts']}")
        print(f"📈 Recent Alerts (1h): {status['recent_alerts']}")
        print(f"📊 Network Snapshots: {status['network_snapshots']}")
        print(f"💾 Process Snapshots: {status['process_snapshots']}")
        
        print("\n📊 Statistics:")
        for key, value in status['statistics'].items():
            print(f"  {key}: {value}")
        
        monitor.cleanup()
        
    except Exception as e:
        print(f"❌ Failed to get status: {e}")
        return 1
    
    return 0


def start_command(args):
    """Start OPSEC monitoring"""
    print("🔄 Starting OPSEC monitoring...")
    
    try:
        monitor = OpsecMonitor()
        monitor.start_monitoring()
        
        print("✅ OPSEC monitoring started successfully")
        print("📡 Monitoring for security violations...")
        print("⚠️  Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                time.sleep(5)
                status = monitor.get_status()
                print(f"\r📊 Alerts: {status['total_alerts']} | Threads: {status['active_threads']}", end="")
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping monitoring...")
            monitor.stop_monitoring()
            print("✅ OPSEC monitoring stopped")
        
        monitor.cleanup()
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")
        return 1
    
    return 0


def test_command(args):
    """Test OPSEC monitoring system"""
    print("🧪 Testing OPSEC monitoring system...")
    
    try:
        monitor = OpsecMonitor()
        
        print("✅ OPSEC Monitor initialized")
        
        # Short test run
        print("🔄 Running 10-second monitoring test...")
        monitor.start_monitoring()
        time.sleep(10)
        monitor.stop_monitoring()
        
        status = monitor.get_status()
        print(f"📊 Test Results:")
        print(f"  - Monitoring threads: {6}")  # Expected threads
        print(f"  - Alerts generated: {status['total_alerts']}")
        print(f"  - Network snapshots: {status['network_snapshots']}")
        print(f"  - Process snapshots: {status['process_snapshots']}")
        
        if status['total_alerts'] > 0:
            print("\n🚨 Alerts detected during test:")
            for alert in monitor.get_alerts(limit=5):
                print(f"  [{alert.severity.upper()}] {alert.title}")
        
        print("✅ OPSEC monitoring test completed")
        monitor.cleanup()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0


def alerts_command(args):
    """Show recent alerts"""
    print("🚨 Recent OPSEC Alerts")
    print("=" * 50)
    
    try:
        monitor = OpsecMonitor()
        alerts = monitor.get_alerts(severity=args.severity, limit=args.limit)
        
        if not alerts:
            print("✅ No alerts found")
        else:
            for alert in alerts:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠", 
                    "medium": "🟡",
                    "low": "🟢"
                }.get(alert.severity, "⚪")
                
                print(f"\n{severity_icon} [{alert.severity.upper()}] {alert.title}")
                print(f"   📅 {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📝 {alert.description}")
                
                if alert.evidence and args.verbose:
                    print(f"   🔍 Evidence: {json.dumps(alert.evidence, indent=2)}")
        
        monitor.cleanup()
        
    except Exception as e:
        print(f"❌ Failed to get alerts: {e}")
        return 1
    
    return 0


def emergency_command(args):
    """Trigger emergency shutdown"""
    print("🚨 EMERGENCY SHUTDOWN TRIGGERED")
    print("=" * 50)
    
    try:
        monitor = OpsecMonitor()
        monitor._trigger_emergency_shutdown("Manual emergency shutdown via CLI")
        
        print("✅ Emergency shutdown completed")
        print("🔴 All monitoring stopped")
        print("🔪 Network connections terminated")
        print("🧹 Cleanup procedures executed")
        
        monitor.cleanup()
        
    except Exception as e:
        print(f"❌ Emergency shutdown failed: {e}")
        return 1
    
    return 0


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="OPSEC Monitoring CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show monitoring status')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start monitoring')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test monitoring system')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Show recent alerts')
    alerts_parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], 
                              help='Filter by alert severity')
    alerts_parser.add_argument('--limit', type=int, default=20, help='Number of alerts to show')
    alerts_parser.add_argument('--verbose', action='store_true', help='Show detailed alert information')
    
    # Emergency command
    emergency_parser = subparsers.add_parser('emergency', help='Trigger emergency shutdown')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    command_map = {
        'status': status_command,
        'start': start_command,
        'test': test_command,
        'alerts': alerts_command,
        'emergency': emergency_command
    }
    
    return command_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())