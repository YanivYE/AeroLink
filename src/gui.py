import threading
from discovery import start_discovery, discovered_devices
from communication import send_file
from advertiser import start_advertising
from server import start_tcp_server

import tkinter as tk
from tkinter.filedialog import askopenfilename
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

class AeroLinkApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cyborg")  # Other themes: 'cyborg', 'superhero', etc.
        self.title("🚀 AeroLink")
        self.geometry("600x500")
        self.resizable(False, False)

        self.zeroconf = None

        self.mode_frame = ttk.Frame(self)
        self.mode_frame.pack(pady=30)

        ttk.Label(self.mode_frame, text="Select Mode", font=("Segoe UI", 14)).pack(pady=5)
        ttk.Button(self.mode_frame, text="🔍 Discover & Send", bootstyle=PRIMARY, command=self.active_mode).pack(pady=10, ipadx=10)
        ttk.Button(self.mode_frame, text="🕊️ Passive Mode", bootstyle=SECONDARY, command=self.passive_mode).pack(ipadx=10)

        self.device_listbox = None
        self.msg_entry = None
        self.msg_log = None

    def active_mode(self):
        self._clear()
        ttk.Label(self, text="Scanning for devices...", font=("Segoe UI", 12)).pack(pady=10)
        threading.Thread(target=self._discover_and_list, daemon=True).start()

    def _discover_and_list(self):
        start_discovery(timeout=10)
        self.after(0, self._build_active_ui)

    def _build_active_ui(self):
        self._clear()

        ttk.Label(self, text="Discovered Devices:", font=("Segoe UI", 12)).pack(pady=10)
        self.device_listbox = tk.Listbox(
            self,
            height=8,
            width=60,
            bg="#2b2b2b",           # dark background
            fg="white",             # text color
            selectbackground="#1f6aa5",  # highlight selected item
            selectforeground="white",
            highlightbackground="#444",  # border outline color
            relief="flat",
            borderwidth=1
        )
        self.device_listbox.pack(pady=5)

        for name, (ip, port) in discovered_devices.items():
            self.device_listbox.insert(END, f"{name} - {ip}:{port}")

        self.msg_entry = ttk.Entry(self, width=40)
        self.msg_entry.pack(pady=10)

        ttk.Button(self, text="Send Message", bootstyle=SUCCESS, command=self._send_selected).pack()

        ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=self._reset).pack(pady=10)

    def _send_selected(self):
        sel = self.device_listbox.curselection()
        if not sel:
            return

        idx = sel[0]
        (_, (ip, port)) = list(discovered_devices.items())[idx]

        # Ask user to select a file
        filepath = askopenfilename(title="Select a file to send")

        if not filepath:
            return  # User cancelled

        send_file(ip, port, filepath)

    def passive_mode(self):
        self._clear()
        start_tcp_server()
        self.zeroconf = start_advertising()

        ttk.Label(self, text="Passive Mode - Waiting for messages", font=("Segoe UI", 12)).pack(pady=10)
        self.msg_log = ScrolledText(
            self,
            width=70,
            height=20,
            autohide=True,
            font=("Consolas", 10),
            wrap="word"
        )
        self.msg_log.config(
            background="#2b2b2b",
            foreground="white",
            insertbackground="white",  # caret color
            borderwidth=1,
            relief="flat"
        )

        self.msg_log.pack(pady=10)

        ttk.Button(self, text="⬅ Back", bootstyle=SECONDARY, command=self._reset).pack(pady=10)
        self._poll_messages()

    def _poll_messages(self):
        # You could hook this to show live messages from the TCP server (needs callback)
        self.after(1000, self._poll_messages)

    def _reset(self):
        if self.zeroconf:
            self.zeroconf.close()
            self.zeroconf = None
        self._clear()
        self.__init__()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = AeroLinkApp()
    app.mainloop()
