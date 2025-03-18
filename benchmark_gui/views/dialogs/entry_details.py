"""
Dialog for displaying leaderboard entry details.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from pathlib import Path
import webbrowser
from tkinter import messagebox

class EntryDetailsDialog:
    """Dialog for displaying detailed information about a leaderboard entry"""
    
    def __init__(self, parent, entry, controller):
        """
        Initialize the entry details dialog.
        
        Args:
            parent: Parent widget
            entry: Entry dictionary with all details
            controller: LeaderboardController instance
        """
        self.parent = parent
        self.entry = entry
        self.controller = controller
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(f"Entry Details: {entry['model_name']}")
        self.dialog.geometry("550x650")
        self.dialog.minsize(500, 600)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create scrollable frame for content
        frame = ScrolledFrame(self.dialog, autohide=True)
        frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Build the UI
        self.create_content(content_frame)
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title and basic information section
        info_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        info_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(info_frame, text="Benchmark Information", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(info_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        info_content = ttk.Frame(info_frame, style="CardContent.TFrame")
        info_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Benchmark title
        ttk.Label(info_content, text=f"Benchmark: {self.entry.get('title', 'Unnamed Benchmark')}", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 5))
        
        # Entry ID with tooltip
        id_frame = ttk.Frame(info_content)
        id_frame.pack(fill=X, pady=2)
        ttk.Label(id_frame, text="Entry ID:").pack(side=LEFT)
        id_label = ttk.Label(id_frame, text=self.entry['id'], style="Info.TLabel")
        id_label.pack(side=LEFT, padx=(5, 0))
        self.create_tooltip(id_label, "Unique identifier for this benchmark entry")
        
        # Model name
        model_frame = ttk.Frame(info_content)
        model_frame.pack(fill=X, pady=2)
        ttk.Label(model_frame, text="Model:").pack(side=LEFT)
        ttk.Label(model_frame, text=self.entry['model_name'], style="Info.TLabel").pack(side=LEFT, padx=(5, 0))
        
        # Timestamp
        time_frame = ttk.Frame(info_content)
        time_frame.pack(fill=X, pady=2)
        ttk.Label(time_frame, text="Date:").pack(side=LEFT)
        ttk.Label(time_frame, text=self.entry['timestamp'], style="Info.TLabel").pack(side=LEFT, padx=(5, 0))
        
        # Model info if available
        if "model_info" in self.entry and self.entry["model_info"]:
            model_info_frame = ttk.Frame(parent_frame, style="Card.TFrame")
            model_info_frame.pack(fill=X, pady=10, padx=5)
            
            ttk.Label(model_info_frame, text="Model Information", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
            ttk.Separator(model_info_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
            
            info_content = ttk.Frame(model_info_frame, style="CardContent.TFrame")
            info_content.pack(fill=X, padx=10, pady=(0, 10))
            
            # Display model info with better formatting and tooltips
            model_info = self.entry["model_info"]
            tooltips = {
                "parameters": "The parameter count of the model (e.g., 7B, 13B)",
                "version": "Version or iteration of the model",
                "architecture": "Model architecture or type",
                "quantization": "Quantization format (e.g., Q4_K_M, F16)"
            }
            
            for key, value in model_info.items():
                info_row = ttk.Frame(info_content)
                info_row.pack(fill=X, pady=2)
                
                label = ttk.Label(info_row, text=f"{key.capitalize()}:")
                label.pack(side=LEFT)
                value_label = ttk.Label(info_row, text=str(value), style="Info.TLabel")
                value_label.pack(side=LEFT, padx=(5, 0))
                
                if key in tooltips:
                    self.create_tooltip(label, tooltips[key])
        
        # Performance metrics
        metrics_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        metrics_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(metrics_frame, text="Performance Metrics", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(metrics_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        metrics_content = ttk.Frame(metrics_frame, style="CardContent.TFrame")
        metrics_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Define tooltips for metrics
        metric_tooltips = {
            "test_pass_rate": "Percentage of tests that passed successfully",
            "api_success_rate": "Percentage of API calls that were successful",
            "execution_success_rate": "Percentage of code samples that executed successfully",
            "avg_response_time": "Average time taken to receive a response from the model",
            "total_tasks": "Total number of tasks included in the benchmark",
            "total_tests": "Total number of tests run across all tasks",
            "completed_tasks": "Number of tasks that were completed successfully"
        }
        
        # Print all available metrics with tooltips
        for key, value in self.entry["summary"].items():
            if key not in ["by_category", "by_difficulty", "by_language"]:
                metric_row = ttk.Frame(metrics_content)
                metric_row.pack(fill=X, pady=2)
                
                formatted_key = key.replace("_", " ").title()
                key_label = ttk.Label(metric_row, text=f"{formatted_key}:")
                key_label.pack(side=LEFT)
                
                # Format value based on type
                if isinstance(value, float):
                    if key.endswith("rate"):
                        formatted_value = f"{value:.2%}"
                    else:
                        formatted_value = f"{value:.2f}"
                        if key == "avg_response_time":
                            formatted_value += "s"
                else:
                    formatted_value = str(value)
                
                value_label = ttk.Label(metric_row, text=formatted_value, style="Info.TLabel")
                value_label.pack(side=LEFT, padx=(5, 0))
                
                # Add tooltip if available
                if key in metric_tooltips:
                    self.create_tooltip(key_label, metric_tooltips[key])
        
        # Resource metrics if available
        if "resource_metrics" in self.entry and self.entry["resource_metrics"]:
            resource_frame = ttk.Frame(parent_frame, style="Card.TFrame")
            resource_frame.pack(fill=X, pady=10, padx=5)
            
            ttk.Label(resource_frame, text="Resource Metrics", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
            ttk.Separator(resource_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
            
            resource_content = ttk.Frame(resource_frame, style="CardContent.TFrame")
            resource_content.pack(fill=X, padx=10, pady=(0, 10))
            
            # Define tooltips for resource metrics
            resource_tooltips = {
                "cpu_avg_percent": "Average CPU utilization during the benchmark",
                "cpu_max_percent": "Peak CPU utilization during the benchmark",
                "memory_avg_gb": "Average memory usage during the benchmark",
                "memory_peak_gb": "Peak memory usage during the benchmark",
                "gpu_avg_utilization": "Average GPU utilization during the benchmark",
                "gpu_max_utilization": "Peak GPU utilization during the benchmark"
            }
            
            # Sort metrics in a logical order
            metric_order = [
                "memory_avg_gb", "memory_peak_gb", 
                "cpu_avg_percent", "cpu_max_percent", 
                "gpu_avg_utilization", "gpu_max_utilization"
            ]
            
            sorted_metrics = []
            # First add metrics in the predefined order
            for metric in metric_order:
                if metric in self.entry["resource_metrics"]:
                    sorted_metrics.append((metric, self.entry["resource_metrics"][metric]))
            
            # Then add any remaining metrics not in the predefined order
            for metric, value in self.entry["resource_metrics"].items():
                if metric not in metric_order:
                    sorted_metrics.append((metric, value))
            
            # Display resource metrics
            for metric, value in sorted_metrics:
                resource_row = ttk.Frame(resource_content)
                resource_row.pack(fill=X, pady=2)
                
                formatted_key = metric.replace("_", " ").title()
                key_label = ttk.Label(resource_row, text=f"{formatted_key}:")
                key_label.pack(side=LEFT)
                
                # Format value based on type
                if "memory" in metric and "gb" in metric:
                    formatted_value = f"{value:.2f} GB"
                elif "percent" in metric or "utilization" in metric:
                    formatted_value = f"{value:.1f}%"
                else:
                    formatted_value = str(value)
                
                value_label = ttk.Label(resource_row, text=formatted_value, style="Info.TLabel")
                value_label.pack(side=LEFT, padx=(5, 0))
                
                # Add tooltip if available
                if metric in resource_tooltips:
                    self.create_tooltip(key_label, resource_tooltips[metric])
            
            # Add interpretation note
            ttk.Label(resource_content, 
                    text="Note: Lower memory and CPU usage values indicate more efficient models.",
                    style="Info.TLabel", wraplength=480).pack(anchor=W, pady=(10, 0))
        
        # Detailed metrics by category
        if "by_category" in self.entry["summary"]:
            self.create_dimension_section(parent_frame, "Performance by Category", 
                                        self.entry["summary"]["by_category"])
        
        # Detailed metrics by difficulty
        if "by_difficulty" in self.entry["summary"]:
            self.create_dimension_section(parent_frame, "Performance by Difficulty", 
                                        self.entry["summary"]["by_difficulty"])
        
        # Detailed metrics by language
        if "by_language" in self.entry["summary"]:
            self.create_dimension_section(parent_frame, "Performance by Language", 
                                        self.entry["summary"]["by_language"])
        
        # Buttons at the bottom
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Button to view analysis file
        if "analysis_file" in self.entry:
            analysis_btn = ttk.Button(buttons_frame, text="View Analysis File", 
                                    command=self.view_analysis_file)
            analysis_btn.pack(side=LEFT, padx=(0, 10))
            self.create_tooltip(analysis_btn, "Open the full analysis JSON file in your default application")
        
        # Button to close dialog
        close_btn = ttk.Button(buttons_frame, text="Close", 
                             style="secondary", command=self.dialog.destroy)
        close_btn.pack(side=RIGHT)
    
    def create_dimension_section(self, parent_frame, title, dimension_data):
        """Create a section for metrics by a specific dimension (category/difficulty/language)"""
        dimension_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        dimension_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(dimension_frame, text=title, style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(dimension_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        dimension_content = ttk.Frame(dimension_frame, style="CardContent.TFrame")
        dimension_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Create a table-like structure
        headers = ["Name", "API Success", "Execution Success", "Test Pass Rate"]
        
        # Table header
        header_frame = ttk.Frame(dimension_content)
        header_frame.pack(fill=X, pady=(0, 5))
        
        for i, header in enumerate(headers):
            ttk.Label(header_frame, text=header, font=("Helvetica", 10, "bold")).grid(row=0, column=i, padx=5, sticky=W)
        
        # Add a separator after headers
        ttk.Separator(dimension_content, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Table rows - sort by test_pass_rate if available, or api_success_rate
        sorted_items = sorted(
            dimension_data.items(),
            key=lambda x: x[1].get("test_pass_rate", x[1].get("api_success_rate", 0)),
            reverse=True
        )
        
        # Table rows
        for i, (name, metrics) in enumerate(sorted_items):
            row_frame = ttk.Frame(dimension_content)
            row_frame.pack(fill=X, pady=2)
            
            # First column - name
            name_label = ttk.Label(row_frame, text=name)
            name_label.grid(row=0, column=0, padx=5, sticky=W)
            
            # API Success Rate
            api_success = metrics.get("api_success_rate", 0)
            api_label = ttk.Label(row_frame, text=f"{api_success:.2%}")
            api_label.grid(row=0, column=1, padx=5)
            self.apply_color_style(api_label, api_success)
            
            # Execution Success Rate
            exec_success = metrics.get("execution_success_rate", 0)
            exec_label = ttk.Label(row_frame, text=f"{exec_success:.2%}")
            exec_label.grid(row=0, column=2, padx=5)
            self.apply_color_style(exec_label, exec_success)
            
            # Test Pass Rate
            test_pass = metrics.get("test_pass_rate", 0)
            test_label = ttk.Label(row_frame, text=f"{test_pass:.2%}")
            test_label.grid(row=0, column=3, padx=5)
            self.apply_color_style(test_label, test_pass)
        
        # Add explanation of color coding
        ttk.Label(dimension_content, 
                text="Color coding: Green (≥80%), Yellow (50-80%), Red (<50%)",
                style="Info.TLabel").pack(anchor=E, pady=(10, 0))
    
    def apply_color_style(self, label, value):
        """Apply color styling to a label based on the metric value"""
        if value >= 0.8:  # 80% or higher - good
            label.configure(foreground="forest green")
        elif value >= 0.5:  # 50% to 80% - medium
            label.configure(foreground="dark orange")
        else:  # Below 50% - poor
            label.configure(foreground="firebrick")
    
    def view_analysis_file(self):
        """View the analysis file associated with this entry"""
        if "analysis_file" in self.entry:
            analysis_file = self.entry["analysis_file"]
            
            # Use controller to open the file
            success = self.controller.open_analysis_file(analysis_file)
            
            if not success:
                messagebox.showerror("Error", f"Failed to open analysis file: {analysis_file}")
                
                # Suggest alternatives
                if messagebox.askyesno("Question", 
                                     "Would you like to try opening the file location instead?"):
                    try:
                        # Open the directory containing the file
                        import os
                        import platform
                        
                        file_path = Path(analysis_file)
                        dir_path = str(file_path.parent)
                        
                        if platform.system() == 'Windows':
                            os.startfile(dir_path)
                        elif platform.system() == 'Darwin':  # macOS
                            os.system(f'open "{dir_path}"')
                        else:  # Linux
                            os.system(f'xdg-open "{dir_path}"')
                    except Exception as e:
                        print(f"Error opening directory: {e}")
                        messagebox.showerror("Error", f"Failed to open directory: {e}")
    
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