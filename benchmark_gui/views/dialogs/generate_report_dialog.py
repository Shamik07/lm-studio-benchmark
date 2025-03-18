"""
Dialog for generating leaderboard reports.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional

from tkinter import messagebox

class GenerateReportDialog:
    """Dialog for generating leaderboard reports"""
    
    def __init__(self, parent, controller):
        """
        Initialize the generate report dialog.
        
        Args:
            parent: Parent widget
            controller: LeaderboardController instance
        """
        self.parent = parent
        self.controller = controller
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Generate Leaderboard Report")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Build the UI
        self.create_content(main_frame)
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title
        ttk.Label(parent_frame, text="Generate Leaderboard Report", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Report Options Section
        options_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        options_frame.pack(fill=X, pady=10)
        
        ttk.Label(options_frame, text="Report Options", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(options_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(options_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Format selection
        format_frame = ttk.Frame(content_frame)
        format_frame.pack(fill=X, pady=(5, 10))
        ttk.Label(format_frame, text="Report Format:").pack(side=LEFT)
        
        self.format_var = tk.StringVar(value="markdown")
        formats = [("Markdown", "markdown"), ("HTML", "html"), ("Plain Text", "text")]
        
        format_group = ttk.Frame(content_frame)
        format_group.pack(fill=X, pady=(0, 10))
        
        for text, value in formats:
            ttk.Radiobutton(format_group, text=text, variable=self.format_var, 
                          value=value).pack(anchor=W, padx=(20, 0), pady=2)
        
        # Number of models
        models_frame = ttk.Frame(content_frame)
        models_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(models_frame, text="Include Top N Models:").pack(side=LEFT)
        
        self.top_n_var = tk.IntVar(value=10)
        ttk.Spinbox(models_frame, from_=1, to=50, textvariable=self.top_n_var, 
                  width=5).pack(side=LEFT, padx=(5, 0))
        
        # Output directory
        output_frame = ttk.Frame(content_frame)
        output_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=W, pady=(0, 5))
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=X)
        
        default_dir = Path(self.controller.state.get("leaderboard_dir", "benchmark_results/leaderboard"))
        self.output_dir_var = tk.StringVar(value=str(default_dir))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=30)
        dir_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_dir_btn = ttk.Button(dir_frame, text="Browse", 
                                  command=self.browse_output_directory)
        browse_dir_btn.pack(side=LEFT, padx=(5, 0))
        
        # Description label
        description_frame = ttk.Frame(parent_frame)
        description_frame.pack(fill=X, pady=10)
        ttk.Label(description_frame, 
                text="This will generate a comprehensive report of the leaderboard with performance metrics for the top models.", 
                wraplength=400, justify=LEFT).pack(anchor=W)
        
        # Buttons
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Cancel", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Generate button
        ttk.Button(buttons_frame, text="Generate Report", 
                 style="success", command=self.generate_report).pack(side=RIGHT, padx=(5, 5))
    
    def browse_output_directory(self):
        """Browse for an output directory"""
        directory = self.controller.browse_for_directory("Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    """
Dialog for generating leaderboard reports.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional

class GenerateReportDialog:
    """Dialog for generating leaderboard reports"""
    
    def __init__(self, parent, controller):
        """
        Initialize the generate report dialog.
        
        Args:
            parent: Parent widget
            controller: LeaderboardController instance
        """
        self.parent = parent
        self.controller = controller
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Generate Leaderboard Report")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Build the UI
        self.create_content(main_frame)
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title
        ttk.Label(parent_frame, text="Generate Leaderboard Report", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Report Options Section
        options_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        options_frame.pack(fill=X, pady=10)
        
        ttk.Label(options_frame, text="Report Options", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(options_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(options_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Format selection
        format_frame = ttk.Frame(content_frame)
        format_frame.pack(fill=X, pady=(5, 10))
        ttk.Label(format_frame, text="Report Format:").pack(side=LEFT)
        
        self.format_var = tk.StringVar(value="markdown")
        formats = [("Markdown", "markdown"), ("HTML", "html"), ("Plain Text", "text")]
        
        format_group = ttk.Frame(content_frame)
        format_group.pack(fill=X, pady=(0, 10))
        
        for text, value in formats:
            ttk.Radiobutton(format_group, text=text, variable=self.format_var, 
                          value=value).pack(anchor=W, padx=(20, 0), pady=2)
        
        # Number of models
        models_frame = ttk.Frame(content_frame)
        models_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(models_frame, text="Include Top N Models:").pack(side=LEFT)
        
        self.top_n_var = tk.IntVar(value=10)
        ttk.Spinbox(models_frame, from_=1, to=50, textvariable=self.top_n_var, 
                  width=5).pack(side=LEFT, padx=(5, 0))
        
        # Output directory
        output_frame = ttk.Frame(content_frame)
        output_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(output_frame, text="Output Directory:").pack(anchor=W, pady=(0, 5))
        
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=X)
        
        default_dir = Path(self.controller.state.get("leaderboard_dir", "benchmark_results/leaderboard"))
        self.output_dir_var = tk.StringVar(value=str(default_dir))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=30)
        dir_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_dir_btn = ttk.Button(dir_frame, text="Browse", 
                                  command=self.browse_output_directory)
        browse_dir_btn.pack(side=LEFT, padx=(5, 0))
        
        # Description label
        description_frame = ttk.Frame(parent_frame)
        description_frame.pack(fill=X, pady=10)
        ttk.Label(description_frame, 
                text="This will generate a comprehensive report of the leaderboard with performance metrics for the top models.", 
                wraplength=400, justify=LEFT).pack(anchor=W)
        
        # Buttons
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Cancel", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Generate button
        ttk.Button(buttons_frame, text="Generate Report", 
                 style="success", command=self.generate_report).pack(side=RIGHT, padx=(5, 5))
    
    def browse_output_directory(self):
        """Browse for an output directory"""
        directory = self.controller.browse_for_directory("Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def generate_report(self):
        """Generate the leaderboard report"""
        try:
            # Get report options
            format_type = self.format_var.get()
            top_n = self.top_n_var.get()
            output_dir = self.output_dir_var.get()
            
            # Generate the report
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True, parents=True)
            
            # Create a timestamp for the filename
            # Extract the timestamp safely in case the last_updated format changes
            try:
                timestamp = self.controller.leaderboard.db["last_updated"].replace(":", "-").replace(" ", "_")
            except (KeyError, AttributeError):
                # Fallback to current time
                import time
                timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
                
            file_extension = {"markdown": "md", "html": "html", "text": "txt"}[format_type]
            report_path = output_path / f"leaderboard_report_{timestamp}.{file_extension}"
            
            # Generate the report using the controller
            report_file = self.controller.generate_leaderboard_report(
                format_type=format_type,
                top_n=top_n,
                output_path=str(report_path)
            )
            
            if report_file:
                messagebox.showinfo("Success", f"Report generated successfully: {report_file}")
                
                # Ask if the user wants to open the report
                if messagebox.askyesno("Open Report", "Would you like to open the report now?"):
                    self.controller.open_analysis_file(report_file)
                
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to generate report.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")