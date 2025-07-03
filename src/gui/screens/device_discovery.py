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
        self.loading = None
        self.device_buttons = []
        self.selected_device_name = None
        self.selected_ip = None
        self.selected_port = None
        self.discovery_active = True  # flag to safely stop discovery if UI destroyed

        self._build_ui()
        self._start_discovery()

    def _build_ui(self):
        from src.gui.screens.select_mode import ModeSelectionScreen

        ttk.Label(self, text="🔎 Scanning for AeroLink Devices...", font=("Segoe UI", 14)).pack(pady=15)

        # Loading bar container - centered with fixed width
        loading_frame = ttk.Frame(self)
        loading_frame.pack(side="bottom", pady=15)
        self.loading = ttk.Progressbar(loading_frame, mode="indeterminate", length=400)
        self.loading.pack()
        self.loading.start()

        # Devices container with border
        self.device_box = ttk.Frame(self, bootstyle="secondary", borderwidth=2, relief="groove")
        self.device_box.pack(padx=40, pady=10, fill="both", expand=False)

        self.device_listbox = tk.Listbox(
            self.device_box, height=8, font=("Segoe UI", 12),
            activestyle="none", selectbackground="#198754", selectforeground="white",
            highlightthickness=0, bd=0
        )
        self.device_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.device_listbox.bind("<<ListboxSelect>>", self._on_device_select)

        self.select_button = ttk.Button(self, text="Select", bootstyle=SUCCESS, width=20, command=self._confirm_selection)
        self.select_button.pack(pady=(5, 15))
        self.select_button["state"] = "disabled"

        # Back button
        ttk.Button(self, text="⬅ Back", bootstyle="secondary", command=lambda: self._go_back(ModeSelectionScreen)).pack(side="bottom", anchor="w", padx=20, pady=5)

    def _start_discovery(self):
        # Clear previously discovered devices to avoid duplicates
        discovered_devices.clear()
        threading.Thread(target=self._discover_devices, daemon=True).start()

    def _discover_devices(self):
        # Continuous discovery
        start_discovery(timeout=None, on_device_discovered=self._add_device)

    def _add_device(self, device_name, ip, port):
        if not self.discovery_active:
            return
        self.after(0, lambda: self._add_device_ui(device_name, ip, port))

    def _add_device_ui(self, device_name, ip, port):
        if not self.device_listbox.winfo_exists():
            return

        display_text = f"{device_name} - {ip}:{port}"
        existing = self.device_listbox.get(0, tk.END)

        if display_text not in existing:
            self.device_listbox.insert(tk.END, display_text)
            discovered_devices[display_text] = (ip, port)

    def _on_device_select(self, event):
        sel = self.device_listbox.curselection()
        if sel:
            index = sel[0]
            device_name = self.device_listbox.get(index)
            self.selected_device_name = device_name
            self.selected_ip, self.selected_port = discovered_devices[device_name]
            self.select_button["state"] = "normal"
        else:
            self.selected_device_name = None
            self.selected_ip = None
            self.selected_port = None
            self.select_button["state"] = "disabled"

    def _confirm_selection(self):
        if self.selected_device_name:
            self.discovery_active = False  # stop further updates
            if self.loading and self.loading.winfo_exists():
                self.loading.stop()
                self.loading.pack_forget()
            self.app.selected_device = (self.selected_device_name, self.selected_ip, self.selected_port)
            self.app._navigate_to(FileTransferScreen)

    def _go_back(self, screen):
        self.discovery_active = False
        self.app._navigate_to(screen)
