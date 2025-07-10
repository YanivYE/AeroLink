import os
import socket

CHUNK_SIZE = 4096

def send_file(ip, port, filepath):
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)

        # 1. Connect to peer
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        # 2. Send metadata (filename and size)
        header = f"{filename}|{filesize}\n"
        sock.sendall(header.encode())

        # 3. Send file content in chunks
        with open(filepath, "rb") as f:
            sent = 0
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                # Optional: Print progress
                percent = (sent / filesize) * 100
                print(f"Sending... {percent:.2f}%", end="\r")

        print(f"\n✅ File '{filename}' sent to {ip}:{port}")

        sock.close()

    except Exception as e:
        print(f"[!] Error sending file: {e}")
