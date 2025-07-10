import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(base_path, filename)

def load_logo(parent):
    try:
        image_path = get_asset_path("logo.png")
        image = Image.open(image_path)
        image = image.resize((140, 140), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(image)
        label = ttk.Label(parent, image=logo)
        label.image = logo  # prevent garbage collection
        return label
    except Exception as e:
        print(f"Failed to load logo: {e}")
        return None
