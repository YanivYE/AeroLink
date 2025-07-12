import os
from ttkbootstrap import Frame, Label, Button
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from ttkbootstrap.constants import SECONDARY

class PassiveModeScreen(Frame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.zeroconf = None
        self.received_files = [] 

        self._build_ui()

    def _build_ui(self):
        from src.advertiser import start_advertising
        from src.server import start_tcp_server
        from src.gui.screens.select_mode import ModeSelectionScreen
        from tkinter import Listbox, Frame

        Label(self, text="🕊️ Passive Mode", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        Label(self, text="Waiting for incoming files...", font=("Segoe UI", 12)).pack(pady=(0, 15))

        self.msg_log = ScrolledText(self, width=80, height=16, font=("Consolas", 10), wrap="word")
        self.msg_log.config(background="#2b2b2b", foreground="white", insertbackground="white", borderwidth=1, relief="flat")
        self.msg_log.pack(pady=10, fill='both', expand=False)

        self.file_listbox = Listbox(self, width=80, height=5)  # smaller height to leave room
        self.file_listbox.pack(pady=(0, 10), fill='x')

        Button(self, text="Save Selected File", bootstyle=SECONDARY, command=self._save_selected_file).pack(pady=(0, 5))
        Button(self, text="⬅ Back", width=25, bootstyle=SECONDARY, command=lambda: self._go_back(ModeSelectionScreen)).pack()

        start_tcp_server(on_file_received=self._on_file_received)
        self.zeroconf = start_advertising()



    def _go_back(self, screen):
        if self.zeroconf:
            self.zeroconf.close()
        self.app._navigate_to(screen)

    def _on_file_received(self, filename, filesize, sender_ip):
        def gui_update():
            # Check if msg_log still exists (i.e., the user didn't switch screens)
            if not self.winfo_exists():
                return  # screen was closed
            try:
                msg = f"[✓] File received: {filename} ({filesize} bytes) from {sender_ip}\n"
                self.msg_log.insert('end', msg)
                self.msg_log.see('end')

                self.file_listbox.insert('end', filename)
                self.received_files.append(filename)
            except Exception as e:
                print(f"[!] Failed to update GUI: {e}")

        self.after(0, gui_update)

    def _save_selected_file(self):
        from tkinter import filedialog
        try:
            selected_idx = self.file_listbox.curselection()
            if not selected_idx:
                messagebox.showinfo("No selection", "Please select a file from the list.")
                return

            filename = self.file_listbox.get(selected_idx[0])
            source_path = os.path.join("received", filename)

            save_path = filedialog.asksaveasfilename(initialfile=filename)
            if not save_path:
                return

            with open(source_path, "rb") as src_file, open(save_path, "wb") as dst_file:
                dst_file.write(src_file.read())

            messagebox.showinfo("Saved", f"File saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")