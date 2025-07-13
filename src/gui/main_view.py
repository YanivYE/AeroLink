from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk

class AeroLinkApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        # Style & layout
        self.style = ttk.Style("darkly")
        self.title("✈️ AeroLink")
        self.geometry("700x600")
        self.resizable(False, False)

        # App-wide state
        self.selected_device = None
        self.zeroconf = None
        self.msg_log = None

        # Toast/status notification bar
        self.toast_label = ttk.Label(
            self,
            text="",
            font=("Segoe UI", 10),
            bootstyle="info",
            anchor="w"
        )
        self.toast_label.place(x=10, y=570, width=680)  # Fixed width for nicer look

        # Start on mode selection screen
        self._navigate_to_mode_selection()

    def _navigate_to(self, screen_class):
        """
        Switch to a new screen (Frame subclass).
        """
        self._clear_screen()
        self.current_screen = screen_class(app=self)
        self.current_screen.pack(fill="both", expand=True)

    def _clear_screen(self):
        """
        Destroy all widgets except the toast label.
        """
        for widget in self.winfo_children():
            if widget is not self.toast_label:
                widget.destroy()
        # Make sure toast label is placed again after clearing
        if self.toast_label.winfo_exists():
            self.toast_label.place(x=10, y=570, width=680)

    def _show_toast(self, message, style="info"):
        """
        Display a temporary message at the bottom of the window.
        """
        self.toast_label.configure(text=message, bootstyle=style)
        self.toast_label.place(x=10, y=570, width=680)
        self.after(4000, self._clear_toast)

    def _clear_toast(self):
        self.toast_label.configure(text="")
        self.toast_label.place_forget()

    def _navigate_to_mode_selection(self):
        """
        Lazy import ModeSelectionScreen to avoid circular imports,
        then navigate to it.
        """
        from src.gui.screens.select_mode import ModeSelectionScreen
        self._navigate_to(ModeSelectionScreen)
