import threading
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
import os
import socket

from src.discovery import start_discovery, discovered_devices
from src.communication import send_message
from src.advertiser import start_advertising
from src.server import start_tcp_server
from src.gui.widgets import load_logo

class AeroLinkApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.style = ttk.Style("darkly")
        self.title("🚀 AeroLink")
        self.geometry("700x600")
        self.resizable(False, False)

        self.zeroconf = None
        self.device_buttons = []
        self.file_path = tk.StringVar()
        self.msg_log = None

        self.toast_label = ttk.Label(self, text="", font=("Segoe UI", 10), bootstyle="info")
        self.toast_label.place(x=10, y=570)

        self._build_mode_selection()

    def _build_mode_selection(self):
        self._clear()

        logo = load_logo(self)
        if logo:
            logo.pack(pady=(20, 10))

        ttk.Label(self, text="Welcome to AeroLink", font=("Segoe UI", 20, "bold")).pack(pady=(0, 10))
        ttk.Label(self, text="Select an operation mode to get started", font=("Segoe UI", 12)).pack(pady=(0, 25))

        ttk.Button(self, text="🔍 Discover & Send File", width=35, bootstyle=PRIMARY, command=self.active_mode).pack(pady=10)
        ttk.Button(self, text="🕊️ Passive Mode (Receive Files)", width=35, bootstyle=SECONDARY, command=self.passive_mode).pack(pady=5)

    def active_mode(self):
        self._clear()
        ttk.Label(self, text="🔎 Scanning for AeroLink Devices...", font=("Segoe UI", 14)).pack(pady=15)
        threading.Thread(target=self._discover_and_list, daemon=True).start()

    def _discover_and_list(self):
        start_discovery(timeout=5)
        self.after(0, self._build_active_ui)

    def _build_active_ui(self):
        self._clear()
        ttk.Label(self, text="📡 Discovered Devices", font=("Segoe UI", 16, "bold")).pack(pady=(15, 10))

        container = ttk.Frame(self)
        container.pack(pady=(0, 15), fill="x")

        self.device_buttons.clear()
        for name, (device_name, ip, port) in discovered_devices.items():
            device_frame = ttk.Frame(container, bootstyle="dark")
            device_frame.pack(fill="x", pady=8, padx=40, ipady=10)

            icon = ttk.Label(device_frame, text="🖥️", font=("Segoe UI Emoji", 14))
            icon.pack(side="left", padx=(10, 5))

            label = ttk.Label(device_frame, text=device_name, font=("Segoe UI", 12, "bold"), anchor="w")
            label.pack(side="left", fill="x", expand=True)

            button = ttk.Button(device_frame, text="Select", bootstyle=SUCCESS, width=10, command=lambda n=device_name: self._select_device(n))
            button.pack(side="right", padx=(0, 10))

            self.device_buttons.append((device_name, button))

        file_frame = ttk.Frame(self)
        file_frame.pack(pady=(0, 10))

        ttk.Entry(file_frame, textvariable=self.file_path, width=45, state="readonly").pack(side="left", padx=(0, 10))
        ttk.Button(file_frame, text="📁 Browse", bootstyle=INFO, command=self._choose_file).pack(side="left")

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

        back_button = ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=self._build_mode_selection)
        back_button.place(x=20, y=560)

    def _select_device(self, device_name):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            self._show_toast("Invalid file path", "danger")
            return

        (ip, port) = discovered_devices[device_name]

        try:
            with open(file_path, "rb") as f:
                data = f.read()
            filename = os.path.basename(file_path).encode()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.sendall(filename + b"\0" + data)
            sock.close()
            self._show_toast(f"Sent {filename.decode()} successfully", "success")
        except Exception as e:
            self._show_toast(f"Send failed: {e}", "danger")

    def _choose_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path if len(path) < 60 else "..." + path[-57:])

    def _on_file_drop(self, event):
        path = event.data.strip("{}")
        self.file_path.set(path if len(path) < 60 else "..." + path[-57:])

    def passive_mode(self):
        self._clear()
        start_tcp_server()
        self.zeroconf = start_advertising()

        ttk.Label(self, text="🕊️ Passive Mode", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        ttk.Label(self, text="Waiting for incoming files...", font=("Segoe UI", 12)).pack(pady=(0, 15))

        self.msg_log = ScrolledText(self, width=80, height=20, font=("Consolas", 10), wrap="word")
        self.msg_log.config(
            background="#2b2b2b",
            foreground="white",
            insertbackground="white",
            borderwidth=1,
            relief="flat"
        )
        self.msg_log.pack(pady=10)

        ttk.Button(self, text="⬅ Back", width=25, bootstyle=SECONDARY, command=self._build_mode_selection).pack(pady=5)
        self._poll_messages()

    def _poll_messages(self):
        self.after(1000, self._poll_messages)

    def _clear(self):
        for widget in self.winfo_children():
            if widget is not self.toast_label:
                widget.destroy()
        if self.toast_label.winfo_exists():
            self.toast_label.place_forget()

    def _show_toast(self, message, style="info"):
        self.toast_label.configure(text=message, bootstyle=style)
        self.toast_label.place(x=10, y=570)
        self.after(4000, lambda: self.toast_label.configure(text=""))