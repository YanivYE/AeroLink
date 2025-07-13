import os
from tkinter import messagebox, filedialog, Listbox
from tkinter.scrolledtext import ScrolledText
from ttkbootstrap import Frame, Label, Button
from ttkbootstrap.constants import SECONDARY

from src.advertiser import start_advertising
from src.server import start_tcp_server

class PassiveModeScreen(Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.zeroconf = None
        self.received_files = []  # List of received filenames

        self._build_ui()
        self._start_server()

    def _build_ui(self):
        Label(self, text="Passive Mode", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        Label(self, text="Waiting for incoming files...", font=("Segoe UI", 12)).pack(pady=(0, 15))

        # Message log
        self._msg_log = ScrolledText(
            self,
            width=80,
            height=16,
            font=("Consolas", 10),
            wrap="word",
            background="#2b2b2b",
            foreground="white",
            insertbackground="white",
            borderwidth=1,
            relief="flat"
        )
        self._msg_log.pack(pady=10, padx=10, fill='both', expand=False)

        # File list
        self._file_listbox = Listbox(self, width=80, height=5)
        self._file_listbox.pack(pady=(0, 10), padx=10, fill='x')

        # Buttons
        Button(self, text="Save Selected File", bootstyle=SECONDARY, command=self._save_selected_file).pack(pady=(0, 5))
        Button(self, text="⬅ Back", width=25, bootstyle=SECONDARY, command=self._go_back_to_main).pack()

    def _start_server(self):
        start_tcp_server(on_file_received=self._on_file_received)
        self.zeroconf = start_advertising()

    def _on_file_received(self, filename, filesize, sender_ip):
        def gui_update():
            if not self.winfo_exists():
                return  # UI was closed

            try:
                msg = f"[✓] File received: {filename} ({filesize} bytes) from {sender_ip}\n"
                self._msg_log.insert('end', msg)
                self._msg_log.see('end')

                self._file_listbox.insert('end', filename)
                self.received_files.append(filename)
            except Exception as e:
                print(f"[!] Failed to update GUI: {e}")

        self.after(0, gui_update)

    def _save_selected_file(self):
        selected = self._file_listbox.curselection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a file from the list.")
            return

        filename = self._file_listbox.get(selected[0])
        source_path = os.path.join("received", filename)

        if not os.path.isfile(source_path):
            messagebox.showerror("File not found", f"The file '{filename}' is missing.")
            return

        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if not save_path:
            return

        if os.path.exists(save_path):
            if not messagebox.askyesno("Overwrite?", f"'{save_path}' already exists. Overwrite?"):
                return

        try:
            self._copy_file(source_path, save_path)
            messagebox.showinfo("Saved", f"File saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def _copy_file(self, src, dst):
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())

    def _go_back(self, screen_cls):
        if self.zeroconf:
            self.zeroconf.close()
        self.app._navigate_to(screen_cls)

    def _go_back_to_main(self):
        # Lazy import here to avoid circular import
        from src.gui.screens.select_mode import ModeSelectionScreen
        self._go_back(ModeSelectionScreen)

