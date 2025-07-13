import os
import socket
import time

from constants import CHUNK_SIZE

def send_file(ip, port, filepath):
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        print(f"[DEBUG] Connecting to {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        # 1. Send header: filename|filesize\n
        header = f"{filename}|{filesize}\n"
        sock.sendall(header.encode())
        print(f"[DEBUG] Sent header: {repr(header.strip())}")

        time.sleep(0.05)  # let header flush

        # 2. Send file in chunks
        with open(filepath, "rb") as f:
            sent = 0
            while (chunk := f.read(CHUNK_SIZE)):
                sock.sendall(chunk)
                sent += len(chunk)
                print(f"[DEBUG] Sent {sent}/{filesize} bytes", end="\r")

        sock.close()
        print(f"\n✅ File '{filename}' sent successfully to {ip}:{port}")

    except Exception as e:
        print(f"[!] Failed to send file: {e}")
