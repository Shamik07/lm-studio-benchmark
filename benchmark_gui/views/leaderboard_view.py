"""
Leaderboard tab UI for LM Studio Benchmark GUI.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import messagebox
from PIL import Image, ImageTk

from controllers.leaderboard_controller import LeaderboardController
from views.dialogs.model_compare import ModelCompareDialog
from views.dialogs.model_history import ModelHistoryDialog
from views.dialogs.resource_viz import ResourceMetricsDialog

class LeaderboardView:
    """Leaderboard tab UI class"""
    
    def __init__(self, parent, state):
        """
        Initialize the leaderboard view.
        
        Args:
            parent: Parent widget
            state: Shared application state
        """
        self.parent = parent
        self.state = state
        self.controller = LeaderboardController(state)
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Set up the panel
        self.setup_panel()
    
    def setup_panel(self):
        """Set up the leaderboard panel UI"""
        # Split into left panel (actions) and right panel (display)
        paned_window = ttk.PanedWindow(self.frame, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=YES)
        
        # Create left panel container first
        left_container = ttk.Frame(paned_window)
        paned_window.add(left_container, weight=1)
        
        # Create ScrolledFrame inside the container
        actions_frame = ScrolledFrame(left_container, autohide=True, width=300)
        actions_frame.pack(fill=BOTH, expand=YES)
        
        # Right panel (leaderboard display)
        display_frame = ttk.Frame(paned_window)
        paned_window.add(display_frame, weight=3)
        
        # Add actions to the left panel
        self.create_leaderboard_actions(actions_frame)
        
        # Add leaderboard display to the right panel
        self.create_leaderboard_display(display_frame)
    
    def create_leaderboard_actions(self, parent_frame):
        """Create the leaderboard actions panel"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Add Entry Section
        add_frame = ttk.Frame(frame, style="Card.TFrame")
        add_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(add_frame, text="Add to Leaderboard", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(add_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(add_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Analysis file for adding
        ttk.Label(content_frame, text="Analysis JSON:").pack(anchor=W, pady=(5, 2))
        file_frame = ttk.Frame(content_frame)
        file_frame.pack(fill=X, pady=(0, 10))
        
        self.add_analysis_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.add_analysis_file_var, width=30)
        file_entry.pack(side=LEFT, fill=X, expand=YES)
        
        browse_btn = ttk.Button(file_frame, text="Browse", 
                              command=self.browse_analysis_file)
        browse_btn.pack(side=LEFT, padx=(5, 0))
        
        # Model name
        ttk.Label(content_frame, text="Model Name:").pack(anchor=W, pady=(5, 2))
        self.model_name_var = tk.StringVar()
        ttk.Entry(content_frame, textvariable=self.model_name_var, width=30).pack(fill=X, pady=(0, 10))
        
        # Model info
        ttk.Label(content_frame, text="Model Info (optional):").pack(anchor=W, pady=(5, 2))
        
        # Parameters field
        param_frame = ttk.Frame(content_frame)
        param_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(param_frame, text="Parameters:").pack(side=LEFT)
        self.model_params_var = tk.StringVar()
        ttk.Entry(param_frame, textvariable=self.model_params_var, width=10).pack(side=LEFT, padx=(5, 0))
        
        # Version field
        version_frame = ttk.Frame(content_frame)
        version_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(version_frame, text="Version:").pack(side=LEFT)
        self.model_version_var = tk.StringVar()
        ttk.Entry(version_frame, textvariable=self.model_version_var, width=10).pack(side=LEFT, padx=(5, 0))
        
        # Architecture field
        arch_frame = ttk.Frame(content_frame)
        arch_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(arch_frame, text="Architecture:").pack(side=LEFT)
        self.model_arch_var = tk.StringVar()
        ttk.Entry(arch_frame, textvariable=self.model_arch_var, width=15).pack(side=LEFT, padx=(5, 0))
        
        # Quantization field
        quant_frame = ttk.Frame(content_frame)
        quant_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(quant_frame, text="Quantization:").pack(side=LEFT)
        self.model_quant_var = tk.StringVar()
        ttk.Entry(quant_frame, textvariable=self.model_quant_var, width=10).pack(side=LEFT, padx=(5, 0))
        
        # Add button
        ttk.Button(content_frame, text="Add to Leaderboard", style="success", 
                 command=self.add_to_leaderboard).pack(fill=X, pady=(5, 0))
        
        # Leaderboard Actions Section
        actions_frame = ttk.Frame(frame, style="Card.TFrame")
        actions_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(actions_frame, text="Leaderboard Actions", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(actions_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(actions_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Action buttons
        ttk.Button(content_frame, text="Refresh Leaderboard", 
                 command=self.refresh_leaderboard).pack(fill=X, pady=(5, 5))
        
        ttk.Button(content_frame, text="Generate Report", 
                 command=self.generate_leaderboard_report).pack(fill=X, pady=(0, 5))
        
        ttk.Button(content_frame, text="Compare Selected Models", 
                 command=self.compare_models).pack(fill=X, pady=(0, 5))
        
        ttk.Button(content_frame, text="View Model History", 
                 command=self.view_model_history).pack(fill=X, pady=(0, 5))
        
        ttk.Button(content_frame, text="Visualize Resource Metrics", 
                 command=self.visualize_resource_metrics).pack(fill=X, pady=(0, 5))
        
        # Model Filter Options
        filter_frame = ttk.Frame(frame, style="Card.TFrame")
        filter_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(filter_frame, text="Filter Options", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(filter_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(filter_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Sort metric
        metric_frame = ttk.Frame(content_frame)
        metric_frame.pack(fill=X, pady=(5, 5))
        ttk.Label(metric_frame, text="Sort by:").pack(side=LEFT)
        
        self.sort_metric_var = tk.StringVar(value="test_pass_rate")
        metrics = ["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"]
        metric_dropdown = ttk.Combobox(metric_frame, textvariable=self.sort_metric_var, 
                                     values=metrics, width=20, state="readonly")
        metric_dropdown.pack(side=LEFT, padx=(5, 0))
        
        # Limit entries
        limit_frame = ttk.Frame(content_frame)
        limit_frame.pack(fill=X, pady=(0, 5))
        ttk.Label(limit_frame, text="Limit:").pack(side=LEFT)
        
        self.limit_var = tk.IntVar(value=10)
        limit_spinbox = ttk.Spinbox(limit_frame, from_=1, to=100, textvariable=self.limit_var, width=5)
        limit_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Apply filters button
        ttk.Button(content_frame, text="Apply Filters", 
                 command=self.apply_leaderboard_filters).pack(fill=X, pady=(5, 0))
    
    def create_leaderboard_display(self, parent_frame):
        """Create the leaderboard display area"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Title
        ttk.Label(frame, text="Leaderboard", style="Header.TLabel").pack(anchor=W)
        ttk.Separator(frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Status information
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=X, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=LEFT)
        self.leaderboard_status_var = tk.StringVar(value="Ready")
        leaderboard_status_label = ttk.Label(status_frame, textvariable=self.leaderboard_status_var, style="Info.TLabel")
        leaderboard_status_label.pack(side=LEFT, padx=5)
        
        # Create tabs for different views
        self.lb_notebook = ttk.Notebook(frame)
        self.lb_notebook.pack(fill=BOTH, expand=YES, pady=10)
        
        # Tab for models table
        self.models_tab = ttk.Frame(self.lb_notebook)
        self.lb_notebook.add(self.models_tab, text="Models")
        
        # Tab for entries table
        self.entries_tab = ttk.Frame(self.lb_notebook)
        self.lb_notebook.add(self.entries_tab, text="Entries")
        
        # Tab for visualizations
        self.lb_viz_tab = ttk.Frame(self.lb_notebook)
        self.lb_notebook.add(self.lb_viz_tab, text="Visualizations")
        
        # Set up the models table
        self.setup_models_table(self.models_tab)
        
        # Set up the entries table
        self.setup_entries_table(self.entries_tab)
        
        # Set up visualization tab
        self.setup_lb_visualization_tab(self.lb_viz_tab)
        
        # Initialize or refresh leaderboard data
        self.refresh_leaderboard()
    
    def setup_models_table(self, parent_frame):
        """Set up the models table"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create Treeview
        columns = ("rank", "name", "best_score", "entry_count", "last_updated")
        self.models_tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        self.models_tree.heading("rank", text="Rank")
        self.models_tree.heading("name", text="Model Name")
        self.models_tree.heading("best_score", text="Best Score")
        self.models_tree.heading("entry_count", text="Entries")
        self.models_tree.heading("last_updated", text="Last Updated")
        
        self.models_tree.column("rank", width=50, anchor=CENTER)
        self.models_tree.column("name", width=200, anchor=W)
        self.models_tree.column("best_score", width=100, anchor=CENTER)
        self.models_tree.column("entry_count", width=70, anchor=CENTER)
        self.models_tree.column("last_updated", width=150, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.models_tree.pack(fill=BOTH, expand=YES)
        
        # Bind selection event
        self.models_tree.bind("<<TreeviewSelect>>", self.on_model_selected)
    
    def setup_entries_table(self, parent_frame):
        """Set up the entries table"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create Treeview
        columns = ("id", "model_name", "timestamp", "test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time")
        self.entries_tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Configure columns
        self.entries_tree.heading("id", text="ID")
        self.entries_tree.heading("model_name", text="Model Name")
        self.entries_tree.heading("timestamp", text="Timestamp")
        self.entries_tree.heading("test_pass_rate", text="Test Pass Rate")
        self.entries_tree.heading("api_success_rate", text="API Success Rate")
        self.entries_tree.heading("execution_success_rate", text="Execution Success")
        self.entries_tree.heading("avg_response_time", text="Avg Response Time")
        
        self.entries_tree.column("id", width=100, anchor=W)
        self.entries_tree.column("model_name", width=150, anchor=W)
        self.entries_tree.column("timestamp", width=150, anchor=CENTER)
        self.entries_tree.column("test_pass_rate", width=100, anchor=CENTER)
        self.entries_tree.column("api_success_rate", width=100, anchor=CENTER)
        self.entries_tree.column("execution_success_rate", width=100, anchor=CENTER)
        self.entries_tree.column("avg_response_time", width=120, anchor=CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=VERTICAL, command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.entries_tree.pack(fill=BOTH, expand=YES)
        
        # Bind selection event
        self.entries_tree.bind("<<TreeviewSelect>>", self.on_entry_selected)
    
    def setup_lb_visualization_tab(self, parent_frame):
        """Set up the leaderboard visualization tab"""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create a frame for the visualization canvas
        self.lb_viz_frame = ttk.Frame(frame)
        self.lb_viz_frame.pack(fill=BOTH, expand=YES)
        
        # Initially show a message
        ttk.Label(self.lb_viz_frame, text="No visualization available. Generate one from the Leaderboard Actions panel.", 
                style="Subtitle.TLabel").pack(pady=20)
    
    def browse_analysis_file(self):
        """Browse for an analysis file"""
        filename = self.controller.browse_for_file("Select Analysis File", [("JSON files", "*.json")])
        if filename:
            self.add_analysis_file_var.set(filename)
    
    def add_to_leaderboard(self):
        """Add an analysis file to the leaderboard"""
        analysis_file = self.add_analysis_file_var.get()
        model_name = self.model_name_var.get()
        
        if not analysis_file:
            messagebox.showwarning("Warning", "Please select an analysis file.")
            return
        
        if not model_name:
            messagebox.showwarning("Warning", "Please enter a model name.")
            return
        
        # Collect model info
        model_info = {}
        if self.model_params_var.get():
            model_info["parameters"] = self.model_params_var.get()
        if self.model_version_var.get():
            model_info["version"] = self.model_version_var.get()
        if self.model_arch_var.get():
            model_info["architecture"] = self.model_arch_var.get()
        if self.model_quant_var.get():
            model_info["quantization"] = self.model_quant_var.get()
        
        # Add to leaderboard via controller
        success = self.controller.add_to_leaderboard(
            analysis_file, model_name, model_info
        )
        
        if success:
            # Clear form fields
            self.add_analysis_file_var.set("")
            self.model_name_var.set("")
            self.model_params_var.set("")
            self.model_version_var.set("")
            self.model_arch_var.set("")
            self.model_quant_var.set("")
            
            # Refresh leaderboard display
            self.refresh_leaderboard()
    
    def refresh_leaderboard(self):
        """Refresh the leaderboard display"""
        # Update via controller
        models, entries = self.controller.refresh_leaderboard(
            metric=self.sort_metric_var.get(),
            limit=self.limit_var.get()
        )
        
        # Update models table
        self.models_tree.delete(*self.models_tree.get_children())
        
        for i, model in enumerate(models):
            self.models_tree.insert(
                "", "end", 
                values=(
                    i + 1, 
                    model["name"], 
                    f"{model['best_score']:.2%}", 
                    model["entry_count"], 
                    model["last_updated"]
                )
            )
        
        # Update entries table
        self.entries_tree.delete(*self.entries_tree.get_children())
        
        for entry in entries:
            # Get values, handling missing fields
            test_pass_rate = entry["summary"].get("test_pass_rate", None)
            test_pass_rate = f"{test_pass_rate:.2%}" if test_pass_rate is not None else "N/A"
            
            api_success_rate = entry["summary"].get("api_success_rate", None)
            api_success_rate = f"{api_success_rate:.2%}" if api_success_rate is not None else "N/A"
            
            execution_success_rate = entry["summary"].get("execution_success_rate", None)
            execution_success_rate = f"{execution_success_rate:.2%}" if execution_success_rate is not None else "N/A"
            
            avg_response_time = entry["summary"].get("avg_response_time", None)
            avg_response_time = f"{avg_response_time:.2f}s" if avg_response_time is not None else "N/A"
            
            self.entries_tree.insert(
                "", "end", 
                values=(
                    entry["id"], 
                    entry["model_name"], 
                    entry["timestamp"], 
                    test_pass_rate,
                    api_success_rate,
                    execution_success_rate,
                    avg_response_time
                )
            )
        
        # Update status
        self.leaderboard_status_var.set(f"Loaded {len(models)} models, {len(entries)} entries")
    
    def on_model_selected(self, event):
        """Handle model selection in the leaderboard"""
        # Get selected item
        selection = self.models_tree.selection()
        if not selection:
            return
        
        # Get model name from the selected item
        model_name = self.models_tree.item(selection[0], "values")[1]
        
        # Get entries for this model via controller
        entries = self.controller.get_model_entries(model_name)
        
        # Update entries table
        self.entries_tree.delete(*self.entries_tree.get_children())
        
        for entry in entries:
            # Get values, handling missing fields
            test_pass_rate = entry["summary"].get("test_pass_rate", None)
            test_pass_rate = f"{test_pass_rate:.2%}" if test_pass_rate is not None else "N/A"
            
            api_success_rate = entry["summary"].get("api_success_rate", None)
            api_success_rate = f"{api_success_rate:.2%}" if api_success_rate is not None else "N/A"
            
            execution_success_rate = entry["summary"].get("execution_success_rate", None)
            execution_success_rate = f"{execution_success_rate:.2%}" if execution_success_rate is not None else "N/A"
            
            avg_response_time = entry["summary"].get("avg_response_time", None)
            avg_response_time = f"{avg_response_time:.2f}s" if avg_response_time is not None else "N/A"
            
            self.entries_tree.insert(
                "", "end", 
                values=(
                    entry["id"], 
                    entry["model_name"], 
                    entry["timestamp"], 
                    test_pass_rate,
                    api_success_rate,
                    execution_success_rate,
                    avg_response_time
                )
            )
        
        # Switch to the entries tab
        self.lb_notebook.select(self.entries_tab)
    
    def on_entry_selected(self, event):
        """Handle entry selection in the leaderboard"""
        # Get selected item
        selection = self.entries_tree.selection()
        if not selection:
            return
        
        # Get entry ID from the selected item
        entry_id = self.entries_tree.item(selection[0], "values")[0]
        
        # Show entry details via controller
        self.controller.show_entry_details(entry_id, self.parent)
    
    def apply_leaderboard_filters(self):
        """Apply filters to the leaderboard display"""
        self.refresh_leaderboard()
    
    def generate_leaderboard_report(self):
        """Generate a leaderboard report"""
        self.controller.show_generate_report_dialog(self.parent)
    
    def compare_models(self):
        """Compare selected models"""
        # Get selected models from the table
        selected_items = self.models_tree.selection()
        
        if len(selected_items) < 2:
            messagebox.showwarning("Warning", "Please select at least two models to compare.")
            return
        
        # Get model names
        model_names = [self.models_tree.item(item, "values")[1] for item in selected_items]
        
        # Show comparison dialog via controller
        dialog = ModelCompareDialog(self.parent, self.controller, model_names)
    
    def view_model_history(self):
        """View history for a selected model"""
        # Get selected model from the table
        selected_items = self.models_tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a model to view its history.")
            return
        
        # Use only the first selected model
        model_name = self.models_tree.item(selected_items[0], "values")[1]
        
        # Show history dialog via controller
        dialog = ModelHistoryDialog(self.parent, self.controller, model_name)

    def generate_leaderboard_report(self):
        """Generate a leaderboard report"""
        # Make sure we're using the controller's method to show the dialog
        self.controller.show_generate_report_dialog(self.parent)
    
    def visualize_resource_metrics(self):
        """Visualize resource metrics across models"""
        # Show resource metrics dialog via controller
        dialog = ResourceMetricsDialog(self.parent, self.controller)
    
    def show_visualization_in_tab(self, file_path):
        """Show a visualization in the leaderboard visualization tab"""
        # Switch to the visualizations tab
        self.lb_notebook.select(self.lb_viz_tab)
        
        # Clear existing content
        for widget in self.lb_viz_frame.winfo_children():
            widget.destroy()
        
        try:
            # Load image
            img = Image.open(file_path)
            
            # Calculate size to fit in the canvas
            canvas_width = self.lb_viz_frame.winfo_width() or 800
            canvas_height = self.lb_viz_frame.winfo_height() or 600
            
            # Resize if needed
            w, h = img.size
            if w > canvas_width or h > canvas_height:
                ratio = min(canvas_width / w, canvas_height / h)
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Add label with image
            img_label = ttk.Label(self.lb_viz_frame, image=photo)
            img_label.image = photo  # Keep a reference to prevent garbage collection
            img_label.pack(padx=10, pady=10)
            
            # Add filename below
            ttk.Label(self.lb_viz_frame, text=Path(file_path).name).pack(pady=(0, 10))
            
            # Add save button
            def save_visualization():
                self.controller.save_visualization(file_path)
            
            ttk.Button(self.lb_viz_frame, text="Save Visualization", 
                     command=save_visualization).pack(pady=10)
            
        except Exception as e:
            print(f"Error displaying visualization: {e}")
            ttk.Label(self.lb_viz_frame, text=f"Error displaying visualization: {e}", 
                    style="Danger.TLabel").pack(pady=20)