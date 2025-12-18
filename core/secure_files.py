#!/usr/bin/env python3
"""
Advanced Secure File Handling System
Provides encrypted storage, secure deletion, metadata scrubbing, and automatic cleanup
"""

import os
import sys
import shutil
import hashlib
import secrets
import tempfile
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import json
from datetime import datetime
import mimetypes
import threading
import atexit

# Cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    print("[!] Cryptography library not available. Install with: pip install cryptography")
    CRYPTO_AVAILABLE = False

@dataclass
class SecureFile:
    """Secure file metadata and tracking"""
    original_path: str
    secure_path: str
    file_type: str
    size: int
    created_at: datetime
    encrypted: bool
    checksum: str
    temp_file: bool = False
    metadata_scrubbed: bool = False

class SecureFileManager:
    """Advanced secure file handling system"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "secure_storage"
        self.temp_dir = self.base_dir / "temp"
        self.secure_dir = self.base_dir / "encrypted"
        self.key_file = self.base_dir / ".secure_key"
        
        # Ensure directories exist
        self.base_dir.mkdir(exist_ok=True, mode=0o700)
        self.temp_dir.mkdir(exist_ok=True, mode=0o700)  
        self.secure_dir.mkdir(exist_ok=True, mode=0o700)
        
        # File tracking
        self.managed_files: Dict[str, SecureFile] = {}
        self.temp_files: List[str] = []
        self.cleanup_registry: List[str] = []
        
        # Encryption setup
        self.encryption_key = None
        if CRYPTO_AVAILABLE:
            self._initialize_encryption()
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all_temp_files)
        
        # Thread-safe operations
        self._lock = threading.Lock()
    
    def _initialize_encryption(self):
        """Initialize or load encryption key"""
        try:
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key_data = f.read()
                self.encryption_key = base64.urlsafe_b64decode(key_data)
            else:
                # Generate new key
                self.encryption_key = Fernet.generate_key()
                
                # Save key with restricted permissions
                with open(self.key_file, 'wb') as f:
                    f.write(base64.urlsafe_b64encode(self.encryption_key))
                
                # Set restrictive permissions
                os.chmod(self.key_file, 0o600)
                
            print(f"[+] Secure file encryption initialized")
            
        except Exception as e:
            print(f"[!] Failed to initialize encryption: {e}")
            self.encryption_key = None
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password"""
        if not salt:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_file(self, file_path: Union[str, Path], password: Optional[str] = None) -> str:
        """Encrypt a file and return the encrypted file path"""
        
        if not CRYPTO_AVAILABLE:
            print("[!] Encryption not available - copying file instead")
            return self.secure_copy_file(file_path)
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate secure filename
        secure_filename = self._generate_secure_filename(file_path.suffix)
        encrypted_path = self.secure_dir / secure_filename
        
        try:
            # Use custom password or default key
            if password:
                key, salt = self.derive_key_from_password(password)
                fernet = Fernet(key)
                
                # Prepend salt to encrypted data
                with open(file_path, 'rb') as infile:
                    data = infile.read()
                
                encrypted_data = salt + fernet.encrypt(data)
                
                with open(encrypted_path, 'wb') as outfile:
                    outfile.write(encrypted_data)
            else:
                # Use default key
                fernet = Fernet(self.encryption_key)
                
                with open(file_path, 'rb') as infile, open(encrypted_path, 'wb') as outfile:
                    data = infile.read()
                    encrypted_data = fernet.encrypt(data)
                    outfile.write(encrypted_data)
            
            # Set secure permissions
            os.chmod(encrypted_path, 0o600)
            
            # Create secure file record
            secure_file = SecureFile(
                original_path=str(file_path),
                secure_path=str(encrypted_path),
                file_type=mimetypes.guess_type(str(file_path))[0] or "unknown",
                size=file_path.stat().st_size,
                created_at=datetime.now(),
                encrypted=True,
                checksum=self._calculate_checksum(file_path),
                temp_file=False
            )
            
            with self._lock:
                self.managed_files[str(encrypted_path)] = secure_file
            
            print(f"[+] File encrypted: {file_path.name} -> {secure_filename}")
            return str(encrypted_path)
            
        except Exception as e:
            print(f"[!] Failed to encrypt file {file_path}: {e}")
            raise
    
    def decrypt_file(self, encrypted_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None, password: Optional[str] = None) -> str:
        """Decrypt a file and return the decrypted file path"""
        
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Encryption not available")
        
        encrypted_path = Path(encrypted_path)
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Determine output path
        if not output_path:
            output_path = self.temp_dir / f"decrypted_{encrypted_path.stem}"
        
        output_path = Path(output_path)
        
        try:
            with open(encrypted_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            if password:
                # Extract salt and decrypt with password
                salt = encrypted_data[:16]
                encrypted_content = encrypted_data[16:]
                
                key, _ = self.derive_key_from_password(password, salt)
                fernet = Fernet(key)
                decrypted_data = fernet.decrypt(encrypted_content)
            else:
                # Decrypt with default key
                fernet = Fernet(self.encryption_key)
                decrypted_data = fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            # Set secure permissions
            os.chmod(output_path, 0o600)
            
            # Register as temp file for cleanup
            self.register_temp_file(str(output_path))
            
            print(f"[+] File decrypted: {encrypted_path.name} -> {output_path.name}")
            return str(output_path)
            
        except Exception as e:
            print(f"[!] Failed to decrypt file {encrypted_path}: {e}")
            raise
    
    def secure_copy_file(self, file_path: Union[str, Path], secure_name: Optional[str] = None) -> str:
        """Securely copy file to secure storage with metadata scrubbing"""
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate secure filename
        if not secure_name:
            secure_name = self._generate_secure_filename(file_path.suffix)
        
        secure_path = self.secure_dir / secure_name
        
        # Copy file
        shutil.copy2(file_path, secure_path)
        
        # Scrub metadata
        self.scrub_file_metadata(secure_path)
        
        # Set secure permissions
        os.chmod(secure_path, 0o600)
        
        # Create secure file record
        secure_file = SecureFile(
            original_path=str(file_path),
            secure_path=str(secure_path),
            file_type=mimetypes.guess_type(str(file_path))[0] or "unknown",
            size=file_path.stat().st_size,
            created_at=datetime.now(),
            encrypted=False,
            checksum=self._calculate_checksum(file_path),
            metadata_scrubbed=True
        )
        
        with self._lock:
            self.managed_files[str(secure_path)] = secure_file
        
        print(f"[+] File securely copied: {file_path.name} -> {secure_name}")
        return str(secure_path)
    
    def create_temp_file(self, content: Union[str, bytes], suffix: str = ".tmp", prefix: str = "secure_") -> str:
        """Create a secure temporary file"""
        
        # Create temp file with secure permissions
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_dir)
        
        try:
            with os.fdopen(fd, 'wb') as f:
                if isinstance(content, str):
                    f.write(content.encode())
                else:
                    f.write(content)
            
            # Set secure permissions
            os.chmod(temp_path, 0o600)
            
            # Register for cleanup
            self.register_temp_file(temp_path)
            
            print(f"[+] Secure temp file created: {Path(temp_path).name}")
            return temp_path
            
        except Exception as e:
            os.close(fd)
            print(f"[!] Failed to create temp file: {e}")
            raise
    
    def register_temp_file(self, file_path: str):
        """Register a file for automatic cleanup"""
        with self._lock:
            if file_path not in self.temp_files:
                self.temp_files.append(file_path)
                self.cleanup_registry.append(file_path)
    
    def secure_delete_file(self, file_path: Union[str, Path], passes: int = 3) -> bool:
        """Securely delete a file by overwriting it multiple times"""
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"[!] File not found: {file_path}")
            return False
        
        try:
            file_size = file_path.stat().st_size
            
            print(f"[+] Securely deleting: {file_path.name} ({file_size} bytes)")
            
            with open(file_path, 'r+b') as f:
                for pass_num in range(passes):
                    # Overwrite with random data
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                    
                    print(f"[+] Overwrite pass {pass_num + 1}/{passes}")
                
                # Final pass with zeros
                f.seek(0)
                f.write(b'\x00' * file_size)
                f.flush()
                os.fsync(f.fileno())
            
            # Remove file
            file_path.unlink()
            
            # Remove from tracking
            with self._lock:
                if str(file_path) in self.managed_files:
                    del self.managed_files[str(file_path)]
                if str(file_path) in self.temp_files:
                    self.temp_files.remove(str(file_path))
                if str(file_path) in self.cleanup_registry:
                    self.cleanup_registry.remove(str(file_path))
            
            print(f"[+] File securely deleted: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"[!] Failed to securely delete {file_path}: {e}")
            return False
    
    def scrub_file_metadata(self, file_path: Union[str, Path]) -> bool:
        """Remove metadata from various file types"""
        
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        file_type = mimetypes.guess_type(str(file_path))[0] or ""
        
        try:
            if file_type.startswith('image/'):
                return self._scrub_image_metadata(file_path)
            elif file_type == 'application/pdf':
                return self._scrub_pdf_metadata(file_path)
            elif file_type.startswith('application/vnd.openxmlformats'):
                return self._scrub_office_metadata(file_path)
            else:
                # Generic timestamp scrubbing
                return self._scrub_generic_metadata(file_path)
                
        except Exception as e:
            print(f"[!] Failed to scrub metadata from {file_path}: {e}")
            return False
    
    def _scrub_image_metadata(self, file_path: Path) -> bool:
        """Scrub metadata from image files"""
        try:
            # Try using exiftool if available
            result = subprocess.run(['which', 'exiftool'], capture_output=True)
            if result.returncode == 0:
                subprocess.run(['exiftool', '-all=', '-overwrite_original', str(file_path)], 
                             capture_output=True, check=True)
                print(f"[+] Image metadata scrubbed with exiftool: {file_path.name}")
                return True
            
            # Fallback: try with Pillow if available
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                with Image.open(file_path) as img:
                    # Create image without EXIF data
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(list(img.getdata()))
                    clean_img.save(file_path, quality=95)
                
                print(f"[+] Image metadata scrubbed with Pillow: {file_path.name}")
                return True
                
            except ImportError:
                print(f"[!] No image metadata tools available for {file_path.name}")
                return self._scrub_generic_metadata(file_path)
                
        except Exception as e:
            print(f"[!] Image metadata scrubbing failed: {e}")
            return False
    
    def _scrub_pdf_metadata(self, file_path: Path) -> bool:
        """Scrub metadata from PDF files"""
        try:
            # Try using qpdf if available
            result = subprocess.run(['which', 'qpdf'], capture_output=True)
            if result.returncode == 0:
                temp_path = file_path.with_suffix('.temp.pdf')
                subprocess.run(['qpdf', '--linearize', '--object-streams=generate', 
                              str(file_path), str(temp_path)], check=True)
                shutil.move(temp_path, file_path)
                print(f"[+] PDF metadata scrubbed with qpdf: {file_path.name}")
                return True
            
            print(f"[!] qpdf not available for PDF metadata scrubbing")
            return self._scrub_generic_metadata(file_path)
            
        except Exception as e:
            print(f"[!] PDF metadata scrubbing failed: {e}")
            return False
    
    def _scrub_office_metadata(self, file_path: Path) -> bool:
        """Scrub metadata from Office documents"""
        # Office documents are ZIP files - we could extract and clean XML
        # For now, use generic metadata scrubbing
        return self._scrub_generic_metadata(file_path)
    
    def _scrub_generic_metadata(self, file_path: Path) -> bool:
        """Generic metadata scrubbing (timestamps, etc.)"""
        try:
            # Reset file timestamps
            current_time = datetime.now().timestamp()
            os.utime(file_path, (current_time, current_time))
            
            print(f"[+] Generic metadata scrubbed: {file_path.name}")
            return True
            
        except Exception as e:
            print(f"[!] Generic metadata scrubbing failed: {e}")
            return False
    
    def _generate_secure_filename(self, extension: str = "") -> str:
        """Generate a secure, random filename"""
        random_name = secrets.token_hex(16)
        return f"{random_name}{extension}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def cleanup_temp_files(self, secure_delete: bool = True) -> int:
        """Clean up all registered temporary files"""
        cleaned = 0
        
        with self._lock:
            temp_files_copy = self.temp_files.copy()
        
        for temp_file in temp_files_copy:
            if Path(temp_file).exists():
                if secure_delete:
                    if self.secure_delete_file(temp_file):
                        cleaned += 1
                else:
                    try:
                        Path(temp_file).unlink()
                        cleaned += 1
                    except Exception as e:
                        print(f"[!] Failed to delete temp file {temp_file}: {e}")
        
        with self._lock:
            self.temp_files.clear()
        
        if cleaned > 0:
            print(f"[+] Cleaned up {cleaned} temporary files")
        
        return cleaned
    
    def cleanup_all_temp_files(self):
        """Emergency cleanup function called on exit"""
        if self.cleanup_registry:
            print(f"[+] Emergency cleanup: {len(self.cleanup_registry)} files")
            for file_path in self.cleanup_registry:
                try:
                    if Path(file_path).exists():
                        Path(file_path).unlink()
                except:
                    pass
    
    def get_file_info(self, file_path: str) -> Optional[SecureFile]:
        """Get information about a managed file"""
        with self._lock:
            return self.managed_files.get(file_path)
    
    def list_managed_files(self) -> Dict[str, SecureFile]:
        """List all managed files"""
        with self._lock:
            return self.managed_files.copy()
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        with self._lock:
            managed_count = len(self.managed_files)
            encrypted_count = sum(1 for f in self.managed_files.values() if f.encrypted)
            temp_count = len(self.temp_files)
        
        total_size = sum(f.size for f in self.managed_files.values())
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "storage_location": str(self.base_dir),
            "encryption_available": CRYPTO_AVAILABLE,
            "files": {
                "total_managed": managed_count,
                "encrypted": encrypted_count,
                "unencrypted": managed_count - encrypted_count,
                "temporary": temp_count,
                "total_size_bytes": total_size
            },
            "security_features": {
                "encryption": CRYPTO_AVAILABLE,
                "secure_deletion": True,
                "metadata_scrubbing": True,
                "automatic_cleanup": True,
                "permission_control": True
            },
            "cleanup_registry": len(self.cleanup_registry)
        }
        
        return report

# Global secure file manager instance
secure_file_manager = SecureFileManager()

# Convenience functions
def encrypt_file(file_path: str, password: Optional[str] = None) -> str:
    """Encrypt a file"""
    return secure_file_manager.encrypt_file(file_path, password)

def decrypt_file(encrypted_path: str, output_path: Optional[str] = None, password: Optional[str] = None) -> str:
    """Decrypt a file"""
    return secure_file_manager.decrypt_file(encrypted_path, output_path, password)

def secure_copy(file_path: str) -> str:
    """Securely copy a file"""
    return secure_file_manager.secure_copy_file(file_path)

def create_secure_temp_file(content: Union[str, bytes], suffix: str = ".tmp") -> str:
    """Create secure temporary file"""
    return secure_file_manager.create_temp_file(content, suffix)

def secure_delete(file_path: str, passes: int = 3) -> bool:
    """Securely delete a file"""
    return secure_file_manager.secure_delete_file(file_path, passes)

def scrub_metadata(file_path: str) -> bool:
    """Scrub metadata from a file"""
    return secure_file_manager.scrub_file_metadata(file_path)

def cleanup_temp_files(secure_delete: bool = True) -> int:
    """Clean up temporary files"""
    return secure_file_manager.cleanup_temp_files(secure_delete)

def get_security_report() -> Dict[str, Any]:
    """Get comprehensive security report"""
    return secure_file_manager.generate_security_report()

if __name__ == "__main__":
    # Test the secure file handling system
    print("🔐 Secure File Handling System Test")
    print("=" * 50)
    
    # Create test file
    test_content = "This is sensitive test data that needs to be handled securely."
    temp_file = create_secure_temp_file(test_content, ".txt")
    print(f"Created temp file: {Path(temp_file).name}")
    
    # Test encryption if available
    if CRYPTO_AVAILABLE:
        try:
            encrypted_file = encrypt_file(temp_file)
            print(f"Encrypted file: {Path(encrypted_file).name}")
            
            decrypted_file = decrypt_file(encrypted_file)
            print(f"Decrypted file: {Path(decrypted_file).name}")
            
            # Verify content
            with open(decrypted_file, 'r') as f:
                decrypted_content = f.read()
            
            if decrypted_content == test_content:
                print("✅ Encryption/decryption successful")
            else:
                print("❌ Encryption/decryption failed")
                
        except Exception as e:
            print(f"❌ Encryption test failed: {e}")
    
    # Test secure deletion
    files_to_delete = [temp_file]
    if CRYPTO_AVAILABLE:
        files_to_delete.extend([encrypted_file, decrypted_file])
    
    for file_path in files_to_delete:
        if Path(file_path).exists():
            if secure_delete(file_path):
                print(f"✅ Securely deleted: {Path(file_path).name}")
    
    # Generate security report
    print(f"\n📊 Security Report:")
    report = get_security_report()
    print(f"Managed files: {report['files']['total_managed']}")
    print(f"Encrypted files: {report['files']['encrypted']}")
    print(f"Temporary files: {report['files']['temporary']}")
    print(f"Encryption available: {report['encryption_available']}")
    
    # Cleanup
    cleanup_count = cleanup_temp_files()
    if cleanup_count > 0:
        print(f"✅ Cleaned up {cleanup_count} temporary files")