import threading
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

from src.discovery import start_discovery, discovered_devices
from src.communication import send_message
from src.advertiser import start_advertising
from src.server import start_tcp_server
from src.gui.widgets import load_logo

class AeroLinkApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("🚀 AeroLink")
        self.geometry("650x550")
        self.resizable(False, False)

        self.zeroconf = None

        self.device_listbox = None
        self.msg_entry = None
        self.msg_log = None

        self._build_mode_selection()

    def _build_mode_selection(self):
        self._clear()

        # Top logo
        logo = load_logo(self)
        if logo:
            logo.pack(pady=(20, 5))

        ttk.Label(self, text="Welcome to AeroLink", font=("Segoe UI", 18, "bold")).pack(pady=(5, 10))
        ttk.Label(self, text="Select Operation Mode", font=("Segoe UI", 12)).pack(pady=(0, 15))

        ttk.Button(self, text="🔍 Discover & Send", width=30, bootstyle=PRIMARY, command=self.active_mode).pack(pady=5, ipadx=5)
        ttk.Button(self, text="🕊️ Passive Mode", width=30, bootstyle=SECONDARY, command=self.passive_mode).pack(pady=5, ipadx=5)

    def active_mode(self):
        self._clear()
        ttk.Label(self, text="🔎 Scanning for AeroLink Devices...", font=("Segoe UI", 12)).pack(pady=10)
        threading.Thread(target=self._discover_and_list, daemon=True).start()

    def _discover_and_list(self):
        start_discovery(timeout=5)
        self.after(0, self._build_active_ui)

    def _build_active_ui(self):
        self._clear()

        ttk.Label(self, text="📡 Discovered Devices", font=("Segoe UI", 14)).pack(pady=(10, 5))

        self.device_listbox = tk.Listbox(
            self,
            height=10,
            width=60,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f6aa5",
            selectforeground="white",
            highlightbackground="#444",
            relief="flat",
            borderwidth=1
        )
        self.device_listbox.pack(pady=(0, 10))

        for name, (ip, port) in discovered_devices.items():
            self.device_listbox.insert(tk.END, f"{name} - {ip}:{port}")

        self.msg_entry = ttk.Entry(self, width=50)
        self.msg_entry.pack(pady=10)

        ttk.Button(self, text="📤 Send Message", bootstyle=SUCCESS, command=self._send_selected).pack(pady=(0, 15))
        ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=self._build_mode_selection).pack()

    def _send_selected(self):
        sel = self.device_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        (_, (ip, port)) = list(discovered_devices.items())[idx]
        message = self.msg_entry.get()
        send_message(ip, port, message)
        self.msg_entry.delete(0, tk.END)

    def passive_mode(self):
        self._clear()
        start_tcp_server()
        self.zeroconf = start_advertising()

        ttk.Label(self, text="🕊️ Passive Mode", font=("Segoe UI", 14)).pack(pady=(15, 5))
        ttk.Label(self, text="Waiting for incoming messages...", font=("Segoe UI", 10)).pack(pady=(0, 10))

        self.msg_log = ScrolledText(
            self,
            width=70,
            height=20,
            font=("Consolas", 10),
            wrap="word"
        )
        self.msg_log.config(
            background="#2b2b2b",
            foreground="white",
            insertbackground="white",
            borderwidth=1,
            relief="flat"
        )
        self.msg_log.pack(pady=10)

        ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=self._build_mode_selection).pack(pady=5)
        self._poll_messages()

    def _poll_messages(self):
        # Optional: hook this up with TCP server's incoming message log
        self.after(1000, self._poll_messages)

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()
