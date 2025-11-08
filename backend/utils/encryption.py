import json
import base64
from cryptography.fernet import Fernet
from config.settings import settings

def get_fernet():
    return Fernet(settings.encryption_key.encode())

def encrypt_credentials(credentials_dict: dict) -> str:
    fernet = get_fernet()
    credentials_json = json.dumps(credentials_dict)
    encrypted_bytes = fernet.encrypt(credentials_json.encode())
    return base64.b64encode(encrypted_bytes).decode()

def decrypt_credentials(encrypted_string: str) -> dict:
    fernet = get_fernet()
    encrypted_bytes = base64.b64decode(encrypted_string.encode())
    decrypted_bytes = fernet.decrypt(encrypted_bytes)
    return json.loads(decrypted_bytes.decode())
