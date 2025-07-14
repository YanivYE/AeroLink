import subprocess
import shutil
import os

print("[INFO] Cleaning previous builds...")

# Remove old build files
for folder in ['build', 'dist']:
    shutil.rmtree(folder, ignore_errors=True)

for file in ['run_gui.spec', os.path.join('dist', 'run_gui.exe')]:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

print("[INFO] Building with PyInstaller...")

cmd = [
    'python', '-m', 'PyInstaller',
    '--noconfirm',
    '--clean',
    '--onefile',
    '--add-data', 
    'src\\gui\\assets\\logo.png;.',
    'run_gui.py'
]

subprocess.run(cmd, check=True)

print("[SUCCESS] Build complete! Find your EXE in the 'dist' folder.")
