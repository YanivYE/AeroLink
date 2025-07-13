import threading
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from src.discovery import start_discovery, discovered_devices
from src.gui.screens.file_transfer import FileTransferScreen

class DeviceDiscoveryScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app

        self.loading = None
        self.device_listbox = None
        self.select_button = None

        self.discovery_active = True
        self.selected_device = None

        self._build_ui()
        self._start_discovery()

    def _build_ui(self):
        ttk.Label(
            self,
            text="🔎 Scanning for AeroLink Devices...",
            font=("Segoe UI", 14)
        ).pack(pady=15)

        # Loading animation
        self.loading = ttk.Progressbar(
            self, mode="indeterminate", length=400
        )
        self.loading.pack(pady=(0, 10))
        self.loading.start()

        # Container for device list
        self.device_box = ttk.Frame(
            self, bootstyle="secondary", borderwidth=2, relief="groove"
        )
        self.device_box.pack(padx=40, pady=10, fill="both")

        self.device_listbox = tk.Listbox(
            self.device_box,
            height=8,
            font=("Segoe UI", 12),
            activestyle="none",
            selectbackground="#198754",
            selectforeground="white",
            highlightthickness=0,
            bd=0
        )
        self.device_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.device_listbox.bind("<<ListboxSelect>>", self._on_selection_change)

        # Select button
        self.select_button = ttk.Button(
            self,
            text="Select Device",
            bootstyle=SUCCESS,
            width=20,
            command=self._confirm_selection
        )
        self.select_button.pack(pady=(5, 15))
        self.select_button.config(state="disabled")

        # Back button
        ttk.Button(
            self,
            text="⬅ Back",
            bootstyle=SECONDARY,
            command=lambda: self._go_back()
        ).pack(side="bottom", anchor="w", padx=20, pady=5)

    def _start_discovery(self):
        discovered_devices.clear()
        threading.Thread(target=self._discover_devices, daemon=True).start()

    def _discover_devices(self):
        start_discovery(timeout=None, on_device_discovered=self._on_device_discovered)

    def _on_device_discovered(self, name, ip, port):
        if not self.discovery_active:
            return
        self.after(0, lambda: self._add_device_to_list(name, ip, port))

    def _add_device_to_list(self, name, ip, port):
        if not self.device_listbox or not self.device_listbox.winfo_exists():
            return

        display_text = f"{name} - {ip}:{port}"
        current_items = self.device_listbox.get(0, tk.END)

        if display_text not in current_items:
            self.device_listbox.insert(tk.END, display_text)
            discovered_devices[display_text] = (ip, port)

    def _on_selection_change(self, event=None):
        selection = self.device_listbox.curselection()
        if selection:
            index = selection[0]
            device_label = self.device_listbox.get(index)
            self.selected_device = (device_label, *discovered_devices[device_label])
            self.select_button.config(state="normal")
        else:
            self.selected_device = None
            self.select_button.config(state="disabled")

    def _confirm_selection(self):
        if self.selected_device:
            self.discovery_active = False
            if self.loading and self.loading.winfo_exists():
                self.loading.stop()
                self.loading.pack_forget()

            self.app.selected_device = self.selected_device
            self.app._navigate_to(FileTransferScreen)

    def _go_back(self, screen_cls=None):
        if screen_cls is None:
            from src.gui.screens.select_mode import ModeSelectionScreen
            screen_cls = ModeSelectionScreen
        self.discovery_active = False
        self.app._navigate_to(screen_cls)
