"""
Dialog for adding benchmark results to the leaderboard.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from pathlib import Path
import json
import re

from tkinter import messagebox

class AddLeaderboardEntryDialog:
    """Dialog for adding benchmark results to the leaderboard"""
    
    def __init__(self, parent, leaderboard, analysis_file, default_name):
        """
        Initialize the add to leaderboard dialog.
        
        Args:
            parent: Parent widget
            leaderboard: Leaderboard instance
            analysis_file: Path to analysis file
            default_name: Default model name
        """
        self.parent = parent
        self.leaderboard = leaderboard
        self.analysis_file = analysis_file
        
        # Try to preload the analysis file to extract details
        self.analysis_data = self.load_analysis_data(analysis_file)
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Add to Leaderboard")
        self.dialog.geometry("450x420")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create content frame with padding
        content_frame = ttk.Frame(self.dialog)
        content_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Title
        ttk.Label(content_frame, text="Add Benchmark to Leaderboard", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Benchmark Information Section
        info_frame = ttk.Frame(content_frame, style="Card.TFrame")
        info_frame.pack(fill=X, pady=10)
        
        ttk.Label(info_frame, text="Benchmark Information", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(info_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        info_content = ttk.Frame(info_frame, style="CardContent.TFrame")
        info_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Benchmark file info
        benchmark_frame = ttk.Frame(info_content)
        benchmark_frame.pack(fill=X, pady=(5, 10))
        
        # Show benchmark title if available
        if self.analysis_data and 'title' in self.analysis_data:
            ttk.Label(benchmark_frame, text=f"Benchmark: {self.analysis_data['title']}",
                    style="Info.TLabel").pack(anchor=W)
        
        # Analysis file path
        file_frame = ttk.Frame(info_content)
        file_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(file_frame, text="Analysis File:").pack(anchor=W)
        
        # Make the path more readable
        file_path = str(analysis_file)
        shortened_path = file_path
        if len(file_path) > 50:
            shortened_path = "..." + file_path[-47:]
            
        ttk.Label(file_frame, text=shortened_path, 
                style="Info.TLabel", wraplength=380).pack(anchor=W, pady=(2, 0))
        
        # Show summary stats if available
        if self.analysis_data and 'summary' in self.analysis_data:
            summary = self.analysis_data['summary']
            summary_frame = ttk.Frame(info_content)
            summary_frame.pack(fill=X, pady=(5, 0))
            
            if 'test_pass_rate' in summary:
                ttk.Label(summary_frame, 
                        text=f"Test Pass Rate: {summary['test_pass_rate']:.2%}",
                        style="Success.TLabel").pack(anchor=W)
            elif 'api_success_rate' in summary:
                ttk.Label(summary_frame, 
                        text=f"API Success Rate: {summary['api_success_rate']:.2%}",
                        style="Success.TLabel").pack(anchor=W)
        
        # Model Section
        model_frame = ttk.Frame(content_frame, style="Card.TFrame")
        model_frame.pack(fill=X, pady=10)
        
        ttk.Label(model_frame, text="Model Information", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(model_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        model_content = ttk.Frame(model_frame, style="CardContent.TFrame")
        model_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Model name with auto-extraction from default name
        ttk.Label(model_content, text="Model Name:*").pack(anchor=W, pady=(5, 2))
        
        # Try to extract just the model name from default_name (which might include timestamp)
        suggested_name = default_name
        if default_name:
            # Try to clean up benchmark_ prefix and timestamp suffix
            match = re.match(r'benchmark_(.+?)(?:_\d+)?$', default_name)
            if match:
                suggested_name = match.group(1)
        
        self.model_name_var = tk.StringVar(value=suggested_name)
        ttk.Entry(model_content, textvariable=self.model_name_var, width=40).pack(fill=X, pady=(0, 10))
        
        # Model parameters field
        param_frame = ttk.Frame(model_content)
        param_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(param_frame, text="Parameters:").pack(side=LEFT)
        self.model_params_var = tk.StringVar()
        ttk.Entry(param_frame, textvariable=self.model_params_var, width=15).pack(side=LEFT, padx=(5, 0))
        ttk.Label(param_frame, text="(e.g., 7B, 13B)", foreground="gray").pack(side=LEFT, padx=(5, 0))
        
        # Version field
        version_frame = ttk.Frame(model_content)
        version_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(version_frame, text="Version:").pack(side=LEFT)
        self.model_version_var = tk.StringVar()
        ttk.Entry(version_frame, textvariable=self.model_version_var, width=15).pack(side=LEFT, padx=(5, 0))
        ttk.Label(version_frame, text="(e.g., v1.0, r2.1)", foreground="gray").pack(side=LEFT, padx=(5, 0))
        
        # Architecture field
        arch_frame = ttk.Frame(model_content)
        arch_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(arch_frame, text="Architecture:").pack(side=LEFT)
        self.model_arch_var = tk.StringVar()
        ttk.Entry(arch_frame, textvariable=self.model_arch_var, width=15).pack(side=LEFT, padx=(5, 0))
        ttk.Label(arch_frame, text="(e.g., Mistral, Llama)", foreground="gray").pack(side=LEFT, padx=(5, 0))
        
        # Quantization field
        quant_frame = ttk.Frame(model_content)
        quant_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(quant_frame, text="Quantization:").pack(side=LEFT)
        self.model_quant_var = tk.StringVar()
        ttk.Entry(quant_frame, textvariable=self.model_quant_var, width=15).pack(side=LEFT, padx=(5, 0))
        ttk.Label(quant_frame, text="(e.g., Q4_K_M, F16)", foreground="gray").pack(side=LEFT, padx=(5, 0))
        
        # Required field notice
        ttk.Label(model_content, text="* Required field", foreground="gray", font=("Helvetica", 8)).pack(anchor=W, pady=(10, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(content_frame)
        buttons_frame.pack(fill=X, pady=(15, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Cancel", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Add button
        ttk.Button(buttons_frame, text="Add to Leaderboard", 
                 style="success", command=self.add_to_leaderboard).pack(side=RIGHT, padx=(5, 5))
    
    def load_analysis_data(self, analysis_file):
        """Load and validate the analysis file data"""
        try:
            with open(analysis_file, "r") as f:
                data = json.load(f)
            return data
        except (json.JSONDecodeError, OSError, IOError) as e:
            print(f"Error loading analysis file: {e}")
            return None
    
    def add_to_leaderboard(self):
        """Add the benchmark to the leaderboard"""
        model_name = self.model_name_var.get().strip()
        
        if not model_name:
            messagebox.showerror("Error", "Model name is required")
            return
        
        # Create model_info dictionary if any fields were filled
        model_info = {}
        if self.model_params_var.get().strip():
            model_info["parameters"] = self.model_params_var.get().strip()
        if self.model_version_var.get().strip():
            model_info["version"] = self.model_version_var.get().strip()
        if self.model_arch_var.get().strip():
            model_info["architecture"] = self.model_arch_var.get().strip()
        if self.model_quant_var.get().strip():
            model_info["quantization"] = self.model_quant_var.get().strip()
        
        try:
            # Add to leaderboard
            entry = self.leaderboard.add_entry(
                analysis_file=self.analysis_file,
                model_name=model_name,
                model_info=model_info if model_info else None
            )
            
            # Show success message with more details
            msg = f"Added {model_name} to leaderboard\n\n"
            if 'summary' in self.analysis_data:
                summary = self.analysis_data['summary']
                if 'test_pass_rate' in summary:
                    msg += f"Test Pass Rate: {summary['test_pass_rate']:.2%}\n"
                if 'api_success_rate' in summary:
                    msg += f"API Success Rate: {summary['api_success_rate']:.2%}\n"
            
            messagebox.showinfo("Success", msg)
            self.dialog.destroy()
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to leaderboard: {e}")
            return False
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            tooltip = ttk.Toplevel(self.dialog)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, style="Info.TLabel", 
                           background="#333333", foreground="white", 
                           relief="solid", borderwidth=1, wraplength=250, 
                           padding=(5, 3))
            label.pack()
            
            widget._tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, "_tooltip"):
                widget._tooltip.destroy()
                del widget._tooltip
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)