import os
import socket
import time

from src.constants import CHUNK_SIZE

def send_file(ip, port, filepath):
    sock = None
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

        # 2. Send file in chunks with throttled progress output
        sent = 0
        last_print = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                now = time.time()
                if now - last_print > 0.5:
                    print(f"[DEBUG] Sent {sent}/{filesize} bytes", end="\r")
                    last_print = now

        print()  # newline after progress
        print(f"File '{filename}' sent successfully to {ip}:{port}")

    except Exception as e:
        print(f"[!] Failed to send file: {e}")

    finally:
        if sock:
            sock.close()
