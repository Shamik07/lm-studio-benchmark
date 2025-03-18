"""
Dashboard application for LM Studio Benchmark.
This file should be placed in the benchmark_gui directory.
"""

import tkinter as tk
import os
import sys
import subprocess
from pathlib import Path
import json
import threading
import time

# Fix import paths more thoroughly
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
views_dir = current_dir / "views"
controllers_dir = current_dir / "controllers"

# Add all relevant directories to sys.path
for path in [str(parent_dir), str(current_dir), str(views_dir), str(controllers_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Fix import paths
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Try to import ttkbootstrap
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.dialogs import Messagebox
except ImportError:
    print("Error: ttkbootstrap package not found.")
    print("Please install it with: pip install ttkbootstrap")
    sys.exit(1)

# Now try to import the controllers
try:
    from controllers.benchmark_controller import BenchmarkController
except ImportError as e:
    print(f"Warning: Could not import benchmark controller: {e}")
    print("Run Benchmark button will show a placeholder message.")
    BenchmarkController = None

class BenchmarkWindow:
    """Modern UI for the benchmark functionality"""
    
    def __init__(self, parent, state, controller):
        self.parent = parent
        self.state = state
        self.controller = controller
        
        # Initialize all state variables first
        self.is_running = False
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text_var = tk.StringVar(value="0/0 tasks completed")
        self.status_var = tk.StringVar(value="Ready to start benchmark")
        self.category_vars = {}
        self.difficulty_vars = {}
        self.language_vars = {}
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(parent, padding=20)
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # Set up the interface
        self.create_header()
        self.create_options()
        self.create_output_area()
        self.create_action_buttons()
        
        # Load available options
        self.load_available_options()
    
    def create_header(self):
        # Header section
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        ttk.Label(
            header_frame, 
            text="Run Benchmark", 
            font=("Inter", 24, "bold")
        ).pack(anchor=W)
        
        # Description
        ttk.Label(
            header_frame,
            text="Configure and run benchmarks to evaluate model performance on coding tasks.",
            wraplength=700
        ).pack(anchor=W, pady=(5, 0))
        
        # Separator
        ttk.Separator(self.main_frame).pack(fill=X, pady=(0, 20))
    
    def create_options(self):
        # Create a frame for benchmark options
        options_frame = ttk.Frame(self.main_frame)
        options_frame.pack(fill=X, pady=(0, 20))
        
        # Create a 2-column layout
        left_column = ttk.Frame(options_frame)
        left_column.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        right_column = ttk.Frame(options_frame)
        right_column.pack(side=LEFT, fill=BOTH, expand=YES, padx=(10, 0))
        
        # Model Endpoint Section (Left Column)
        endpoint_frame = ttk.LabelFrame(left_column, text="Model Endpoint", padding=10)
        endpoint_frame.pack(fill=X, pady=(0, 10))
        
        # Endpoint entry
        self.endpoint_var = tk.StringVar(value="http://localhost:1234/v1/chat/completions")
        ttk.Label(endpoint_frame, text="API Endpoint:").pack(anchor=W, pady=(5, 2))
        ttk.Entry(endpoint_frame, textvariable=self.endpoint_var).pack(fill=X, pady=(0, 5))
        
        # Timeout setting
        timeout_frame = ttk.Frame(endpoint_frame)
        timeout_frame.pack(fill=X, pady=(5, 0))
        ttk.Label(timeout_frame, text="Timeout (seconds):").pack(side=LEFT)
        self.timeout_var = tk.IntVar(value=120)
        ttk.Spinbox(timeout_frame, from_=10, to=300, textvariable=self.timeout_var, width=5).pack(side=LEFT, padx=(5, 0))
        
        # Benchmark Configuration (Left Column)
        config_frame = ttk.LabelFrame(left_column, text="Benchmark Configuration", padding=10)
        config_frame.pack(fill=X, pady=(10, 0))
        
        # Title entry
        ttk.Label(config_frame, text="Benchmark Title:").pack(anchor=W, pady=(5, 2))
        self.title_var = tk.StringVar(value=f"benchmark_{int(time.time())}")
        ttk.Entry(config_frame, textvariable=self.title_var).pack(fill=X, pady=(0, 10))
        
        # Settings checkboxes
        self.execute_code_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            config_frame, 
            text="Execute code to verify functionality", 
            variable=self.execute_code_var
        ).pack(anchor=W, pady=(0, 5))
        
        self.monitor_resources_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            config_frame, 
            text="Monitor system resources", 
            variable=self.monitor_resources_var
        ).pack(anchor=W, pady=(0, 5))
        
        # Task Selection (Right Column)
        tasks_frame = ttk.LabelFrame(right_column, text="Task Selection", padding=10)
        tasks_frame.pack(fill=BOTH, expand=YES)
        
        # Categories
        ttk.Label(tasks_frame, text="Categories:").pack(anchor=W, pady=(5, 2))
        self.categories_frame = ttk.Frame(tasks_frame)
        self.categories_frame.pack(fill=X, pady=(0, 10))
        
        # Difficulties
        ttk.Label(tasks_frame, text="Difficulties:").pack(anchor=W, pady=(5, 2))
        self.difficulties_frame = ttk.Frame(tasks_frame)
        self.difficulties_frame.pack(fill=X, pady=(0, 10))
        
        # Languages
        ttk.Label(tasks_frame, text="Languages:").pack(anchor=W, pady=(5, 2))
        self.languages_frame = ttk.Frame(tasks_frame)
        self.languages_frame.pack(fill=X, pady=(0, 10))
    
    def create_output_area(self):
        # Create output area
        output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding=10)
        output_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Status information
        status_frame = ttk.Frame(output_frame)
        status_frame.pack(fill=X, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=LEFT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(output_frame)
        progress_frame.pack(fill=X, pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(anchor=W)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            length=100, 
            mode="determinate"
        )
        self.progress_bar.pack(fill=X, pady=5)
        
        ttk.Label(progress_frame, textvariable=self.progress_text_var).pack(anchor=E)
        
        # Output text area with scrollbar
        output_text_frame = ttk.Frame(output_frame)
        output_text_frame.pack(fill=BOTH, expand=YES, pady=(5, 0))
        
        self.output_text = tk.Text(output_text_frame, height=10, wrap=tk.WORD)
        self.output_text.pack(side=LEFT, fill=BOTH, expand=YES)
        
        scrollbar = ttk.Scrollbar(output_text_frame, command=self.output_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Configure tags for different log levels
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("info", foreground="white")
        
        # Make text read-only
        self.output_text.config(state=DISABLED)
    
    def create_action_buttons(self):
        # Create action buttons
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=X)
        
        # Run button
        self.run_button = ttk.Button(
            buttons_frame, 
            text="Run Benchmark", 
            command=self.run_benchmark,
            bootstyle="success",
            width=15
        )
        self.run_button.pack(side=LEFT, padx=(0, 10))
        
        # Stop button (initially disabled)
        self.stop_button = ttk.Button(
            buttons_frame, 
            text="Stop", 
            command=self.stop_benchmark,
            bootstyle="danger",
            width=15,
            state=DISABLED
        )
        self.stop_button.pack(side=LEFT)
        
        # Reset button
        ttk.Button(
            buttons_frame, 
            text="Reset", 
            command=self.reset_benchmark_settings,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT, padx=(10, 0))
    
    def load_available_options(self):
        """Load available categories, difficulties, and languages"""
        if self.controller:
            try:
                categories, difficulties, languages = self.controller.get_available_options()
                
                # Populate categories
                self.category_vars = {}
                for category in categories:
                    var = tk.BooleanVar(value=True)
                    self.category_vars[category] = var
                    ttk.Checkbutton(self.categories_frame, text=category, variable=var).pack(anchor=W)
                
                # Populate difficulties
                self.difficulty_vars = {}
                for difficulty in difficulties:
                    var = tk.BooleanVar(value=True)
                    self.difficulty_vars[difficulty] = var
                    ttk.Checkbutton(self.difficulties_frame, text=difficulty, variable=var).pack(anchor=W)
                
                # Populate languages
                self.language_vars = {}
                for language in languages:
                    var = tk.BooleanVar(value=True)
                    self.language_vars[language] = var
                    ttk.Checkbutton(self.languages_frame, text=language, variable=var).pack(anchor=W)
                    
                self.log("Available options loaded successfully", level="info")
                return True
            except Exception as e:
                self.log(f"Error loading options: {e}", level="error")
                return False
        else:
            # Default values if controller is not available
            default_categories = ["syntax", "algorithms", "data_structures", "debugging"]
            default_difficulties = ["easy", "medium", "hard"]
            default_languages = ["python", "javascript", "java", "cpp"]
            
            # Populate with defaults
            self.category_vars = {}
            for category in default_categories:
                var = tk.BooleanVar(value=True)
                self.category_vars[category] = var
                ttk.Checkbutton(self.categories_frame, text=category, variable=var).pack(anchor=W)
            
            self.difficulty_vars = {}
            for difficulty in default_difficulties:
                var = tk.BooleanVar(value=True)
                self.difficulty_vars[difficulty] = var
                ttk.Checkbutton(self.difficulties_frame, text=difficulty, variable=var).pack(anchor=W)
            
            self.language_vars = {}
            for language in default_languages:
                var = tk.BooleanVar(value=True)
                self.language_vars[language] = var
                ttk.Checkbutton(self.languages_frame, text=language, variable=var).pack(anchor=W)
                
            self.log("Loaded default options (controller not available)", level="warning")
            return False
    
    def log(self, message, level="info"):
        """Log a message to the output text"""
        try:
            self.output_text.config(state=NORMAL)
            
            # Add timestamp
            ts = time.strftime("%H:%M:%S")
            prefix = f"[{ts}] "
            
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
            self.output_text.insert("end", log_line, tag)
            
            # Scroll to end
            self.output_text.see("end")
            self.output_text.config(state=DISABLED)
        except Exception as e:
            print(f"Error logging message: {e}")
    
    def run_benchmark(self):
        """Run the benchmark with the current settings"""
        if self.is_running:
            return
        
        # Get selected categories, difficulties, and languages
        categories = [cat for cat, var in self.category_vars.items() if var.get()]
        difficulties = [diff for diff, var in self.difficulty_vars.items() if var.get()]
        languages = [lang for lang, var in self.language_vars.items() if var.get()]
        
        # Validate selections
        if not categories:
            Messagebox.show_warning("Warning", "Please select at least one category.")
            return
            
        if not difficulties:
            Messagebox.show_warning("Warning", "Please select at least one difficulty level.")
            return
            
        if not languages:
            Messagebox.show_warning("Warning", "Please select at least one programming language.")
            return
        
        # Check if controller is available
        if not self.controller:
            Messagebox.show_info(
                "Benchmark", 
                "Benchmark controller is not available. This would normally run the benchmark."
            )
            return
        
        # Update UI state
        self.is_running = True
        self.run_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        
        # Clear output
        self.output_text.config(state=NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=DISABLED)
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_text_var.set("0/0 tasks completed")
        self.status_var.set("Running benchmark...")
        
        # Update benchmark settings in controller
        benchmark_config = {
            "endpoint": self.endpoint_var.get(),
            "timeout": self.timeout_var.get(),
            "title": self.title_var.get(),
            "execute_code": self.execute_code_var.get(),
            "monitor_resources": self.monitor_resources_var.get()
        }
        
        # Configure the controller
        result = self.controller.configure_benchmark(benchmark_config)
        if not result:
            self.log("Error configuring benchmark", level="error")
            self.is_running = False
            self.run_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
            return
        
        # Log start
        self.log("Benchmark started")
        self.log(f"Selected categories: {', '.join(categories)}")
        self.log(f"Selected difficulties: {', '.join(difficulties)}")
        self.log(f"Selected languages: {', '.join(languages)}")
        
        # Create and start benchmark thread
        self.benchmark_thread = threading.Thread(
            target=self.benchmark_worker,
            args=(categories, difficulties, languages)
        )
        self.benchmark_thread.daemon = True
        self.benchmark_thread.start()
        
        # Start progress checking
        self.parent.after(100, self.check_benchmark_progress)
    
    def benchmark_worker(self, categories, difficulties, languages):
        """Worker function for running benchmark in a separate thread"""
        try:
            # Run benchmark
            results = self.controller.run_benchmark(categories, difficulties, languages)
            
            # Check if cancelled
            if not self.is_running:
                self.log("Benchmark cancelled by user", level="warning")
                return
                
            # Analyze results
            self.log("Benchmark completed, analyzing results...")
            analysis = self.controller.analyze_results(results)
            
            # Display results summary
            self.parent.after(0, lambda: self.display_results_summary(analysis))
            
            # Update status
            self.status_var.set("Benchmark completed")
            self.log("Benchmark and analysis successfully completed")
            
        except Exception as e:
            # Log the error
            error_message = str(e)
            self.log(f"Error running benchmark: {error_message}", level="error")
            
            # Update status
            self.status_var.set("Benchmark failed")
            
            # Show error dialog on the main thread
            self.parent.after(0, lambda: Messagebox.show_error("Benchmark Error", 
                                                    f"Error running benchmark: {error_message}"))
        
        finally:
            # Update running state
            self.is_running = False
            
            # Re-enable run button and disable stop button
            self.parent.after(0, lambda: self.run_button.config(state=NORMAL))
            self.parent.after(0, lambda: self.stop_button.config(state=DISABLED))
    
    def check_benchmark_progress(self):
        """Check benchmark progress and update UI"""
        if self.is_running:
            # Update the progress bar
            if hasattr(self.controller.benchmark, 'completed_tasks') and hasattr(self.controller.benchmark, 'total_tasks'):
                total = self.controller.benchmark.total_tasks
                completed = self.controller.benchmark.completed_tasks
                
                if total > 0:
                    progress = completed / total
                    self.progress_var.set(progress)
                    self.progress_text_var.set(f"{completed}/{total} tasks completed")
                    self.status_var.set(f"Running benchmark... {progress*100:.1f}%")
            
            # Schedule next check
            self.parent.after(100, self.check_benchmark_progress)
    
    def stop_benchmark(self):
        """Stop the currently running benchmark"""
        if not self.is_running:
            return
        
        if Messagebox.show_question("Confirm Stop", "Are you sure you want to stop the benchmark?", 
                                  parent=self.parent):
            # Set running flag to false
            self.is_running = False
            
            # Update status
            self.status_var.set("Stopping benchmark...")
            self.log("Stopping benchmark...", level="warning")
            
            # Try to cancel any ongoing operations in the controller
            if hasattr(self.controller, 'benchmark') and hasattr(self.controller.benchmark, 'cancel'):
                try:
                    self.controller.benchmark.cancel()
                except Exception as e:
                    print(f"Error cancelling benchmark: {e}")
            
            # Update buttons
            self.run_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
    
    def reset_benchmark_settings(self):
        """Reset benchmark settings to defaults"""
        # Reset variables
        self.endpoint_var.set("http://localhost:1234/v1/chat/completions")
        self.timeout_var.set(120)
        self.title_var.set(f"benchmark_{int(time.time())}")
        self.execute_code_var.set(True)
        self.monitor_resources_var.set(True)
        
        # Reset checkboxes
        for var in self.category_vars.values():
            var.set(True)
        for var in self.difficulty_vars.values():
            var.set(True)
        for var in self.language_vars.values():
            var.set(True)
            
        # Clear output
        self.output_text.config(state=NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=DISABLED)
        
        # Reset progress
        self.progress_var.set(0)
        self.progress_text_var.set("0/0 tasks completed")
        self.status_var.set("Ready")
        
        self.log("Settings reset to defaults", level="info")
    
    def display_results_summary(self, analysis):
        """Display a summary of benchmark results"""
        if not analysis or "summary" not in analysis:
            self.log("No analysis data available to display", level="warning")
            return
            
        # Log summary information
        self.log("=== BENCHMARK RESULTS SUMMARY ===", level="info")
        
        # Overall metrics
        summary = analysis["summary"]
        
        # Response time
        if "avg_response_time" in summary:
            self.log(f"Average Response Time: {summary['avg_response_time']:.2f}s", level="info")
            
        # API Success Rate
        if "api_success_rate" in summary:
            self.log(f"API Success Rate: {summary['api_success_rate']*100:.2f}%", level="info")
            
        # Execution Success Rate (if available)
        if "execution_success_rate" in summary:
            self.log(f"Execution Success Rate: {summary['execution_success_rate']*100:.2f}%", level="info")
            
        # Test Pass Rate (if available)
        if "test_pass_rate" in summary:
            self.log(f"Test Pass Rate: {summary['test_pass_rate']*100:.2f}%", level="info")
            
        # Task counts
        if "total_tasks" in summary:
            self.log(f"Total Tasks: {summary['total_tasks']}", level="info")
            
        if "completed_tasks" in summary:
            self.log(f"Completed Tasks: {summary['completed_tasks']}", level="info")
            
        if "total_tests" in summary:
            self.log(f"Total Tests Run: {summary['total_tests']}", level="info")
            
        # Add resource metrics if available
        if "resource_metrics" in analysis:
            metrics = analysis["resource_metrics"]
            self.log("=== RESOURCE USAGE ===", level="info")
            
            if "cpu" in metrics:
                self.log(f"CPU Usage: Avg {metrics['cpu']['percent']['mean']:.1f}%, Max {metrics['cpu']['percent']['max']:.1f}%", level="info")
                
            if "memory" in metrics:
                self.log(f"Memory Usage: Avg {metrics['memory']['used_gb']['mean']:.2f} GB, Peak {metrics['memory']['used_gb']['max']:.2f} GB", level="info")
                
            if "gpu" in metrics and metrics["gpu"]:
                if "utilization" in metrics["gpu"]:
                    self.log(f"GPU Utilization: Avg {metrics['gpu']['utilization']['mean']:.1f}%, Max {metrics['gpu']['utilization']['max']:.1f}%", level="info")
                elif "devices" in metrics["gpu"]:
                    for device, stats in metrics["gpu"]["devices"].items():
                        if "utilization" in stats:
                            self.log(f"{device}: Avg {stats['utilization']['mean']:.1f}%, Max {stats['utilization']['max']:.1f}%", level="info")

        # Suggest next steps
        self.log("\n=== NEXT STEPS ===", level="info")
        self.log("1. View detailed analysis file", level="info")
        self.log("2. Generate visualizations", level="info")
        self.log("3. Add results to leaderboard", level="info")


class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LM Studio Benchmark")
        self.root.geometry("900x700")
        
        # Initialize controllers if available
        self.init_controllers()
        
        # Set up the main container with padding
        self.main_container = ttk.Frame(root, padding=20)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Create the header
        self.create_header()
        
        # Create the main content
        self.create_content()
        
        # Create the footer with status
        self.create_footer()
    
    def init_controllers(self):
        """Initialize controller instances if possible"""
        # Create shared state dictionary
        self.state = {
            "is_running": False,
            "benchmark": None,
            "leaderboard": None,
            "output_dir": "benchmark_results"
        }
        
        # Try to initialize benchmark controller
        if BenchmarkController:
            try:
                self.benchmark_controller = BenchmarkController(self.state)
                print("Successfully initialized benchmark controller")
            except Exception as e:
                print(f"Error initializing benchmark controller: {e}")
                self.benchmark_controller = None
        else:
            self.benchmark_controller = None
    
    def create_header(self):
        """Create the header section with title and description"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 30))
        
        # Title with large font
        title_label = ttk.Label(
            header_frame, 
            text="LM Studio Benchmark", 
            font=("Inter", 28, "bold"),
            bootstyle="dark"
        )
        title_label.pack(pady=(0, 10))
        
        # Description
        description = ("A comprehensive tool for evaluating LM Studio models on coding tasks. "
                      "Benchmark, visualize, and compare model performance.")
        
        desc_label = ttk.Label(
            header_frame, 
            text=description,
            font=("Inter", 12),
            bootstyle="secondary",
            wraplength=700,
            justify="center"
        )
        desc_label.pack()
    
    def create_content(self):
        """Create the main content with action cards"""
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=BOTH, expand=YES, pady=20)
        
        # Create a 2x2 grid of cards
        self.create_card(
            content_frame,
            "Run Benchmark",
            "Evaluate model performance on coding tasks with detailed metrics and analysis.",
            "RUN",
            self.run_benchmark,
            0, 0
        )
        
        self.create_card(
            content_frame,
            "Visualize Results",
            "Generate and explore visualizations from benchmark analyses.",
            "VIEW",
            self.visualize_results,
            0, 1
        )
        
        self.create_card(
            content_frame,
            "Leaderboard",
            "Compare model performance and track improvements over time.",
            "COMPARE",
            self.open_leaderboard,
            1, 0
        )
        
        self.create_card(
            content_frame,
            "Settings",
            "Configure benchmark parameters, paths, and appearance.",
            "CONFIGURE",
            self.open_settings,
            1, 1
        )
    
    def create_card(self, parent, title, description, action_text, action_command, row, col):
        """Create a card widget with title, description and action button"""
        # Create a frame with borders and padding
        card = ttk.Frame(parent, bootstyle="default")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Add padding inside the card
        card_content = ttk.Frame(card, padding=20)
        card_content.pack(fill=BOTH, expand=YES)
        
        # Card title
        title_label = ttk.Label(
            card_content, 
            text=title, 
            font=("Inter", 16, "bold")
        )
        title_label.pack(anchor=W, pady=(0, 10))
        
        # Card description
        desc_label = ttk.Label(
            card_content, 
            text=description,
            wraplength=300,
            font=("Inter", 11)
        )
        desc_label.pack(anchor=W, pady=(0, 20), fill=X)
        
        # Action button - using success style for primary actions
        button_style = "success" if action_text == "RUN" else "secondary"
        action_button = ttk.Button(
            card_content, 
            text=action_text,
            command=action_command,
            bootstyle=button_style,
            width=15
        )
        action_button.pack(anchor=SE)
        
        # Configure grid for equal sizing
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
    
    def create_footer(self):
        """Create footer with status bar"""
        footer_frame = ttk.Frame(self.main_container, padding=(0, 10, 0, 0))
        footer_frame.pack(fill=X, side=BOTTOM)
        
        # Status label on the left
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            footer_frame, 
            textvariable=self.status_var,
            bootstyle="secondary"
        )
        status_label.pack(side=LEFT)
        
        # Version on the right
        version_label = ttk.Label(
            footer_frame, 
            text="v1.0.0",
            bootstyle="secondary"
        )
        version_label.pack(side=RIGHT)
    
    def run_benchmark(self):
        """Run the benchmark with improved error handling and path management"""
        self.status_var.set("Starting benchmark...")
        
        try:
            # Create a new toplevel window for the benchmark panel
            benchmark_window = ttk.Toplevel(self.root)
            benchmark_window.title("Run Benchmark")
            benchmark_window.geometry("1000x800")
            
            # Fix import paths
            import sys
            from pathlib import Path
            
            # Get the current directory and parent directory
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            
            # Add parent directory to sys.path
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Check if controller is available or needs to be created
            if not hasattr(self, 'benchmark_controller') or self.benchmark_controller is None:
                try:
                    from controllers.benchmark_controller import BenchmarkController
                    self.benchmark_controller = BenchmarkController(self.state)
                    print("Successfully initialized benchmark controller")
                except ImportError as e:
                    print(f"Error importing benchmark controller: {e}")
                    self.create_fallback_ui(benchmark_window, "Benchmark", 
                        f"Error importing benchmark controller: {str(e)}")
                    benchmark_window.transient(self.root)
                    self.status_var.set("Error: Benchmark controller not available")
                    return
                except Exception as e:
                    print(f"Error initializing benchmark controller: {e}")
                    import traceback
                    traceback.print_exc()
                    self.create_fallback_ui(benchmark_window, "Benchmark", 
                        f"Error initializing benchmark controller: {str(e)}")
                    benchmark_window.transient(self.root)
                    self.status_var.set("Error: Benchmark initialization failed")
                    return
            
            try:
                # Create our custom benchmark interface
                print("Creating benchmark panel...")
                benchmark_panel = BenchmarkWindow(
                    benchmark_window, 
                    self.state, 
                    self.benchmark_controller
                )
                print("Benchmark panel created successfully")
                
                # Make the window transient
                benchmark_window.transient(self.root)
                benchmark_window.focus_set()
                
                # Force update to ensure rendering
                benchmark_window.update()
                
                self.status_var.set("Benchmark window opened")
                
            except Exception as e:
                print(f"Error creating benchmark panel: {e}")
                import traceback
                traceback.print_exc()
                
                # Create fallback UI
                self.create_fallback_ui(benchmark_window, "Benchmark", 
                    f"Error creating benchmark panel: {str(e)}")
                benchmark_window.transient(self.root)
                self.status_var.set("Error: Benchmark interface failed")
        except Exception as e:
            self.status_var.set("Error launching benchmark")
            print(f"Error launching benchmark: {e}")
            import traceback
            traceback.print_exc()
            Messagebox.show_error(
                "Error", 
                f"Could not launch benchmark: {str(e)}\n\nSee console for details."
            )
    
    def visualize_results(self):
        """Open the visualization view with improved error handling and frame packing"""
        self.status_var.set("Opening visualization tools...")
        
        try:
            # Create a new toplevel window for the visualization panel
            visualize_window = ttk.Toplevel(self.root)
            visualize_window.title("Visualize Results")
            visualize_window.geometry("1100x750")
            
            # Explicitly add the frame to ensure it's displayed
            main_frame = ttk.Frame(visualize_window, padding=20)
            main_frame.pack(fill=BOTH, expand=YES)
            
            # Fix import paths
            import sys
            from pathlib import Path
            from tkinter import filedialog
            
            # Get the current directory and parent directory
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            
            # Add parent directory to sys.path
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            try:
                # Import the controllers first
                from controllers.visualize_controller import VisualizeController
                print("Successfully imported visualization controller")
                
                # Initialize the controller with our state
                if not hasattr(self, 'visualize_controller'):
                    self.visualize_controller = VisualizeController(self.state)
                    self.state['visualize_controller'] = self.visualize_controller
                    print("Visualization controller initialized")
                
                # Now import and create the view with proper parent frame
                from views.visualize_view import VisualizeView
                print("Successfully imported visualization view")
                
                # Create the view with the main frame as parent
                visualize_view = VisualizeView(main_frame, self.state)
                print("Created visualization view")
                
                # IMPORTANT: Make sure the frame is properly packed in the main frame
                print(f"Visualization view frame exists: {hasattr(visualize_view, 'frame')}")
                if hasattr(visualize_view, 'frame'):
                    # Unpack if already packed (shouldn't be needed but just in case)
                    try:
                        visualize_view.frame.pack_forget()
                    except:
                        pass
                    
                    # Explicitly pack the frame with full size
                    visualize_view.frame.pack(fill=BOTH, expand=YES)
                    print("Explicitly packed visualization view frame")
                    
                    # Force update to ensure rendering
                    visualize_window.update()
                
                # Make the window transient
                visualize_window.transient(self.root)
                visualize_window.focus_set()
                
                self.status_var.set("Visualization window opened")
            except ImportError as e:
                print(f"Import error: {e}")
                # Create fallback UI
                self.create_visualization_interface(visualize_window)
                visualize_window.transient(self.root)
                self.status_var.set("Simple visualization view opened")
            except Exception as e:
                print(f"Error creating visualization view: {e}")
                import traceback
                traceback.print_exc()
                
                # Create fallback UI
                self.create_visualization_interface(visualize_window)
                visualize_window.transient(self.root)
                self.status_var.set("Error: Visualization interface failed")
        except Exception as e:
            self.status_var.set("Error launching visualization")
            print(f"Error launching visualization: {e}")
            import traceback
            traceback.print_exc()
            Messagebox.show_error(
                "Error", 
                f"Could not launch visualization tools: {str(e)}\n\nSee console for details."
            )
   
    def create_visualization_interface(self, parent):
        """Create a simplified visualization interface when the full view can't be loaded"""
        # Container with padding
        main_frame = ttk.Frame(parent, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Add a header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        ttk.Label(
            header_frame, 
            text="Visualization Tools", 
            font=("Inter", 24, "bold")
        ).pack(anchor=W)
        
        # Description
        ttk.Label(
            header_frame,
            text="Generate visualizations from benchmark results.",
            wraplength=700
        ).pack(anchor=W, pady=(5, 0))
        
        # Separator
        ttk.Separator(main_frame).pack(fill=X, pady=(0, 20))
        
        # Create a simple visualization interface
        actions_frame = ttk.LabelFrame(main_frame, text="Visualization Actions", padding=10)
        actions_frame.pack(fill=X, pady=(0, 20))
        
        # File selection
        file_frame = ttk.Frame(actions_frame)
        file_frame.pack(fill=X, pady=10)
        
        ttk.Label(file_frame, text="Analysis File:").pack(side=LEFT)
        analysis_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=analysis_file_var, width=40).pack(side=LEFT, padx=5)
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Analysis File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                analysis_file_var.set(filename)
        
        ttk.Button(file_frame, text="Browse", command=browse_file).pack(side=LEFT)
        
        # Visualization types
        viz_frame = ttk.LabelFrame(main_frame, text="Visualization Types", padding=10)
        viz_frame.pack(fill=X, pady=(0, 20))
        
        viz_types = [
            ("Performance Metrics", "Generate charts of key performance metrics."),
            ("Language Comparison", "Compare performance across programming languages."),
            ("Difficulty Analysis", "Analyze performance by difficulty level."),
            ("Resource Usage", "Visualize resource utilization during benchmark.")
        ]
        
        for title, desc in viz_types:
            type_frame = ttk.Frame(viz_frame)
            type_frame.pack(fill=X, pady=5)
            
            ttk.Label(type_frame, text=title, font=("Inter", 12, "bold")).pack(anchor=W)
            ttk.Label(type_frame, text=desc).pack(anchor=W, pady=(0, 5))
            ttk.Button(type_frame, text="Generate", state="disabled").pack(anchor=W)
            ttk.Separator(viz_frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Preview area
        preview_frame = ttk.LabelFrame(main_frame, text="Visualization Preview", padding=10)
        preview_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        ttk.Label(
            preview_frame,
            text="To generate visualizations, please select an analysis file and visualization type.",
            wraplength=700,
            justify="center"
        ).pack(pady=50)
        
        # Status message
        ttk.Label(
            main_frame,
            text="Note: Full visualization capabilities are not available. Please check for errors in the console.",
            font=("Inter", 10, "italic"),
            foreground="#FF5555"
        ).pack(pady=(0, 10))
        
        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=parent.destroy,
            style="secondary.TButton"
        ).pack(side=RIGHT)

    def open_leaderboard(self):
        """Open the leaderboard view with frame packing fix"""
        self.status_var.set("Opening leaderboard...")
        
        try:
            # Create a new toplevel window for the leaderboard panel
            leaderboard_window = ttk.Toplevel(self.root)
            leaderboard_window.title("Leaderboard")
            leaderboard_window.geometry("1100x750")
            
            # Explicitly add the frame to ensure it's displayed
            main_frame = ttk.Frame(leaderboard_window, padding=20)
            main_frame.pack(fill=BOTH, expand=YES)
            
            # Fix import paths for leaderboard
            import sys
            from pathlib import Path
            
            # Get the current directory and parent directory
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            
            # Add parent directory to sys.path to find leaderboard.py
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Import controllers and views with proper paths
            try:
                # Import the controllers first
                from controllers.leaderboard_controller import LeaderboardController
                print("Successfully imported leaderboard controller")
                
                # Initialize the controller with our state
                leaderboard_controller = LeaderboardController(self.state)
                self.state['leaderboard_controller'] = leaderboard_controller
                print("Leaderboard controller initialized")
                
                # Now import and create the view with proper parent frame
                from views.leaderboard_view import LeaderboardView
                print("Successfully imported leaderboard view")
                
                # Create the view with the main frame as parent
                leaderboard_view = LeaderboardView(main_frame, self.state)
                print("Created leaderboard view")
                
                # IMPORTANT: Make sure the frame is properly packed in the main frame
                print(f"Leaderboard view frame exists: {hasattr(leaderboard_view, 'frame')}")
                if hasattr(leaderboard_view, 'frame'):
                    # Unpack if already packed (shouldn't be needed but just in case)
                    try:
                        leaderboard_view.frame.pack_forget()
                    except:
                        pass
                    
                    # Explicitly pack the frame with full size
                    leaderboard_view.frame.pack(fill=BOTH, expand=YES)
                    print("Explicitly packed leaderboard view frame")
                    
                    # Force update to ensure rendering
                    leaderboard_window.update()
                
                # Make the window transient
                leaderboard_window.transient(self.root)
                leaderboard_window.focus_set()
                
                # Force refresh of the view's components
                if hasattr(leaderboard_view, 'refresh_leaderboard'):
                    try:
                        print("Attempting to refresh leaderboard data")
                        leaderboard_view.refresh_leaderboard()
                    except Exception as e:
                        print(f"Error refreshing leaderboard: {e}")
                
                self.status_var.set("Leaderboard window opened")
            except ImportError as e:
                print(f"Import error: {e}")
                # Create fallback UI
                self.create_fallback_ui(main_frame, "Leaderboard", 
                    f"Error importing leaderboard modules: {str(e)}")
            except Exception as e:
                print(f"Error creating leaderboard view: {e}")
                import traceback
                traceback.print_exc()
                # Create fallback UI
                self.create_fallback_ui(main_frame, "Leaderboard", 
                    f"Error creating leaderboard view: {str(e)}")
        except Exception as e:
            self.status_var.set("Error launching leaderboard")
            print(f"Error launching leaderboard: {e}")
            import traceback
            traceback.print_exc()
            Messagebox.show_error(
                "Error", 
                f"Could not launch leaderboard: {str(e)}\n\nSee console for details."
            )

    def create_fallback_ui(self, parent, title, message):
        """Create a comprehensive fallback UI when a module can't be loaded"""
        # Container with padding
        container = ttk.Frame(parent, padding=20)
        container.pack(fill=BOTH, expand=YES)
        
        # Add a header
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Title
        ttk.Label(
            header_frame, 
            text=title, 
            font=("Inter", 24, "bold")
        ).pack(anchor=W)
        
        # Separator
        ttk.Separator(container).pack(fill=X, pady=(0, 20))
        
        # Message in a card-like frame
        message_frame = ttk.Frame(container, padding=15)
        message_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            message_frame,
            text=message,
            wraplength=700,
            justify="left"
        ).pack(anchor=W)
        
        # Technical info section
        tech_frame = ttk.LabelFrame(container, text="Technical Information", padding=15)
        tech_frame.pack(fill=X, pady=(0, 20))
        
        # Python path
        import sys
        ttk.Label(
            tech_frame,
            text="Python Path:",
            font=("Inter", 10, "bold")
        ).pack(anchor=W, pady=(0, 5))
        
        path_text = ttk.Text(tech_frame, height=5, wrap="word")
        path_text.pack(fill=X, pady=(0, 10))
        path_text.insert("1.0", "\n".join(sys.path))
        path_text.config(state="disabled")
        
        # Current directory
        from pathlib import Path
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        
        ttk.Label(
            tech_frame,
            text=f"Current directory: {current_dir}",
        ).pack(anchor=W, pady=2)
        
        ttk.Label(
            tech_frame,
            text=f"Parent directory: {parent_dir}",
        ).pack(anchor=W, pady=2)
        
        # Action buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Close",
            command=lambda: parent.master.destroy(),
            style="secondary.TButton"
        ).pack(side=RIGHT)
        
        # Try to add a fix button if we can
        ttk.Button(
            button_frame,
            text="Fix Import Paths",
            command=self.fix_import_paths,
            style="success.TButton"
        ).pack(side=RIGHT, padx=10)

    def fix_import_paths(self):
        """Attempt to fix import paths"""
        try:
            import sys
            from pathlib import Path
            import shutil
            
            # Get the current directory
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            
            # Add parent directory to sys.path
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Create a symlink or copy the leaderboard.py file if it exists
            leaderboard_file = parent_dir / "leaderboard.py"
            target_file = current_dir / "leaderboard.py"
            
            if leaderboard_file.exists() and not target_file.exists():
                # Copy the file
                shutil.copy2(leaderboard_file, target_file)
                messagebox.showinfo(
                    "Import Path Fixed", 
                    f"The leaderboard.py file has been copied to {target_file}.\n\n" +
                    "Please restart the application for the changes to take effect."
                )
            else:
                messagebox.showinfo(
                    "Import Path Status", 
                    f"Parent directory ({parent_dir}) added to Python path.\n\n" +
                    f"Leaderboard file exists at parent: {leaderboard_file.exists()}\n" +
                    f"Leaderboard file exists at current: {target_file.exists()}\n\n" +
                    "Please restart the application for the changes to take effect."
                )
            
            return True
        except Exception as e:
            messagebox.showerror(
                "Error Fixing Import Paths", 
                f"Failed to fix import paths: {str(e)}"
            )
            return False
   
    def open_settings(self):
        """Open the settings view with proper frame packing"""
        self.status_var.set("Opening settings...")
        
        try:
            # Create a new toplevel window for the settings panel
            settings_window = ttk.Toplevel(self.root)
            settings_window.title("Settings")
            settings_window.geometry("900x700")
            
            # Explicitly add the frame to ensure it's displayed
            main_frame = ttk.Frame(settings_window, padding=20)
            main_frame.pack(fill=BOTH, expand=YES)
            
            # Fix import paths
            import sys
            from pathlib import Path
            
            # Get the current directory and parent directory
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            
            # Add parent directory to sys.path
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            # Import controllers and views with proper paths
            try:
                # Import the controllers first
                from controllers.settings_controller import SettingsController
                print("Successfully imported settings controller")
                
                # Initialize the controller with our state
                settings_controller = SettingsController(self.state)
                self.state['settings_controller'] = settings_controller
                print("Settings controller initialized")
                
                # Now import and create the view with proper parent frame
                from views.settings_view import SettingsView
                print("Successfully imported settings view")
                
                # Create the view with the main frame as parent
                settings_view = SettingsView(main_frame, self.state)
                print("Created settings view")
                
                # IMPORTANT: Make sure the frame is properly packed in the main frame
                print(f"Settings view frame exists: {hasattr(settings_view, 'frame')}")
                if hasattr(settings_view, 'frame'):
                    # Unpack if already packed (shouldn't be needed but just in case)
                    try:
                        settings_view.frame.pack_forget()
                    except:
                        pass
                    
                    # Explicitly pack the frame with full size
                    settings_view.frame.pack(fill=BOTH, expand=YES)
                    print("Explicitly packed settings view frame")
                    
                    # Force update to ensure rendering
                    settings_window.update()
                
                # Make the window transient
                settings_window.transient(self.root)
                settings_window.focus_set()
                
                # Force refresh of the view's components if available
                if hasattr(settings_view, 'load_settings'):
                    try:
                        print("Attempting to load settings data")
                        settings_view.load_settings()
                    except Exception as e:
                        print(f"Error loading settings: {e}")
                
                self.status_var.set("Settings window opened")
            except ImportError as e:
                print(f"Import error: {e}")
                # Create fallback UI
                self.create_fallback_ui(main_frame, "Settings", 
                    f"Error importing settings modules: {str(e)}")
            except Exception as e:
                print(f"Error creating settings view: {e}")
                import traceback
                traceback.print_exc()
                # Create fallback UI
                self.create_fallback_ui(main_frame, "Settings", 
                    f"Error creating settings view: {str(e)}")
        except Exception as e:
            self.status_var.set("Error launching settings")
            print(f"Error launching settings: {e}")
            import traceback
            traceback.print_exc()
            Messagebox.show_error(
                "Error", 
                f"Could not launch settings: {str(e)}\n\nSee console for details."
            )



def main():
    # Load settings to get theme before creating window
    config_dir = Path.home() / ".lm-studio-benchmark"
    config_file = config_dir / "config.json"
    theme = "darkly"  # Default dark theme
    
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                settings = json.load(f)
                if settings.get("theme") == "light":
                    theme = "cosmo"  # Use 'cosmo' as the light theme
        except:
            pass

    # Try to make the UI look better on high DPI displays
    try:
        # For Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # For macOS, set a higher scaling factor
    if os.name == 'posix':
        os.environ['TK_SCALING'] = '2.0'
    
    # Create the root window with ttkbootstrap
    root = ttk.Window(
        title="LM Studio Benchmark",
        themename=theme,
        size=(900, 700),
        position=(100, 100),
        minsize=(800, 600),
        resizable=(True, True)
    )
    
    # Create the dashboard application
    app = DashboardApp(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()