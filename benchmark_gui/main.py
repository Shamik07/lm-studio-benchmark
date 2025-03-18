import json
import tkinter as tk
import ttkbootstrap as ttk
from pathlib import Path

from app import BenchmarkApp

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
    
    # Create the root window with ttkbootstrap
    root = ttk.Window(
        title="LM Studio Coding Benchmark",
        themename=theme,  # Use loaded theme
        size=(1200, 800),
        position=(100, 100),
        minsize=(800, 600),
        iconphoto="",
    )
    
    # Create the application
    app = BenchmarkApp(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()