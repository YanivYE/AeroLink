import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

def load_logo(parent):
    try:
        image_path = os.path.join(ASSETS_PATH, "logo.png")
        image = Image.open(image_path)
        image = image.resize((140, 140), Image.Resampling.LANCZOS)  # resize to 200x80 px
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(parent, image=photo)
        label.image = photo  # keep a reference to prevent GC
        return label
    except Exception as e:
        print(f"Failed to load logo: {e}")
        return None