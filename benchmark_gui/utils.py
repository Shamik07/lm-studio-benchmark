"""
Utility functions for the LM Studio Benchmark GUI.
"""

import json
import os
import platform
import threading
import time
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path  # Add this import for Path

from tkinter import Text

def log_message(text_widget, message: str, level: str = "info", timestamp: bool = True):
    """
    Log a message to a text widget with formatting.
    
    Args:
        text_widget: The tkinter Text widget to log to
        message: The message to log
        level: The log level (info, warning, error)
        timestamp: Whether to include a timestamp
    """
    try:
        text_widget.config(state="normal")
        
        # Add timestamp
        if timestamp:
            ts = time.strftime("%H:%M:%S")
            prefix = f"[{ts}] "
        else:
            prefix = ""
        
        # Format based on level
        if level == "error":
            tag = "error"
            prefix += "ERROR: "
        elif level == "warning":
            tag = "warning"
            prefix += "WARNING: "
        else:
            tag = "info"
            prefix += "INFO: "
        
        # Add the message
        log_line = f"{prefix}{message}\n"
        text_widget.insert("end", log_line, tag)
        
        # Scroll to end
        text_widget.see("end")
        text_widget.config(state="disabled")
    except Exception as e:
        print(f"Error logging message: {e}")

def run_in_thread(func: Callable, callback: Optional[Callable] = None, daemon: bool = True):
    """
    Run a function in a separate thread.
    
    Args:
        func: The function to run
        callback: Optional callback to run when the function completes
        daemon: Whether the thread should be a daemon thread
    
    Returns:
        The created thread
    """
    def _wrapper():
        result = func()
        if callback:
            callback(result)
    
    thread = threading.Thread(target=_wrapper)
    thread.daemon = daemon
    thread.start()
    return thread

def open_file(file_path: Path):
    """
    Open a file with the default application.
    
    Args:
        file_path: Path to the file to open
    """
    try:
        if platform.system() == 'Windows':
            os.startfile(str(file_path))
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open "{file_path}"')
        else:  # Linux
            os.system(f'xdg-open "{file_path}"')
    except Exception as e:
        print(f"Error opening file: {e}")

def save_json(data: Any, file_path: Path, indent: int = 2):
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        file_path: Path to save the file
        indent: JSON indentation level
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def load_json(file_path: Path) -> Dict:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        The loaded data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

def format_percentage(value: float) -> str:
    """
    Format a float as a percentage.
    
    Args:
        value: The value to format
    
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.2f}%"

def format_time(seconds: float) -> str:
    """
    Format seconds as a human-readable time.
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    return f"{seconds:.2f}s"

def get_task_count(benchmark, categories: List[str], difficulties: List[str], languages: List[str]) -> int:
    """
    Calculate the total number of tasks based on filters.
    
    Args:
        benchmark: The benchmark instance
        categories: Selected categories
        difficulties: Selected difficulty levels
        languages: Selected programming languages
    
    Returns:
        Total number of tasks
    """
    total_tasks = 0
    for task in benchmark.tasks:
        if task["category"] in categories and task["difficulty"] in difficulties:
            task_languages = [lang for lang in languages if lang in task["languages"]]
            total_tasks += len(task_languages)
    return total_tasks