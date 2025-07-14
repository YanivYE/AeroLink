# generate_key.py
import os

key = os.urandom(32)  # 256-bit AES key
with open("aes.key", "wb") as f:
    f.write(key)

print("[✓] AES key saved to aes.key")
