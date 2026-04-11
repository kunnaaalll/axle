import os
import pytest
from pathlib import Path
from axle.secrets.vault import Vault

@pytest.fixture
def temp_vault_path(tmp_path):
    return tmp_path / "test_vault.enc"

def test_vault_encryption_roundtrip(temp_vault_path):
    # Create vault and set a key
    vault = Vault(password="super-secret", vault_path=temp_vault_path)
    vault.set("API_KEY", "12345")
    
    # Assert physical file exists
    assert temp_vault_path.exists()
    assert temp_vault_path.with_suffix(".salt").exists()
    
    # Make sure we can't read the plain text in the file
    content = temp_vault_path.read_text()
    assert "12345" not in content
    assert "API_KEY" not in content

    # Load with same password
    vault2 = Vault(password="super-secret", vault_path=temp_vault_path)
    assert vault2.get("API_KEY") == "12345"

def test_vault_invalid_password(temp_vault_path):
    vault = Vault(password="correct-horse", vault_path=temp_vault_path)
    vault.set("TEST", "hello")
    
    # Try loading with wrong password
    with pytest.raises(ValueError, match="Invalid vault password."):
        Vault(password="wrong-password", vault_path=temp_vault_path)

def test_vault_crud_operations(temp_vault_path):
    vault = Vault(password="test", vault_path=temp_vault_path)
    
    vault.set("A", "Apple")
    vault.set("B", "Banana")
    
    assert vault.get("A") == "Apple"
    
    keys = vault.list_keys()
    assert "A" in keys
    assert "B" in keys
    assert "Apple" not in keys  # ensure isolation
    
    assert vault.delete("A") is True
    assert vault.get("A") is None
    assert vault.delete("NON_EXISTENT") is False

def test_vault_write_env_file(temp_vault_path, tmp_path):
    vault = Vault(password="test", vault_path=temp_vault_path)
    vault.set("DB_PASS", "s3cr3t!")
    
    env_file = tmp_path / ".env"
    vault.write_to_env_file(env_file)
    
    assert env_file.exists()
    content = env_file.read_text()
    assert 'DB_PASS="s3cr3t!"' in content
