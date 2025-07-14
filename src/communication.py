import os
import socket
import time
from src.constants import CHUNK_SIZE
from src.crypto.crypto_utils import create_cipher, encrypt_chunk, finalize_encryption
from cryptography.hazmat.primitives import padding

def send_file(ip, port, filepath):
    sock = None
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        print(f"[DEBUG] Connecting to {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        # Send header
        header = f"{filename}|{filesize}\n"
        sock.sendall(header.encode())
        print(f"[DEBUG] Sent header: {repr(header.strip())}")

        time.sleep(0.05)

        # Generate IV, send it first
        iv = os.urandom(16)
        sock.sendall(iv)

        # AES CBC cipher setup
        cipher = create_cipher(iv)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()

        sent = 0
        last_print = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                encrypted = encrypt_chunk(chunk, cipher, encryptor, padder)
                sock.sendall(encrypted)
                sent += len(chunk)
                if time.time() - last_print > 0.5:
                    print(f"[DEBUG] Sent {sent}/{filesize} bytes", end="\r")
                    last_print = time.time()

        # Finalize encryption and send
        sock.sendall(finalize_encryption(encryptor, padder))

        print()
        print(f"[✓] File '{filename}' sent securely to {ip}:{port}")

    except Exception as e:
        print(f"[!] Failed to send file: {e}")

    finally:
        if sock:
            sock.close()
