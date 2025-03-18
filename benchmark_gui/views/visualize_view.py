"""
Visualization tab UI for LM Studio Benchmark GUI.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from pathlib import Path
from PIL import Image, ImageTk

from controllers.visualize_controller import VisualizeController

from tkinter import messagebox
from PIL import Image, ImageTk
import time

class VisualizeView:
    """Visualization tab UI class"""
    
    def __init__(self, parent, state):
        """
        Initialize the visualization view.
        
        Args:
            parent: Parent widget
            state: Shared application state
        """
        self.parent = parent
        self.state = state
        self.controller = VisualizeController(state)
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Initialize UI components
        self.viz_files = []
        self.current_viz_index = 0
        self.current_viz_file = None
        
        # Set up the panel
        self.setup_panel()
        
        # Check if visualization files are in state (from benchmark tab)
        self.check_for_new_visualizations()
    
    def setup_panel(self):
        """Set up the visualization panel UI"""
        # Split into left panel (settings) and right panel (visualization)
        paned_window = ttk.PanedWindow(self.frame, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=YES)
        
        # Create left panel container first (a regular frame)
        left_container = ttk.Frame(paned_window)
        paned_window.add(left_container, weight=1)
        
        # Create ScrolledFrame inside the container
        settings_frame = ScrolledFrame(left_container, autohide=True, width=300)
        settings_frame.pack(fill=BOTH, expand=YES)
        
        # Right panel (visualization)
        visualization_frame = ttk.Frame(paned_window)
        paned_window.add(visualization_frame, weight=3)
        
        # Add settings to the left panel
        self.create_visualization_settings(settings_frame)
        
        # Add visualization area to the right panel
        self.create_visualization_area(visualization_frame)
    
    def create_visualization_settings(self, parent_frame):
        """Create the visualization settings panel"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Analysis File Section
        file_frame = ttk.Frame(frame, style="Card.TFrame")
        file_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(file_frame, text="Analysis File", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(file_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(file_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # File path
        ttk.Label(content_frame, text="Analysis JSON:").pack(anchor=W, pady=(5, 2))
        self.analysis_file_var = tk.StringVar()
        file_entry = ttk.Entry(content_frame, textvariable=self.analysis_file_var, width=30)
        file_entry.pack(side=LEFT, fill=X, expand=YES, pady=(0, 10))
        
        browse_btn = ttk.Button(content_frame, text="Browse", command=self.browse_analysis_file)
        browse_btn.pack(side=LEFT, padx=(5, 0), pady=(0, 10))
        
        # Visualization Options Section
        options_frame = ttk.Frame(frame, style="Card.TFrame")
        options_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(options_frame, text="Visualization Options", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(options_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(options_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Visualization types
        ttk.Label(content_frame, text="Chart Types:").pack(anchor=W, pady=(5, 2))
        
        self.visualization_types = [
            "Success Metrics Comparison",
            "Test Pass Rate by Category",
            "Test Pass Rate by Difficulty",
            "Test Pass Rate by Language",
            "Task Performance Heatmap",
            "Response Time by Category",
            "Success Rate by Category",
            "Response Time by Difficulty",
            "Success Rate by Difficulty",
            "Response Time by Language",
            "Success Rate by Language",
            "Task Comparison"
        ]
        
        self.viz_type_vars = {}
        for viz_type in self.visualization_types:
            var = tk.BooleanVar(value=True)
            self.viz_type_vars[viz_type] = var
            ttk.Checkbutton(content_frame, text=viz_type, variable=var).pack(anchor=W)
        
        # Output directory
        ttk.Label(content_frame, text="Output Directory:").pack(anchor=W, pady=(10, 2))
        dir_frame = ttk.Frame(content_frame)
        dir_frame.pack(fill=X, pady=(0, 10))
        
        self.viz_output_dir_var = tk.StringVar(value=str(self.state.get("output_dir", "benchmark_results")))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.viz_output_dir_var, width=30)
        dir_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_dir_btn = ttk.Button(dir_frame, text="Browse", 
                                  command=self.browse_output_directory)
        browse_dir_btn.pack(side=LEFT, padx=(5, 0))
        
        # Action buttons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=X, pady=15)
        
        self.visualize_button = ttk.Button(buttons_frame, text="Generate Visualizations", 
                                         style="success", command=self.generate_visualizations)
        self.visualize_button.pack(side=LEFT, padx=5)
    
    def create_visualization_area(self, parent_frame):
        """Create the visualization display area"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Title
        ttk.Label(frame, text="Visualization Preview", style="Header.TLabel").pack(anchor=W)
        ttk.Separator(frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Status information
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=X, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=LEFT)
        self.viz_status_var = tk.StringVar(value="No visualization loaded")
        viz_status_label = ttk.Label(status_frame, textvariable=self.viz_status_var, style="Info.TLabel")
        viz_status_label.pack(side=LEFT, padx=5)
        
        # Canvas for visualization
        canvas_frame = ttk.Frame(frame, style="Card.TFrame")
        canvas_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        # Create an empty canvas first
        self.viz_canvas_frame = ttk.Frame(canvas_frame)
        self.viz_canvas_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Navigation buttons for multiple visualizations
        self.nav_frame = ttk.Frame(frame)
        self.nav_frame.pack(fill=X, pady=5)
        
        self.prev_viz_btn = ttk.Button(self.nav_frame, text="Previous", command=self.prev_visualization, state=DISABLED)
        self.prev_viz_btn.pack(side=LEFT, padx=5)
        
        self.viz_counter_var = tk.StringVar(value="0/0")
        ttk.Label(self.nav_frame, textvariable=self.viz_counter_var).pack(side=LEFT, padx=5)
        
        self.next_viz_btn = ttk.Button(self.nav_frame, text="Next", command=self.next_visualization, state=DISABLED)
        self.next_viz_btn.pack(side=LEFT, padx=5)
        
        # Save button
        self.save_viz_btn = ttk.Button(self.nav_frame, text="Save Current Visualization", 
                                     command=self.save_current_visualization, state=DISABLED)
        self.save_viz_btn.pack(side=RIGHT, padx=5)
    
    def check_for_new_visualizations(self):
        """Check if visualizations are passed from benchmark tab with improved error handling"""
        viz_files = self.state.get("visualization_files")
        if viz_files:
            try:
                # Validate the visualization files
                valid_files = []
                for file_path in viz_files:
                    path = Path(file_path)
                    if path.exists() and path.suffix.lower() == '.png':
                        valid_files.append(path)
                    else:
                        print(f"Warning: Invalid visualization file: {file_path}")
                
                if not valid_files:
                    self.viz_status_var.set("No valid visualizations found")
                    
                    # Show helpful message in preview area
                    for widget in self.viz_canvas_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(self.viz_canvas_frame, 
                            text="No valid visualization files were found.", 
                            style="Warning.TLabel").pack(pady=10)
                    ttk.Label(self.viz_canvas_frame, 
                            text="Try generating visualizations using the options on the left.", 
                            style="Info.TLabel").pack(pady=5)
                    return
                    
                self.viz_files = valid_files
                self.current_viz_index = 0
                
                # Store current file info in state for persistence
                self.state["current_visualization"] = {
                    "files": [str(f) for f in valid_files],
                    "index": 0,
                    "timestamp": time.time()
                }
                
                self.show_visualization(self.viz_files[self.current_viz_index])
                
                # Update visualization status
                self.viz_status_var.set(f"Loaded {len(valid_files)} visualizations")
                
                # Enable navigation buttons
                self.prev_viz_btn.config(state=DISABLED)
                self.next_viz_btn.config(state=NORMAL if len(valid_files) > 1 else DISABLED)
                self.save_viz_btn.config(state=NORMAL)
                
                # Update counter
                self.viz_counter_var.set(f"1/{len(valid_files)}")
                
            except Exception as e:
                print(f"Error loading visualizations: {e}")
                self.viz_status_var.set(f"Error loading visualizations: {e}")
                
                # Show error message in preview area
                for widget in self.viz_canvas_frame.winfo_children():
                    widget.destroy()
                ttk.Label(self.viz_canvas_frame, 
                        text=f"Error loading visualizations: {str(e)}", 
                        style="Danger.TLabel").pack(pady=10)
                ttk.Label(self.viz_canvas_frame, 
                        text="Try generating visualizations again or check console for details.", 
                        style="Info.TLabel").pack(pady=5)
                
            # Always clear from state to avoid reloading
            self.state.pop("visualization_files", None)
        
        # Check if we have previously loaded visualizations
        elif "current_visualization" in self.state:
            try:
                viz_info = self.state["current_visualization"]
                timestamp = viz_info.get("timestamp", 0)
                
                # Only restore if saved within the last hour (to avoid showing very old visualizations)
                if time.time() - timestamp < 3600:  # 3600 seconds = 1 hour
                    # Validate files still exist
                    files = [Path(f) for f in viz_info.get("files", [])]
                    valid_files = [f for f in files if f.exists()]
                    
                    if valid_files:
                        self.viz_files = valid_files
                        
                        # Ensure index is valid
                        saved_index = viz_info.get("index", 0)
                        self.current_viz_index = min(saved_index, len(valid_files) - 1)
                        
                        self.show_visualization(self.viz_files[self.current_viz_index])
                        
                        # Update visualization status
                        self.viz_status_var.set(f"Restored {len(valid_files)} visualizations")
                        
                        # Enable navigation buttons
                        self.prev_viz_btn.config(state=DISABLED if self.current_viz_index == 0 else NORMAL)
                        self.next_viz_btn.config(state=DISABLED if self.current_viz_index >= len(valid_files) - 1 else NORMAL)
                        self.save_viz_btn.config(state=NORMAL)
                        
                        # Update counter
                        self.viz_counter_var.set(f"{self.current_viz_index + 1}/{len(valid_files)}")
            except Exception as e:
                print(f"Error restoring previous visualizations: {e}")
                # Don't show an error to the user, just silently fail for this convenience feature
    
    def browse_analysis_file(self):
        """Browse for an analysis file"""
        filename = self.controller.browse_for_file("Select Analysis File", [("JSON files", "*.json")])
        if filename:
            self.analysis_file_var.set(filename)
    
    def browse_output_directory(self):
        """Browse for an output directory"""
        directory = self.controller.browse_for_directory("Select Output Directory")
        if directory:
            self.viz_output_dir_var.set(directory)
    
    def generate_visualizations(self):
        """Generate visualizations for the selected analysis file"""
        analysis_file = self.analysis_file_var.get()
        
        if not analysis_file:
            tk.messagebox.showwarning("Warning", "Please select an analysis file.")
            return
        
        # Get selected visualization types
        selected_types = [viz_type for viz_type, var in self.viz_type_vars.items() if var.get()]
        
        if not selected_types:
            tk.messagebox.showwarning("Warning", "Please select at least one visualization type.")
            return
        
        # Generate visualizations through controller
        output_dir = self.viz_output_dir_var.get()
        
        viz_files = self.controller.generate_visualizations(
            analysis_file, output_dir, selected_types
        )
        
        if viz_files:
            self.viz_files = viz_files
            self.current_viz_index = 0
            self.show_visualization(self.viz_files[self.current_viz_index])
            
            # Update visualization status
            self.viz_status_var.set(f"Generated {len(viz_files)} visualizations")
            
            # Enable navigation buttons
            self.prev_viz_btn.config(state=DISABLED)
            self.next_viz_btn.config(state=NORMAL if len(viz_files) > 1 else DISABLED)
            self.save_viz_btn.config(state=NORMAL)
            
            # Update counter
            self.viz_counter_var.set(f"1/{len(viz_files)}")
        else:
            self.viz_status_var.set("No visualizations were generated")
    
    def show_visualization(self, file_path):
        """Show a visualization in the canvas"""
        # Clear existing canvas
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
        
        try:
            # Load image
            img = Image.open(file_path)
            
            # Calculate size to fit in the canvas (preserving aspect ratio)
            canvas_width = self.viz_canvas_frame.winfo_width() or 800
            canvas_height = self.viz_canvas_frame.winfo_height() or 600
            
            # Resize if needed
            w, h = img.size
            if w > canvas_width or h > canvas_height:
                ratio = min(canvas_width / w, canvas_height / h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Add label with image
            img_label = ttk.Label(self.viz_canvas_frame, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack(padx=10, pady=10)
            
            # Add filename below
            ttk.Label(self.viz_canvas_frame, text=file_path.name).pack(pady=(0, 10))
            
            # Store the current file path
            self.current_viz_file = file_path
            
        except Exception as e:
            print(f"Error displaying visualization: {e}")
            ttk.Label(self.viz_canvas_frame, text=f"Error displaying {file_path.name}: {e}", 
                    style="Danger.TLabel").pack(pady=20)
    
    def next_visualization(self):
        """Show the next visualization with improved error handling"""
        if hasattr(self, 'viz_files') and self.viz_files:
            try:
                if self.current_viz_index < len(self.viz_files) - 1:
                    self.current_viz_index += 1
                    
                    # Update state for persistence
                    if "current_visualization" in self.state:
                        self.state["current_visualization"]["index"] = self.current_viz_index
                    
                    self.show_visualization(self.viz_files[self.current_viz_index])
                    
                    # Update counter
                    self.viz_counter_var.set(f"{self.current_viz_index + 1}/{len(self.viz_files)}")
                    
                    # Update navigation buttons
                    self.prev_viz_btn.config(state=NORMAL)
                    self.next_viz_btn.config(state=DISABLED if self.current_viz_index >= len(self.viz_files) - 1 else NORMAL)
            except Exception as e:
                print(f"Error navigating to next visualization: {e}")
                messagebox.showerror("Error", f"Error navigating to next visualization: {e}")

    def prev_visualization(self):
        """Show the previous visualization with improved error handling"""
        if hasattr(self, 'viz_files') and self.viz_files:
            try:
                if self.current_viz_index > 0:
                    self.current_viz_index -= 1
                    
                    # Update state for persistence
                    if "current_visualization" in self.state:
                        self.state["current_visualization"]["index"] = self.current_viz_index
                    
                    self.show_visualization(self.viz_files[self.current_viz_index])
                    
                    # Update counter
                    self.viz_counter_var.set(f"{self.current_viz_index + 1}/{len(self.viz_files)}")
                    
                    # Update navigation buttons
                    self.prev_viz_btn.config(state=DISABLED if self.current_viz_index <= 0 else NORMAL)
                    self.next_viz_btn.config(state=NORMAL)
            except Exception as e:
                print(f"Error navigating to previous visualization: {e}")
                messagebox.showerror("Error", f"Error navigating to previous visualization: {e}")
    
    def save_current_visualization(self):
        """Save the current visualization to a file"""
        if hasattr(self, 'current_viz_file') and self.current_viz_file:
            self.controller.save_visualization(self.current_viz_file)