"""
Dialog for comparing multiple models from the leaderboard.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from typing import List, Dict, Any

from tkinter import messagebox

class ModelCompareDialog:
    """Dialog for comparing multiple models from the leaderboard"""
    
    def __init__(self, parent, controller, model_names):
        """
        Initialize the model comparison dialog.
        
        Args:
            parent: Parent widget
            controller: LeaderboardController instance
            model_names: List of model names to compare
        """
        self.parent = parent
        self.controller = controller
        self.model_names = model_names
        self.comparison_path = None
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Compare Models")
        self.dialog.geometry("600x700")
        self.dialog.minsize(500, 600)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Build the UI
        self.create_content(main_frame)
        
        # Check if we have valid models to compare
        if len(self.model_names) < 2:
            messagebox.showwarning("Warning", 
                                 "At least two models are required for comparison. Please select more models.")
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title
        ttk.Label(parent_frame, text="Compare Models", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Selected models
        models_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        models_frame.pack(fill=X, pady=10)
        
        ttk.Label(models_frame, text="Selected Models", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(models_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        models_content = ttk.Frame(models_frame, style="CardContent.TFrame")
        models_content.pack(fill=X, padx=10, pady=(0, 10))
        
        for model in self.model_names:
            ttk.Label(models_content, text=f"• {model}").pack(anchor=W, pady=2)
        
        # Metrics to compare
        metrics_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        metrics_frame.pack(fill=X, pady=10)
        
        ttk.Label(metrics_frame, text="Metrics to Compare", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
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
        
        # Metric checkboxes
        self.metric_vars = {}
        for metric in available_metrics:
            var = tk.BooleanVar(value=True)
            self.metric_vars[metric] = var
            
            # Format metric name for display
            display_name = metric.replace("_", " ").title()
            ttk.Checkbutton(metrics_content, text=display_name, 
                          variable=var).pack(anchor=W, pady=2)
        
        # Resource metrics
        resource_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        resource_frame.pack(fill=X, pady=10)
        
        ttk.Label(resource_frame, text="Resource Metrics to Include", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(resource_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        resource_content = ttk.Frame(resource_frame, style="CardContent.TFrame")
        resource_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Define available resource metrics
        available_resource_metrics = [
            "memory_peak_gb", 
            "memory_avg_gb", 
            "cpu_max_percent", 
            "cpu_avg_percent", 
            "gpu_avg_utilization",
            "gpu_max_utilization"
        ]
        
        # Resource metric checkboxes
        self.resource_metric_vars = {}
        for metric in available_resource_metrics:
            var = tk.BooleanVar(value=True)
            self.resource_metric_vars[metric] = var
            
            # Format metric name for display
            display_name = metric.replace("_", " ").title()
            ttk.Checkbutton(resource_content, text=display_name, 
                          variable=var).pack(anchor=W, pady=2)
        
        # Add description
        ttk.Label(resource_content, 
                text="Note: For memory and CPU metrics, lower values indicate better efficiency.",
                style="Info.TLabel", wraplength=400).pack(anchor=W, pady=(10, 0))
        
        # Visualization preview area
        preview_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        preview_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        ttk.Label(preview_frame, text="Visualization Preview", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(preview_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        self.preview_content = ttk.Frame(preview_frame, style="CardContent.TFrame")
        self.preview_content.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        # Default placeholder
        ttk.Label(self.preview_content, text="Click 'Generate Comparison' to see visualization", 
                style="Subtitle.TLabel").pack(pady=20)
        
        # Buttons
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Close", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Generate comparison button
        ttk.Button(buttons_frame, text="Generate Comparison", 
                 style="success", command=self.generate_comparison).pack(side=RIGHT, padx=(5, 5))
        
        # Save button (initially disabled)
        self.save_button = ttk.Button(buttons_frame, text="Save Visualization", 
                                    command=self.save_visualization, state=DISABLED)
        self.save_button.pack(side=LEFT, padx=(0, 5))
    
    def generate_comparison(self):
        """Generate the comparison visualization with improved error handling"""
        # Get selected metrics
        selected_metrics = [m for m, v in self.metric_vars.items() if v.get()]
        selected_resource_metrics = [m for m, v in self.resource_metric_vars.items() if v.get()]
        
        if not selected_metrics:
            messagebox.showwarning("Warning", "Please select at least one performance metric.")
            return
        
        # Check if we have at least two models to compare
        if len(self.model_names) < 2:
            messagebox.showwarning("Warning", "At least two models are required for comparison.")
            return
        
        # Generate visualization through controller
        try:
            # Show a "Please wait" message or cursor
            self.preview_content.config(cursor="watch")
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            wait_label = ttk.Label(self.preview_content, text="Generating comparison...", 
                    style="Info.TLabel")
            wait_label.pack(pady=20)
            self.preview_content.update()
            
            # Generate the comparison
            self.comparison_path = self.controller.compare_models(
                model_names=self.model_names,
                metrics=selected_metrics,
                resource_metrics=selected_resource_metrics if selected_resource_metrics else None
            )
            
            if self.comparison_path:
                # Display the visualization
                self.show_visualization(self.comparison_path)
                
                # Enable save button
                self.save_button.config(state=NORMAL)
            else:
                # Handle the case where no visualization was generated but no exception was raised
                messagebox.showerror("Error", "Failed to generate comparison visualization. Check the console for details.")
                # Log the error
                print(f"Error: compare_models returned None for models {self.model_names}")
                
                # Add a helpful message to the preview
                for widget in self.preview_content.winfo_children():
                    widget.destroy()
                ttk.Label(self.preview_content, text="Visualization generation failed", 
                        style="Danger.TLabel").pack(pady=10)
                ttk.Label(self.preview_content, 
                        text="Try selecting different metrics or models and generate again.",
                        style="Info.TLabel").pack(pady=5)
                    
        except Exception as e:
            # Log the error
            print(f"Error generating comparison: {e}")
            messagebox.showerror("Error", f"Error generating comparison: {e}")
            
            # Add a helpful message to the preview
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            ttk.Label(self.preview_content, text=f"Error: {e}", 
                    style="Danger.TLabel").pack(pady=10)
            ttk.Label(self.preview_content, 
                    text="Try selecting different metrics or models and generate again.",
                    style="Info.TLabel").pack(pady=5)
        finally:
            # Reset cursor
            self.preview_content.config(cursor="")
    
    def show_visualization(self, file_path):
        """Show the visualization in the preview area with improved handling"""
        # Clear existing content
        for widget in self.preview_content.winfo_children():
            widget.destroy()
        
        try:
            # Load image
            img = Image.open(file_path)
            
            # Store original image dimensions
            original_width, original_height = img.size
            
            # Calculate size to fit in preview (preserving aspect ratio)
            preview_width = self.preview_content.winfo_width() or 550
            preview_height = self.preview_content.winfo_height() or 400
            
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
            
            # Add information about the image dimensions
            ttk.Label(self.preview_content, 
                    text=f"Original size: {original_width}x{original_height}",
                    style="Info.TLabel").pack(pady=(0, 5))
            
            # Add note about included models
            ttk.Label(self.preview_content, 
                    text=f"Comparing {len(self.model_names)} models",
                    style="Info.TLabel").pack(pady=(0, 5))
            
            # Add interpretation note for radar chart
            ttk.Label(self.preview_content, 
                    text="Interpretation: Higher values on the chart indicate better performance for each metric.",
                    style="Info.TLabel", wraplength=400).pack(pady=(5, 0))
            
        except Exception as e:
            # Log the error
            print(f"Error displaying visualization: {e}")
            ttk.Label(self.preview_content, text=f"Error displaying visualization: {e}", 
                    style="Danger.TLabel").pack(pady=20)
            
            # Suggest a solution
            ttk.Label(self.preview_content, 
                    text="Try selecting different metrics or models and generate again.",
                    style="Info.TLabel").pack(pady=5)
    
    def save_visualization(self):
        """Save the visualization to a file"""
        if not hasattr(self, 'comparison_path') or not self.comparison_path:
            messagebox.showerror("Error", "No visualization available to save.")
            return
            
        try:
            # Use controller to save the visualization
            success = self.controller.save_visualization(Path(self.comparison_path))
            
            if success:
                messagebox.showinfo("Success", "Visualization saved successfully.")
            else:
                messagebox.showinfo("Info", "Save operation cancelled.")
                
        except Exception as e:
            print(f"Error saving visualization: {e}")
            messagebox.showerror("Error", f"Failed to save visualization: {e}")