"""
Dialog for visualizing resource metrics across models.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from typing import List, Optional

from tkinter import messagebox

class ResourceMetricsDialog:
    """Dialog for visualizing resource metrics across models"""
    
    def __init__(self, parent, controller):
        """
        Initialize the resource metrics visualization dialog.
        
        Args:
            parent: Parent widget
            controller: LeaderboardController instance
        """
        self.parent = parent
        self.controller = controller
        self.resource_path = None
        
        # Create the dialog window
        self.dialog = ttk.Toplevel(parent)
        self.dialog.title("Visualize Resource Metrics")
        self.dialog.geometry("550x650")
        self.dialog.minsize(500, 550)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=BOTH, expand=YES, padx=20, pady=20)
        
        # Build the UI
        self.create_content(main_frame)
        
        # Verify that there are entries with resource metrics available
        self.check_resource_metrics_availability()
    
    def create_content(self, parent_frame):
        """Create the dialog content"""
        # Title
        ttk.Label(parent_frame, text="Visualize Resource Metrics", 
                style="Title.TLabel").pack(anchor=W, pady=(0, 10))
        
        # Metric Selection Section
        metrics_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        metrics_frame.pack(fill=X, pady=10)
        
        ttk.Label(metrics_frame, text="Resource Metric Selection", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(metrics_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        metrics_content = ttk.Frame(metrics_frame, style="CardContent.TFrame")
        metrics_content.pack(fill=X, padx=10, pady=(0, 10))
        
        # Metric selection
        metric_frame = ttk.Frame(metrics_content)
        metric_frame.pack(fill=X, pady=(10, 5))
        ttk.Label(metric_frame, text="Resource Metric:").pack(side=LEFT)
        
        # Define available resource metrics
        self.available_resource_metrics = [
            "memory_peak_gb", 
            "memory_avg_gb", 
            "cpu_max_percent", 
            "cpu_avg_percent", 
            "gpu_avg_utilization",
            "gpu_max_utilization"
        ]
        
        # Display names for metrics
        self.metric_display_names = {
            "memory_peak_gb": "Peak Memory Usage (GB)",
            "memory_avg_gb": "Average Memory Usage (GB)",
            "cpu_max_percent": "Peak CPU Usage (%)",
            "cpu_avg_percent": "Average CPU Usage (%)",
            "gpu_avg_utilization": "Average GPU Utilization (%)",
            "gpu_max_utilization": "Peak GPU Utilization (%)"
        }
        
        self.metric_var = tk.StringVar(value="memory_peak_gb")
        metric_dropdown = ttk.Combobox(metric_frame, textvariable=self.metric_var, 
                                     values=[self.metric_display_names[m] for m in self.available_resource_metrics], 
                                     width=30, state="readonly")
        metric_dropdown.pack(side=LEFT, padx=(5, 0))
        
        # Number of top models
        top_frame = ttk.Frame(metrics_content)
        top_frame.pack(fill=X, pady=(5, 10))
        ttk.Label(top_frame, text="Number of models to include:").pack(side=LEFT)
        
        self.top_n_var = tk.IntVar(value=10)
        ttk.Spinbox(top_frame, from_=1, to=50, textvariable=self.top_n_var, width=5).pack(side=LEFT, padx=(5, 0))
        
        # Description
        ttk.Label(metrics_content, text="This visualization shows the specified resource metric across different models, allowing you to compare efficiency.", 
                wraplength=480).pack(anchor=W, pady=5)
        
        # Additional information based on metric
        self.metric_info_var = tk.StringVar()
        self.update_metric_info()  # Set initial info
        metric_info_label = ttk.Label(metrics_content, textvariable=self.metric_info_var, 
                                    style="Info.TLabel", wraplength=480)
        metric_info_label.pack(anchor=W, pady=5)
        
        # Update info when metric changes
        metric_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_metric_info())
        
        # Visualization preview area
        preview_frame = ttk.Frame(parent_frame, style="Card.TFrame")
        preview_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        ttk.Label(preview_frame, text="Visualization Preview", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(preview_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        self.preview_content = ttk.Frame(preview_frame, style="CardContent.TFrame")
        self.preview_content.pack(fill=BOTH, expand=YES, padx=10, pady=(0, 10))
        
        # Default placeholder
        ttk.Label(self.preview_content, text="Click 'Generate Visualization' to see resource metrics", 
                style="Subtitle.TLabel").pack(pady=20)
        
        # Buttons
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill=X, pady=(20, 0))
        
        # Cancel button
        ttk.Button(buttons_frame, text="Close", 
                 style="secondary", command=self.dialog.destroy).pack(side=RIGHT, padx=(5, 0))
        
        # Generate visualization button
        ttk.Button(buttons_frame, text="Generate Visualization", 
                 style="success", command=self.generate_visualization).pack(side=RIGHT, padx=(5, 5))
        
        # Save button (initially disabled)
        self.save_button = ttk.Button(buttons_frame, text="Save Visualization", 
                                    command=self.save_visualization, state=DISABLED)
        self.save_button.pack(side=LEFT, padx=(0, 5))
    
    def check_resource_metrics_availability(self):
        """Check if there are any entries with resource metrics available"""
        # Safe check if leaderboard exists
        if not self.controller.leaderboard:
            return
            
        # Check if there are any entries with resource metrics
        entries_with_metrics = []
        for entry in self.controller.leaderboard.db.get("entries", []):
            if "resource_metrics" in entry:
                entries_with_metrics.append(entry)
        
        if not entries_with_metrics:
            ttk.Label(self.preview_content, 
                    text="No entries with resource metrics found in the leaderboard.",
                    style="Warning.TLabel").pack(pady=(0, 5))
            ttk.Label(self.preview_content, 
                    text="Run benchmarks with 'Monitor Resources' enabled to collect resource metrics.",
                    style="Info.TLabel").pack(pady=(0, 5))
    
    def update_metric_info(self):
        """Update the information text based on the selected metric"""
        selected_display = self.metric_var.get()
        
        # Find the actual metric key
        selected_metric = None
        for metric, display in self.metric_display_names.items():
            if display == selected_display:
                selected_metric = metric
                break
        
        if not selected_metric:
            return
        
        # Set appropriate info
        if "memory" in selected_metric:
            self.metric_info_var.set("Lower values indicate more memory-efficient models. This is important for deployment on resource-constrained devices.")
        elif "cpu" in selected_metric:
            self.metric_info_var.set("Lower values indicate more CPU-efficient models. This affects both inference speed and energy consumption.")
        elif "gpu" in selected_metric:
            self.metric_info_var.set("GPU utilization shows how effectively the model uses available GPU resources. Optimal values depend on your use case.")
    
    def get_selected_metric(self):
        """Get the actual metric key from the display name"""
        selected_display = self.metric_var.get()
        
        for metric, display in self.metric_display_names.items():
            if display == selected_display:
                return metric
        
        # Fall back to default if not found
        return "memory_peak_gb"
    
    def generate_visualization(self):
        """Generate the resource metrics visualization"""
        # Get selected metric and top n
        selected_metric = self.get_selected_metric()
        top_n = self.top_n_var.get()
        
        # Generate visualization through controller
        try:
            # Show a "Please wait" message and watch cursor
            self.preview_content.config(cursor="watch")
            for widget in self.preview_content.winfo_children():
                widget.destroy()
            wait_label = ttk.Label(self.preview_content, text="Generating visualization...", 
                    style="Info.TLabel")
            wait_label.pack(pady=20)
            self.preview_content.update()
            
            # Generate the visualization
            self.resource_path = self.controller.visualize_resource_metrics(
                metric=selected_metric,
                top_n=top_n
            )
            
            if self.resource_path:
                # Display the visualization
                self.show_visualization(self.resource_path)
                
                # Enable save button
                self.save_button.config(state=NORMAL)
            else:
                # Handle the case where no visualization was generated but no exception was raised
                messagebox.showerror("Error", "Failed to generate resource metrics visualization.")
                
                # Clear preview area and add explanation
                for widget in self.preview_content.winfo_children():
                    widget.destroy()
                    
                ttk.Label(self.preview_content, text="No visualization could be generated.", 
                        style="Danger.TLabel").pack(pady=10)
                ttk.Label(self.preview_content, 
                        text="This could be because no entries have the selected resource metric.",
                        style="Info.TLabel").pack(pady=5)
                ttk.Label(self.preview_content, 
                        text="Try selecting a different metric or run benchmarks with resource monitoring enabled.",
                        style="Info.TLabel").pack(pady=5)
                
        except Exception as e:
            # Log the error
            print(f"Error generating resource metrics: {e}")
            messagebox.showerror("Error", f"Error generating resource metrics: {e}")
            
            # Clear preview area and add explanation
            for widget in self.preview_content.winfo_children():
                widget.destroy()
                
            ttk.Label(self.preview_content, text=f"Error: {e}", 
                    style="Danger.TLabel").pack(pady=10)
            
            if "No entries found with resource metric" in str(e):
                ttk.Label(self.preview_content, 
                        text="No entries have the selected resource metric recorded.",
                        style="Info.TLabel").pack(pady=5)
                ttk.Label(self.preview_content, 
                        text="Try selecting a different metric or run benchmarks with resource monitoring enabled.",
                        style="Info.TLabel").pack(pady=5)
            else:
                ttk.Label(self.preview_content, 
                        text="Try selecting a different metric or number of models.",
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
            
            # Add information about the image dimensions
            ttk.Label(self.preview_content, 
                    text=f"Original size: {original_width}x{original_height}",
                    style="Info.TLabel").pack(pady=(0, 5))
            
            # Add interpretation guidance based on metric type
            selected_metric = self.get_selected_metric()
            if "memory" in selected_metric or "cpu" in selected_metric:
                ttk.Label(self.preview_content, 
                        text="Note: For memory and CPU metrics, lower values indicate more efficient models.",
                        style="Info.TLabel", wraplength=450).pack(pady=5)
            elif "gpu" in selected_metric:
                ttk.Label(self.preview_content, 
                        text="Note: GPU utilization should be interpreted based on your specific use case. Higher values may indicate better GPU utilization, but also higher power consumption.",
                        style="Info.TLabel", wraplength=450).pack(pady=5)
            
        except Exception as e:
            print(f"Error displaying visualization: {e}")
            ttk.Label(self.preview_content, text=f"Error displaying visualization: {e}", 
                    style="Danger.TLabel").pack(pady=20)
            
            # Suggest a solution
            ttk.Label(self.preview_content, 
                    text="Try selecting a different metric or number of models.",
                    style="Info.TLabel").pack(pady=5)
    
    def save_visualization(self):
        """Save the visualization to a file"""
        if not hasattr(self, 'resource_path') or not self.resource_path:
            messagebox.showerror("Error", "No visualization available to save.")
            return
            
        try:
            # Use controller to save the visualization
            success = self.controller.save_visualization(Path(self.resource_path))
            
            if success:
                messagebox.showinfo("Success", "Visualization saved successfully.")
            else:
                messagebox.showinfo("Info", "Save operation cancelled.")
                
        except Exception as e:
            print(f"Error saving visualization: {e}")
            messagebox.showerror("Error", f"Failed to save visualization: {e}")