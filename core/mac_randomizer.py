#!/usr/bin/env python3
"""
MAC Address Randomization and Network Interface Management
Provides automated MAC address changing for enhanced anonymity
"""

import os
import sys
import re
import random
import subprocess
import platform
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    original_mac: str
    current_mac: str
    interface_type: str  # wifi, ethernet, virtual, etc.
    status: str  # up, down
    vendor: str  # OUI vendor info
    
@dataclass
class MACChangeRecord:
    """Record of MAC address changes"""
    timestamp: datetime
    interface: str
    old_mac: str
    new_mac: str
    success: bool
    method: str  # macchanger, ifconfig, networksetup, etc.

class MACRandomizer:
    """Cross-platform MAC address randomization system"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.interfaces: Dict[str, NetworkInterface] = {}
        self.change_history: List[MACChangeRecord] = []
        self.backup_file = "mac_backup.json"
        
        # Common vendor OUIs for realistic MAC addresses
        self.common_vendors = {
            "Apple": ["00:03:93", "00:0d:93", "00:17:f2", "28:cf:da", "40:6c:8f"],
            "Dell": ["00:14:22", "00:1e:c9", "00:21:70", "00:25:64", "d4:ae:52"],
            "Intel": ["00:02:b3", "00:0e:0c", "00:13:02", "00:15:00", "ac:72:89"],
            "Samsung": ["00:0d:e5", "00:12:fb", "00:15:b9", "00:1f:e2", "38:aa:3c"],
            "Broadcom": ["00:10:18", "00:90:4c", "00:17:10", "b8:ae:ed", "00:26:37"],
            "Realtek": ["00:e0:4c", "00:0e:2e", "52:54:00", "00:21:91", "1c:39:47"]
        }
        
        self.discover_interfaces()
    
    def discover_interfaces(self):
        """Discover all network interfaces on the system"""
        print("[+] Discovering network interfaces...")
        
        if self.platform == "darwin":  # macOS
            self._discover_interfaces_macos()
        elif self.platform == "linux":
            self._discover_interfaces_linux()
        elif self.platform == "windows":
            self._discover_interfaces_windows()
        else:
            print(f"[!] Platform {self.platform} not fully supported")
    
    def _discover_interfaces_macos(self):
        """Discover interfaces on macOS"""
        try:
            # Get interface list
            result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                  capture_output=True, text=True)
            
            current_port = None
            current_device = None
            
            for line in result.stdout.split('\n'):
                if line.startswith('Hardware Port:'):
                    current_port = line.split(':', 1)[1].strip()
                elif line.startswith('Device:') and current_port:
                    current_device = line.split(':', 1)[1].strip()
                    
                    if current_device and current_device != "(null)":
                        # Get MAC address
                        mac_result = subprocess.run(['ifconfig', current_device], 
                                                  capture_output=True, text=True)
                        
                        mac_match = re.search(r'ether ([0-9a-f:]{17})', mac_result.stdout)
                        if mac_match:
                            mac_addr = mac_match.group(1)
                            
                            interface = NetworkInterface(
                                name=current_device,
                                original_mac=mac_addr,
                                current_mac=mac_addr,
                                interface_type=self._classify_interface_type(current_port),
                                status="up" if "UP" in mac_result.stdout else "down",
                                vendor=self._get_vendor_from_mac(mac_addr)
                            )
                            
                            self.interfaces[current_device] = interface
                            print(f"[+] Found interface: {current_device} ({mac_addr}) - {current_port}")
                    
                    current_port = None
                    current_device = None
                    
        except Exception as e:
            print(f"[!] Error discovering macOS interfaces: {e}")
    
    def _discover_interfaces_linux(self):
        """Discover interfaces on Linux"""
        try:
            # Read from /proc/net/dev
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip header lines
            
            for line in lines:
                interface_name = line.split(':')[0].strip()
                
                if interface_name in ['lo']:  # Skip loopback
                    continue
                
                # Get interface details
                try:
                    result = subprocess.run(['ip', 'link', 'show', interface_name], 
                                          capture_output=True, text=True)
                    
                    mac_match = re.search(r'link/ether ([0-9a-f:]{17})', result.stdout)
                    if mac_match:
                        mac_addr = mac_match.group(1)
                        
                        interface = NetworkInterface(
                            name=interface_name,
                            original_mac=mac_addr,
                            current_mac=mac_addr,
                            interface_type=self._classify_interface_type(interface_name),
                            status="up" if "UP" in result.stdout else "down",
                            vendor=self._get_vendor_from_mac(mac_addr)
                        )
                        
                        self.interfaces[interface_name] = interface
                        print(f"[+] Found interface: {interface_name} ({mac_addr})")
                        
                except Exception as e:
                    print(f"[!] Error getting details for {interface_name}: {e}")
                    
        except Exception as e:
            print(f"[!] Error discovering Linux interfaces: {e}")
    
    def _discover_interfaces_windows(self):
        """Discover interfaces on Windows"""
        try:
            result = subprocess.run(['getmac', '/fo', 'csv', '/nh'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = [p.strip('"') for p in line.split('","')]
                    if len(parts) >= 2:
                        interface_name = parts[0]
                        mac_addr = parts[1].replace('-', ':').lower()
                        
                        if mac_addr != "n/a" and interface_name != "N/A":
                            interface = NetworkInterface(
                                name=interface_name,
                                original_mac=mac_addr,
                                current_mac=mac_addr,
                                interface_type=self._classify_interface_type(interface_name),
                                status="up",  # Assume up if listed
                                vendor=self._get_vendor_from_mac(mac_addr)
                            )
                            
                            self.interfaces[interface_name] = interface
                            print(f"[+] Found interface: {interface_name} ({mac_addr})")
                            
        except Exception as e:
            print(f"[!] Error discovering Windows interfaces: {e}")
    
    def _classify_interface_type(self, name_or_port: str) -> str:
        """Classify interface type based on name"""
        name_lower = name_or_port.lower()
        
        if any(wifi in name_lower for wifi in ['wi-fi', 'wireless', 'wlan', 'airport']):
            return "wifi"
        elif any(eth in name_lower for eth in ['ethernet', 'eth', 'en0', 'eno']):
            return "ethernet"
        elif any(virt in name_lower for virt in ['vmware', 'virtualbox', 'docker', 'veth']):
            return "virtual"
        elif 'usb' in name_lower:
            return "usb"
        elif 'bluetooth' in name_lower:
            return "bluetooth"
        else:
            return "unknown"
    
    def _get_vendor_from_mac(self, mac_addr: str) -> str:
        """Get vendor from MAC address OUI"""
        oui = mac_addr[:8].upper()
        
        for vendor, ouis in self.common_vendors.items():
            if any(oui.startswith(vendor_oui.replace(':', '').upper()) for vendor_oui in ouis):
                return vendor
        
        return "Unknown"
    
    def generate_random_mac(self, vendor: Optional[str] = None, locally_administered: bool = True) -> str:
        """Generate a random MAC address"""
        
        if vendor and vendor in self.common_vendors:
            # Use vendor-specific OUI
            oui = random.choice(self.common_vendors[vendor])
            oui_bytes = [int(x, 16) for x in oui.split(':')]
        else:
            # Generate random OUI
            oui_bytes = [random.randint(0x00, 0xFF) for _ in range(3)]
            
            if locally_administered:
                # Set locally administered bit (bit 1 of first byte)
                oui_bytes[0] |= 0x02
                # Clear multicast bit (bit 0 of first byte)  
                oui_bytes[0] &= 0xFE
        
        # Generate random device identifier (last 3 bytes)
        device_bytes = [random.randint(0x00, 0xFF) for _ in range(3)]
        
        # Combine OUI and device identifier
        mac_bytes = oui_bytes + device_bytes
        
        return ':'.join([f'{b:02x}' for b in mac_bytes])
    
    def backup_current_macs(self):
        """Backup current MAC addresses"""
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'interfaces': {}
        }
        
        for name, interface in self.interfaces.items():
            backup_data['interfaces'][name] = {
                'original_mac': interface.original_mac,
                'current_mac': interface.current_mac,
                'interface_type': interface.interface_type
            }
        
        try:
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            print(f"[+] MAC addresses backed up to {self.backup_file}")
        except Exception as e:
            print(f"[!] Failed to backup MAC addresses: {e}")
    
    def restore_original_macs(self):
        """Restore original MAC addresses from backup"""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r') as f:
                    backup_data = json.load(f)
                
                restored = 0
                for interface_name, data in backup_data['interfaces'].items():
                    if interface_name in self.interfaces:
                        success = self.change_mac_address(interface_name, data['original_mac'])
                        if success:
                            restored += 1
                
                print(f"[+] Restored {restored} interfaces to original MAC addresses")
                return restored
            else:
                print(f"[!] No backup file found: {self.backup_file}")
                return 0
                
        except Exception as e:
            print(f"[!] Failed to restore MAC addresses: {e}")
            return 0
    
    def change_mac_address(self, interface_name: str, new_mac: str) -> bool:
        """Change MAC address for specified interface"""
        
        if interface_name not in self.interfaces:
            print(f"[!] Interface {interface_name} not found")
            return False
        
        interface = self.interfaces[interface_name]
        old_mac = interface.current_mac
        
        print(f"[+] Changing MAC for {interface_name}: {old_mac} -> {new_mac}")
        
        success = False
        method = "unknown"
        
        try:
            if self.platform == "darwin":  # macOS
                success, method = self._change_mac_macos(interface_name, new_mac)
            elif self.platform == "linux":
                success, method = self._change_mac_linux(interface_name, new_mac)  
            elif self.platform == "windows":
                success, method = self._change_mac_windows(interface_name, new_mac)
            
            # Update interface record
            if success:
                interface.current_mac = new_mac
                print(f"[+] Successfully changed MAC for {interface_name}")
            else:
                print(f"[!] Failed to change MAC for {interface_name}")
            
            # Record the change attempt
            record = MACChangeRecord(
                timestamp=datetime.now(),
                interface=interface_name,
                old_mac=old_mac,
                new_mac=new_mac,
                success=success,
                method=method
            )
            self.change_history.append(record)
            
        except Exception as e:
            print(f"[!] Error changing MAC for {interface_name}: {e}")
            success = False
        
        return success
    
    def _change_mac_macos(self, interface: str, new_mac: str) -> Tuple[bool, str]:
        """Change MAC address on macOS"""
        try:
            # Method 1: Try with sudo ifconfig
            result = subprocess.run(['sudo', 'ifconfig', interface, 'ether', new_mac], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "ifconfig"
            
            # Method 2: Try bringing interface down first
            subprocess.run(['sudo', 'ifconfig', interface, 'down'], capture_output=True)
            result = subprocess.run(['sudo', 'ifconfig', interface, 'ether', new_mac], 
                                  capture_output=True, text=True)
            subprocess.run(['sudo', 'ifconfig', interface, 'up'], capture_output=True)
            
            return result.returncode == 0, "ifconfig-down-up"
            
        except Exception as e:
            print(f"[!] macOS MAC change error: {e}")
            return False, "error"
    
    def _change_mac_linux(self, interface: str, new_mac: str) -> Tuple[bool, str]:
        """Change MAC address on Linux"""
        try:
            # Method 1: Try macchanger if available
            result = subprocess.run(['which', 'macchanger'], capture_output=True)
            if result.returncode == 0:
                result = subprocess.run(['sudo', 'macchanger', '-m', new_mac, interface], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True, "macchanger"
            
            # Method 2: Use ip link
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], 
                          capture_output=True)
            result = subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac], 
                                  capture_output=True, text=True)
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], 
                          capture_output=True)
            
            return result.returncode == 0, "ip-link"
            
        except Exception as e:
            print(f"[!] Linux MAC change error: {e}")
            return False, "error"
    
    def _change_mac_windows(self, interface: str, new_mac: str) -> Tuple[bool, str]:
        """Change MAC address on Windows (requires admin rights)"""
        # Windows MAC changing is more complex and often requires registry changes
        # This is a placeholder for basic implementation
        print("[!] Windows MAC changing not fully implemented")
        print("[!] Manual method: Use Device Manager -> Network Adapters -> Properties -> Advanced -> Network Address")
        return False, "manual-required"
    
    def randomize_all_interfaces(self, exclude_types: List[str] = None) -> int:
        """Randomize MAC addresses for all eligible interfaces"""
        
        if exclude_types is None:
            exclude_types = ['virtual', 'bluetooth']  # Don't randomize virtual interfaces by default
        
        self.backup_current_macs()
        
        randomized = 0
        for interface_name, interface in self.interfaces.items():
            if interface.interface_type not in exclude_types and interface.status == "up":
                new_mac = self.generate_random_mac()
                if self.change_mac_address(interface_name, new_mac):
                    randomized += 1
                    
                # Add small delay between interface changes
                time.sleep(1)
        
        print(f"[+] Randomized {randomized} interfaces")
        return randomized
    
    def get_interface_status(self) -> Dict[str, Dict]:
        """Get current status of all interfaces"""
        status = {}
        
        for name, interface in self.interfaces.items():
            status[name] = {
                'original_mac': interface.original_mac,
                'current_mac': interface.current_mac,
                'changed': interface.original_mac != interface.current_mac,
                'interface_type': interface.interface_type,
                'status': interface.status,
                'vendor': interface.vendor
            }
        
        return status
    
    def print_interface_report(self):
        """Print detailed interface report"""
        print("\n" + "=" * 70)
        print("🔍 NETWORK INTERFACE REPORT")
        print("=" * 70)
        
        for name, interface in self.interfaces.items():
            changed = "✅ CHANGED" if interface.original_mac != interface.current_mac else "⚪ UNCHANGED"
            
            print(f"\n📡 Interface: {name}")
            print(f"   Type: {interface.interface_type.title()}")
            print(f"   Status: {interface.status.upper()}")
            print(f"   Original MAC: {interface.original_mac}")
            print(f"   Current MAC:  {interface.current_mac}")
            print(f"   Vendor: {interface.vendor}")
            print(f"   Status: {changed}")
        
        if self.change_history:
            print(f"\n📊 Change History ({len(self.change_history)} changes):")
            for record in self.change_history[-5:]:  # Show last 5 changes
                status = "✅" if record.success else "❌"
                print(f"   {status} {record.timestamp.strftime('%H:%M:%S')} - {record.interface}: {record.old_mac} -> {record.new_mac}")

# Global MAC randomizer instance
mac_randomizer = MACRandomizer()

# Convenience functions
def randomize_all_macs(exclude_virtual: bool = True) -> int:
    """Randomize all network interface MAC addresses"""
    exclude_types = ['virtual', 'bluetooth'] if exclude_virtual else []
    return mac_randomizer.randomize_all_interfaces(exclude_types)

def restore_original_macs() -> int:
    """Restore original MAC addresses"""
    return mac_randomizer.restore_original_macs()

def change_interface_mac(interface: str, mac: str) -> bool:
    """Change MAC address for specific interface"""
    return mac_randomizer.change_mac_address(interface, mac)

def generate_random_mac(vendor: str = None) -> str:
    """Generate a random MAC address"""
    return mac_randomizer.generate_random_mac(vendor)

def get_interfaces_status() -> Dict[str, Dict]:
    """Get status of all network interfaces"""
    return mac_randomizer.get_interface_status()

if __name__ == "__main__":
    # Test MAC randomization system
    print("🔀 MAC Address Randomization System")
    print("=" * 50)
    
    # Print current interface status
    mac_randomizer.print_interface_report()
    
    # Demo random MAC generation
    print(f"\n🎲 Random MAC examples:")
    for vendor in ["Apple", "Dell", "Intel"]:
        random_mac = generate_random_mac(vendor)
        print(f"   {vendor}: {random_mac}")
    
    print(f"\n⚠️  Use 'sudo python3 {__file__}' to actually change MAC addresses")
    
    # If running with sufficient privileges, offer to randomize
    if len(sys.argv) > 1 and sys.argv[1] == "--randomize":
        print("\n🔄 Randomizing MAC addresses...")
        count = randomize_all_macs()
        print(f"\n📊 Final Report:")
        mac_randomizer.print_interface_report()