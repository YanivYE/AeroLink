# server.py
import socket
import threading
import os

def handle_client(client_socket, addr, callback=None):
    sender_ip = addr[0]

    # Step 1: Receive header
    header = b""
    while not header.endswith(b"\n"):
        chunk = client_socket.recv(1)
        if not chunk:
            break
        header += chunk
    try:
        filename, filesize = header.decode().strip().split("|")
        filesize = int(filesize)
    except:
        client_socket.close()
        return

    # Step 2: Prepare to write the file
    save_path = os.path.join("received", filename)
    os.makedirs("received", exist_ok=True)
    received_bytes = 0

    with open(save_path, "wb") as f:
        while received_bytes < filesize:
            chunk = client_socket.recv(min(4096, filesize - received_bytes))
            if not chunk:
                break
            f.write(chunk)
            received_bytes += len(chunk)

    # Step 3: Notify via callback or print
    msg = f"📁 Received file '{filename}' ({filesize} bytes) from {sender_ip}"
    if callback:
        callback(msg)
    else:
        print(msg)

    client_socket.close()

def start_tcp_server(port=8888, on_message_received=None):
    def _server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', port))
        server.listen(5)
        print(f"[+] TCP server listening on port {port}")

        while True:
            client_socket, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client_socket, addr, on_message_received),
                daemon=True
            ).start()

    thread = threading.Thread(target=_server_loop, daemon=True)
    thread.start()
