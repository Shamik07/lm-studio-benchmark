"""
Settings tab UI for LM Studio Benchmark GUI.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import messagebox
from pathlib import Path
import json

from controllers.settings_controller import SettingsController

import webbrowser
from pathlib import Path

class SettingsView:
    """Settings tab UI class"""
    
    def __init__(self, parent, state):
        """
        Initialize the settings view.
        
        Args:
            parent: Parent widget
            state: Shared application state
        """
        self.parent = parent
        self.state = state
        self.controller = SettingsController(state)
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Set up the panel
        self.setup_panel()
        
        # Initialize settings
        self.load_settings()
    
    def setup_panel(self):
        """Set up the settings panel UI"""
        # Use a scrollable frame for settings
        frame = ScrolledFrame(self.frame, autohide=True)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # General Settings Section
        general_frame = ttk.Frame(main_frame, style="Card.TFrame")
        general_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(general_frame, text="General Settings", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(general_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(general_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # API Endpoint
        ttk.Label(content_frame, text="Default API Endpoint:").pack(anchor=W, pady=(5, 2))
        self.endpoint_var = tk.StringVar(value="http://localhost:1234/v1/chat/completions")
        endpoint_entry = ttk.Entry(content_frame, textvariable=self.endpoint_var, width=40)
        endpoint_entry.pack(fill=X, pady=(0, 10))
        
        # Default output directory
        ttk.Label(content_frame, text="Default Output Directory:").pack(anchor=W, pady=(5, 2))
        dir_frame = ttk.Frame(content_frame)
        dir_frame.pack(fill=X, pady=(0, 10))
        
        self.default_output_dir_var = tk.StringVar(value=str(self.state.get("output_dir", "benchmark_results")))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.default_output_dir_var, width=30)
        dir_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_dir_btn = ttk.Button(dir_frame, text="Browse", 
                                  command=self.browse_output_directory)
        browse_dir_btn.pack(side=LEFT, padx=(5, 0))
        
        # Request timeout
        timeout_frame = ttk.Frame(content_frame)
        timeout_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(timeout_frame, text="Default Timeout (seconds):").pack(side=LEFT)
        self.timeout_var = tk.IntVar(value=120)
        timeout_spinbox = ttk.Spinbox(timeout_frame, from_=10, to=300, textvariable=self.timeout_var, width=5)
        timeout_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Theme selection
        theme_frame = ttk.Frame(content_frame)
        theme_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(theme_frame, text="Theme:").pack(side=LEFT)
        
        self.theme_var = self.state.get("theme_var", tk.StringVar(value="dark"))
        theme_mode = ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var,
                                   value="dark", command=self.toggle_theme)
        theme_mode.pack(side=LEFT, padx=(10, 5))
        
        theme_mode = ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var,
                                   value="light", command=self.toggle_theme)
        theme_mode.pack(side=LEFT, padx=5)
        
        # Save settings button
        ttk.Button(content_frame, text="Save Settings", 
                 style="success", command=self.save_settings).pack(anchor=W, pady=(10, 5))
        
        # Leaderboard Settings Section
        lb_frame = ttk.Frame(main_frame, style="Card.TFrame")
        lb_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(lb_frame, text="Leaderboard Settings", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(lb_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(lb_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Leaderboard directory
        ttk.Label(content_frame, text="Leaderboard Directory:").pack(anchor=W, pady=(5, 2))
        lb_dir_frame = ttk.Frame(content_frame)
        lb_dir_frame.pack(fill=X, pady=(0, 10))
        
        self.leaderboard_dir_var = tk.StringVar(value=self.state.get("leaderboard_dir", "benchmark_results/leaderboard"))
        lb_dir_entry = ttk.Entry(lb_dir_frame, textvariable=self.leaderboard_dir_var, width=30)
        lb_dir_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_lb_dir_btn = ttk.Button(lb_dir_frame, text="Browse", 
                                    command=self.browse_leaderboard_directory)
        browse_lb_dir_btn.pack(side=LEFT, padx=(5, 0))
        
        # Default report format
        format_frame = ttk.Frame(content_frame)
        format_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(format_frame, text="Default Report Format:").pack(side=LEFT)
        
        self.report_format_var = tk.StringVar(value="markdown")
        format_dropdown = ttk.Combobox(format_frame, textvariable=self.report_format_var, 
                                     values=["markdown", "html", "text"], width=15, state="readonly")
        format_dropdown.pack(side=LEFT, padx=(5, 0))
        
        # Reset leaderboard button
        reset_frame = ttk.Frame(content_frame)
        reset_frame.pack(fill=X, pady=(10, 5))
        
        ttk.Button(reset_frame, text="Reset Leaderboard", 
                 style="danger", command=self.confirm_reset_leaderboard).pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(reset_frame, text="Warning: This will delete all leaderboard data!", 
                style="Danger.TLabel").pack(side=LEFT)
        
        # Default Benchmark Options Section
        options_frame = ttk.Frame(main_frame, style="Card.TFrame")
        options_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(options_frame, text="Default Benchmark Options", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(options_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(options_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Execute code
        self.execute_code_var = tk.BooleanVar(value=True)
        execute_check = ttk.Checkbutton(content_frame, text="Execute code to verify functionality", variable=self.execute_code_var)
        execute_check.pack(anchor=W, pady=(0, 5))
        
        # Monitor resources
        self.monitor_resources_var = tk.BooleanVar(value=True)
        monitor_check = ttk.Checkbutton(content_frame, text="Monitor system resources", variable=self.monitor_resources_var)
        monitor_check.pack(anchor=W, pady=(0, 5))
        
        # Parallel execution
        parallel_frame = ttk.Frame(content_frame)
        parallel_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(parallel_frame, text="Default Parallel Tasks:").pack(side=LEFT)
        self.parallel_var = tk.IntVar(value=1)
        parallel_spinbox = ttk.Spinbox(parallel_frame, from_=1, to=10, textvariable=self.parallel_var, width=5)
        parallel_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Runs per task
        runs_frame = ttk.Frame(content_frame)
        runs_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(runs_frame, text="Default Runs per Task:").pack(side=LEFT)
        self.runs_var = tk.IntVar(value=1)
        runs_spinbox = ttk.Spinbox(runs_frame, from_=1, to=10, textvariable=self.runs_var, width=5)
        runs_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # About Section
        about_frame = ttk.Frame(main_frame, style="Card.TFrame")
        about_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(about_frame, text="About", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(about_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(about_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttk.Label(content_frame, text="LM Studio Coding Benchmark GUI", style="Title.TLabel").pack(anchor=W, pady=(5, 2))
        ttk.Label(content_frame, text="A comprehensive tool for evaluating LM Studio models on coding tasks.").pack(anchor=W, pady=(0, 10))
        
        version_frame = ttk.Frame(content_frame)
        version_frame.pack(fill=X)
        ttk.Label(version_frame, text="Version:").pack(side=LEFT)
        ttk.Label(version_frame, text="1.0.0", style="Info.TLabel").pack(side=LEFT, padx=(5, 0))
        
        # Repository link
        repo_frame = ttk.Frame(content_frame)
        repo_frame.pack(fill=X, pady=(5, 0))
        ttk.Label(repo_frame, text="GitHub:").pack(side=LEFT)
        
        # Create a hyperlink-style label
        repo_link = ttk.Label(repo_frame, text="github.com/organization/lm-studio-benchmark", 
                            style="Info.TLabel", cursor="hand2")
        repo_link.pack(side=LEFT, padx=(5, 0))
        repo_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/organization/lm-studio-benchmark"))
    
    def load_settings(self):
        """Load settings from controller"""
        settings = self.controller.load_settings()
        
        # Apply settings to UI
        if "endpoint" in settings:
            self.endpoint_var.set(settings["endpoint"])
        
        if "output_dir" in settings:
            self.default_output_dir_var.set(settings["output_dir"])
        
        if "leaderboard_dir" in settings:
            self.leaderboard_dir_var.set(settings["leaderboard_dir"])
        
        if "timeout" in settings:
            self.timeout_var.set(settings["timeout"])
        
        if "execute_code" in settings:
            self.execute_code_var.set(settings["execute_code"])
        
        if "monitor_resources" in settings:
            self.monitor_resources_var.set(settings["monitor_resources"])
        
        if "parallel" in settings:
            self.parallel_var.set(settings["parallel"])
        
        if "runs" in settings:
            self.runs_var.set(settings["runs"])
        
        if "report_format" in settings:
            self.report_format_var.set(settings["report_format"])
        
        if "theme" in settings:
            self.theme_var.set(settings["theme"])
    
    def save_settings(self):
        """Save settings via controller"""
        settings = {
            "endpoint": self.endpoint_var.get(),
            "output_dir": self.default_output_dir_var.get(),
            "leaderboard_dir": self.leaderboard_dir_var.get(),
            "timeout": self.timeout_var.get(),
            "execute_code": self.execute_code_var.get(),
            "monitor_resources": self.monitor_resources_var.get(),
            "parallel": self.parallel_var.get(),
            "runs": self.runs_var.get(),
            "report_format": self.report_format_var.get(),
            "theme": self.theme_var.get()
        }
        
        success = self.controller.save_settings(settings)
        
        if success:
            messagebox.showinfo("Success", "Settings saved successfully.")
            
            # Update state
            self.state["output_dir"] = self.default_output_dir_var.get()
            self.state["leaderboard_dir"] = self.leaderboard_dir_var.get()
        else:
            messagebox.showerror("Error", "Failed to save settings.")
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = self.controller.browse_for_directory("Select Output Directory")
        if directory:
            self.default_output_dir_var.set(directory)
    
    def browse_leaderboard_directory(self):
        """Browse for leaderboard directory"""
        directory = self.controller.browse_for_directory("Select Leaderboard Directory")
        if directory:
            self.leaderboard_dir_var.set(directory)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
         # Update app-level theme variable
        self.state["theme_var"].set(self.theme_var.get())
        # This function is called when theme radio buttons are clicked
        # The actual theme switching is handled by the application
        pass
    
    def confirm_reset_leaderboard(self):
        """Confirm and reset leaderboard"""
        if messagebox.askyesno("Confirm Reset", 
                          "Are you sure you want to reset the leaderboard? This will delete all leaderboard data!",
                          icon="warning"):
            success = self.controller.reset_leaderboard()
            
            if success:
                messagebox.showinfo("Success", "Leaderboard has been reset.")
            else:
                messagebox.showerror("Error", "Failed to reset leaderboard.")
    
    def save_configuration(self):
        """Save current configuration to a file"""
        filename = self.controller.save_configuration_to_file({
            "endpoint": self.endpoint_var.get(),
            "output_dir": self.default_output_dir_var.get(),
            "leaderboard_dir": self.leaderboard_dir_var.get(),
            "timeout": self.timeout_var.get(),
            "execute_code": self.execute_code_var.get(),
            "monitor_resources": self.monitor_resources_var.get(),
            "parallel": self.parallel_var.get(),
            "runs": self.runs_var.get(),
            "theme": self.theme_var.get()
        })
        
        if filename:
            messagebox.showinfo("Success", f"Configuration saved to {filename}")
    
    def load_configuration(self):
        """Load configuration from a file"""
        config = self.controller.load_configuration_from_file()
        
        if not config:
            return
        
        # Apply configuration to UI
        if "endpoint" in config:
            self.endpoint_var.set(config["endpoint"])
        
        if "output_dir" in config:
            self.default_output_dir_var.set(config["output_dir"])
        
        if "leaderboard_dir" in config:
            self.leaderboard_dir_var.set(config["leaderboard_dir"])
        
        if "timeout" in config:
            self.timeout_var.set(config["timeout"])
        
        if "execute_code" in config:
            self.execute_code_var.set(config["execute_code"])
        
        if "monitor_resources" in config:
            self.monitor_resources_var.set(config["monitor_resources"])
        
        if "parallel" in config:
            self.parallel_var.set(config["parallel"])
        
        if "runs" in config:
            self.runs_var.set(config["runs"])
        
        if "theme" in config:
            self.theme_var.set(config["theme"])
            self.toggle_theme()
        
        messagebox.showinfo("Success", "Configuration loaded successfully.")
    
    def open_url(self, url):
        """Open a URL in the default browser"""
        import webbrowser
        webbrowser.open(url)