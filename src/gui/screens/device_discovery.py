import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import threading

from src.discovery import start_discovery, discovered_devices
from src.gui.screens.file_transfer import FileTransferScreen

class DeviceDiscoveryScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.device_frames = {}

        ttk.Label(self, text="📡 Discovering Devices...", font=("Segoe UI", 16, "bold")).pack(pady=10)
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=20)

        self.loading = ttk.Progressbar(self, mode="indeterminate", bootstyle="info")
        self.loading.pack(pady=(5, 10))
        self.loading.start()

        ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=lambda: app._navigate_to(app.__class__)).place(x=20, y=560)

        threading.Thread(target=self._discover_devices, daemon=True).start()

    def _discover_devices(self):
        start_discovery(timeout=6, on_device_discovered=self._add_device)

        self.app.after(0, self._stop_loading)

    def _stop_loading(self):
        if hasattr(self, "loading") and self.loading.winfo_exists():
            self.loading.stop()
            self.loading.pack_forget()

    def _add_device(self, device_name, ip, port):
        if device_name in self.device_frames:
            return

        frame = ttk.Frame(self.container, bootstyle="dark")
        frame.pack(fill="x", pady=8, padx=10, ipady=8)

        ttk.Label(frame, text="🖥️", font=("Segoe UI Emoji", 14)).pack(side="left", padx=10)
        ttk.Label(frame, text=device_name, font=("Segoe UI", 12, "bold")).pack(side="left", expand=True)

        ttk.Button(frame, text="Select", width=10, bootstyle=SUCCESS, command=lambda: self._select_device(device_name)).pack(side="right", padx=10)

        self.device_frames[device_name] = frame

    def _select_device(self, device_name):
        self.app.selected_device = device_name
        self.app._navigate_to(FileTransferScreen)
