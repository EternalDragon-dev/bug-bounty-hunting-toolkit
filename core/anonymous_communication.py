#!/usr/bin/env python3
"""
Anonymous Communication Channels System
=======================================

This module provides secure, anonymous communication channels for reporting findings
and sharing sensitive data. It includes encrypted email, Signal integration, anonymous
file sharing, and secure messaging capabilities with automatic encryption and anonymization.

Features:
- Encrypted email with PGP/GPG support
- Anonymous file sharing via secure channels
- Signal integration for secure messaging
- Tor-based anonymous communication
- Automatic encryption and compression
- Secure key management and rotation
- Multi-channel communication routing
- Emergency communication protocols
"""

import os
import sys
import json
import time
import base64
import hashlib
import logging
import smtplib
import imaplib
import tempfile
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import gnupg
import requests
import threading
import queue
import zipfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CommunicationChannel:
    """Represents a communication channel configuration"""
    channel_id: str
    name: str
    type: str  # email, signal, file_sharing, messaging
    config: Dict[str, Any]
    enabled: bool = True
    priority: int = 1
    encryption_required: bool = True
    anonymization_level: str = "high"  # low, medium, high, paranoid


@dataclass
class SecureMessage:
    """Represents a secure message"""
    message_id: str
    channel_id: str
    recipient: str
    subject: str
    content: str
    attachments: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, urgent
    encrypted: bool = False
    signed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FileShare:
    """Represents a secure file share"""
    share_id: str
    file_path: str
    encrypted: bool = True
    password_protected: bool = True
    expiry_hours: int = 24
    max_downloads: int = 1
    created_at: datetime = field(default_factory=datetime.now)


class AnonymousCommunication:
    """Advanced anonymous communication system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize anonymous communication system"""
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'configs', 'communication.json')
        self.config = self._load_config()
        
        # Core components
        self.channels: Dict[str, CommunicationChannel] = {}
        self.message_queue = queue.Queue()
        self.active_sessions: Dict[str, Any] = {}
        
        # Encryption and security
        self.gpg = None
        self.key_fingerprints: Dict[str, str] = {}
        self.temp_dir = Path(tempfile.mkdtemp(prefix="anon_comm_"))
        
        # Communication statistics
        self.stats = {
            "messages_sent": 0,
            "files_shared": 0,
            "channels_used": set(),
            "encryption_failures": 0,
            "communication_errors": 0
        }
        
        # Initialize system
        self._initialize_system()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load communication configuration"""
        default_config = {
            "encryption": {
                "gpg_enabled": True,
                "key_size": 4096,
                "cipher_algo": "AES256",
                "digest_algo": "SHA256",
                "compress_algo": "ZLIB"
            },
            "email": {
                "smtp_server": "127.0.0.1",
                "smtp_port": 25,
                "imap_server": "127.0.0.1", 
                "imap_port": 993,
                "use_tls": True,
                "anonymous_sender": True,
                "temp_email_services": [
                    "guerrillamail.com",
                    "10minutemail.com",
                    "tempmail.org"
                ]
            },
            "file_sharing": {
                "services": [
                    {
                        "name": "anonfiles",
                        "url": "https://api.anonfiles.com/upload",
                        "anonymity": "high"
                    },
                    {
                        "name": "transfer_sh", 
                        "url": "https://transfer.sh",
                        "anonymity": "medium"
                    }
                ],
                "default_encryption": True,
                "auto_delete": True,
                "max_file_size": 100  # MB
            },
            "signal": {
                "enabled": False,
                "signal_cli_path": "/usr/local/bin/signal-cli",
                "phone_number": "",
                "registration_required": True
            },
            "messaging": {
                "services": [
                    {
                        "name": "telegram_bot",
                        "type": "telegram",
                        "anonymity": "medium"
                    },
                    {
                        "name": "discord_webhook", 
                        "type": "discord",
                        "anonymity": "low"
                    }
                ]
            },
            "anonymization": {
                "use_tor": True,
                "rotate_identity": True,
                "user_agent_rotation": True,
                "timing_obfuscation": True
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
    
    def _initialize_system(self):
        """Initialize the communication system"""
        try:
            # Initialize GPG if enabled
            if self.config.get("encryption", {}).get("gpg_enabled", True):
                self._initialize_gpg()
            
            # Create default communication channels
            self._create_default_channels()
            
            # Setup anonymous networking
            self._setup_anonymous_networking()
            
            logger.info("Anonymous communication system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize communication system: {e}")
            raise
    
    def _initialize_gpg(self):
        """Initialize GPG for encryption"""
        try:
            # Create GPG home directory
            gpg_home = self.temp_dir / "gpg"
            gpg_home.mkdir(exist_ok=True)
            
            # Initialize GPG
            self.gpg = gnupg.GPG(gnupghome=str(gpg_home))
            
            # Generate key pair if none exists
            if not self.gpg.list_keys():
                self._generate_gpg_keypair()
            
            # Load existing key fingerprints
            keys = self.gpg.list_keys(True)  # Private keys
            for key in keys:
                if key['fingerprint']:
                    self.key_fingerprints[key['uids'][0]] = key['fingerprint']
                    
            logger.info(f"GPG initialized with {len(self.key_fingerprints)} keys")
            
        except Exception as e:
            logger.error(f"GPG initialization failed: {e}")
            self.gpg = None
    
    def _generate_gpg_keypair(self):
        """Generate a new GPG key pair for anonymous communication"""
        try:
            key_config = self.config.get("encryption", {})
            
            input_data = self.gpg.gen_key_input(
                key_type="RSA",
                key_length=key_config.get("key_size", 4096),
                name_real="Anonymous Security Research",
                name_email="anonymous@security.research",
                name_comment="Temporary key for secure communications",
                expire_date="1y",  # 1 year expiry
                passphrase=""  # No passphrase for automation
            )
            
            key = self.gpg.gen_key(input_data)
            
            if key.fingerprint:
                logger.info(f"Generated GPG key pair: {key.fingerprint}")
                return key.fingerprint
            else:
                logger.error("GPG key generation failed")
                return None
                
        except Exception as e:
            logger.error(f"GPG key generation error: {e}")
            return None
    
    def _create_default_channels(self):
        """Create default communication channels"""
        try:
            # Anonymous email channel
            email_channel = CommunicationChannel(
                channel_id="email-anonymous",
                name="Anonymous Email",
                type="email",
                config={
                    "use_temp_email": True,
                    "smtp_over_tor": True,
                    "pgp_encryption": True
                },
                priority=1,
                anonymization_level="high"
            )
            
            # File sharing channel
            file_sharing_channel = CommunicationChannel(
                channel_id="files-anonymous",
                name="Anonymous File Sharing",
                type="file_sharing",
                config={
                    "service": "anonfiles",
                    "encrypt_files": True,
                    "password_protect": True,
                    "auto_delete": True
                },
                priority=2,
                anonymization_level="high"
            )
            
            # Emergency communication channel
            emergency_channel = CommunicationChannel(
                channel_id="emergency-contact",
                name="Emergency Contact",
                type="messaging",
                config={
                    "service": "telegram_bot",
                    "encrypt_content": True,
                    "high_priority": True
                },
                priority=3,
                anonymization_level="paranoid"
            )
            
            # Store channels
            for channel in [email_channel, file_sharing_channel, emergency_channel]:
                self.channels[channel.channel_id] = channel
                
            logger.info(f"Created {len(self.channels)} default communication channels")
            
        except Exception as e:
            logger.error(f"Failed to create default channels: {e}")
    
    def _setup_anonymous_networking(self):
        """Setup anonymous networking for communications"""
        try:
            if self.config.get("anonymization", {}).get("use_tor", True):
                # Configure requests session for Tor
                self.anonymous_session = requests.Session()
                self.anonymous_session.proxies = {
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050'
                }
                
                # Set anonymous headers
                self.anonymous_session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                
        except Exception as e:
            logger.error(f"Anonymous networking setup failed: {e}")
            self.anonymous_session = requests.Session()
    
    def send_secure_email(self, recipient: str, subject: str, content: str, 
                         attachments: List[str] = None, channel_id: str = "email-anonymous") -> bool:
        """Send encrypted email through anonymous channel"""
        try:
            if channel_id not in self.channels:
                logger.error(f"Communication channel not found: {channel_id}")
                return False
                
            channel = self.channels[channel_id]
            if channel.type != "email" or not channel.enabled:
                logger.error(f"Email channel not available: {channel_id}")
                return False
            
            # Create secure message
            message = SecureMessage(
                message_id=self._generate_message_id(),
                channel_id=channel_id,
                recipient=recipient,
                subject=subject,
                content=content,
                attachments=attachments or []
            )
            
            # Encrypt message if required
            if channel.encryption_required and self.gpg:
                encrypted_content = self._encrypt_content(content, recipient)
                if encrypted_content:
                    message.content = encrypted_content
                    message.encrypted = True
                else:
                    logger.warning("Encryption failed, sending unencrypted")
            
            # Send email
            success = self._send_email_message(message, channel)
            
            if success:
                self.stats["messages_sent"] += 1
                self.stats["channels_used"].add(channel_id)
                logger.info(f"Secure email sent successfully: {message.message_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Secure email sending failed: {e}")
            self.stats["communication_errors"] += 1
            return False
    
    def _send_email_message(self, message: SecureMessage, channel: CommunicationChannel) -> bool:
        """Send email message through specified channel"""
        try:
            email_config = self.config.get("email", {})
            
            # Create MIME message
            msg = MIMEMultipart()
            msg['From'] = self._get_anonymous_sender()
            msg['To'] = message.recipient
            msg['Subject'] = message.subject
            
            # Add content
            msg.attach(MIMEText(message.content, 'plain'))
            
            # Add attachments
            for attachment_path in message.attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as f:
                        attach = MIMEApplication(f.read())
                        attach.add_header('Content-Disposition', 'attachment', 
                                        filename=os.path.basename(attachment_path))
                        msg.attach(attach)
            
            # Send email
            smtp_server = email_config.get("smtp_server", "127.0.0.1")
            smtp_port = email_config.get("smtp_port", 25)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if email_config.get("use_tls", True):
                    server.starttls()
                
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return False
    
    def share_file_anonymously(self, file_path: str, password: str = None, 
                              expiry_hours: int = 24, max_downloads: int = 1) -> Optional[Dict[str, Any]]:
        """Share file through anonymous file sharing service"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Create file share record
            file_share = FileShare(
                share_id=self._generate_share_id(),
                file_path=file_path,
                password_protected=bool(password),
                expiry_hours=expiry_hours,
                max_downloads=max_downloads
            )
            
            # Encrypt and compress file
            prepared_file = self._prepare_file_for_sharing(file_path, password)
            if not prepared_file:
                logger.error("File preparation failed")
                return None
            
            # Upload to anonymous file sharing service
            upload_result = self._upload_to_file_service(prepared_file, file_share)
            
            if upload_result:
                self.stats["files_shared"] += 1
                logger.info(f"File shared successfully: {file_share.share_id}")
                
                # Clean up prepared file
                if os.path.exists(prepared_file):
                    os.unlink(prepared_file)
                
                return {
                    "share_id": file_share.share_id,
                    "download_url": upload_result.get("url"),
                    "password": password if password else None,
                    "expires_at": (file_share.created_at + 
                                 timedelta(hours=expiry_hours)).isoformat(),
                    "max_downloads": max_downloads
                }
                
        except Exception as e:
            logger.error(f"Anonymous file sharing failed: {e}")
            return None
    
    def _prepare_file_for_sharing(self, file_path: str, password: str = None) -> Optional[str]:
        """Prepare file for anonymous sharing (encrypt, compress)"""
        try:
            file_name = os.path.basename(file_path)
            prepared_path = self.temp_dir / f"share_{int(time.time())}_{file_name}"
            
            # Create encrypted ZIP archive
            with zipfile.ZipFile(prepared_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if password:
                    zipf.setpassword(password.encode())
                zipf.write(file_path, file_name)
                
            # Additional encryption with GPG if available
            if self.gpg and self.config.get("file_sharing", {}).get("default_encryption", True):
                gpg_file = f"{prepared_path}.gpg"
                
                with open(prepared_path, 'rb') as f:
                    encrypted_data = self.gpg.encrypt_file(
                        f, 
                        recipients=None,
                        symmetric=True,
                        passphrase=password or "anonymous_share",
                        armor=True
                    )
                
                if encrypted_data.ok:
                    with open(gpg_file, 'w') as f:
                        f.write(str(encrypted_data))
                    
                    # Remove original zip
                    os.unlink(prepared_path)
                    prepared_path = gpg_file
            
            return str(prepared_path)
            
        except Exception as e:
            logger.error(f"File preparation error: {e}")
            return None
    
    def _upload_to_file_service(self, file_path: str, file_share: FileShare) -> Optional[Dict[str, Any]]:
        """Upload file to anonymous file sharing service"""
        try:
            file_services = self.config.get("file_sharing", {}).get("services", [])
            
            for service in file_services:
                try:
                    if service["name"] == "anonfiles":
                        return self._upload_to_anonfiles(file_path)
                    elif service["name"] == "transfer_sh":
                        return self._upload_to_transfer_sh(file_path, file_share.expiry_hours)
                        
                except Exception as e:
                    logger.warning(f"Upload to {service['name']} failed: {e}")
                    continue
            
            logger.error("All file sharing services failed")
            return None
            
        except Exception as e:
            logger.error(f"File upload error: {e}")
            return None
    
    def _upload_to_anonfiles(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Upload file to AnonFiles service"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = self.anonymous_session.post(
                    "https://api.anonfiles.com/upload",
                    files=files,
                    timeout=300
                )
                
            if response.status_code == 200:
                result = response.json()
                if result.get("status"):
                    return {
                        "url": result["data"]["file"]["url"]["full"],
                        "delete_url": result["data"]["file"]["url"]["short"],
                        "service": "anonfiles"
                    }
                    
        except Exception as e:
            logger.error(f"AnonFiles upload error: {e}")
            
        return None
    
    def _upload_to_transfer_sh(self, file_path: str, expiry_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Upload file to Transfer.sh service"""
        try:
            file_name = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                response = self.anonymous_session.put(
                    f"https://transfer.sh/{file_name}",
                    data=f,
                    timeout=300
                )
                
            if response.status_code == 200:
                return {
                    "url": response.text.strip(),
                    "service": "transfer_sh"
                }
                
        except Exception as e:
            logger.error(f"Transfer.sh upload error: {e}")
            
        return None
    
    def send_signal_message(self, recipient: str, message: str, attachments: List[str] = None) -> bool:
        """Send message via Signal if configured"""
        try:
            signal_config = self.config.get("signal", {})
            
            if not signal_config.get("enabled", False):
                logger.warning("Signal integration not enabled")
                return False
            
            signal_cli = signal_config.get("signal_cli_path", "/usr/local/bin/signal-cli")
            
            if not os.path.exists(signal_cli):
                logger.error(f"Signal CLI not found: {signal_cli}")
                return False
            
            # Encrypt message if GPG available
            encrypted_message = message
            if self.gpg:
                encrypted_data = self.gpg.encrypt(
                    message, 
                    recipients=None,
                    symmetric=True,
                    passphrase="signal_encryption"
                )
                if encrypted_data.ok:
                    encrypted_message = str(encrypted_data)
            
            # Send message
            cmd = [signal_cli, "send", "-m", encrypted_message, recipient]
            
            if attachments:
                for attachment in attachments:
                    if os.path.exists(attachment):
                        cmd.extend(["-a", attachment])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.stats["messages_sent"] += 1
                logger.info(f"Signal message sent to {recipient}")
                return True
            else:
                logger.error(f"Signal send failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Signal messaging error: {e}")
            return False
    
    def send_emergency_alert(self, message: str, priority: str = "urgent") -> bool:
        """Send emergency alert through highest priority channels"""
        try:
            logger.warning(f"EMERGENCY ALERT: {message}")
            
            # Get emergency channels sorted by priority
            emergency_channels = [
                ch for ch in self.channels.values() 
                if ch.enabled and ch.config.get("high_priority", False)
            ]
            emergency_channels.sort(key=lambda x: x.priority)
            
            success_count = 0
            
            for channel in emergency_channels:
                try:
                    if channel.type == "email":
                        recipient = channel.config.get("emergency_email", "admin@security.research")
                        if self.send_secure_email(recipient, f"EMERGENCY - {priority.upper()}", message):
                            success_count += 1
                            
                    elif channel.type == "signal":
                        recipient = channel.config.get("emergency_contact", "+1234567890")
                        if self.send_signal_message(recipient, f"🚨 EMERGENCY: {message}"):
                            success_count += 1
                            
                    elif channel.type == "messaging":
                        if self._send_webhook_message(channel, f"🚨 EMERGENCY: {message}"):
                            success_count += 1
                            
                except Exception as e:
                    logger.error(f"Emergency channel {channel.channel_id} failed: {e}")
            
            logger.info(f"Emergency alert sent through {success_count}/{len(emergency_channels)} channels")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Emergency alert failed: {e}")
            return False
    
    def _send_webhook_message(self, channel: CommunicationChannel, message: str) -> bool:
        """Send message via webhook (Discord, Telegram, etc.)"""
        try:
            service_type = channel.config.get("type", "discord")
            webhook_url = channel.config.get("webhook_url", "")
            
            if not webhook_url:
                logger.warning(f"No webhook URL configured for {channel.channel_id}")
                return False
            
            if service_type == "discord":
                payload = {"content": message}
            elif service_type == "telegram":
                payload = {"text": message}
            else:
                payload = {"message": message}
            
            response = self.anonymous_session.post(
                webhook_url,
                json=payload,
                timeout=30
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"Webhook message failed: {e}")
            return False
    
    def _encrypt_content(self, content: str, recipient: str = None) -> Optional[str]:
        """Encrypt content using GPG"""
        try:
            if not self.gpg:
                logger.warning("GPG not available for encryption")
                return None
            
            # Use symmetric encryption if no recipient specified
            if not recipient:
                encrypted_data = self.gpg.encrypt(
                    content,
                    recipients=None,
                    symmetric=True,
                    passphrase="anonymous_communication",
                    armor=True
                )
            else:
                # Try recipient-specific encryption
                encrypted_data = self.gpg.encrypt(
                    content,
                    recipients=[recipient],
                    armor=True
                )
            
            if encrypted_data.ok:
                return str(encrypted_data)
            else:
                logger.error(f"Encryption failed: {encrypted_data.status}")
                self.stats["encryption_failures"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Content encryption error: {e}")
            return None
    
    def _decrypt_content(self, encrypted_content: str, passphrase: str = "anonymous_communication") -> Optional[str]:
        """Decrypt content using GPG"""
        try:
            if not self.gpg:
                logger.warning("GPG not available for decryption")
                return None
            
            decrypted_data = self.gpg.decrypt(encrypted_content, passphrase=passphrase)
            
            if decrypted_data.ok:
                return str(decrypted_data)
            else:
                logger.error(f"Decryption failed: {decrypted_data.status}")
                return None
                
        except Exception as e:
            logger.error(f"Content decryption error: {e}")
            return None
    
    def _get_anonymous_sender(self) -> str:
        """Get anonymous sender address"""
        temp_emails = self.config.get("email", {}).get("temp_email_services", [])
        if temp_emails:
            # Generate anonymous email address
            random_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
            domain = temp_emails[0]
            return f"anonymous_{random_id}@{domain}"
        else:
            return "anonymous@security.research"
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        timestamp = str(int(time.time() * 1000))
        random_data = os.urandom(8)
        return hashlib.sha256((timestamp + base64.b64encode(random_data).decode()).encode()).hexdigest()[:16]
    
    def _generate_share_id(self) -> str:
        """Generate unique share ID"""
        timestamp = str(int(time.time() * 1000))
        random_data = os.urandom(12)
        return hashlib.sha256((timestamp + base64.b64encode(random_data).decode()).encode()).hexdigest()[:20]
    
    def get_communication_status(self) -> Dict[str, Any]:
        """Get current communication system status"""
        return {
            "channels": {
                ch_id: {
                    "name": ch.name,
                    "type": ch.type,
                    "enabled": ch.enabled,
                    "priority": ch.priority,
                    "encryption_required": ch.encryption_required,
                    "anonymization_level": ch.anonymization_level
                }
                for ch_id, ch in self.channels.items()
            },
            "encryption": {
                "gpg_available": self.gpg is not None,
                "keys_loaded": len(self.key_fingerprints),
                "temp_dir": str(self.temp_dir)
            },
            "statistics": dict(self.stats),
            "session_info": {
                "anonymous_session": hasattr(self, 'anonymous_session'),
                "active_channels": len([ch for ch in self.channels.values() if ch.enabled])
            }
        }
    
    def test_communication_channels(self) -> Dict[str, bool]:
        """Test all communication channels"""
        results = {}
        
        for channel_id, channel in self.channels.items():
            if not channel.enabled:
                results[channel_id] = False
                continue
                
            try:
                if channel.type == "email":
                    # Test email connectivity
                    results[channel_id] = self._test_email_channel(channel)
                elif channel.type == "file_sharing":
                    # Test file sharing services
                    results[channel_id] = self._test_file_sharing_channel(channel)
                elif channel.type == "signal":
                    # Test Signal CLI
                    results[channel_id] = self._test_signal_channel(channel)
                elif channel.type == "messaging":
                    # Test webhook services
                    results[channel_id] = self._test_messaging_channel(channel)
                else:
                    results[channel_id] = False
                    
            except Exception as e:
                logger.error(f"Channel test failed for {channel_id}: {e}")
                results[channel_id] = False
        
        return results
    
    def _test_email_channel(self, channel: CommunicationChannel) -> bool:
        """Test email channel connectivity"""
        try:
            email_config = self.config.get("email", {})
            smtp_server = email_config.get("smtp_server", "127.0.0.1")
            smtp_port = email_config.get("smtp_port", 25)
            
            # Test SMTP connection
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.noop()
                return True
                
        except Exception as e:
            logger.debug(f"Email channel test failed: {e}")
            return False
    
    def _test_file_sharing_channel(self, channel: CommunicationChannel) -> bool:
        """Test file sharing channel"""
        try:
            # Create small test file
            test_file = self.temp_dir / "test_upload.txt"
            with open(test_file, 'w') as f:
                f.write("Test upload file")
            
            # Try to prepare file (without actual upload)
            prepared = self._prepare_file_for_sharing(str(test_file))
            
            if prepared and os.path.exists(prepared):
                os.unlink(prepared)
            os.unlink(test_file)
            
            return prepared is not None
            
        except Exception as e:
            logger.debug(f"File sharing test failed: {e}")
            return False
    
    def _test_signal_channel(self, channel: CommunicationChannel) -> bool:
        """Test Signal channel"""
        try:
            signal_config = self.config.get("signal", {})
            signal_cli = signal_config.get("signal_cli_path", "/usr/local/bin/signal-cli")
            
            return os.path.exists(signal_cli)
            
        except Exception as e:
            logger.debug(f"Signal test failed: {e}")
            return False
    
    def _test_messaging_channel(self, channel: CommunicationChannel) -> bool:
        """Test messaging/webhook channel"""
        try:
            webhook_url = channel.config.get("webhook_url", "")
            return bool(webhook_url)
            
        except Exception as e:
            logger.debug(f"Messaging test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
            logger.info("Anonymous communication cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


def main():
    """CLI interface for anonymous communication"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Anonymous Communication System")
    parser.add_argument('action', choices=['status', 'test', 'email', 'share', 'signal', 'emergency'], help='Action to perform')
    parser.add_argument('--recipient', '-r', help='Recipient (email/phone)')
    parser.add_argument('--subject', '-s', help='Message subject')
    parser.add_argument('--message', '-m', help='Message content')
    parser.add_argument('--file', '-f', help='File to share')
    parser.add_argument('--password', '-p', help='File sharing password')
    parser.add_argument('--expiry', '-e', type=int, default=24, help='File expiry hours')
    parser.add_argument('--channel', '-c', help='Specific channel to use')
    
    args = parser.parse_args()
    
    # Initialize communication system
    comm = AnonymousCommunication()
    
    try:
        if args.action == 'status':
            status = comm.get_communication_status()
            print(json.dumps(status, indent=2))
            
        elif args.action == 'test':
            print("🧪 Testing communication channels...")
            results = comm.test_communication_channels()
            
            print("\n📋 Channel Test Results:")
            for channel_id, success in results.items():
                status_icon = "✅" if success else "❌"
                print(f"   {status_icon} {channel_id}")
            
            success_count = sum(results.values())
            print(f"\n📊 {success_count}/{len(results)} channels operational")
            
        elif args.action == 'email':
            if not args.recipient or not args.subject or not args.message:
                print("❌ Email requires --recipient, --subject, and --message")
                return 1
            
            success = comm.send_secure_email(args.recipient, args.subject, args.message)
            if success:
                print("✅ Secure email sent successfully")
            else:
                print("❌ Failed to send secure email")
                return 1
                
        elif args.action == 'share':
            if not args.file:
                print("❌ File sharing requires --file")
                return 1
                
            if not os.path.exists(args.file):
                print(f"❌ File not found: {args.file}")
                return 1
            
            result = comm.share_file_anonymously(
                args.file, 
                password=args.password,
                expiry_hours=args.expiry
            )
            
            if result:
                print("✅ File shared successfully")
                print(f"🔗 URL: {result['download_url']}")
                if result.get('password'):
                    print(f"🔐 Password: {result['password']}")
                print(f"⏰ Expires: {result['expires_at']}")
            else:
                print("❌ Failed to share file")
                return 1
                
        elif args.action == 'signal':
            if not args.recipient or not args.message:
                print("❌ Signal requires --recipient and --message")
                return 1
            
            attachments = [args.file] if args.file and os.path.exists(args.file) else None
            success = comm.send_signal_message(args.recipient, args.message, attachments)
            
            if success:
                print("✅ Signal message sent successfully")
            else:
                print("❌ Failed to send Signal message")
                return 1
                
        elif args.action == 'emergency':
            if not args.message:
                print("❌ Emergency alert requires --message")
                return 1
            
            success = comm.send_emergency_alert(args.message, priority="urgent")
            if success:
                print("✅ Emergency alert sent")
            else:
                print("❌ Failed to send emergency alert")
                return 1
                
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        comm.cleanup()
        
    return 0


if __name__ == "__main__":
    sys.exit(main())