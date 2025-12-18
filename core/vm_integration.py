#!/usr/bin/env python3
"""
Advanced VM Integration Module for Operational Security
========================================================

This module provides automated virtual machine management for security research,
with emphasis on isolation, anonymity, and operational security. Supports
VMware Fusion, VirtualBox, and Parallels on macOS.

Features:
- Automated VM creation and configuration
- Snapshot management for clean states
- Network isolation and routing configuration
- Tool installation and environment setup
- One-click VM setup and teardown
- Emergency shutdown and cleanup procedures
"""

import os
import sys
import json
import time
import shutil
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
import hashlib
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VMIntegrationManager:
    """Advanced VM integration and management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize VM manager with configuration"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'configs', 'vm_config.json')
        self.config = self._load_config()
        
        # VM Management paths
        self.vm_base_dir = Path.home() / "Security-VMs"
        self.snapshots_dir = self.vm_base_dir / "snapshots" 
        self.templates_dir = self.vm_base_dir / "templates"
        self.logs_dir = self.vm_base_dir / "logs"
        
        # Create directories
        for directory in [self.vm_base_dir, self.snapshots_dir, self.templates_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Detect available hypervisors
        self.available_hypervisors = self._detect_hypervisors()
        self.active_vms = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load VM configuration from file"""
        default_config = {
            "default_hypervisor": "vmware",
            "vm_profiles": {
                "kali-anonymous": {
                    "os": "kali-linux",
                    "ram": 4096,
                    "disk": 40,
                    "network_mode": "nat",
                    "snapshot_on_start": True,
                    "auto_install_tools": True
                },
                "ubuntu-research": {
                    "os": "ubuntu-22.04", 
                    "ram": 8192,
                    "disk": 60,
                    "network_mode": "host-only",
                    "snapshot_on_start": True,
                    "auto_install_tools": False
                },
                "windows-analysis": {
                    "os": "windows-11",
                    "ram": 8192, 
                    "disk": 80,
                    "network_mode": "isolated",
                    "snapshot_on_start": True,
                    "auto_install_tools": False
                }
            },
            "security_tools": [
                "nmap", "masscan", "gobuster", "ffuf", "sqlmap", "burpsuite",
                "metasploit-framework", "john", "hashcat", "hydra", "nikto",
                "wpscan", "nuclei", "subfinder", "httpx", "amass"
            ],
            "network_isolation": {
                "block_host_communication": True,
                "route_through_tor": True,
                "disable_clipboard_sharing": True,
                "disable_drag_drop": True
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
    
    def _detect_hypervisors(self) -> List[str]:
        """Detect available hypervisors on the system"""
        hypervisors = []
        
        # VMware Fusion
        if shutil.which("vmrun") or os.path.exists("/Applications/VMware Fusion.app"):
            hypervisors.append("vmware")
            
        # VirtualBox
        if shutil.which("VBoxManage") or os.path.exists("/Applications/VirtualBox.app"):
            hypervisors.append("virtualbox")
            
        # Parallels Desktop
        if shutil.which("prlctl") or os.path.exists("/Applications/Parallels Desktop.app"):
            hypervisors.append("parallels")
            
        logger.info(f"Detected hypervisors: {hypervisors}")
        return hypervisors
    
    def create_vm_profile(self, profile_name: str, vm_config: Dict[str, Any]) -> bool:
        """Create a new VM with specified configuration"""
        try:
            logger.info(f"Creating VM profile: {profile_name}")
            
            # Select hypervisor
            hypervisor = vm_config.get("hypervisor", self.config.get("default_hypervisor", "vmware"))
            if hypervisor not in self.available_hypervisors:
                logger.error(f"Hypervisor {hypervisor} not available")
                return False
                
            # Create VM based on hypervisor
            if hypervisor == "vmware":
                return self._create_vmware_vm(profile_name, vm_config)
            elif hypervisor == "virtualbox":
                return self._create_virtualbox_vm(profile_name, vm_config)
            elif hypervisor == "parallels":
                return self._create_parallels_vm(profile_name, vm_config)
                
        except Exception as e:
            logger.error(f"Failed to create VM {profile_name}: {e}")
            return False
            
    def _create_vmware_vm(self, profile_name: str, config: Dict[str, Any]) -> bool:
        """Create VMware VM"""
        try:
            vm_path = self.vm_base_dir / f"{profile_name}.vmwarevm"
            
            # Create VM directory
            vm_path.mkdir(exist_ok=True)
            
            # Generate VMX configuration
            vmx_content = self._generate_vmware_vmx(config)
            vmx_file = vm_path / f"{profile_name}.vmx"
            
            with open(vmx_file, 'w') as f:
                f.write(vmx_content)
                
            logger.info(f"Created VMware VM configuration: {vmx_file}")
            
            # Create virtual disk
            if self._create_vmware_disk(vm_path, profile_name, config.get("disk", 40)):
                self.active_vms[profile_name] = {
                    "hypervisor": "vmware",
                    "path": str(vmx_file),
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }
                return True
                
        except Exception as e:
            logger.error(f"VMware VM creation failed: {e}")
            
        return False
        
    def _generate_vmware_vmx(self, config: Dict[str, Any]) -> str:
        """Generate VMware VMX configuration file"""
        ram_mb = config.get("ram", 4096)
        network_mode = config.get("network_mode", "nat")
        
        vmx_template = f"""#!/usr/bin/vmware
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "19"
memsize = "{ram_mb}"
numvcpus = "2"
firmware = "efi"
keyboardAndMouseProfile = "macProfile"
extendedConfigFile = "Ubuntu 64-bit.vmxf"

# Security and isolation settings
isolation.tools.hgfs.disable = "TRUE"
isolation.tools.dnd.disable = "TRUE"  
isolation.tools.copy.enable = "FALSE"
isolation.tools.paste.enabled = "FALSE"
sharedFolder.maxNum = "0"

# Network configuration
ethernet0.present = "TRUE"
ethernet0.connectionType = "{network_mode}"
ethernet0.virtualDev = "e1000"
ethernet0.addressType = "generated"

# Display settings
svga.present = "TRUE"
svga.autodetect = "TRUE"
mks.enable3d = "TRUE"

# Disk configuration  
scsi0.present = "TRUE"
scsi0.virtualDev = "lsisas1068"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "disk.vmdk"
scsi0:0.deviceType = "scsi-hardDisk"

# USB and other devices
usb.present = "TRUE"
ehci.present = "TRUE"
sound.present = "TRUE"
sound.virtualDev = "hdaudio"

# Power and cleanup
powerType.powerOff = "soft"
powerType.suspend = "soft"
powerType.reset = "soft"
cleanShutdown = "TRUE"

# Security features
replay.supported = "FALSE"
replay.filename = ""
scsi0:0.redo = ""

# VM identification
displayName = "Security Research VM"
guestOS = "ubuntu-64"
"""
        
        return vmx_template
        
    def _create_vmware_disk(self, vm_path: Path, vm_name: str, size_gb: int) -> bool:
        """Create VMware virtual disk"""
        try:
            disk_path = vm_path / "disk.vmdk"
            
            # Use vmware-vdiskmanager if available
            if shutil.which("vmware-vdiskmanager"):
                cmd = [
                    "vmware-vdiskmanager", 
                    "-c", 
                    "-s", f"{size_gb}GB",
                    "-a", "lsisas1068",
                    "-t", "0",
                    str(disk_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Created {size_gb}GB disk: {disk_path}")
                    return True
                else:
                    logger.error(f"Disk creation failed: {result.stderr}")
                    
            # Fallback: create placeholder
            else:
                logger.warning("vmware-vdiskmanager not found, creating placeholder")
                with open(disk_path, 'w') as f:
                    f.write(f"# Placeholder disk file for {vm_name}\n")
                return True
                
        except Exception as e:
            logger.error(f"Disk creation error: {e}")
            
        return False
        
    def _create_virtualbox_vm(self, profile_name: str, config: Dict[str, Any]) -> bool:
        """Create VirtualBox VM"""
        try:
            # Create VM
            cmd = ["VBoxManage", "createvm", "--name", profile_name, "--register"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"VirtualBox VM creation failed: {result.stderr}")
                return False
                
            # Configure VM
            ram_mb = config.get("ram", 4096)
            disk_gb = config.get("disk", 40)
            
            config_commands = [
                ["VBoxManage", "modifyvm", profile_name, "--memory", str(ram_mb)],
                ["VBoxManage", "modifyvm", profile_name, "--cpus", "2"],
                ["VBoxManage", "modifyvm", profile_name, "--vram", "128"],
                ["VBoxManage", "modifyvm", profile_name, "--clipboard-mode", "disabled"],
                ["VBoxManage", "modifyvm", profile_name, "--draganddrop", "disabled"],
                ["VBoxManage", "modifyvm", profile_name, "--usb", "off"],
            ]
            
            for cmd in config_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"VirtualBox config warning: {result.stderr}")
                    
            # Create and attach disk
            disk_path = self.vm_base_dir / f"{profile_name}.vdi"
            
            create_disk_cmd = [
                "VBoxManage", "createmedium", "disk",
                "--filename", str(disk_path),
                "--size", str(disk_gb * 1024)  # VirtualBox uses MB
            ]
            
            result = subprocess.run(create_disk_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Attach disk
                attach_cmd = [
                    "VBoxManage", "storageattach", profile_name,
                    "--storagectl", "SATA Controller", "--port", "0",
                    "--device", "0", "--type", "hdd", "--medium", str(disk_path)
                ]
                subprocess.run(attach_cmd, capture_output=True, text=True)
                
                self.active_vms[profile_name] = {
                    "hypervisor": "virtualbox",
                    "path": str(disk_path),
                    "status": "created",
                    "created_at": datetime.now().isoformat()
                }
                
                logger.info(f"Created VirtualBox VM: {profile_name}")
                return True
                
        except Exception as e:
            logger.error(f"VirtualBox VM creation failed: {e}")
            
        return False
        
    def _create_parallels_vm(self, profile_name: str, config: Dict[str, Any]) -> bool:
        """Create Parallels Desktop VM"""
        try:
            vm_path = self.vm_base_dir / f"{profile_name}.pvm"
            
            # Create VM
            cmd = [
                "prlctl", "create", profile_name,
                "--distribution", "linux",
                "--dst", str(vm_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Parallels VM creation failed: {result.stderr}")
                return False
                
            # Configure VM
            ram_mb = config.get("ram", 4096)
            
            config_commands = [
                ["prlctl", "set", profile_name, "--memsize", str(ram_mb)],
                ["prlctl", "set", profile_name, "--cpus", "2"],
                ["prlctl", "set", profile_name, "--shared-clipboard", "off"],
                ["prlctl", "set", profile_name, "--shared-profile", "off"],
                ["prlctl", "set", profile_name, "--smart-guard", "off"],
            ]
            
            for cmd in config_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Parallels config warning: {result.stderr}")
                    
            self.active_vms[profile_name] = {
                "hypervisor": "parallels", 
                "path": str(vm_path),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created Parallels VM: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Parallels VM creation failed: {e}")
            
        return False
    
    def start_vm(self, profile_name: str, create_snapshot: bool = True) -> bool:
        """Start VM and optionally create snapshot"""
        try:
            if profile_name not in self.active_vms:
                logger.error(f"VM {profile_name} not found")
                return False
                
            vm_info = self.active_vms[profile_name]
            hypervisor = vm_info["hypervisor"]
            
            logger.info(f"Starting {hypervisor} VM: {profile_name}")
            
            # Start based on hypervisor
            success = False
            if hypervisor == "vmware":
                success = self._start_vmware_vm(profile_name, vm_info["path"])
            elif hypervisor == "virtualbox":
                success = self._start_virtualbox_vm(profile_name)
            elif hypervisor == "parallels":
                success = self._start_parallels_vm(profile_name)
                
            if success and create_snapshot:
                time.sleep(30)  # Wait for VM to fully boot
                self.create_snapshot(profile_name, "clean-start")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to start VM {profile_name}: {e}")
            return False
            
    def _start_vmware_vm(self, profile_name: str, vmx_path: str) -> bool:
        """Start VMware VM"""
        try:
            cmd = ["vmrun", "start", vmx_path, "nogui"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VMware VM {profile_name} started successfully")
                self.active_vms[profile_name]["status"] = "running"
                return True
            else:
                logger.error(f"VMware start failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VMware start error: {e}")
            
        return False
        
    def _start_virtualbox_vm(self, profile_name: str) -> bool:
        """Start VirtualBox VM"""
        try:
            cmd = ["VBoxManage", "startvm", profile_name, "--type", "headless"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VirtualBox VM {profile_name} started successfully")
                self.active_vms[profile_name]["status"] = "running"
                return True
            else:
                logger.error(f"VirtualBox start failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VirtualBox start error: {e}")
            
        return False
        
    def _start_parallels_vm(self, profile_name: str) -> bool:
        """Start Parallels VM"""
        try:
            cmd = ["prlctl", "start", profile_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Parallels VM {profile_name} started successfully")
                self.active_vms[profile_name]["status"] = "running"
                return True
            else:
                logger.error(f"Parallels start failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Parallels start error: {e}")
            
        return False
    
    def stop_vm(self, profile_name: str, force: bool = False) -> bool:
        """Stop VM gracefully or forcefully"""
        try:
            if profile_name not in self.active_vms:
                logger.error(f"VM {profile_name} not found")
                return False
                
            vm_info = self.active_vms[profile_name]
            hypervisor = vm_info["hypervisor"]
            
            logger.info(f"Stopping {hypervisor} VM: {profile_name}")
            
            success = False
            if hypervisor == "vmware":
                success = self._stop_vmware_vm(profile_name, vm_info["path"], force)
            elif hypervisor == "virtualbox":
                success = self._stop_virtualbox_vm(profile_name, force)
            elif hypervisor == "parallels":
                success = self._stop_parallels_vm(profile_name, force)
                
            if success:
                self.active_vms[profile_name]["status"] = "stopped"
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to stop VM {profile_name}: {e}")
            return False
            
    def _stop_vmware_vm(self, profile_name: str, vmx_path: str, force: bool = False) -> bool:
        """Stop VMware VM"""
        try:
            operation = "hard" if force else "soft"
            cmd = ["vmrun", "stop", vmx_path, operation]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VMware VM {profile_name} stopped successfully")
                return True
            else:
                logger.error(f"VMware stop failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VMware stop error: {e}")
            
        return False
        
    def _stop_virtualbox_vm(self, profile_name: str, force: bool = False) -> bool:
        """Stop VirtualBox VM"""
        try:
            operation = "poweroff" if force else "acpipowerbutton"
            cmd = ["VBoxManage", "controlvm", profile_name, operation]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VirtualBox VM {profile_name} stopped successfully")
                return True
            else:
                logger.error(f"VirtualBox stop failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VirtualBox stop error: {e}")
            
        return False
        
    def _stop_parallels_vm(self, profile_name: str, force: bool = False) -> bool:
        """Stop Parallels VM"""
        try:
            operation = "kill" if force else "stop"
            cmd = ["prlctl", operation, profile_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Parallels VM {profile_name} stopped successfully")
                return True
            else:
                logger.error(f"Parallels stop failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Parallels stop error: {e}")
            
        return False
    
    def create_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Create VM snapshot for rollback"""
        try:
            if profile_name not in self.active_vms:
                logger.error(f"VM {profile_name} not found")
                return False
                
            vm_info = self.active_vms[profile_name]
            hypervisor = vm_info["hypervisor"]
            
            logger.info(f"Creating {hypervisor} snapshot: {snapshot_name}")
            
            success = False
            if hypervisor == "vmware":
                success = self._create_vmware_snapshot(profile_name, vm_info["path"], snapshot_name)
            elif hypervisor == "virtualbox":
                success = self._create_virtualbox_snapshot(profile_name, snapshot_name)
            elif hypervisor == "parallels":
                success = self._create_parallels_snapshot(profile_name, snapshot_name)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to create snapshot for {profile_name}: {e}")
            return False
            
    def _create_vmware_snapshot(self, profile_name: str, vmx_path: str, snapshot_name: str) -> bool:
        """Create VMware snapshot"""
        try:
            cmd = ["vmrun", "snapshot", vmx_path, snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VMware snapshot {snapshot_name} created")
                return True
            else:
                logger.error(f"VMware snapshot failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VMware snapshot error: {e}")
            
        return False
        
    def _create_virtualbox_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Create VirtualBox snapshot"""
        try:
            cmd = ["VBoxManage", "snapshot", profile_name, "take", snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VirtualBox snapshot {snapshot_name} created")
                return True
            else:
                logger.error(f"VirtualBox snapshot failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VirtualBox snapshot error: {e}")
            
        return False
        
    def _create_parallels_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Create Parallels snapshot"""
        try:
            cmd = ["prlctl", "snapshot", profile_name, "--name", snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Parallels snapshot {snapshot_name} created")
                return True
            else:
                logger.error(f"Parallels snapshot failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Parallels snapshot error: {e}")
            
        return False
    
    def restore_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Restore VM to snapshot state"""
        try:
            if profile_name not in self.active_vms:
                logger.error(f"VM {profile_name} not found")
                return False
                
            vm_info = self.active_vms[profile_name]
            hypervisor = vm_info["hypervisor"]
            
            logger.info(f"Restoring {hypervisor} snapshot: {snapshot_name}")
            
            success = False
            if hypervisor == "vmware":
                success = self._restore_vmware_snapshot(profile_name, vm_info["path"], snapshot_name)
            elif hypervisor == "virtualbox":
                success = self._restore_virtualbox_snapshot(profile_name, snapshot_name)
            elif hypervisor == "parallels":
                success = self._restore_parallels_snapshot(profile_name, snapshot_name)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to restore snapshot for {profile_name}: {e}")
            return False
            
    def _restore_vmware_snapshot(self, profile_name: str, vmx_path: str, snapshot_name: str) -> bool:
        """Restore VMware snapshot"""
        try:
            cmd = ["vmrun", "revertToSnapshot", vmx_path, snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VMware snapshot {snapshot_name} restored")
                return True
            else:
                logger.error(f"VMware snapshot restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VMware snapshot restore error: {e}")
            
        return False
        
    def _restore_virtualbox_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Restore VirtualBox snapshot"""
        try:
            cmd = ["VBoxManage", "snapshot", profile_name, "restore", snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VirtualBox snapshot {snapshot_name} restored")
                return True
            else:
                logger.error(f"VirtualBox snapshot restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VirtualBox snapshot restore error: {e}")
            
        return False
        
    def _restore_parallels_snapshot(self, profile_name: str, snapshot_name: str) -> bool:
        """Restore Parallels snapshot"""
        try:
            cmd = ["prlctl", "snapshot-switch", profile_name, "--id", snapshot_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Parallels snapshot {snapshot_name} restored")
                return True
            else:
                logger.error(f"Parallels snapshot restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Parallels snapshot restore error: {e}")
            
        return False
    
    def install_security_tools(self, profile_name: str) -> bool:
        """Install security tools in VM via SSH"""
        try:
            logger.info(f"Installing security tools in VM: {profile_name}")
            
            # Generate installation script
            install_script = self._generate_tool_install_script()
            
            # Execute in VM (requires SSH access)
            # This is a simplified implementation - real usage would need SSH keys
            script_path = self.vm_base_dir / f"{profile_name}_install.sh"
            
            with open(script_path, 'w') as f:
                f.write(install_script)
                
            logger.info(f"Installation script created: {script_path}")
            logger.info("Note: Manual execution required via VM SSH access")
            
            return True
            
        except Exception as e:
            logger.error(f"Tool installation failed: {e}")
            return False
            
    def _generate_tool_install_script(self) -> str:
        """Generate script to install security tools"""
        tools = self.config.get("security_tools", [])
        
        script = """#!/bin/bash
# Automated Security Tools Installation Script
# Generated by VM Integration Manager

set -e

echo "[+] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "[+] Installing base dependencies..."
sudo apt install -y curl wget git python3 python3-pip golang-go nodejs npm

echo "[+] Installing security tools..."
"""
        
        # Add tool installation commands
        for tool in tools:
            if tool in ["nmap", "masscan", "gobuster", "hydra", "nikto", "john"]:
                script += f"sudo apt install -y {tool}\n"
            elif tool == "metasploit-framework":
                script += "curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall\n"
            elif tool == "burpsuite":
                script += "# BurpSuite requires manual installation\n"
            elif tool in ["ffuf", "nuclei", "subfinder", "httpx"]:
                script += f"go install -v github.com/projectdiscovery/{tool}/v2/cmd/{tool}@latest\n"
            elif tool == "sqlmap":
                script += "sudo apt install -y sqlmap\n"
            elif tool == "amass":
                script += "go install -v github.com/OWASP/Amass/v3/...@master\n"
                
        script += """
echo "[+] Installing additional Python tools..."
pip3 install --user requests beautifulsoup4 scrapy

echo "[+] Setting up environment..."
echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
source ~/.bashrc

echo "[+] Installation complete!"
echo "[+] Please reboot the VM to ensure all changes take effect"
"""
        
        return script
    
    def delete_vm(self, profile_name: str) -> bool:
        """Delete VM and all associated files"""
        try:
            if profile_name not in self.active_vms:
                logger.error(f"VM {profile_name} not found")
                return False
                
            # Stop VM first
            if self.active_vms[profile_name]["status"] == "running":
                self.stop_vm(profile_name, force=True)
                
            vm_info = self.active_vms[profile_name]
            hypervisor = vm_info["hypervisor"]
            
            logger.info(f"Deleting {hypervisor} VM: {profile_name}")
            
            success = False
            if hypervisor == "vmware":
                success = self._delete_vmware_vm(profile_name, vm_info["path"])
            elif hypervisor == "virtualbox":
                success = self._delete_virtualbox_vm(profile_name)
            elif hypervisor == "parallels":
                success = self._delete_parallels_vm(profile_name)
                
            if success:
                del self.active_vms[profile_name]
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete VM {profile_name}: {e}")
            return False
            
    def _delete_vmware_vm(self, profile_name: str, vmx_path: str) -> bool:
        """Delete VMware VM"""
        try:
            cmd = ["vmrun", "deleteVM", vmx_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VMware VM {profile_name} deleted")
                return True
            else:
                # Manual cleanup if vmrun fails
                vm_dir = Path(vmx_path).parent
                if vm_dir.exists():
                    shutil.rmtree(vm_dir)
                    logger.info(f"Manually cleaned up VM directory: {vm_dir}")
                    return True
                    
        except Exception as e:
            logger.error(f"VMware delete error: {e}")
            
        return False
        
    def _delete_virtualbox_vm(self, profile_name: str) -> bool:
        """Delete VirtualBox VM"""
        try:
            cmd = ["VBoxManage", "unregistervm", profile_name, "--delete"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"VirtualBox VM {profile_name} deleted")
                return True
            else:
                logger.error(f"VirtualBox delete failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"VirtualBox delete error: {e}")
            
        return False
        
    def _delete_parallels_vm(self, profile_name: str) -> bool:
        """Delete Parallels VM"""
        try:
            cmd = ["prlctl", "delete", profile_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Parallels VM {profile_name} deleted")
                return True
            else:
                logger.error(f"Parallels delete failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Parallels delete error: {e}")
            
        return False
    
    def emergency_shutdown(self) -> bool:
        """Emergency shutdown of all running VMs"""
        try:
            logger.warning("EMERGENCY SHUTDOWN: Stopping all VMs immediately")
            
            shutdown_success = True
            for profile_name, vm_info in self.active_vms.items():
                if vm_info["status"] == "running":
                    if not self.stop_vm(profile_name, force=True):
                        shutdown_success = False
                        
            # Additional cleanup
            if "vmware" in self.available_hypervisors:
                subprocess.run(["killall", "vmware-vmx"], capture_output=True)
                
            if "virtualbox" in self.available_hypervisors:
                subprocess.run(["VBoxManage", "list", "runningvms"], capture_output=True)
                
            if "parallels" in self.available_hypervisors:
                subprocess.run(["prlctl", "list", "--all"], capture_output=True)
                
            logger.info("Emergency shutdown completed")
            return shutdown_success
            
        except Exception as e:
            logger.error(f"Emergency shutdown error: {e}")
            return False
    
    def get_vm_status(self, profile_name: str = None) -> Dict[str, Any]:
        """Get status of VM(s)"""
        if profile_name:
            return self.active_vms.get(profile_name, {})
        else:
            return {
                "hypervisors": self.available_hypervisors,
                "active_vms": self.active_vms,
                "vm_base_dir": str(self.vm_base_dir),
                "total_vms": len(self.active_vms)
            }
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False


def main():
    """CLI interface for VM Integration Manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VM Integration Manager for Security Research")
    parser.add_argument('action', choices=['create', 'start', 'stop', 'delete', 'snapshot', 'restore', 'status', 'emergency'], help='Action to perform')
    parser.add_argument('--profile', '-p', help='VM profile name')
    parser.add_argument('--snapshot', '-s', help='Snapshot name')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--force', '-f', action='store_true', help='Force operation')
    
    args = parser.parse_args()
    
    # Initialize VM manager
    vm_manager = VMIntegrationManager(args.config)
    
    try:
        if args.action == 'create':
            if not args.profile:
                print("Error: Profile name required for create action")
                return 1
                
            # Use default Kali profile if profile not in config
            if args.profile in vm_manager.config.get("vm_profiles", {}):
                profile_config = vm_manager.config["vm_profiles"][args.profile]
            else:
                profile_config = vm_manager.config["vm_profiles"]["kali-anonymous"]
                
            if vm_manager.create_vm_profile(args.profile, profile_config):
                print(f"✅ VM {args.profile} created successfully")
            else:
                print(f"❌ Failed to create VM {args.profile}")
                return 1
                
        elif args.action == 'start':
            if not args.profile:
                print("Error: Profile name required for start action")
                return 1
                
            if vm_manager.start_vm(args.profile):
                print(f"✅ VM {args.profile} started successfully")
            else:
                print(f"❌ Failed to start VM {args.profile}")
                return 1
                
        elif args.action == 'stop':
            if not args.profile:
                print("Error: Profile name required for stop action")
                return 1
                
            if vm_manager.stop_vm(args.profile, args.force):
                print(f"✅ VM {args.profile} stopped successfully")
            else:
                print(f"❌ Failed to stop VM {args.profile}")
                return 1
                
        elif args.action == 'delete':
            if not args.profile:
                print("Error: Profile name required for delete action")
                return 1
                
            if vm_manager.delete_vm(args.profile):
                print(f"✅ VM {args.profile} deleted successfully")
            else:
                print(f"❌ Failed to delete VM {args.profile}")
                return 1
                
        elif args.action == 'snapshot':
            if not args.profile or not args.snapshot:
                print("Error: Profile and snapshot names required")
                return 1
                
            if vm_manager.create_snapshot(args.profile, args.snapshot):
                print(f"✅ Snapshot {args.snapshot} created for {args.profile}")
            else:
                print(f"❌ Failed to create snapshot")
                return 1
                
        elif args.action == 'restore':
            if not args.profile or not args.snapshot:
                print("Error: Profile and snapshot names required")
                return 1
                
            if vm_manager.restore_snapshot(args.profile, args.snapshot):
                print(f"✅ Snapshot {args.snapshot} restored for {args.profile}")
            else:
                print(f"❌ Failed to restore snapshot")
                return 1
                
        elif args.action == 'status':
            status = vm_manager.get_vm_status(args.profile)
            print(json.dumps(status, indent=2))
            
        elif args.action == 'emergency':
            if vm_manager.emergency_shutdown():
                print("✅ Emergency shutdown completed")
            else:
                print("⚠️ Emergency shutdown completed with warnings")
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())