import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
import sys

def get_asset_path(filename):
    """
    Get the absolute path to an asset, compatible with PyInstaller bundles.
    """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.join(os.path.dirname(__file__), "assets")
    return os.path.join(base_path, filename)

def load_logo(parent):
    """
    Load and return a ttk.Label widget containing the logo image resized to 140x140.
    Returns None on failure.
    """
    try:
        image_path = get_asset_path("logo.png")
        with Image.open(image_path) as img:
            img = img.resize((140, 140), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(img)
        label = ttk.Label(parent, image=logo)
        label.image = logo  # Keep reference to prevent garbage collection
        return label
    except Exception as e:
        print("[Warning] Failed to load logo image:", e)
        return None
