"""
Dialog for visualizing a model's performance history.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from typing import List, Optional

from tkinter import messagebox

class ModelHistoryDialog:
    """Dialog for visualizing a model's performance history"""
    
    def __init__(self, parent, controller, model_name):
        """
        Initialize the model history dialog.
        
        Args:
            parent: Parent widget
            controller: LeaderboardController instance
            model_name: Name of the model to visualize
        """
        self.parent = parent
        self.controller = controller
        self.model_name = model_name
        self.history_path = None
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title(f"Model History: {model_name}")
        self.dialog.geometry("550x600")
        self.dialog.minsize(500, 500)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Build the UI
        self.create_content(main_frame)
        
        # Check if the model has sufficient history entries
        self.check_history_availability()
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title
        ttk.Label(parent_frame, text=f"Performance History for {self.model_name}", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Metrics to include
        metrics_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        metrics_frame.pack(fill=X, pady=10)
        
        ttk.Label(metrics_frame, text="Metrics to Include", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(metrics_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        metrics_content = ttk.Frame(metrics_frame, style="CardContent.TFrame")
        metrics_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Define available metrics
        available_metrics = [
            "test_pass_rate", 
            "api_success_rate", 
            "execution_success_rate", 
            "avg_response_time"
        ]
        
        # Metric display names
        metric_display_names = {
            "test_pass_rate": "Test Pass Rate",
            "api_success_rate": "API Success Rate",
            "execution_success_rate": "Execution Success Rate",
            "avg_response_time": "Average Response Time"
        }
        
        # Metric checkboxes
        self.metric_vars = {}
        for metric in available_metrics:
            # Default to selecting test_pass_rate and api_success_rate
            default_selected = metric in ["test_pass_rate", "api_success_rate"]
            var = tk.BooleanVar(value=default_selected)
            self.metric_vars[metric] = var
            
            # Format metric name for display
            display_name = metric_display_names.get(metric, metric.replace("_", " ").title())
            ttk.Checkbutton(metrics_content, text=display_name, 
                          variable=var).pack(anchor=W, pady=2)
        
        # Description
        desc_frame = ttk.Frame(parent_frame)
        desc_frame.pack(fill=X, pady=5)
        
        ttk.Label(desc_frame, text="This will generate a line chart showing how the model's performance has changed over time across multiple benchmark runs.", 
                wraplength=500).pack(anchor=W, pady=5)
        
        # Status message
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(desc_frame, textvariable=self.status_var, 
                                     style="Info.TLabel", wraplength=500)
        self.status_label.pack(anchor=W, pady=5)
        
        # Visualization preview area
        preview_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        preview_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        ttk.Label(preview_frame, text="Visualization Preview", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(preview_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        self.preview_content = ttk.Frame(preview_frame, style="CardContent.TFrame")
        self.preview_content.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        # Default placeholder
        ttk.Label(self.preview_content, text="Click 'Generate History' to see visualization", 
                style="Subtitle.TLabel").pack(pady=20)
        
        # Buttons
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Close", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Generate history button
        self.generate_button = ttk.Button(buttons_frame, text="Generate History", 
                                       style="success", command=self.generate_history)
        self.generate_button.pack(side=RIGHT, padx=(5, 5))
        
        # Save button (initially disabled)
        self.save_button = ttk.Button(buttons_frame, text="Save Visualization", 
                                    command=self.save_visualization, state=DISABLED)
        self.save_button.pack(side=LEFT, padx=(0, 5))
    
    def check_history_availability(self):
        """Check if the model has sufficient history entries"""
        try:
            # Get model entries from controller
            entries = self.controller.get_model_entries(self.model_name)
            
            # Update status based on number of entries
            if not entries:
                self.status_var.set(f"No benchmark entries found for model '{self.model_name}'.")
                self.generate_button.config(state=DISABLED)
            elif len(entries) == 1:
                self.status_var.set(f"Only one benchmark entry found. At least two entries are needed to show performance trends.")
                # Still allow generating with one entry, but warn the user
            else:
                self.status_var.set(f"Found {len(entries)} benchmark entries for this model.")
        except Exception as e:
            print(f"Error checking history availability: {e}")
            self.status_var.set(f"Error checking model history: {e}")
            self.generate_button.config(state=DISABLED)
    
    def generate_history(self):
        """Generate the history visualization"""
        # Get selected metrics
        selected_metrics = [m for m, v in self.metric_vars.items() if v.get()]
        
        if not selected_metrics:
            messagebox.showwarning("Warning", "Please select at least one metric.")
            return
        
        # Generate visualization through controller
        try:
            # Show a "Please wait" message and watch cursor
            self.preview_content.config(cursor="watch")
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            wait_label = ttk.Label(self.preview_content, text="Generating history visualization...", 
                                  style="Info.TLabel")
            wait_label.pack(pady=20)
            self.preview_content.update()
            
            # Generate the visualization
            self.history_path = self.controller.visualize_model_history(
                model_name=self.model_name,
                metrics=selected_metrics
            )
            
            if self.history_path:
                # Display the visualization
                self.show_visualization(self.history_path)
                
                # Enable save button
                self.save_button.config(state=NORMAL)
            else:
                # Handle the case where no visualization was generated but no exception was raised
                messagebox.showerror("Error", "Failed to generate history visualization.")
                
                # Clear preview area and add explanation
                for widget in self.preview_content.winfo_children():
                    widget.destroy()
                
                ttk.Label(self.preview_content, text="No visualization could be generated.", 
                        style="Danger.TLabel").pack(pady=10)
                ttk.Label(self.preview_content, 
                        text="This could be because there are not enough entries or the metrics are missing.",
                        style="Info.TLabel").pack(pady=5)
                
        except Exception as e:
            # Log the error
            print(f"Error generating history: {e}")
            messagebox.showerror("Error", f"Error generating history: {e}")
            
            # Clear preview area and add explanation
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            
            error_msg = str(e)
            ttk.Label(self.preview_content, text=f"Error: {error_msg}", 
                    style="Danger.TLabel").pack(pady=10)
            
            if "No history found" in error_msg:
                ttk.Label(self.preview_content, 
                        text="Try running more benchmarks with this model to build a history.",
                        style="Info.TLabel").pack(pady=5)
            else:
                ttk.Label(self.preview_content, 
                        text="Try selecting different metrics or check if metrics data is available.",
                        style="Info.TLabel").pack(pady=5)
                
        finally:
            # Reset cursor
            self.preview_content.config(cursor="")
    
    def show_visualization(self, file_path):
        """Show the visualization in the preview area"""
        # Clear existing content
        for widget in self.preview_content.winfo_children():
            widget.destroy()
        
        try:
            # Load image
            img = Image.open(file_path)
            
            # Store original image dimensions
            original_width, original_height = img.size
            
            # Calculate size to fit in preview (preserving aspect ratio)
            preview_width = self.preview_content.winfo_width() or 500
            preview_height = self.preview_content.winfo_height() or 350
            
            # Resize if needed
            w, h = img.size
            if w > preview_width or h > preview_height:
                ratio = min(preview_width / w, preview_height / h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Add label with image
            img_label = ttk.Label(self.preview_content, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack(padx=10, pady=10)
            
            # Add information about the visualization
            ttk.Label(self.preview_content, 
                    text=f"Original size: {original_width}x{original_height}",
                    style="Info.TLabel").pack(pady=(0, 5))
            
            # Add interpretation guidance
            ttk.Label(self.preview_content, 
                    text="Interpretation: Lines show performance trends over time. Upward trends indicate improvement.",
                    style="Info.TLabel", wraplength=450).pack(pady=(5, 0))
            
            # Get model entries
            entries = self.controller.get_model_entries(self.model_name)
            if entries and len(entries) == 1:
                ttk.Label(self.preview_content, 
                        text="Note: This model only has one benchmark entry. More entries are needed to see performance trends.",
                        style="Warning.TLabel", wraplength=450).pack(pady=(5, 0))
            elif entries:
                oldest = min(entries, key=lambda e: e["timestamp"])
                newest = max(entries, key=lambda e: e["timestamp"])
                
                time_span = f"Data spans from {oldest['timestamp']} to {newest['timestamp']}"
                ttk.Label(self.preview_content, text=time_span,
                        style="Info.TLabel", wraplength=450).pack(pady=(5, 0))
            
        except Exception as e:
            print(f"Error displaying visualization: {e}")
            ttk.Label(self.preview_content, text=f"Error displaying visualization: {e}", 
                    style="Danger.TLabel").pack(pady=20)
            
            # Suggest a solution
            ttk.Label(self.preview_content, 
                    text="Try selecting different metrics or run more benchmarks.",
                    style="Info.TLabel").pack(pady=5)
    
    def save_visualization(self):
        """Save the visualization to a file"""
        if not hasattr(self, 'history_path') or not self.history_path:
            messagebox.showerror("Error", "No visualization available to save.")
            return
            
        try:
            # Use controller to save the visualization
            success = self.controller.save_visualization(Path(self.history_path))
            
            if success:
                messagebox.showinfo("Success", "Visualization saved successfully.")
            else:
                messagebox.showinfo("Info", "Save operation cancelled.")
                
        except Exception as e:
            print(f"Error saving visualization: {e}")
            messagebox.showerror("Error", f"Failed to save visualization: {e}")