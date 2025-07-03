from ttkbootstrap import Frame, Label, Button
from tkinter.scrolledtext import ScrolledText
from ttkbootstrap.constants import SECONDARY
from src.advertiser import start_advertising
from src.server import start_tcp_server

class PassiveModeScreen(Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.zeroconf = None

        self._build_ui()

    def _build_ui(self):
        from src.advertiser import start_advertising
        from src.server import start_tcp_server
        from src.gui.screens.select_mode import ModeSelectionScreen

        Label(self, text="🕊️ Passive Mode", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        Label(self, text="Waiting for incoming files...", font=("Segoe UI", 12)).pack(pady=(0, 15))

        self.msg_log = ScrolledText(self, width=80, height=20, font=("Consolas", 10), wrap="word")
        self.msg_log.config(background="#2b2b2b", foreground="white", insertbackground="white", borderwidth=1, relief="flat")
        self.msg_log.pack(pady=10)

        Button(self, text="⬅ Back", width=25, bootstyle=SECONDARY,
                   command=lambda: self._go_back(ModeSelectionScreen)).pack(pady=5)

        start_tcp_server()
        self.zeroconf = start_advertising()

    def _go_back(self, screen):
        if self.zeroconf:
            self.zeroconf.close()
        self.app._navigate_to(screen)
