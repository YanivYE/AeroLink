from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def load_key(path="src/crypto/aes.key"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[!] AES key file not found: {path}")
    with open(path, "rb") as f:
        key = f.read()
    if len(key) != 32:
        raise ValueError("[!] AES key must be 32 bytes long")
    return key

AES_KEY = load_key()  # 32 bytes = 256-bit AES key (shared secret key)

def encrypt_chunk(chunk, cipher, encryptor, padder):
    padded_data = padder.update(chunk)
    return encryptor.update(padded_data)

def finalize_encryption(encryptor, padder):
    padded_data = padder.finalize()
    return encryptor.update(padded_data) + encryptor.finalize()

def decrypt_chunk(chunk, decryptor, unpadder):
    decrypted_data = decryptor.update(chunk)
    return unpadder.update(decrypted_data)

def finalize_decryption(decryptor, unpadder):
    decrypted_data = decryptor.finalize()
    return unpadder.update(decrypted_data) + unpadder.finalize()

def create_cipher(iv):
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    return cipher
