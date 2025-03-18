#!/usr/bin/env python3
"""
Simple launcher script for the LM Studio Benchmark GUI.
Place this file in the root directory (parent of benchmark_gui folder).
"""

import sys
import os
from pathlib import Path

# Get the directory containing this script
root_dir = Path(__file__).parent.absolute()

# Add it to the Python path
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Check if required packages are installed
try:
    import tkinter as tk
    import ttkbootstrap
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install the required dependencies:")
    print("pip install ttkbootstrap")
    sys.exit(1)

# Run the application
if __name__ == "__main__":
    try:
        # Import benchmark_gui's main module
        from benchmark_gui.main import main
        main()
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)