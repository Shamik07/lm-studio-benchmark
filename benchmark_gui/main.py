"""
Main entry point for the LM Studio Benchmark GUI.
"""

import json
import tkinter as tk
import sys
import os
from pathlib import Path

# Add parent directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Now try to import ttkbootstrap
try:
    import ttkbootstrap as ttk
except ImportError:
    print("Error: ttkbootstrap package not found.")
    print("Please install it with: pip install ttkbootstrap")
    sys.exit(1)

# Simple app class that doesn't depend on other imports
class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LM Studio Benchmark")
        self.root.geometry("800x600")
        
        # Create a label
        ttk.Label(
            root, 
            text="LM Studio Benchmark GUI", 
            font=("Helvetica", 24)
        ).pack(pady=40)
        
        # Create a frame for buttons
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)
        
        # Add some buttons
        ttk.Button(
            btn_frame, 
            text="Run Benchmark",
            style="success.TButton",
            width=20
        ).pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="View Results",
            style="secondary.TButton", 
            width=20
        ).pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Settings",
            style="secondary.TButton", 
            width=20
        ).pack(pady=10)
        
        # Status bar
        status_frame = ttk.Frame(root)
        status_frame.pack(side="bottom", fill="x")
        ttk.Label(
            status_frame, 
            text="Ready", 
            relief="sunken", 
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

def main():
    # Load settings to get theme before creating window
    config_dir = Path.home() / ".lm-studio-benchmark"
    config_file = config_dir / "config.json"
    theme = "darkly"  # Default dark theme
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                settings = json.load(f)
                if settings.get("theme") == "light":
                    theme = "cosmo"  # Use 'cosmo' as the light theme
        except:
            pass

    # Try to make the UI look better on high DPI displays
    try:
        # For Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # For macOS, set a higher scaling factor
    if os.name == 'posix':
        os.environ['TK_SCALING'] = '2.0'
    
    # Create the root window with ttkbootstrap
    root = ttk.Window(
        title="LM Studio Coding Benchmark",
        themename=theme,  # Use loaded theme
        size=(1280, 800),
        position=(100, 100),
        minsize=(900, 600),
    )
    
    # Let's just create a simple app for now
    app = SimpleApp(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()