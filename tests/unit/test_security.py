import pytest
from services.security.auth_service import AuthService
from services.security.rbac import RoleBasedAccessControl
from services.security.encryption_service import EncryptionService

def test_password_hashing():
    auth = AuthService()
    password = "test_password_123"
    hashed = auth.hash_password(password)
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrong_password", hashed)

def test_create_access_token():
    auth = AuthService()
    token = auth.create_access_token("user123", "admin")
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_token():
    auth = AuthService()
    token = auth.create_access_token("user123", "admin")
    payload = auth.verify_token(token)
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"

def test_rbac_admin_permissions():
    rbac = RoleBasedAccessControl()
    assert rbac.authorize_action("admin", "read")
    assert rbac.authorize_action("admin", "write")
    assert rbac.authorize_action("admin", "delete")
    assert rbac.authorize_action("admin", "migrate")

def test_rbac_viewer_permissions():
    rbac = RoleBasedAccessControl()
    assert rbac.authorize_action("viewer", "read")
    assert not rbac.authorize_action("viewer", "write")
    assert not rbac.authorize_action("viewer", "delete")

def test_encryption_decrypt():
    service = EncryptionService()
    original_data = b"sensitive_data_here"
    encrypted = service.encrypt_data(original_data)
    decrypted = service.decrypt_data(encrypted)
    assert decrypted == original_data

def test_generate_encryption_key():
    key = EncryptionService.generate_key()
    assert isinstance(key, str)
    assert len(key) > 0
