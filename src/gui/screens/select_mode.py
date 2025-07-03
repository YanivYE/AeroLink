import ttkbootstrap as ttk
from src.gui.widgets import load_logo
from src.gui.screens.device_discovery import DeviceDiscoveryScreen
from src.gui.screens.passive_mode import PassiveModeScreen

class ModeSelectionScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app

        logo = load_logo(self)
        if logo:
            logo.pack(pady=(20, 10))

        ttk.Label(self, text="Welcome to AeroLink", font=("Segoe UI", 20, "bold")).pack(pady=(0, 10))
        ttk.Label(self, text="Select an operation mode", font=("Segoe UI", 12)).pack(pady=(0, 25))

        ttk.Button(self, text="🔍 Discover & Send File", width=35, bootstyle="primary", command=lambda: app._navigate_to(DeviceDiscoveryScreen)).pack(pady=10)
        ttk.Button(self, text="🕊️ Passive Mode (Receive Files)", width=35, bootstyle="secondary", command=lambda: app._navigate_to(PassiveModeScreen)).pack(pady=5)
