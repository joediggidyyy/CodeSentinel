"""
CodeSentinel - Secure Credential Manager

Created by: joediggidyyy
Architecture: SECURITY > EFFICIENCY > MINIMALISM

This module provides secure credential storage and management using
Windows Credential Manager and encryption for sensitive data.
"""

import os
import json
import base64
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureCredentialManager:
    """
    Secure credential management system that replaces plaintext storage
    with encrypted credentials using Windows Credential Manager.
    """
    
    def __init__(self, service_name: str = "CodeSentinel"):
        self.service_name = service_name
        self._encryption_key = None
        
    def _get_encryption_key(self) -> bytes:
        """Generate or retrieve encryption key for token storage."""
        if self._encryption_key is None:
            # Try to get existing key from keyring
            stored_key = keyring.get_password(self.service_name, "encryption_key")
            
            if stored_key:
                self._encryption_key = base64.urlsafe_b64decode(stored_key)
            else:
                # Generate new key
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                self._encryption_key = kdf.derive(b"CodeSentinel-1.0")
                
                # Store key securely
                key_b64 = base64.urlsafe_b64encode(self._encryption_key).decode()
                keyring.set_password(self.service_name, "encryption_key", key_b64)
                
        return self._encryption_key
    
    def store_password(self, username: str, password: str, context: str = "email") -> bool:
        """
        Securely store password using Windows Credential Manager.
        
        Args:
            username: The username/email for the credential
            password: The password to store securely
            context: Context for the credential (email, database, etc.)
            
        Returns:
            bool: True if successfully stored
        """
        try:
            credential_id = f"{context}:{username}"
            keyring.set_password(self.service_name, credential_id, password)
            return True
        except Exception as e:
            print(f"Error storing credential: {e}")
            return False
    
    def get_password(self, username: str, context: str = "email") -> Optional[str]:
        """
        Retrieve securely stored password.
        
        Args:
            username: The username/email for the credential
            context: Context for the credential
            
        Returns:
            Optional[str]: The password if found, None otherwise
        """
        try:
            credential_id = f"{context}:{username}"
            return keyring.get_password(self.service_name, credential_id)
        except Exception as e:
            print(f"Error retrieving credential: {e}")
            return None
    
    def store_token(self, token: str, token_type: str = "github") -> bool:
        """
        Securely store API tokens with encryption.
        
        Args:
            token: The API token to store
            token_type: Type of token (github, slack, etc.)
            
        Returns:
            bool: True if successfully stored
        """
        try:
            # Encrypt the token
            fernet = Fernet(base64.urlsafe_b64encode(self._get_encryption_key()))
            encrypted_token = fernet.encrypt(token.encode())
            
            # Store encrypted token
            token_b64 = base64.urlsafe_b64encode(encrypted_token).decode()
            keyring.set_password(self.service_name, f"token:{token_type}", token_b64)
            return True
        except Exception as e:
            print(f"Error storing token: {e}")
            return False
    
    def get_token(self, token_type: str = "github") -> Optional[str]:
        """
        Retrieve and decrypt API token.
        
        Args:
            token_type: Type of token to retrieve
            
        Returns:
            Optional[str]: The decrypted token if found, None otherwise
        """
        try:
            # Get encrypted token
            encrypted_token_b64 = keyring.get_password(self.service_name, f"token:{token_type}")
            if not encrypted_token_b64:
                return None
            
            # Decrypt token
            encrypted_token = base64.urlsafe_b64decode(encrypted_token_b64)
            fernet = Fernet(base64.urlsafe_b64encode(self._get_encryption_key()))
            token = fernet.decrypt(encrypted_token).decode()
            return token
        except Exception as e:
            print(f"Error retrieving token: {e}")
            return None
    
    def delete_credential(self, username: str, context: str = "email") -> bool:
        """Delete a stored credential."""
        try:
            credential_id = f"{context}:{username}"
            keyring.delete_password(self.service_name, credential_id)
            return True
        except Exception as e:
            print(f"Error deleting credential: {e}")
            return False
    
    def delete_token(self, token_type: str = "github") -> bool:
        """Delete a stored token."""
        try:
            keyring.delete_password(self.service_name, f"token:{token_type}")
            return True
        except Exception as e:
            print(f"Error deleting token: {e}")
            return False
    
    def validate_smtp_credentials(self, smtp_server: str, port: int, username: str) -> bool:
        """
        Validate SMTP credentials by attempting connection.
        
        Args:
            smtp_server: SMTP server address
            port: SMTP port
            username: Username for authentication
            
        Returns:
            bool: True if credentials are valid
        """
        import smtplib
        
        password = self.get_password(username, "email")
        if not password:
            return False
        
        try:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(username, password)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP validation failed: {e}")
            return False
    
    def test_github_token(self, token_type: str = "github") -> bool:
        """
        Test GitHub token validity by making API call.
        
        Args:
            token_type: Type of token to test
            
        Returns:
            bool: True if token is valid
        """
        import requests
        
        token = self.get_token(token_type)
        if not token:
            return False
        
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"GitHub token validation failed: {e}")
            return False
    
    def export_config_safe(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export configuration with sensitive data removed/masked.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict[str, Any]: Safe configuration for storage
        """
        safe_config = config.copy()
        
        # Remove sensitive fields
        sensitive_fields = ['password', 'token', 'secret', 'key', 'credential']
        
        def mask_sensitive(obj):
            if isinstance(obj, dict):
                return {k: '***SECURE***' if any(field in k.lower() for field in sensitive_fields) 
                       else mask_sensitive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [mask_sensitive(item) for item in obj]
            else:
                return obj
        
        return mask_sensitive(safe_config)


# Singleton instance for global use
credential_manager = SecureCredentialManager()