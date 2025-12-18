# Identity Compartmentalization System

## Overview

The Identity Compartmentalization System provides advanced operational profile management for security research activities. It creates completely isolated operational personas with unique configurations, network routing, tool sets, and behavioral patterns to prevent cross-contamination and enhance operational security.

## Features

- ✅ **Isolated Operational Profiles**: Complete separation of different research activities
- ✅ **Profile-Specific Network Routing**: Unique proxy configurations per profile  
- ✅ **Tool Set Isolation**: Different enabled tools and configurations per profile
- ✅ **Behavioral Pattern Separation**: Unique timing and activity patterns
- ✅ **Secure Profile Switching**: Automatic cleanup and environment isolation
- ✅ **Cross-Profile Contamination Prevention**: Zero data leakage between profiles
- ✅ **Profile Lifecycle Management**: Creation, deletion, and secure cleanup

## Core Concepts

### Operational Profiles (Personas)

Each operational profile represents a completely isolated identity for different types of security research:

- **Reconnaissance Profile**: Network scanning and information gathering
- **Exploitation Profile**: Active vulnerability testing and exploitation
- **Research Profile**: OSINT and passive intelligence gathering  
- **Development Profile**: Tool development and testing environment

### Isolation Layers

#### 1. Network Isolation
- Profile-specific proxy configurations
- Unique exit nodes and routing paths
- Isolated DNS settings
- User agent profile separation

#### 2. Tool Isolation  
- Profile-specific enabled tool sets
- Unique tool configurations and paths
- Isolated environment variables
- Working directory separation

#### 3. Behavioral Isolation
- Timing profile separation (stealth/balanced/aggressive)
- Unique activity patterns
- Session duration isolation
- Randomization factor separation

#### 4. Security Isolation
- Profile-specific isolation levels
- Encrypted temporary file handling
- Secure deletion policies
- Memory protection settings

## Quick Start

### Basic Operations

```bash
# List all available profiles
python3 core/identity_compartmentalization.py list

# Create a new profile
python3 core/identity_compartmentalization.py create --name "Advanced OSINT" --category research --description "Deep OSINT research profile"

# Switch to a profile
python3 core/identity_compartmentalization.py switch --profile research-001

# Check current active profile
python3 core/identity_compartmentalization.py current

# Get profile statistics
python3 core/identity_compartmentalization.py stats

# Emergency reset all profiles
python3 core/identity_compartmentalization.py reset
```

### Profile Categories

#### Reconnaissance (`reconnaissance`)
- **Purpose**: Network scanning, subdomain enumeration, port scanning
- **Default Network**: Tor with scanner user agent profile
- **Default Tools**: nmap, masscan, subfinder, amass, httpx
- **Security Level**: Medium
- **Timing Profile**: Balanced

#### Exploitation (`exploitation`)  
- **Purpose**: Active vulnerability testing and exploitation
- **Default Network**: Tor with aggressive user agent profile
- **Default Tools**: sqlmap, burpsuite, metasploit, nuclei
- **Security Level**: High (VM recommended)
- **Timing Profile**: Aggressive

#### Research (`research`)
- **Purpose**: OSINT and passive intelligence gathering
- **Default Network**: Tor with browser user agent profile  
- **Default Tools**: OSINT tools, social media scrapers
- **Security Level**: High (encrypted temp files)
- **Timing Profile**: Stealth

#### Development (`development`)
- **Purpose**: Tool development and testing
- **Default Network**: Direct connection
- **Default Tools**: Development tools, debuggers, compilers
- **Security Level**: Low
- **Timing Profile**: Balanced

## Python API Usage

### Basic Profile Operations

```python
from core.identity_compartmentalization import IdentityCompartmentalization

# Initialize system
identity_system = IdentityCompartmentalization()

# Create a new profile
profile_id = identity_system.create_profile(
    name="Advanced Exploitation",
    category="exploitation", 
    description="Advanced exploitation testing"
)

# Switch to profile
identity_system.switch_profile(profile_id)

# Get current profile
current = identity_system.get_current_profile()
print(f"Active profile: {current.name}")

# List profiles by category
recon_profiles = identity_system.list_profiles(category="reconnaissance")
```

### Context Manager Usage

```python
# Temporary profile switching
with identity_system.profile_context("research-001"):
    # All operations run in research profile context
    # Network routing, tools, and environment automatically configured
    pass
# Automatically switches back to original profile
```

### Profile Configuration Updates

```python
# Update network configuration
identity_system.update_profile_config("exploit-001", "network", {
    "proxy_type": "socks5",
    "proxy_port": 9051,
    "exit_nodes": ["CH", "SE", "IS"]
})

# Update tools configuration  
identity_system.update_profile_config("recon-001", "tools", {
    "enabled_tools": ["nmap", "masscan", "nuclei", "subfinder"],
    "environment_vars": {"SCAN_INTENSITY": "aggressive"}
})

# Update behavioral configuration
identity_system.update_profile_config("research-001", "behavioral", {
    "timing_profile": "stealth",
    "session_duration": (1800, 7200),  # 30 minutes to 2 hours
    "randomization_factor": 0.5
})

# Update security configuration
identity_system.update_profile_config("exploit-001", "security", {
    "isolation_level": "paranoid",
    "vm_required": True,
    "secure_deletion": True
})
```

## Configuration Reference

### Network Configuration

```python
NetworkConfig(
    proxy_type="tor",           # tor, socks5, http, direct
    proxy_host="127.0.0.1",     # Proxy server host
    proxy_port=9050,            # Proxy server port
    exit_nodes=["US", "GB"],    # Preferred exit node countries
    user_agent_profile="balanced", # scanner, browser, aggressive, developer
    dns_servers=["1.1.1.1"],   # Custom DNS servers
    max_connections=10,         # Maximum concurrent connections
    request_timeout=30          # Request timeout in seconds
)
```

### Tools Configuration

```python
ToolsConfig(
    enabled_tools=["nmap", "burpsuite"],     # List of enabled tools
    tool_paths={                             # Custom tool paths
        "nmap": "/usr/local/bin/nmap",
        "burpsuite": "/opt/BurpSuite/burpsuite"
    },
    custom_configs={                         # Tool-specific configurations
        "nmap": {"timing": "T4", "scripts": "vuln"},
        "burpsuite": {"proxy_port": 8080}
    },
    environment_vars={                       # Profile-specific environment
        "TOOLKIT_MODE": "exploitation",
        "SCAN_INTENSITY": "medium"
    },
    working_directory="/tmp/exploit-workspace"  # Profile working directory
)
```

### Behavioral Configuration

```python
BehavioralConfig(
    timing_profile="stealth",               # stealth, balanced, aggressive
    activity_patterns=[                     # Activity pattern indicators
        "systematic_scan", "payload_delivery"
    ],
    session_duration=(600, 3600),          # Min/max session duration (seconds)
    break_intervals=(120, 600),            # Min/max break intervals (seconds)
    randomization_factor=0.4               # Timing randomization factor
)
```

### Security Configuration

```python
SecurityConfig(
    isolation_level="high",                # low, medium, high, paranoid
    temp_file_encryption=True,            # Encrypt temporary files
    secure_deletion=True,                 # Securely delete files on cleanup
    memory_protection=True,               # Enable memory protection
    network_isolation=True,               # Enable network isolation
    vm_required=False                     # Require VM for this profile
)
```

## Advanced Usage

### Profile Templates

Create profiles from existing templates:

```python
# Create profile based on existing profile
new_profile_id = identity_system.create_profile(
    name="Custom Recon",
    category="reconnaissance",
    template="recon-001"  # Use existing profile as template
)
```

### Cleanup Handlers

Add custom cleanup handlers for profile switching:

```python
def custom_cleanup(profile):
    """Custom cleanup when switching away from profile"""
    print(f"Cleaning up profile: {profile.name}")
    # Custom cleanup logic here

# Add cleanup handler
identity_system.add_cleanup_handler(custom_cleanup)
```

### Profile Statistics and Monitoring

```python
# Get comprehensive statistics
stats = identity_system.get_profile_statistics()
print(f"Total profiles: {stats['total_profiles']}")
print(f"Active profile: {stats['active_profile']}")
print(f"Categories: {stats['categories']}")

# Get profile-specific statistics
profile_stats = identity_system.get_profile_statistics("recon-001")
print(f"Profile: {profile_stats['name']}")
print(f"Last used: {profile_stats['last_used']}")
print(f"Session data: {profile_stats['session_data']}")
```

## Integration with Other Systems

### Anonymization System Integration

Profiles automatically integrate with the anonymization toggle:

```bash
# Enable global anonymization
export TOOLKIT_ANONYMOUS=true

# Profile network settings will automatically use anonymization
python3 core/identity_compartmentalization.py switch --profile exploit-001
```

### VM Integration

High-security profiles can enforce VM usage:

```python
# Profile with VM requirement
if current_profile.security_config.vm_required:
    # VM integration system will enforce VM usage
    # Profile will not activate without VM
    pass
```

### Traffic Analysis Protection Integration

Profiles automatically configure traffic analysis protection:

```python
# Profile behavioral settings integrate with traffic protection
current_behavioral = current_profile.behavioral_config
traffic_protection.timing_analyzer.current_profile = current_behavioral.timing_profile
```

## Security Considerations

### Profile Isolation Levels

#### Low Isolation
- Basic environment separation
- Shared network configuration allowed
- Minimal cleanup on switch
- **Use for**: Development and testing

#### Medium Isolation  
- Network configuration separation
- Environment variable isolation
- Standard cleanup procedures
- **Use for**: General reconnaissance

#### High Isolation
- Complete network separation
- Encrypted temporary files
- Secure file deletion
- **Use for**: Sensitive research and exploitation

#### Paranoid Isolation
- VM enforcement
- Memory protection
- Complete forensic cleanup
- **Use for**: High-risk operations

### Cross-Profile Contamination Prevention

The system implements multiple layers to prevent contamination:

1. **Environment Variable Isolation**: Complete cleanup between switches
2. **Network Configuration Separation**: Unique routing per profile  
3. **File System Isolation**: Profile-specific directories
4. **Secure Deletion**: Cryptographic wiping of sensitive data
5. **Memory Protection**: Secure memory handling where possible

### Best Practices

1. **Use Appropriate Isolation Levels**
   ```python
   # High-risk operations
   profile.security_config.isolation_level = "paranoid"
   profile.security_config.vm_required = True
   
   # Development work
   profile.security_config.isolation_level = "low"
   ```

2. **Regular Profile Cleanup**
   ```python
   # Manually trigger secure cleanup
   identity_system.emergency_reset()
   ```

3. **Monitor Profile Usage**
   ```python
   # Regular statistics review
   stats = identity_system.get_profile_statistics()
   for event in stats['recent_activity']:
       print(f"{event['timestamp']}: {event['action']}")
   ```

## Troubleshooting

### Common Issues

**Issue**: Profile switching fails
```bash
# Check profile exists and is valid
python3 core/identity_compartmentalization.py list

# Try emergency reset
python3 core/identity_compartmentalization.py reset
```

**Issue**: Environment variables not set correctly
```python
# Check profile configuration
profile = identity_system.get_current_profile()
print(profile.tools_config.environment_vars)

# Manually verify environment
import os
print(os.environ.get('TOOLKIT_MODE'))
```

**Issue**: Network routing not working
```python
# Check network configuration
profile = identity_system.get_current_profile()
print(f"Proxy: {profile.network_config.proxy_type}")
print(f"Host: {profile.network_config.proxy_host}")
print(f"Port: {profile.network_config.proxy_port}")

# Verify proxy environment variables
import os
print(os.environ.get('HTTP_PROXY'))
print(os.environ.get('HTTPS_PROXY'))
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from core.identity_compartmentalization import IdentityCompartmentalization
identity_system = IdentityCompartmentalization()
```

### Emergency Procedures

```python
# Complete system reset
identity_system.emergency_reset()

# Secure deletion of all profile data
for profile_id in list(identity_system.profiles.keys()):
    identity_system.delete_profile(profile_id, secure_deletion=True)
```

## Performance Considerations

### Resource Usage
- **Memory**: ~50-200MB depending on active profile complexity
- **Disk**: ~1-10MB per profile for configuration and temporary files
- **CPU**: Minimal overhead during normal operation
- **Network**: Profile-dependent based on proxy configuration

### Optimization Tips

1. **Minimize Active Profiles**: Keep only necessary profiles active
2. **Regular Cleanup**: Periodically clean up unused profile data
3. **Appropriate Isolation Levels**: Don't use paranoid isolation unnecessarily
4. **Profile Reuse**: Use templates to avoid recreating similar profiles

---

**⚠️ Important**: Profile switching affects global system state including environment variables, network routing, and working directory. Always verify the active profile before performing sensitive operations.