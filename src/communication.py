import socket

def send_message(ip, port, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, port))
            sock.sendall(message.encode())
        print(f"[✓] Sent message to {ip}:{port}")
    except Exception as e:
        print(f"[!] Failed to send: {e}")
