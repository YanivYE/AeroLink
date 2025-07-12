import socket
import threading
from src.constants import DEFAULT_PORT

def handle_client(client_socket, addr):
    print(f"[<] Connection from {addr}")
    data = client_socket.recv(4096)
    print(f"[✓] Received: {data.decode()}")
    client_socket.close()

def start_tcp_server(port=DEFAULT_PORT):
    def _server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the port
        server.bind(('', port))
        server.listen(5)
        print(f"[+] TCP server listening on port {port}")

        while True:
            client_socket, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

    threading.Thread(target=_server_loop, daemon=True).start()
