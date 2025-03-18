#!/usr/bin/env python3
"""
Simple launcher script for the LM Studio Benchmark Dashboard.
Place this file in the benchmark_gui directory alongside dashboard.py

Run this script to launch the dashboard with proper import paths.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the current directory and parent directory to Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    # Verify ttkbootstrap is installed
    try:
        import ttkbootstrap
    except ImportError:
        print("ttkbootstrap is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap"])
            print("ttkbootstrap installed successfully!")
        except Exception as e:
            print(f"Error installing ttkbootstrap: {e}")
            print("Please install it manually with: pip install ttkbootstrap")
            sys.exit(1)
            
    # Run the dashboard
    try:
        # Import must be done after checking for ttkbootstrap
        from dashboard import main
        main()
    except Exception as e:
        print(f"Error launching dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Give the user some time to read the error
        input("\nPress Enter to exit...")