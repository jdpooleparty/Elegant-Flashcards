import PyInstaller.__main__
import os

# Get the absolute path of the script
script_path = os.path.abspath(__file__)
# Get the directory containing the script
base_path = os.path.dirname(script_path)

PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    '--windowed',
    '--add-data', f'{os.path.join(base_path, "data")}:data',
    '--add-data', f'{os.path.join(base_path, "resources")}:resources',
    '--add-data', f'{os.path.join(base_path, "Flashcards")}:Flashcards',
    '--add-data', f'{os.path.join(base_path, "config.ini")}:.',
    '--name', 'Elegant-Flashcards'
])