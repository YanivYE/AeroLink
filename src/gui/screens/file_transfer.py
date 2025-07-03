import ttkbootstrap as ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES
import os
import socket
import tkinter as tk
from ttkbootstrap.constants import *

from src.discovery import discovered_devices

class FileTransferScreen(ttk.Frame):
    def __init__(self, app):
        from src.gui.screens.select_mode import ModeSelectionScreen

        super().__init__(app)
        self.app = app
        self.file_path = tk.StringVar()

        ttk.Label(self, text="📁 Send a File", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))

        file_frame = ttk.Frame(self)
        file_frame.pack(pady=(0, 10))

        ttk.Entry(file_frame, textvariable=self.file_path, width=45, state="readonly").pack(side="left", padx=(0, 10))
        ttk.Button(file_frame, text="Browse", bootstyle=INFO, command=self._choose_file).pack(side="left")

        drop_box = ttk.Label(
            self,
            text="⬇️ Drop file here",
            relief="ridge",
            borderwidth=2,
            width=60,
            anchor="center",
            padding=20,
            font=("Segoe UI", 10)
        )
        drop_box.pack(pady=15)
        drop_box.drop_target_register(DND_FILES)
        drop_box.dnd_bind('<<Drop>>', self._on_file_drop)

        ttk.Button(self, text="📤 Send File", width=25, bootstyle=SUCCESS, command=self._send_file).pack(pady=(5, 10))
        ttk.Button(self, text="⬅ Back", width=25, bootstyle=SECONDARY, command=lambda: app._navigate_to(ModeSelectionScreen)).pack()

    def _choose_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path if len(path) < 60 else "..." + path[-57:])

    def _on_file_drop(self, event):
        path = event.data.strip("{}")
        self.file_path.set(path if len(path) < 60 else "..." + path[-57:])

    def _send_file(self):
        path = self.file_path.get()
        if not path or not os.path.exists(path):
            self.app._show_toast("Invalid file path", "danger")
            return

        device_name = self.app.selected_device
        ip, port = discovered_devices[device_name]

        try:
            with open(path, "rb") as f:
                data = f.read()
            filename = os.path.basename(path).encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.sendall(filename + b"\0" + data)
            sock.close()
            self.app._show_toast(f"Sent {filename.decode()} successfully", "success")
        except Exception as e:
            self.app._show_toast(f"Send failed: {e}", "danger")
