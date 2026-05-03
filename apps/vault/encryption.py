# apps/vault/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.conf import settings

def generate_data_key():
    """Generate a new 256-bit data key for envelope encryption"""
    return Fernet.generate_key()

def encrypt_file_content(file_content: bytes, data_key: bytes) -> bytes:
    """Encrypt file content using the per-file data key"""
    fernet = Fernet(data_key)
    return fernet.encrypt(file_content)

def decrypt_file_content(encrypted_content: bytes, data_key: bytes) -> bytes:
    """Decrypt file content"""
    fernet = Fernet(data_key)
    return fernet.decrypt(encrypted_content)

def encrypt_data_key(data_key: bytes, master_key: bytes = None) -> str:
    """Encrypt data key with master key (envelope)"""
    if master_key is None:
        master_key = settings.ENCRYPTION_KEY.encode()
    fernet = Fernet(master_key)
    return fernet.encrypt(data_key).decode()

def decrypt_data_key(encrypted_data_key: str, master_key: bytes = None) -> bytes:
    """Decrypt data key"""
    if master_key is None:
        master_key = settings.ENCRYPTION_KEY.encode()
    fernet = Fernet(master_key)
    return fernet.decrypt(encrypted_data_key.encode())