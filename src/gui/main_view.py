import tkinter as tk
from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk

from src.gui.screens.select_mode import ModeSelectionScreen

class AeroLinkApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Style & layout
        self.style = ttk.Style("darkly")
        self.title("🚀 AeroLink")
        self.geometry("700x600")
        self.resizable(False, False)

        # App-wide state
        self.selected_device = None
        self.zeroconf = None
        self.msg_log = None

        # Toast/status notification bar
        self.toast_label = ttk.Label(self, text="", font=("Segoe UI", 10), bootstyle="info")
        self.toast_label.place(x=10, y=570)

        # Start on mode selection screen
        self._navigate_to(ModeSelectionScreen)

    def _navigate_to(self, screen_class):
        """
        Switch to a new screen (Frame class).
        """
        self._clear_screen()
        screen = screen_class(app=self)
        screen.pack(fill="both", expand=True)

    def _clear_screen(self):
        for widget in self.winfo_children():
            if widget is not self.toast_label:
                widget.destroy()
        if self.toast_label.winfo_exists():
            self.toast_label.place_forget()

    def _show_toast(self, message, style="info"):
        """
        Display a temporary message at the bottom of the window.
        """
        self.toast_label.configure(text=message, bootstyle=style)
        self.toast_label.place(x=10, y=570)
        self.after(4000, lambda: self.toast_label.configure(text=""))
