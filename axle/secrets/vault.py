"""
AXLE OS — Secrets Vault (T-094 to T-100)

Manages sensitive environment variables via AES-256 encryption at rest.
"""
import json
import base64
import os
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from axle.config.settings import settings


class Vault:
    """Encrypted secrets manager."""

    def __init__(self, password: str, vault_path: Optional[Path] = None):
        self.settings = settings
        self.vault_path = vault_path or Path(self.settings.axle_vault_path)
        self.salt_path = self.vault_path.with_suffix(".salt")
        
        # Initialize or load key
        self.fernet = self._derive_key(password)
        self._cache: Dict[str, str] = {}
        self._load()

    def _derive_key(self, password: str) -> Fernet:
        """Derive AES-256 key from a password using PBKDF2. (T-096)"""
        # Load or create salt
        if self.salt_path.exists():
            salt = self.salt_path.read_bytes()
        else:
            salt = os.urandom(16)
            if self.vault_path.parent.exists():
                self.salt_path.write_bytes(salt)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _load(self):
        """Load and decrypt the vault from disk."""
        if not self.vault_path.exists():
            self._cache = {}
            return

        try:
            encrypted_data = self.vault_path.read_bytes()
            if not encrypted_data:
                self._cache = {}
                return
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self._cache = json.loads(decrypted_data.decode())
        except InvalidToken:
            raise ValueError("Invalid vault password.")
        except Exception as e:
            raise RuntimeError(f"Failed to load vault: {e}")

    def _save(self):
        """Encrypt and save the cache to disk."""
        # Ensure directory exists just in case
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = json.dumps(self._cache).encode()
        encrypted_data = self.fernet.encrypt(data)
        
        # Write salt if we haven't already
        if not self.salt_path.exists():
             self.salt_path.write_bytes(os.urandom(16)) # Will be overwritten by _derive_key but just for safety
            
        self.vault_path.write_bytes(encrypted_data)
        # Ensure secure permissions (only owner can read/write)
        os.chmod(self.vault_path, 0o600)

    def set(self, key: str, value: str):
        """Store a secret. (T-097)"""
        self._cache[key] = value
        self._save()

    def get(self, key: str) -> Optional[str]:
        """Retrieve a secret."""
        return self._cache.get(key)

    def delete(self, key: str) -> bool:
        """Delete a secret."""
        if key in self._cache:
            del self._cache[key]
            self._save()
            return True
        return False

    def list_keys(self) -> List[str]:
        """List all keys. Returns ONLY keys, never values. (T-099)"""
        return list(self._cache.keys())

    def write_to_env_file(self, target_path: Path):
        """Write secrets to a systemd EnvironmentFile. (T-098)"""
        lines = []
        for key, value in self._cache.items():
            # Escape quotes just in case
            safe_val = value.replace('"', '\\"')
            lines.append(f'{key}="{safe_val}"')
            
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("\n".join(lines) + "\n")
        os.chmod(target_path, 0o600)
