from cryptography.fernet import Fernet
from config.settings import settings

class EncryptionService:
    def __init__(self):
        self.fernet = Fernet(settings.encryption_key.encode())
    def encrypt_data(self, data: bytes) -> bytes:
        return self.fernet.encrypt(data)
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        return self.fernet.decrypt(encrypted_data)
    def encrypt_file(self, file_path: str, output_path: str):
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = self.encrypt_data(data)
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    def decrypt_file(self, encrypted_path: str, output_path: str):
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted = self.decrypt_data(encrypted_data)
        with open(output_path, 'wb') as f:
            f.write(decrypted)
    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()
    async def rotate_keys(self, data_object_id: str, db):
        data_obj = db["data_objects"].find_one({"_id": data_object_id})
        if not data_obj:
            return False
        old_key = self.fernet
        new_key = Fernet(Fernet.generate_key())
        temp_decrypted = old_key.decrypt(data_obj.get("encrypted_data", b""))
        new_encrypted = new_key.encrypt(temp_decrypted)
        db["data_objects"].update_one(
            {"_id": data_object_id},
            {"$set": {"encrypted_data": new_encrypted, "encryption_key_version": data_obj.get("encryption_key_version", 0) + 1}}
        )
        return True
