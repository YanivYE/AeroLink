import socket
import threading
import os
from src.constants import CHUNK_SIZE, DEFAULT_PORT
from src.crypto.crypto_utils import create_cipher, decrypt_chunk, finalize_decryption
from cryptography.hazmat.primitives import padding

def read_header(client_socket):
    header = b""
    while not header.endswith(b"\n"):
        chunk = client_socket.recv(1)
        if not chunk:
            raise ConnectionError("Client disconnected before sending header")
        header += chunk

    filename, filesize_str = header.decode().strip().split("|")
    filesize = int(filesize_str)
    filename = os.path.basename(filename)
    return filename, filesize

def receive_file(client_socket, filepath, filesize):
    received_bytes = 0
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    # Receive IV first (16 bytes)
    iv = client_socket.recv(16)
    cipher = create_cipher(iv)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    with open(filepath, "wb") as f:
        while True:
            chunk = client_socket.recv(CHUNK_SIZE)
            if not chunk:
                break
            decrypted = decrypt_chunk(chunk, decryptor, unpadder)
            f.write(decrypted)
            received_bytes += len(chunk)  # We track encrypted size for debug

        # Finalize decryption
        final = finalize_decryption(decryptor, unpadder)
        f.write(final)

    return received_bytes

def handle_client(client_socket, addr, on_file_received=None):
    sender_ip = addr[0]
    try:
        client_socket.settimeout(30)
        filename, filesize = read_header(client_socket)
        save_path = os.path.join("received", filename)

        received_bytes = receive_file(client_socket, save_path, filesize)

        print(f"[✓] File received and decrypted: {filename} from {sender_ip}")
        if on_file_received:
            on_file_received(filename, filesize, sender_ip)

    except Exception as e:
        print(f"[!] Error handling client {sender_ip}: {e}")

    finally:
        client_socket.close()

def start_tcp_server(port=DEFAULT_PORT, on_file_received=None):
    def _server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', port))
        server.listen(5)
        print(f"[+] TCP server listening on port {port}")

        while True:
            client_socket, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client_socket, addr, on_file_received),
                daemon=True
            ).start()

    threading.Thread(target=_server_loop, daemon=True).start()

