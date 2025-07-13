import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY, SECONDARY
from src.gui.widgets import load_logo
from src.gui.screens.device_discovery import DeviceDiscoveryScreen

class ModeSelectionScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # Load and place logo
        logo = load_logo(self)
        if logo:
            logo.pack(pady=(20, 10))

        # Title
        ttk.Label(
            self,
            text="Welcome to AeroLink",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(0, 10))

        ttk.Label(
            self,
            text="Select an operation mode",
            font=("Segoe UI", 12)
        ).pack(pady=(0, 25))

        # Mode Buttons
        ttk.Button(
            self,
            text="Discover & Send File",
            width=35,
            bootstyle=PRIMARY,
            command=lambda: self.app._navigate_to(DeviceDiscoveryScreen)
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Passive Mode (Receive Files)",
            width=35,
            bootstyle=SECONDARY,
            command=self._load_passive_mode
        ).pack(pady=5)

    def _load_passive_mode(self):
        from src.gui.screens.passive_mode import PassiveModeScreen
        self.app._navigate_to(PassiveModeScreen)


