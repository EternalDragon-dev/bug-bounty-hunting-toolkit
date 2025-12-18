#!/usr/bin/env python3
"""
Identity Compartmentalization System
===================================

This module provides advanced identity compartmentalization for security research operations.
It creates isolated operational profiles with unique configurations, network routing,
tool sets, and behavioral patterns to prevent cross-contamination and enhance OPSEC.

Features:
- Isolated operational profiles (personas)
- Profile-specific network routing and exit nodes
- Unique tool configurations per profile
- Behavioral pattern isolation
- Secure profile switching with cleanup
- Cross-profile contamination prevention
- Profile lifecycle management
"""

import os
import sys
import json
import time
import shutil
import hashlib
import logging
import subprocess
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
import tempfile
import threading
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Network configuration for a profile"""
    proxy_type: str = "tor"  # tor, socks5, http, direct
    proxy_host: str = "127.0.0.1"
    proxy_port: int = 9050
    exit_nodes: List[str] = field(default_factory=list)
    user_agent_profile: str = "balanced"
    dns_servers: List[str] = field(default_factory=lambda: ["1.1.1.1", "8.8.8.8"])
    max_connections: int = 10
    request_timeout: int = 30


@dataclass
class ToolsConfig:
    """Tools configuration for a profile"""
    enabled_tools: List[str] = field(default_factory=list)
    tool_paths: Dict[str, str] = field(default_factory=dict)
    custom_configs: Dict[str, Dict] = field(default_factory=dict)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    working_directory: str = ""


@dataclass
class BehavioralConfig:
    """Behavioral patterns configuration"""
    timing_profile: str = "balanced"  # stealth, balanced, aggressive
    activity_patterns: List[str] = field(default_factory=list)
    session_duration: Tuple[int, int] = (300, 3600)  # min, max seconds
    break_intervals: Tuple[int, int] = (60, 300)  # min, max seconds
    randomization_factor: float = 0.3


@dataclass
class SecurityConfig:
    """Security settings for a profile"""
    isolation_level: str = "high"  # low, medium, high, paranoid
    temp_file_encryption: bool = True
    secure_deletion: bool = True
    memory_protection: bool = True
    network_isolation: bool = True
    vm_required: bool = False


@dataclass
class OperationalProfile:
    """Complete operational profile (persona)"""
    profile_id: str
    name: str
    description: str
    category: str  # reconnaissance, exploitation, research, reporting
    created_at: datetime
    last_used: Optional[datetime] = None
    active: bool = False
    
    # Configuration components
    network_config: NetworkConfig = field(default_factory=NetworkConfig)
    tools_config: ToolsConfig = field(default_factory=ToolsConfig)
    behavioral_config: BehavioralConfig = field(default_factory=BehavioralConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Runtime data
    session_data: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IdentityCompartmentalization:
    """Advanced identity compartmentalization system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize identity compartmentalization system"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'configs', 'identity_profiles.json')
        self.profiles_dir = Path.home() / ".toolkit_profiles"
        self.current_profile: Optional[OperationalProfile] = None
        self.profiles: Dict[str, OperationalProfile] = {}
        self.profile_lock = threading.Lock()
        
        # System state
        self.isolation_active = False
        self.cleanup_handlers = []
        self.profile_history = []
        
        # Initialize system
        self._initialize_system()
        self._load_profiles()
        
    def _initialize_system(self):
        """Initialize the compartmentalization system"""
        try:
            # Create profiles directory
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
            
            # Create profile-specific subdirectories
            for subdir in ["configs", "temp", "logs", "data", "tools"]:
                (self.profiles_dir / subdir).mkdir(exist_ok=True)
                
            logger.info(f"Identity compartmentalization system initialized at {self.profiles_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    def _load_profiles(self):
        """Load existing profiles from configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    profiles_data = json.load(f)
                    
                for profile_data in profiles_data.get("profiles", []):
                    profile = self._deserialize_profile(profile_data)
                    self.profiles[profile.profile_id] = profile
                    
                logger.info(f"Loaded {len(self.profiles)} operational profiles")
            else:
                # Create default profiles
                self._create_default_profiles()
                
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            # Create minimal default profile
            self._create_default_profiles()
    
    def _create_default_profiles(self):
        """Create default operational profiles"""
        try:
            # Reconnaissance profile
            recon_profile = OperationalProfile(
                profile_id="recon-001",
                name="Reconnaissance",
                description="General reconnaissance and information gathering",
                category="reconnaissance",
                created_at=datetime.now(),
                network_config=NetworkConfig(
                    proxy_type="tor",
                    user_agent_profile="scanner",
                    exit_nodes=["US", "CA", "GB"]
                ),
                tools_config=ToolsConfig(
                    enabled_tools=["nmap", "masscan", "subfinder", "amass", "httpx"],
                    environment_vars={"TOOLKIT_MODE": "recon"}
                ),
                behavioral_config=BehavioralConfig(
                    timing_profile="balanced",
                    activity_patterns=["systematic_scan", "passive_enum"]
                ),
                security_config=SecurityConfig(
                    isolation_level="medium",
                    network_isolation=True
                )
            )
            
            # Exploitation profile
            exploit_profile = OperationalProfile(
                profile_id="exploit-001", 
                name="Exploitation",
                description="Active exploitation and vulnerability testing",
                category="exploitation",
                created_at=datetime.now(),
                network_config=NetworkConfig(
                    proxy_type="tor",
                    user_agent_profile="aggressive",
                    exit_nodes=["NL", "CH", "SE"]
                ),
                tools_config=ToolsConfig(
                    enabled_tools=["sqlmap", "burpsuite", "metasploit", "nuclei"],
                    environment_vars={"TOOLKIT_MODE": "exploit"}
                ),
                behavioral_config=BehavioralConfig(
                    timing_profile="aggressive",
                    activity_patterns=["focused_testing", "payload_delivery"]
                ),
                security_config=SecurityConfig(
                    isolation_level="high",
                    vm_required=True,
                    secure_deletion=True
                )
            )
            
            # Research profile
            research_profile = OperationalProfile(
                profile_id="research-001",
                name="Research",
                description="OSINT and passive research activities",
                category="research",
                created_at=datetime.now(),
                network_config=NetworkConfig(
                    proxy_type="tor",
                    user_agent_profile="browser",
                    exit_nodes=["DE", "FR", "IT"]
                ),
                tools_config=ToolsConfig(
                    enabled_tools=["osint_tools", "social_media_scrapers"],
                    environment_vars={"TOOLKIT_MODE": "research"}
                ),
                behavioral_config=BehavioralConfig(
                    timing_profile="stealth",
                    activity_patterns=["human_browsing", "document_research"]
                ),
                security_config=SecurityConfig(
                    isolation_level="high",
                    temp_file_encryption=True
                )
            )
            
            # Development profile
            dev_profile = OperationalProfile(
                profile_id="dev-001",
                name="Development",
                description="Tool development and testing",
                category="development", 
                created_at=datetime.now(),
                network_config=NetworkConfig(
                    proxy_type="direct",
                    user_agent_profile="developer"
                ),
                tools_config=ToolsConfig(
                    enabled_tools=["development_tools", "debuggers", "compilers"],
                    environment_vars={"TOOLKIT_MODE": "development"}
                ),
                behavioral_config=BehavioralConfig(
                    timing_profile="balanced"
                ),
                security_config=SecurityConfig(
                    isolation_level="low"
                )
            )
            
            # Add profiles to system
            for profile in [recon_profile, exploit_profile, research_profile, dev_profile]:
                self.profiles[profile.profile_id] = profile
                
            # Save default profiles
            self._save_profiles()
            logger.info("Created 4 default operational profiles")
            
        except Exception as e:
            logger.error(f"Failed to create default profiles: {e}")
    
    def create_profile(self, name: str, category: str, description: str = "", 
                      template: Optional[str] = None) -> str:
        """Create a new operational profile"""
        try:
            with self.profile_lock:
                # Generate unique profile ID
                profile_id = f"{category}-{uuid.uuid4().hex[:8]}"
                
                # Create profile from template or default
                if template and template in self.profiles:
                    base_profile = self.profiles[template]
                    # Deep copy configuration components
                    profile = OperationalProfile(
                        profile_id=profile_id,
                        name=name,
                        description=description,
                        category=category,
                        created_at=datetime.now(),
                        network_config=NetworkConfig(**asdict(base_profile.network_config)),
                        tools_config=ToolsConfig(**asdict(base_profile.tools_config)),
                        behavioral_config=BehavioralConfig(**asdict(base_profile.behavioral_config)),
                        security_config=SecurityConfig(**asdict(base_profile.security_config))
                    )
                else:
                    # Create minimal profile
                    profile = OperationalProfile(
                        profile_id=profile_id,
                        name=name,
                        description=description,
                        category=category,
                        created_at=datetime.now()
                    )
                
                # Create profile-specific directory
                profile_dir = self.profiles_dir / profile_id
                profile_dir.mkdir(exist_ok=True)
                
                # Create subdirectories
                for subdir in ["config", "temp", "logs", "data"]:
                    (profile_dir / subdir).mkdir(exist_ok=True)
                
                # Store profile
                self.profiles[profile_id] = profile
                self._save_profiles()
                
                logger.info(f"Created operational profile: {name} ({profile_id})")
                return profile_id
                
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            raise
    
    def delete_profile(self, profile_id: str, secure_deletion: bool = True) -> bool:
        """Delete an operational profile and its data"""
        try:
            with self.profile_lock:
                if profile_id not in self.profiles:
                    logger.error(f"Profile {profile_id} not found")
                    return False
                
                if self.current_profile and self.current_profile.profile_id == profile_id:
                    logger.error("Cannot delete active profile")
                    return False
                
                profile = self.profiles[profile_id]
                profile_dir = self.profiles_dir / profile_id
                
                # Secure deletion if requested
                if secure_deletion and profile_dir.exists():
                    self._secure_delete_directory(profile_dir)
                elif profile_dir.exists():
                    shutil.rmtree(profile_dir)
                
                # Remove from profiles
                del self.profiles[profile_id]
                self._save_profiles()
                
                logger.info(f"Deleted operational profile: {profile.name} ({profile_id})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete profile: {e}")
            return False
    
    def switch_profile(self, profile_id: str) -> bool:
        """Switch to a different operational profile"""
        try:
            with self.profile_lock:
                if profile_id not in self.profiles:
                    logger.error(f"Profile {profile_id} not found")
                    return False
                
                # Cleanup current profile if active
                if self.current_profile:
                    self._cleanup_current_profile()
                
                # Switch to new profile
                new_profile = self.profiles[profile_id]
                
                # Initialize profile environment
                if not self._initialize_profile_environment(new_profile):
                    logger.error(f"Failed to initialize profile environment: {profile_id}")
                    return False
                
                # Update profile state
                new_profile.active = True
                new_profile.last_used = datetime.now()
                
                # Record profile switch
                self.profile_history.append({
                    "timestamp": datetime.now(),
                    "action": "switch",
                    "from_profile": self.current_profile.profile_id if self.current_profile else None,
                    "to_profile": profile_id
                })
                
                self.current_profile = new_profile
                logger.info(f"Switched to operational profile: {new_profile.name} ({profile_id})")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to switch profile: {e}")
            return False
    
    def _initialize_profile_environment(self, profile: OperationalProfile) -> bool:
        """Initialize the environment for a profile"""
        try:
            profile_dir = self.profiles_dir / profile.profile_id
            
            # Set working directory
            if profile.tools_config.working_directory:
                os.chdir(profile.tools_config.working_directory)
            else:
                os.chdir(str(profile_dir))
            
            # Set environment variables
            for key, value in profile.tools_config.environment_vars.items():
                os.environ[key] = value
            
            # Configure network settings
            self._configure_profile_network(profile)
            
            # Initialize tools
            self._initialize_profile_tools(profile)
            
            # Set up behavioral patterns
            self._configure_behavioral_patterns(profile)
            
            # Apply security settings
            self._apply_security_settings(profile)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize profile environment: {e}")
            return False
    
    def _configure_profile_network(self, profile: OperationalProfile):
        """Configure network settings for profile"""
        try:
            network_config = profile.network_config
            
            # Set proxy configuration
            if network_config.proxy_type != "direct":
                os.environ['HTTP_PROXY'] = f"socks5h://{network_config.proxy_host}:{network_config.proxy_port}"
                os.environ['HTTPS_PROXY'] = f"socks5h://{network_config.proxy_host}:{network_config.proxy_port}"
                
                # Configure proxychains if available
                self._configure_proxychains(network_config)
            else:
                # Clear proxy settings for direct connection
                for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                    os.environ.pop(var, None)
            
            # Set user agent profile
            os.environ['TOOLKIT_USER_AGENT_PROFILE'] = network_config.user_agent_profile
            
            # Configure DNS if specified
            if network_config.dns_servers:
                os.environ['TOOLKIT_DNS_SERVERS'] = ','.join(network_config.dns_servers)
                
            logger.debug(f"Configured network for profile: proxy={network_config.proxy_type}")
            
        except Exception as e:
            logger.error(f"Failed to configure network: {e}")
    
    def _configure_proxychains(self, network_config: NetworkConfig):
        """Configure proxychains for the profile"""
        try:
            profile_dir = self.profiles_dir / self.current_profile.profile_id
            proxychains_conf = profile_dir / "config" / "proxychains.conf"
            
            # Generate proxychains configuration
            config_content = f"""# Proxychains configuration for profile
strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
{network_config.proxy_type} {network_config.proxy_host} {network_config.proxy_port}
"""
            
            with open(proxychains_conf, 'w') as f:
                f.write(config_content)
            
            # Set proxychains configuration path
            os.environ['PROXYCHAINS_CONF_FILE'] = str(proxychains_conf)
            
        except Exception as e:
            logger.error(f"Failed to configure proxychains: {e}")
    
    def _initialize_profile_tools(self, profile: OperationalProfile):
        """Initialize tools for the profile"""
        try:
            tools_config = profile.tools_config
            
            # Set tool-specific environment variables
            for tool in tools_config.enabled_tools:
                # Enable tool in environment
                os.environ[f'TOOLKIT_ENABLE_{tool.upper()}'] = 'true'
                
                # Set tool-specific config if available
                if tool in tools_config.custom_configs:
                    config_data = json.dumps(tools_config.custom_configs[tool])
                    os.environ[f'TOOLKIT_{tool.upper()}_CONFIG'] = config_data
            
            # Set tool paths if specified
            for tool, path in tools_config.tool_paths.items():
                os.environ[f'TOOLKIT_{tool.upper()}_PATH'] = path
                
            logger.debug(f"Initialized {len(tools_config.enabled_tools)} tools for profile")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
    
    def _configure_behavioral_patterns(self, profile: OperationalProfile):
        """Configure behavioral patterns for the profile"""
        try:
            behavioral_config = profile.behavioral_config
            
            # Set timing profile
            os.environ['TOOLKIT_TIMING_PROFILE'] = behavioral_config.timing_profile
            
            # Set activity patterns
            if behavioral_config.activity_patterns:
                os.environ['TOOLKIT_ACTIVITY_PATTERNS'] = ','.join(behavioral_config.activity_patterns)
            
            # Configure session parameters
            os.environ['TOOLKIT_SESSION_MIN'] = str(behavioral_config.session_duration[0])
            os.environ['TOOLKIT_SESSION_MAX'] = str(behavioral_config.session_duration[1])
            
            # Set randomization factor
            os.environ['TOOLKIT_RANDOMIZATION'] = str(behavioral_config.randomization_factor)
            
        except Exception as e:
            logger.error(f"Failed to configure behavioral patterns: {e}")
    
    def _apply_security_settings(self, profile: OperationalProfile):
        """Apply security settings for the profile"""
        try:
            security_config = profile.security_config
            
            # Set isolation level
            os.environ['TOOLKIT_ISOLATION_LEVEL'] = security_config.isolation_level
            
            # Configure encryption settings
            if security_config.temp_file_encryption:
                os.environ['TOOLKIT_ENCRYPT_TEMP'] = 'true'
            
            # Configure secure deletion
            if security_config.secure_deletion:
                os.environ['TOOLKIT_SECURE_DELETE'] = 'true'
            
            # Memory protection
            if security_config.memory_protection:
                os.environ['TOOLKIT_MEMORY_PROTECT'] = 'true'
            
            # Network isolation
            if security_config.network_isolation:
                os.environ['TOOLKIT_NETWORK_ISOLATE'] = 'true'
            
            # VM requirement
            if security_config.vm_required:
                os.environ['TOOLKIT_VM_REQUIRED'] = 'true'
                
        except Exception as e:
            logger.error(f"Failed to apply security settings: {e}")
    
    def _cleanup_current_profile(self):
        """Cleanup current profile environment"""
        try:
            if not self.current_profile:
                return
                
            profile = self.current_profile
            
            # Mark profile as inactive
            profile.active = False
            
            # Clear profile-specific environment variables
            env_vars_to_clear = [key for key in os.environ.keys() if key.startswith('TOOLKIT_')]
            for var in env_vars_to_clear:
                os.environ.pop(var, None)
            
            # Clear proxy settings
            for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                os.environ.pop(var, None)
            
            # Run cleanup handlers
            for handler in self.cleanup_handlers:
                try:
                    handler(profile)
                except Exception as e:
                    logger.error(f"Cleanup handler error: {e}")
            
            # Secure cleanup if required
            if profile.security_config.secure_deletion:
                self._secure_cleanup_profile(profile)
            
            logger.debug(f"Cleaned up profile: {profile.name}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup profile: {e}")
    
    def _secure_cleanup_profile(self, profile: OperationalProfile):
        """Perform secure cleanup of profile data"""
        try:
            profile_dir = self.profiles_dir / profile.profile_id / "temp"
            
            # Securely delete temporary files
            if profile_dir.exists():
                for file_path in profile_dir.rglob("*"):
                    if file_path.is_file():
                        self._secure_delete_file(file_path)
                        
        except Exception as e:
            logger.error(f"Secure cleanup failed: {e}")
    
    def _secure_delete_file(self, file_path: Path):
        """Securely delete a file by overwriting"""
        try:
            if file_path.exists():
                file_size = file_path.stat().st_size
                with open(file_path, 'rb+') as f:
                    # Overwrite with random data 3 times
                    for _ in range(3):
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                
                # Finally delete the file
                file_path.unlink()
                
        except Exception as e:
            logger.error(f"Secure file deletion failed: {e}")
    
    def _secure_delete_directory(self, dir_path: Path):
        """Securely delete a directory and all contents"""
        try:
            if dir_path.exists():
                # Secure delete all files
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        self._secure_delete_file(file_path)
                
                # Remove empty directories
                shutil.rmtree(dir_path, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"Secure directory deletion failed: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[OperationalProfile]:
        """Get a specific operational profile"""
        return self.profiles.get(profile_id)
    
    def list_profiles(self, category: Optional[str] = None) -> List[OperationalProfile]:
        """List operational profiles, optionally filtered by category"""
        profiles = list(self.profiles.values())
        if category:
            profiles = [p for p in profiles if p.category == category]
        return sorted(profiles, key=lambda p: p.created_at, reverse=True)
    
    def get_current_profile(self) -> Optional[OperationalProfile]:
        """Get the currently active profile"""
        return self.current_profile
    
    def update_profile_config(self, profile_id: str, config_type: str, config_data: Dict[str, Any]) -> bool:
        """Update configuration for a specific profile"""
        try:
            with self.profile_lock:
                if profile_id not in self.profiles:
                    logger.error(f"Profile {profile_id} not found")
                    return False
                
                profile = self.profiles[profile_id]
                
                if config_type == "network":
                    for key, value in config_data.items():
                        if hasattr(profile.network_config, key):
                            setattr(profile.network_config, key, value)
                            
                elif config_type == "tools":
                    for key, value in config_data.items():
                        if hasattr(profile.tools_config, key):
                            setattr(profile.tools_config, key, value)
                            
                elif config_type == "behavioral":
                    for key, value in config_data.items():
                        if hasattr(profile.behavioral_config, key):
                            setattr(profile.behavioral_config, key, value)
                            
                elif config_type == "security":
                    for key, value in config_data.items():
                        if hasattr(profile.security_config, key):
                            setattr(profile.security_config, key, value)
                            
                else:
                    logger.error(f"Unknown config type: {config_type}")
                    return False
                
                self._save_profiles()
                logger.info(f"Updated {config_type} config for profile {profile_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update profile config: {e}")
            return False
    
    def get_profile_statistics(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a profile or all profiles"""
        try:
            if profile_id:
                if profile_id not in self.profiles:
                    return {}
                profile = self.profiles[profile_id]
                return {
                    "profile_id": profile_id,
                    "name": profile.name,
                    "category": profile.category,
                    "created_at": profile.created_at.isoformat(),
                    "last_used": profile.last_used.isoformat() if profile.last_used else None,
                    "active": profile.active,
                    "statistics": profile.statistics,
                    "session_data": profile.session_data
                }
            else:
                # Return statistics for all profiles
                stats = {
                    "total_profiles": len(self.profiles),
                    "active_profile": self.current_profile.profile_id if self.current_profile else None,
                    "categories": {},
                    "recent_activity": []
                }
                
                # Count by category
                for profile in self.profiles.values():
                    if profile.category not in stats["categories"]:
                        stats["categories"][profile.category] = 0
                    stats["categories"][profile.category] += 1
                
                # Recent activity from profile history
                stats["recent_activity"] = self.profile_history[-10:]  # Last 10 events
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get profile statistics: {e}")
            return {}
    
    @contextmanager
    def profile_context(self, profile_id: str):
        """Context manager for temporary profile switching"""
        original_profile = self.current_profile.profile_id if self.current_profile else None
        
        try:
            # Switch to requested profile
            if not self.switch_profile(profile_id):
                raise ValueError(f"Failed to switch to profile {profile_id}")
            
            yield self.current_profile
            
        finally:
            # Switch back to original profile
            if original_profile:
                self.switch_profile(original_profile)
            elif self.current_profile:
                self._cleanup_current_profile()
                self.current_profile = None
    
    def add_cleanup_handler(self, handler: callable):
        """Add a cleanup handler for profile switching"""
        self.cleanup_handlers.append(handler)
    
    def remove_cleanup_handler(self, handler: callable):
        """Remove a cleanup handler"""
        if handler in self.cleanup_handlers:
            self.cleanup_handlers.remove(handler)
    
    def emergency_reset(self) -> bool:
        """Emergency reset of all profile state"""
        try:
            logger.warning("EMERGENCY RESET: Clearing all profile state")
            
            # Cleanup current profile
            if self.current_profile:
                self._cleanup_current_profile()
                self.current_profile = None
            
            # Clear environment variables
            env_vars_to_clear = [key for key in os.environ.keys() if key.startswith('TOOLKIT_')]
            for var in env_vars_to_clear:
                os.environ.pop(var, None)
            
            # Clear proxy settings
            for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                os.environ.pop(var, None)
            
            # Reset all profile states
            for profile in self.profiles.values():
                profile.active = False
                profile.session_data.clear()
            
            # Clear history
            self.profile_history.clear()
            
            logger.info("Emergency reset completed")
            return True
            
        except Exception as e:
            logger.error(f"Emergency reset failed: {e}")
            return False
    
    def _serialize_profile(self, profile: OperationalProfile) -> Dict[str, Any]:
        """Serialize profile to dictionary"""
        return {
            "profile_id": profile.profile_id,
            "name": profile.name,
            "description": profile.description,
            "category": profile.category,
            "created_at": profile.created_at.isoformat(),
            "last_used": profile.last_used.isoformat() if profile.last_used else None,
            "network_config": asdict(profile.network_config),
            "tools_config": asdict(profile.tools_config),
            "behavioral_config": asdict(profile.behavioral_config),
            "security_config": asdict(profile.security_config),
            "statistics": profile.statistics,
            "metadata": profile.metadata
        }
    
    def _deserialize_profile(self, data: Dict[str, Any]) -> OperationalProfile:
        """Deserialize profile from dictionary"""
        return OperationalProfile(
            profile_id=data["profile_id"],
            name=data["name"],
            description=data["description"],
            category=data["category"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            network_config=NetworkConfig(**data.get("network_config", {})),
            tools_config=ToolsConfig(**data.get("tools_config", {})),
            behavioral_config=BehavioralConfig(**data.get("behavioral_config", {})),
            security_config=SecurityConfig(**data.get("security_config", {})),
            statistics=data.get("statistics", {}),
            metadata=data.get("metadata", {})
        )
    
    def _save_profiles(self):
        """Save profiles to configuration file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            profiles_data = {
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "profiles": [self._serialize_profile(profile) for profile in self.profiles.values()]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(profiles_data, f, indent=2)
                
            logger.debug("Saved profile configurations")
            
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")


def main():
    """CLI interface for identity compartmentalization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Identity Compartmentalization System")
    parser.add_argument('action', choices=['list', 'create', 'delete', 'switch', 'current', 'stats', 'reset'], help='Action to perform')
    parser.add_argument('--profile', '-p', help='Profile ID or name')
    parser.add_argument('--name', '-n', help='Profile name for creation')
    parser.add_argument('--category', '-c', choices=['reconnaissance', 'exploitation', 'research', 'development'], help='Profile category')
    parser.add_argument('--description', '-d', help='Profile description')
    parser.add_argument('--template', '-t', help='Template profile ID for creation')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize identity compartmentalization
    identity_system = IdentityCompartmentalization(args.config)
    
    try:
        if args.action == 'list':
            profiles = identity_system.list_profiles(args.category)
            
            print(f"📋 Operational Profiles ({len(profiles)} total)")
            print("=" * 60)
            
            current_id = identity_system.current_profile.profile_id if identity_system.current_profile else None
            
            for profile in profiles:
                status_icon = "🟢" if profile.profile_id == current_id else "⚪"
                last_used = profile.last_used.strftime("%Y-%m-%d %H:%M") if profile.last_used else "Never"
                
                print(f"{status_icon} {profile.name} ({profile.profile_id})")
                print(f"   Category: {profile.category}")
                print(f"   Description: {profile.description}")
                print(f"   Last used: {last_used}")
                print(f"   Network: {profile.network_config.proxy_type}")
                print(f"   Security: {profile.security_config.isolation_level}")
                print()
                
        elif args.action == 'create':
            if not args.name or not args.category:
                print("❌ Profile name and category are required for creation")
                return 1
            
            profile_id = identity_system.create_profile(
                name=args.name,
                category=args.category,
                description=args.description or "",
                template=args.template
            )
            
            print(f"✅ Created operational profile: {args.name} ({profile_id})")
            
        elif args.action == 'delete':
            if not args.profile:
                print("❌ Profile ID is required for deletion")
                return 1
            
            if identity_system.delete_profile(args.profile, secure_deletion=True):
                print(f"✅ Deleted operational profile: {args.profile}")
            else:
                print(f"❌ Failed to delete profile: {args.profile}")
                return 1
                
        elif args.action == 'switch':
            if not args.profile:
                print("❌ Profile ID is required for switching")
                return 1
            
            if identity_system.switch_profile(args.profile):
                profile = identity_system.get_profile(args.profile)
                print(f"✅ Switched to operational profile: {profile.name} ({args.profile})")
                print(f"🔹 Category: {profile.category}")
                print(f"🔹 Network: {profile.network_config.proxy_type}")
                print(f"🔹 Security: {profile.security_config.isolation_level}")
            else:
                print(f"❌ Failed to switch to profile: {args.profile}")
                return 1
                
        elif args.action == 'current':
            current = identity_system.get_current_profile()
            if current:
                print(f"🎯 Current Profile: {current.name} ({current.profile_id})")
                print(f"   Category: {current.category}")
                print(f"   Description: {current.description}")
                print(f"   Network: {current.network_config.proxy_type}://{current.network_config.proxy_host}:{current.network_config.proxy_port}")
                print(f"   Security Level: {current.security_config.isolation_level}")
                print(f"   Enabled Tools: {', '.join(current.tools_config.enabled_tools)}")
            else:
                print("⚪ No active profile")
                
        elif args.action == 'stats':
            if args.profile:
                stats = identity_system.get_profile_statistics(args.profile)
                print(f"📊 Profile Statistics: {stats.get('name', 'Unknown')}")
                print(json.dumps(stats, indent=2))
            else:
                stats = identity_system.get_profile_statistics()
                print("📊 System Statistics")
                print(json.dumps(stats, indent=2))
                
        elif args.action == 'reset':
            if identity_system.emergency_reset():
                print("✅ Emergency reset completed")
            else:
                print("⚠️ Emergency reset completed with warnings")
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())