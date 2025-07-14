import os
import socket
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES
from ttkbootstrap.constants import *

from src.communication import send_file

class FileTransferScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.file_path = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        ttk.Label(
            self,
            text="Send a File",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 10))

        # File selector row
        file_frame = ttk.Frame(self)
        file_frame.pack(pady=(0, 10))

        ttk.Entry(
            file_frame,
            textvariable=self.file_path,
            width=45,
            state="readonly"
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            file_frame,
            text="Browse",
            bootstyle=INFO,
            command=self._choose_file
        ).pack(side="left")

        # Drag-and-drop area
        drop_box = ttk.Label(
            self,
            text="Drop file here",
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

        # Action buttons
        ttk.Button(
            self,
            text="Send File",
            width=25,
            bootstyle=SUCCESS,
            command=self._send_file
        ).pack(pady=(5, 10))

        self.status_label = ttk.Label(self, text="", font=("Segoe UI", 10))
        self.status_label.pack(pady=(5, 10))

        ttk.Button(
            self,
            text="⬅ Back",
            width=25,
            bootstyle=SECONDARY,
            command=self._go_back
        ).pack()


    def _choose_file(self):
        path = filedialog.askopenfilename()
        self._set_display_path(path)

    def _on_file_drop(self, event):
        # Handle dropped file paths with braces or spaces
        raw_path = event.data.strip("{}")
        self._set_display_path(raw_path)

    def _set_display_path(self, path):
        if path and os.path.exists(path):
            # Truncate for display if needed
            display_path = path if len(path) < 60 else f"...{path[-57:]}"
            self.file_path.set(display_path)
            self._full_path = path
        else:
            self.file_path.set("")
            self._full_path = None

    def _send_file(self):
        path = getattr(self, "_full_path", None)

        if not path or not os.path.isfile(path):
            self._set_status("Invalid file path", "danger")
            return

        if not self.app.selected_device:
            self._set_status("No device selected", "danger")
            return

        device_name, ip, port = self.app.selected_device

        try:
            send_file(ip, port, path)
            self._set_status(f"Sent {os.path.basename(path)} successfully", "success")

        except Exception as e:
            self._set_status(f"Send failed: {e}", "danger")

    def _go_back(self):
        from src.gui.screens.select_mode import ModeSelectionScreen
        self.app._navigate_to(ModeSelectionScreen)

    def _set_status(self, message, level="info", duration=3000):
        colors = {
            "success": "green",
            "danger": "red",
            "info": "blue",
        }
        color = colors.get(level, "black")
        self.status_label.configure(text=message, foreground=color)

        self.after(duration, lambda: self.status_label.configure(text=""))
