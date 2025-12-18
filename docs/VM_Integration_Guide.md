# VM Integration System Usage Guide

## Overview

The VM Integration System provides automated virtual machine management for security research with a focus on operational security (OPSEC) and isolation. It supports VMware Fusion, VirtualBox, and Parallels Desktop on macOS.

## Features

- ✅ **Automated VM Creation**: Pre-configured security research VMs
- ✅ **Snapshot Management**: Clean state rollbacks for consistent testing
- ✅ **Network Isolation**: Prevent host system exposure
- ✅ **Security Tools Installation**: Automated setup of penetration testing tools
- ✅ **Emergency Shutdown**: Immediate cleanup in case of compromise
- ✅ **Cross-Platform Support**: VMware, VirtualBox, and Parallels

## Quick Start

### 1. Check System Status
```bash
# Check available hypervisors and VM status
python3 core/vm_integration.py status
```

### 2. Create a Security Research VM
```bash
# Create Kali Linux VM for anonymous research
python3 core/vm_integration.py create --profile kali-research

# Create Ubuntu VM for general research
python3 core/vm_integration.py create --profile ubuntu-research

# Create Windows VM for malware analysis
python3 core/vm_integration.py create --profile windows-analysis
```

### 3. Start and Manage VMs
```bash
# Start VM with automatic snapshot
python3 core/vm_integration.py start --profile kali-research

# Create manual snapshot
python3 core/vm_integration.py snapshot --profile kali-research --snapshot pre-testing

# Restore to clean state
python3 core/vm_integration.py restore --profile kali-research --snapshot pre-testing

# Stop VM gracefully
python3 core/vm_integration.py stop --profile kali-research

# Force stop VM immediately
python3 core/vm_integration.py stop --profile kali-research --force
```

### 4. Emergency Procedures
```bash
# Emergency shutdown all running VMs
python3 core/vm_integration.py emergency
```

## VM Profiles

### Kali Anonymous (`kali-anonymous`)
- **Purpose**: Anonymous penetration testing and research
- **RAM**: 4GB
- **Disk**: 40GB  
- **Network**: NAT with Tor routing
- **Security Features**: 
  - Clipboard sharing disabled
  - Drag & drop disabled
  - Shared folders disabled
  - Auto-snapshot on start
  - Pre-installed security tools

### Ubuntu Research (`ubuntu-research`)
- **Purpose**: General security research and development
- **RAM**: 8GB
- **Disk**: 60GB
- **Network**: Host-only networking
- **Security Features**:
  - Network isolation from internet
  - Development tools included
  - Manual tool installation

### Windows Analysis (`windows-analysis`)
- **Purpose**: Malware analysis and Windows security testing
- **RAM**: 8GB
- **Disk**: 80GB
- **Network**: Completely isolated
- **Security Features**:
  - No network access
  - Snapshot-based analysis
  - Clean rollback capability

## Security Tools Installation

The system can automatically install common penetration testing tools:

```bash
# Available tools include:
- nmap, masscan (network scanning)
- gobuster, ffuf (directory/file fuzzing)
- sqlmap (SQL injection testing)  
- burpsuite (web application proxy)
- metasploit-framework (exploitation framework)
- john, hashcat, hydra (password attacks)
- nikto, wpscan (web vulnerability scanners)
- nuclei (vulnerability scanner)
- subfinder, amass (subdomain enumeration)
- httpx (HTTP probe utility)
```

## Network Isolation Modes

### NAT Mode
- VM can access internet through host
- Host cannot directly access VM
- **Use for**: General research requiring internet access

### Host-Only Mode  
- VM and host can communicate
- No internet access from VM
- **Use for**: Development and testing without internet exposure

### Isolated Mode
- No network access at all
- Complete isolation from host and internet
- **Use for**: Malware analysis and dangerous code execution

## Python API Usage

```python
from core.vm_integration import VMIntegrationManager

# Initialize VM manager
vm_manager = VMIntegrationManager()

# Create VM programmatically
config = {
    "ram": 4096,
    "disk": 40, 
    "network_mode": "nat",
    "auto_install_tools": True
}

success = vm_manager.create_vm_profile("test-vm", config)

if success:
    # Start VM with snapshot
    vm_manager.start_vm("test-vm", create_snapshot=True)
    
    # Your security testing here...
    
    # Restore to clean state  
    vm_manager.restore_snapshot("test-vm", "clean-start")
    
    # Stop VM when done
    vm_manager.stop_vm("test-vm")
```

## Security Considerations

### Network OPSEC
- All VMs are configured with minimal network fingerprints
- MAC addresses are randomized (if host system supports it)
- Network isolation prevents accidental exposure of host system
- Tor routing available for anonymous research

### Data Protection
- Snapshots ensure clean states for each research session
- Emergency shutdown capability for immediate cleanup
- No shared folders or clipboard to prevent data leakage
- Encrypted VM storage (depends on hypervisor settings)

### Host Protection
- VMs cannot access host filesystem by default
- Drag & drop disabled to prevent malware transfer
- Network isolation prevents lateral movement
- Emergency procedures for immediate containment

## Troubleshooting

### Common Issues

**Issue**: Hypervisor not detected
```bash
# Solution: Install VMware Fusion, VirtualBox, or Parallels Desktop
# Ensure command-line tools are installed and accessible
```

**Issue**: VM creation fails
```bash
# Check available disk space
df -h

# Verify hypervisor is running
# VMware: ps aux | grep vmware
# VirtualBox: ps aux | grep VBox  
# Parallels: ps aux | grep prl
```

**Issue**: VM won't start
```bash
# Check VM status
python3 core/vm_integration.py status --profile vm-name

# Try force stop and restart
python3 core/vm_integration.py stop --profile vm-name --force
python3 core/vm_integration.py start --profile vm-name
```

### Emergency Recovery

**Compromised VM**:
1. Immediately run emergency shutdown
2. Do not save any changes
3. Restore from clean snapshot
4. Review host system for any signs of compromise

**Host System Concerns**:
1. Emergency shutdown all VMs
2. Disconnect from network
3. Run host system security scan
4. Review VM network logs for suspicious activity

## Best Practices

### Before Starting Research
1. Create fresh snapshot labeled with date/project
2. Verify network isolation settings
3. Ensure emergency shutdown procedures are ready
4. Document research scope and expected tools

### During Research
1. Take regular snapshots at key milestones
2. Monitor resource usage to avoid host system impact
3. Keep detailed logs of all activities
4. Use secure communication channels for any external contact

### After Research
1. Save important findings to encrypted storage
2. Securely delete any sensitive temporary files  
3. Restore VM to clean snapshot
4. Document lessons learned and update procedures

## Advanced Configuration

### Custom VM Profiles

Edit `configs/vm_config.json` to add custom profiles:

```json
{
  "vm_profiles": {
    "custom-profile": {
      "os": "kali-linux",
      "ram": 6144,
      "disk": 80,
      "network_mode": "host-only",
      "snapshot_on_start": true,
      "auto_install_tools": false,
      "custom_scripts": ["setup-custom-tools.sh"]
    }
  }
}
```

### Hypervisor-Specific Settings

Each hypervisor has specific optimization settings applied automatically:

- **VMware**: Hardware acceleration, memory ballooning disabled
- **VirtualBox**: Nested virtualization, hardware acceleration  
- **Parallels**: Coherence disabled, isolation features enabled

## Integration with Anonymization System

The VM system integrates with the anonymization toggle:

```bash
# Enable anonymous mode before VM operations
export TOOLKIT_ANONYMOUS=true

# VM network traffic will be routed through Tor
python3 core/vm_integration.py start --profile kali-research
```

This ensures all VM internet access is automatically routed through Tor when anonymization is enabled globally.

---

**⚠️ Security Warning**: VMs provide isolation but are not foolproof. Always assume sophisticated malware might escape VM boundaries and maintain defense-in-depth security posture.