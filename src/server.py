import socket
import threading
from src.constants import CHUNK_SIZE, DEFAULT_PORT
import os


def handle_client(client_socket, addr, on_file_received=None):
    sender_ip = addr[0]

    # Read header first
    header = b""
    while not header.endswith(b"\n"):
        chunk = client_socket.recv(1)
        if not chunk:
            break
        header += chunk

    try:
        filename, filesize = header.decode().strip().split("|")
        filesize = int(filesize)
    except Exception as e:
        print(f"[!] Failed to parse header: {header!r} — {e}")
        client_socket.close()
        return

    save_path = os.path.join("received", filename)
    os.makedirs("received", exist_ok=True)
    received_bytes = 0

    with open(save_path, "wb") as f:
        while received_bytes < filesize:
            chunk = client_socket.recv(min(CHUNK_SIZE, filesize - received_bytes))
            if not chunk:
                break
            f.write(chunk)
            received_bytes += len(chunk)

    print(f"[✓] File received: {filename} ({filesize} bytes) from {sender_ip}")

    if on_file_received:
        on_file_received(filename, filesize, sender_ip)

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
            threading.Thread(target=handle_client, args=(client_socket, addr, on_file_received), daemon=True).start()

    threading.Thread(target=_server_loop, daemon=True).start()
