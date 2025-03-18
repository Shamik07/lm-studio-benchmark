"""
Benchmark tab UI for LM Studio Benchmark GUI.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import time
import threading
import builtins
from typing import Dict, List, Any

from controllers.benchmark_controller import BenchmarkController
from utils import log_message, get_task_count
from tkinter import messagebox

class BenchmarkView:
    """Benchmark tab UI class"""
    
    def __init__(self, parent, state):
        """
        Initialize the benchmark view.
        
        Args:
            parent: Parent widget
            state: Shared application state
        """
        self.parent = parent
        self.state = state
        self.controller = BenchmarkController(state)
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        
        # Initialize UI components
        self.available_categories = []
        self.available_difficulties = []
        self.available_languages = []
        self.category_vars = {}
        self.difficulty_vars = {}
        self.language_vars = {}
        
        # Set up the panel
        self.setup_panel()
        
        # Load available options
        self.load_available_options()
    
    def setup_panel(self):
        """Set up the benchmark panel UI"""
        # Split into left panel (settings) and right panel (output)
        paned_window = ttk.PanedWindow(self.frame, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=YES)
        
        # Create left panel container first (a regular frame)
        left_container = ttk.Frame(paned_window)
        paned_window.add(left_container, weight=1)
        
        # Create ScrolledFrame inside the container
        self.settings_frame = ScrolledFrame(left_container, autohide=True, width=300)
        self.settings_frame.pack(fill=BOTH, expand=YES)
        
        # Right panel (output)
        output_frame = ttk.Frame(paned_window)
        paned_window.add(output_frame, weight=3)
        
        # Add settings to the left panel
        self.create_benchmark_settings()  # Changed from create_visualization_settings
        
        # Add output area to the right panel
        self.create_output_area(output_frame)  # Changed from create_visualization_area
    
    def create_benchmark_settings(self):
        """Create the benchmark settings panel"""
        frame = self.settings_frame
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Model Endpoint Section
        endpoint_frame = ttk.Frame(main_frame, style="Card.TFrame")
        endpoint_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(endpoint_frame, text="Model Endpoint", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(endpoint_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(endpoint_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Endpoint entry
        ttk.Label(content_frame, text="API Endpoint:").pack(anchor=W, pady=(5, 2))
        self.endpoint_var = tk.StringVar(value="http://localhost:1234/v1/chat/completions")
        endpoint_entry = ttk.Entry(content_frame, textvariable=self.endpoint_var, width=40)
        endpoint_entry.pack(fill=X, pady=(0, 10))
        
        # Timeout setting
        timeout_frame = ttk.Frame(content_frame)
        timeout_frame.pack(fill=X)
        ttk.Label(timeout_frame, text="Timeout (seconds):").pack(side=LEFT)
        self.timeout_var = tk.IntVar(value=120)
        timeout_spinbox = ttk.Spinbox(timeout_frame, from_=10, to=300, textvariable=self.timeout_var, width=5)
        timeout_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Benchmark Configuration Section
        config_frame = ttk.Frame(main_frame, style="Card.TFrame")
        config_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(config_frame, text="Benchmark Configuration", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(config_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(config_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Title entry
        ttk.Label(content_frame, text="Benchmark Title:").pack(anchor=W, pady=(5, 2))
        self.title_var = tk.StringVar(value=f"benchmark_{int(time.time())}")
        title_entry = ttk.Entry(content_frame, textvariable=self.title_var, width=40)
        title_entry.pack(fill=X, pady=(0, 10))
        
        # Number of runs
        runs_frame = ttk.Frame(content_frame)
        runs_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(runs_frame, text="Runs per task:").pack(side=LEFT)
        self.runs_var = tk.IntVar(value=1)
        runs_spinbox = ttk.Spinbox(runs_frame, from_=1, to=10, textvariable=self.runs_var, width=5)
        runs_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Parallel execution
        parallel_frame = ttk.Frame(content_frame)
        parallel_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(parallel_frame, text="Parallel tasks:").pack(side=LEFT)
        self.parallel_var = tk.IntVar(value=1)
        parallel_spinbox = ttk.Spinbox(parallel_frame, from_=1, to=10, textvariable=self.parallel_var, width=5)
        parallel_spinbox.pack(side=LEFT, padx=(5, 0))
        
        # Execute code
        self.execute_code_var = tk.BooleanVar(value=True)
        execute_check = ttk.Checkbutton(content_frame, text="Execute code to verify functionality", variable=self.execute_code_var)
        execute_check.pack(anchor=W, pady=(0, 5))
        
        # Monitor resources
        self.monitor_resources_var = tk.BooleanVar(value=True)
        monitor_check = ttk.Checkbutton(content_frame, text="Monitor system resources", variable=self.monitor_resources_var)
        monitor_check.pack(anchor=W, pady=(0, 5))
        
        # Task Selection Section
        tasks_frame = ttk.Frame(main_frame, style="Card.TFrame")
        tasks_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Label(tasks_frame, text="Task Selection", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(tasks_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        content_frame = ttk.Frame(tasks_frame, style="CardContent.TFrame")
        content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # Categories
        ttk.Label(content_frame, text="Categories:").pack(anchor=W, pady=(5, 2))
        self.categories_frame = ttk.Frame(content_frame)
        self.categories_frame.pack(fill=X, pady=(0, 10))
        
        # Difficulties
        ttk.Label(content_frame, text="Difficulties:").pack(anchor=W, pady=(5, 2))
        self.difficulties_frame = ttk.Frame(content_frame)
        self.difficulties_frame.pack(fill=X, pady=(0, 10))
        
        # Languages
        ttk.Label(content_frame, text="Languages:").pack(anchor=W, pady=(5, 2))
        self.languages_frame = ScrolledFrame(content_frame, height=150, autohide=True)
        self.languages_frame.pack(fill=X, pady=(0, 10))
        
        # Action buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=X, pady=15)
        
        self.run_button = ttk.Button(buttons_frame, text="Run Benchmark", style="success", 
                                   command=self.run_benchmark)
        self.run_button.pack(side=LEFT, padx=5)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", style="danger", 
                                   command=self.stop_benchmark, state=DISABLED)
        self.stop_button.pack(side=LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Reset", style="secondary", 
                 command=self.reset_benchmark_settings).pack(side=LEFT, padx=5)
    
    def create_output_area(self, parent_frame):
        """Create the output area for benchmark results"""
        # Create a frame for output with a title
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=BOTH, expand=YES, padx=15, pady=15)
        
        # Title
        ttk.Label(frame, text="Benchmark Output", style="Header.TLabel").pack(anchor=W)
        ttk.Separator(frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Status information
        self.status_frame = ttk.Frame(frame)
        self.status_frame.pack(fill=X, pady=5)
        
        ttk.Label(self.status_frame, text="Status:").pack(side=LEFT)
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, style="Info.TLabel")
        self.status_label.pack(side=LEFT, padx=5)
        
        # Progress bar
        self.progress_frame = ttk.Frame(frame)
        self.progress_frame.pack(fill=X, pady=5)
        
        ttk.Label(self.progress_frame, text="Progress:").pack(anchor=W)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                         length=100, mode="determinate")
        self.progress_bar.pack(fill=X, pady=5)
        
        self.progress_text_var = tk.StringVar(value="0/0 tasks completed")
        ttk.Label(self.progress_frame, textvariable=self.progress_text_var).pack(anchor=E)
        
        # Output text
        ttk.Label(frame, text="Console Output:").pack(anchor=W, pady=(10, 5))
        
        # Use Text widget with vertical scrollbar for output
        output_frame = ttk.Frame(frame)
        output_frame.pack(fill=BOTH, expand=YES)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=20)
        self.output_text.pack(side=LEFT, fill=BOTH, expand=YES)
        
        # Configure tags for different log levels
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("warning", foreground="orange")
        self.output_text.tag_configure("info", foreground="white")
        
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Make text read-only
        self.output_text.config(state=DISABLED)
        
        # Results summary section
        self.results_frame = ttk.Frame(frame, style="Card.TFrame")
        self.results_frame.pack(fill=X, pady=10)
        
        ttk.Label(self.results_frame, text="Results Summary", style="Header.TLabel").pack(anchor=W, padx=10, pady=(10, 5))
        ttk.Separator(self.results_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=5)
        
        # Create an empty container for results that will be populated when available
        self.results_content_frame = ttk.Frame(self.results_frame, style="CardContent.TFrame")
        self.results_content_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttk.Label(self.results_content_frame, text="No results available yet", 
                style="Subtitle.TLabel").pack(anchor=CENTER, pady=20)
    
    def load_available_options(self):
        """Load available categories, difficulties, and languages"""
        # Load options from the controller
        self.available_categories, self.available_difficulties, self.available_languages = (
            self.controller.get_available_options()
        )
        
        # Populate categories
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
            
        self.category_vars = {}
        for category in self.available_categories:
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            ttk.Checkbutton(self.categories_frame, text=category, variable=var).pack(anchor=W)
        
        # Populate difficulties
        for widget in self.difficulties_frame.winfo_children():
            widget.destroy()
            
        self.difficulty_vars = {}
        for difficulty in self.available_difficulties:
            var = tk.BooleanVar(value=True)
            self.difficulty_vars[difficulty] = var
            ttk.Checkbutton(self.difficulties_frame, text=difficulty, variable=var).pack(anchor=W)
        
        # Populate languages
        for widget in self.languages_frame.winfo_children():
            widget.destroy()
            
        self.language_vars = {}
        for language in self.available_languages:
            var = tk.BooleanVar(value=True)
            self.language_vars[language] = var
            ttk.Checkbutton(self.languages_frame, text=language, variable=var).pack(anchor=W)
    
    def reset_benchmark_settings(self):
        """Reset benchmark settings to defaults"""
        # Reset variables
        self.endpoint_var.set("http://localhost:1234/v1/chat/completions")
        self.timeout_var.set(120)
        self.title_var.set(f"benchmark_{int(time.time())}")
        self.runs_var.set(1)
        self.parallel_var.set(1)
        self.execute_code_var.set(True)
        self.monitor_resources_var.set(True)
        
        # Reset checkboxes
        for var in self.category_vars.values():
            var.set(True)
        for var in self.difficulty_vars.values():
            var.set(True)
        for var in self.language_vars.values():
            var.set(True)
    
    def log(self, message, level="info"):
        """Log a message to the output text widget"""
        log_message(self.output_text, message, level)
    
    def run_benchmark(self):
        """Run the benchmark with the current settings"""
        if self.state.get("is_running", False):
            return
        
        # Get selected categories, difficulties, and languages
        categories = [cat for cat, var in self.category_vars.items() if var.get()]
        difficulties = [diff for diff, var in self.difficulty_vars.items() if var.get()]
        languages = [lang for lang, var in self.language_vars.items() if var.get()]
        
        if not categories:
            tk.messagebox.showwarning("Warning", "Please select at least one category.")
            return
            
        if not difficulties:
            tk.messagebox.showwarning("Warning", "Please select at least one difficulty level.")
            return
            
        if not languages:
            tk.messagebox.showwarning("Warning", "Please select at least one programming language.")
            return
        
        # Update benchmark settings in controller
        benchmark_config = {
            "endpoint": self.endpoint_var.get(),
            "timeout": self.timeout_var.get(),
            "title": self.title_var.get(),
            "execute_code": self.execute_code_var.get(),
            "monitor_resources": self.monitor_resources_var.get(),
            "runs": self.runs_var.get(),
            "parallel": self.parallel_var.get()
        }
        
        self.controller.configure_benchmark(benchmark_config)
        
        # Disable run button and enable stop button
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
        
        # Set running state
        self.state["is_running"] = True
        
        # Create and start benchmark thread
        self.benchmark_thread = threading.Thread(
            target=self.benchmark_worker,
            args=(categories, difficulties, languages)
        )
        self.benchmark_thread.daemon = True
        self.benchmark_thread.start()
        
        # Update UI periodically
        self.parent.after(100, self.check_benchmark_progress)
    
    def benchmark_worker(self, categories, difficulties, languages):
        """Worker function for running benchmark in a separate thread with improved error handling and cancellation support"""
        # Store state for progress tracking
        self.total_tasks = get_task_count(
            self.controller.benchmark, categories, difficulties, languages
        )
        self.completed_tasks = 0
        
        # Set up flag for cancellation
        self.is_cancelled = False
        
        # Override print to capture output
        original_print = print
        
        def custom_print(*args, **kwargs):
            # Call original print
            original_print(*args, **kwargs)
            
            # Skip updating if cancelled
            if self.is_cancelled:
                return
                
            # Also update GUI
            text = " ".join(str(arg) for arg in args)
            self.log(text)
            
            # Update progress when a task is completed
            if "Running task:" in text:
                self.completed_tasks += 1
                progress = self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0
                self.progress_var.set(progress)
                self.progress_text_var.set(f"{self.completed_tasks}/{self.total_tasks} tasks completed")
            
            # Update UI to keep it responsive
            try:
                self.parent.update_idletasks()
            except Exception:
                pass
        
        # Replace print function
        builtins_module = __import__('builtins')
        setattr(builtins_module, 'print', custom_print)
        
        try:
            # Update status
            self.status_var.set("Initializing benchmark...")
            self.log("Benchmark started")
            self.log(f"Selected categories: {', '.join(categories)}")
            self.log(f"Selected difficulties: {', '.join(difficulties)}")
            self.log(f"Selected languages: {', '.join(languages)}")
            self.log(f"Total tasks: {self.total_tasks}")
            
            # Configure the benchmark with the selected options
            self.controller.benchmark.execute_code = self.execute_code_var.get()
            self.controller.benchmark.monitor_resources = self.monitor_resources_var.get()
            
            # Run benchmark
            self.status_var.set("Running benchmark tasks...")
            self.results = self.controller.run_benchmark(categories, difficulties, languages)
            
            # Check if cancelled
            if self.is_cancelled:
                self.log("Benchmark cancelled by user", level="warning")
                self.status_var.set("Benchmark cancelled")
                return
                
            # Analyze results
            self.status_var.set("Analyzing results...")
            self.log("Benchmark completed, analyzing results...")
            self.analysis = self.controller.analyze_results(self.results)
            
            # Check if cancelled
            if self.is_cancelled:
                self.log("Analysis cancelled by user", level="warning")
                self.status_var.set("Analysis cancelled")
                return
                
            # Display results summary
            self.parent.after(0, lambda: self.display_results_summary(self.analysis))
            
            # Update status
            self.status_var.set("Benchmark completed")
            self.log("Benchmark and analysis successfully completed")
            
            # Ask if user wants to add to leaderboard
            self.parent.after(500, self.prompt_add_to_leaderboard)
            
        except Exception as e:
            # Log the error
            error_message = str(e)
            self.log(f"Error running benchmark: {error_message}", level="error")
            
            # Show more details for specific error types
            if "connection" in error_message.lower():
                self.log("Check that the LM Studio server is running and the endpoint is correct", level="warning")
            elif "timeout" in error_message.lower():
                self.log("Consider increasing the timeout value in settings", level="warning")
            elif "file" in error_message.lower() and "permission" in error_message.lower():
                self.log("Check file permissions for the output directory", level="warning")
            
            # Update status
            self.status_var.set("Benchmark failed")
            
            # Show error dialog on the main thread
            self.parent.after(0, lambda: messagebox.showerror("Benchmark Error", 
                                                        f"Error running benchmark: {error_message}"))
        
        finally:
            # Restore original print
            setattr(builtins_module, 'print', original_print)
            
            # Update running state
            self.state["is_running"] = False
            
            # Re-enable run button and disable stop button
            self.parent.after(0, lambda: self.run_button.config(state=NORMAL))
            self.parent.after(0, lambda: self.stop_button.config(state=DISABLED))
    
    def check_benchmark_progress(self):
        """Check benchmark progress and update UI with improved responsiveness"""
        if self.state.get("is_running", False):
            try:
                # Update the progress bar animation
                self.progress_bar.update_idletasks()
                
                # Check for cancellation
                if hasattr(self, 'is_cancelled') and self.is_cancelled:
                    return  # Stop checking if cancelled
                    
                # Update status text
                if hasattr(self, 'completed_tasks') and hasattr(self, 'total_tasks'):
                    percentage = self.completed_tasks / self.total_tasks * 100 if self.total_tasks > 0 else 0
                    self.status_var.set(f"Running benchmark... {percentage:.1f}%")
                    
                # Schedule next check - use shorter interval for more responsive UI
                self.parent.after(100, self.check_benchmark_progress)
                    
            except Exception as e:
                # Silently handle errors in the UI update
                print(f"Error updating progress UI: {e}")
                # Still try to schedule next check
                self.parent.after(100, self.check_benchmark_progress)
        else:
            # Final update if benchmark is no longer running
            if hasattr(self, 'completed_tasks') and hasattr(self, 'total_tasks'):
                if self.completed_tasks < self.total_tasks:
                    self.progress_text_var.set(f"{self.completed_tasks}/{self.total_tasks} tasks completed (stopped)")
    
    def stop_benchmark(self):
        """Stop the currently running benchmark with improved cancellation"""
        if not self.state.get("is_running", False):
            return
        
        if tk.messagebox.askyesno("Confirm Stop", "Are you sure you want to stop the benchmark?"):
            # Set cancellation flag
            self.is_cancelled = True
            
            # Update status
            self.status_var.set("Stopping benchmark...")
            self.log("Stopping benchmark...", level="warning")
            
            # Set the state flag
            self.state["is_running"] = False
            
            # Try to cancel any ongoing operations in the controller
            if hasattr(self.controller, 'benchmark') and hasattr(self.controller.benchmark, 'cancel'):
                try:
                    self.controller.benchmark.cancel()
                except Exception as e:
                    print(f"Error cancelling benchmark: {e}")
            
            # Re-enable run button and disable stop button
            self.run_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
    
    def display_results_summary(self, analysis):
        """Display the benchmark results summary with improved organization and information"""
        # Clear previous content
        for widget in self.results_content_frame.winfo_children():
            widget.destroy()
        
        # Add summary information
        ttk.Label(self.results_content_frame, text="Summary", style="Subtitle.TLabel").pack(anchor=W, pady=(5, 10))
        
        # Overall metrics
        overall_frame = ttk.Frame(self.results_content_frame)
        overall_frame.pack(fill=X, pady=5)
        
        # Create a table-like structure for metrics
        metrics_table = ttk.Frame(overall_frame)
        metrics_table.pack(fill=X)
        
        # Row 1: Response Time and API Success Rate
        row1 = ttk.Frame(metrics_table)
        row1.pack(fill=X, pady=2)
        
        # Response time
        ttk.Label(row1, text="Average Response Time:", width=25, anchor="w").grid(row=0, column=0, sticky="w")
        ttk.Label(row1, text=f"{analysis['summary'].get('avg_response_time', 0):.2f}s", 
                style="Info.TLabel").grid(row=0, column=1, padx=(5, 20), sticky="w")
        
        # API Success Rate
        ttk.Label(row1, text="API Success Rate:", width=20, anchor="w").grid(row=0, column=2, sticky="w")
        api_rate = analysis['summary'].get('api_success_rate', 0)
        color_style = "Success.TLabel" if api_rate >= 0.8 else ("Warning.TLabel" if api_rate >= 0.5 else "Danger.TLabel")
        ttk.Label(row1, text=f"{api_rate*100:.2f}%", 
                style=color_style).grid(row=0, column=3, padx=(5, 0), sticky="w")
        
        # Row 2: Execution Success Rate and Test Pass Rate (if available)
        if "execution_success_rate" in analysis["summary"] or "test_pass_rate" in analysis["summary"]:
            row2 = ttk.Frame(metrics_table)
            row2.pack(fill=X, pady=2)
            
            col = 0
            
            # Execution Success Rate (if available)
            if "execution_success_rate" in analysis["summary"]:
                ttk.Label(row2, text="Execution Success Rate:", width=25, anchor="w").grid(row=0, column=col, sticky="w")
                col += 1
                
                exec_rate = analysis['summary'].get('execution_success_rate', 0)
                color_style = "Success.TLabel" if exec_rate >= 0.8 else ("Warning.TLabel" if exec_rate >= 0.5 else "Danger.TLabel")
                ttk.Label(row2, text=f"{exec_rate*100:.2f}%", 
                        style=color_style).grid(row=0, column=col, padx=(5, 20), sticky="w")
                col += 1
            
            # Test Pass Rate (if available)
            if "test_pass_rate" in analysis["summary"]:
                ttk.Label(row2, text="Test Pass Rate:", width=20, anchor="w").grid(row=0, column=col, sticky="w")
                col += 1
                
                test_rate = analysis['summary'].get('test_pass_rate', 0)
                color_style = "Success.TLabel" if test_rate >= 0.8 else ("Warning.TLabel" if test_rate >= 0.5 else "Danger.TLabel")
                ttk.Label(row2, text=f"{test_rate*100:.2f}%", 
                        style=color_style).grid(row=0, column=col, padx=(5, 0), sticky="w")
        
        # Add task count information
        tasks_frame = ttk.Frame(overall_frame)
        tasks_frame.pack(fill=X, pady=(10, 5))
        
        if "total_tasks" in analysis["summary"]:
            ttk.Label(tasks_frame, text=f"Tasks: {analysis['summary']['total_tasks']}").pack(side=LEFT, padx=(0, 15))
        
        if "completed_tasks" in analysis["summary"]:
            ttk.Label(tasks_frame, text=f"Completed: {analysis['summary']['completed_tasks']}").pack(side=LEFT, padx=(0, 15))
        
        if "total_tests" in analysis["summary"]:
            ttk.Label(tasks_frame, text=f"Tests Run: {analysis['summary']['total_tests']}").pack(side=LEFT)
        
        # Add resource metrics if available
        if hasattr(self, 'results') and "resource_metrics" in self.results:
            ttk.Separator(self.results_content_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
            ttk.Label(self.results_content_frame, text="Resource Usage", 
                    style="Subtitle.TLabel").pack(anchor=W, pady=(5, 10))
            
            resource_frame = ttk.Frame(self.results_content_frame)
            resource_frame.pack(fill=X, pady=5)
            
            metrics = self.results["resource_metrics"]
            
            # CPU metrics
            if "cpu" in metrics:
                cpu_frame = ttk.Frame(resource_frame)
                cpu_frame.pack(fill=X, pady=2)
                
                ttk.Label(cpu_frame, text="CPU Usage:", width=15, anchor="w").pack(side=LEFT)
                ttk.Label(cpu_frame, text=f"Avg: {metrics['cpu']['percent']['mean']:.1f}%", 
                        style="Info.TLabel").pack(side=LEFT, padx=(5, 10))
                ttk.Label(cpu_frame, text=f"Max: {metrics['cpu']['percent']['max']:.1f}%", 
                        style="Info.TLabel").pack(side=LEFT)
            
            # Memory metrics
            if "memory" in metrics:
                mem_frame = ttk.Frame(resource_frame)
                mem_frame.pack(fill=X, pady=2)
                
                ttk.Label(mem_frame, text="Memory Usage:", width=15, anchor="w").pack(side=LEFT)
                ttk.Label(mem_frame, text=f"Avg: {metrics['memory']['used_gb']['mean']:.2f} GB", 
                        style="Info.TLabel").pack(side=LEFT, padx=(5, 10))
                ttk.Label(mem_frame, text=f"Peak: {metrics['memory']['used_gb']['max']:.2f} GB", 
                        style="Info.TLabel").pack(side=LEFT)
            
            # GPU metrics if available
            if "gpu" in metrics and metrics["gpu"]:
                gpu_frame = ttk.Frame(resource_frame)
                gpu_frame.pack(fill=X, pady=2)
                
                if "utilization" in metrics["gpu"]:
                    ttk.Label(gpu_frame, text="GPU Utilization:", width=15, anchor="w").pack(side=LEFT)
                    ttk.Label(gpu_frame, text=f"Avg: {metrics['gpu']['utilization']['mean']:.1f}%", 
                            style="Info.TLabel").pack(side=LEFT, padx=(5, 10))
                    ttk.Label(gpu_frame, text=f"Max: {metrics['gpu']['utilization']['max']:.1f}%", 
                            style="Info.TLabel").pack(side=LEFT)
                elif "devices" in metrics["gpu"]:
                    for device, stats in metrics["gpu"]["devices"].items():
                        if "utilization" in stats:
                            ttk.Label(gpu_frame, text=f"{device}:", width=15, anchor="w").pack(side=LEFT)
                            ttk.Label(gpu_frame, text=f"Avg: {stats['utilization']['mean']:.1f}%", 
                                    style="Info.TLabel").pack(side=LEFT, padx=(5, 10))
                            ttk.Label(gpu_frame, text=f"Max: {stats['utilization']['max']:.1f}%", 
                                    style="Info.TLabel").pack(side=LEFT)
                            break
        
        # Add category, difficulty, and language breakdown if available
        if "by_category" in analysis["summary"] or "by_difficulty" in analysis["summary"] or "by_language" in analysis["summary"]:
            ttk.Separator(self.results_content_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
            ttk.Label(self.results_content_frame, text="Performance Breakdown", 
                    style="Subtitle.TLabel").pack(anchor=W, pady=(5, 10))
            
            breakdown_frame = ttk.Notebook(self.results_content_frame)
            breakdown_frame.pack(fill=X, pady=5)
            
            # Add tabs for each breakdown type
            if "by_category" in analysis["summary"]:
                category_frame = ttk.Frame(breakdown_frame)
                breakdown_frame.add(category_frame, text="By Category")
                self.create_breakdown_table(category_frame, analysis["summary"]["by_category"])
            
            if "by_difficulty" in analysis["summary"]:
                difficulty_frame = ttk.Frame(breakdown_frame)
                breakdown_frame.add(difficulty_frame, text="By Difficulty")
                self.create_breakdown_table(difficulty_frame, analysis["summary"]["by_difficulty"])
            
            if "by_language" in analysis["summary"]:
                language_frame = ttk.Frame(breakdown_frame)
                breakdown_frame.add(language_frame, text="By Language")
                self.create_breakdown_table(language_frame, analysis["summary"]["by_language"])

         # Add buttons to view results
        buttons_frame = ttk.Frame(self.results_content_frame)
        buttons_frame.pack(fill=X, pady=(20, 10))
        
        # Button to open analysis file
        analysis_btn = ttk.Button(buttons_frame, text="Open Analysis File", 
                                command=self.open_analysis_file)
        analysis_btn.pack(side=LEFT, padx=(0, 10))
        self.create_tooltip(analysis_btn, "Open the full analysis JSON file in your default application")
        
        # Button to view visualizations
        viz_btn = ttk.Button(buttons_frame, text="View Visualizations", 
                        command=self.view_benchmark_visualizations)
        viz_btn.pack(side=LEFT, padx=(0, 10))
        self.create_tooltip(viz_btn, "Switch to the visualization tab to explore benchmark charts")
        
        # Button to add to leaderboard
        lb_btn = ttk.Button(buttons_frame, text="Add to Leaderboard", 
                        command=self.prompt_add_to_leaderboard)
        lb_btn.pack(side=LEFT)
        self.create_tooltip(lb_btn, "Add these benchmark results to the leaderboard for comparison")
    
    def open_analysis_file(self):
        """Open the analysis file in the default application"""
        self.controller.open_analysis_file()

    def create_breakdown_table(self, parent_frame, breakdown_data):
        """Create a table to display performance breakdown data"""
        # Create a frame for the table
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Headers
        headers = ["Name", "API Success", "Execution Success", "Test Pass Rate"]
        
        # Create header row
        header_frame = ttk.Frame(table_frame)
        header_frame.pack(fill=X, pady=(0, 5))
        
        for i, header in enumerate(headers):
            ttk.Label(header_frame, text=header, font=("Helvetica", 10, "bold")).grid(row=0, column=i, padx=5, sticky=W)
        
        # Add a separator after headers
        ttk.Separator(table_frame, orient=HORIZONTAL).pack(fill=X, pady=5)
        
        # Sort items by test_pass_rate (if available) or api_success_rate
        sorted_items = sorted(
            breakdown_data.items(),
            key=lambda x: x[1].get("test_pass_rate", x[1].get("api_success_rate", 0)),
            reverse=True
        )
        
        # Create data rows
        for i, (name, metrics) in enumerate(sorted_items):
            row_frame = ttk.Frame(table_frame)
            row_frame.pack(fill=X, pady=2)
            
            # Name column
            ttk.Label(row_frame, text=name, width=15, anchor=W).grid(row=0, column=0, padx=5, sticky=W)
            
            # API Success Rate
            api_success = metrics.get("api_success_rate", 0)
            api_label = ttk.Label(row_frame, text=f"{api_success:.2%}")
            api_label.grid(row=0, column=1, padx=5)
            self.apply_color_style(api_label, api_success)
            
            # Execution Success Rate
            exec_success = metrics.get("execution_success_rate", 0)
            if "execution_success_rate" in metrics:
                exec_label = ttk.Label(row_frame, text=f"{exec_success:.2%}")
            else:
                exec_label = ttk.Label(row_frame, text="N/A")
            exec_label.grid(row=0, column=2, padx=5)
            if "execution_success_rate" in metrics:
                self.apply_color_style(exec_label, exec_success)
            
            # Test Pass Rate
            test_pass = metrics.get("test_pass_rate", 0)
            if "test_pass_rate" in metrics:
                test_label = ttk.Label(row_frame, text=f"{test_pass:.2%}")
            else:
                test_label = ttk.Label(row_frame, text="N/A")
            test_label.grid(row=0, column=3, padx=5)
            if "test_pass_rate" in metrics:
                self.apply_color_style(test_label, test_pass)
        
        # Add explanation of color coding
        ttk.Label(table_frame, 
                text="Color coding: Green (≥80%), Yellow (50-80%), Red (<50%)",
                style="Info.TLabel").pack(anchor=E, pady=(10, 0))

    # Helper method for applying color styles to labels
    def apply_color_style(self, label, value):
        """Apply color styling to a label based on the metric value"""
        if value >= 0.8:  # 80% or higher - good
            label.configure(foreground="forest green")
        elif value >= 0.5:  # 50% to 80% - medium
            label.configure(foreground="dark orange")
        else:  # Below 50% - poor
            label.configure(foreground="firebrick")

    # Helper method for creating tooltips
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            tooltip = ttk.Toplevel(self.parent)
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
    
    def view_benchmark_visualizations(self):
        """View the benchmark visualizations in the visualize tab with improved tab navigation"""
        try:
            # Delegate to the controller
            viz_files = self.controller.get_visualization_files()
            
            if not viz_files:
                messagebox.showinfo("Information", "No visualization files available for this benchmark.")
                return
                
            # Notify the parent to switch to visualize tab and load files
            self.state["visualization_files"] = viz_files
            
            # Use the notebook reference to switch tabs by name rather than index
            notebook = self.parent.master
            
            # Find the visualize tab by its text attribute
            visualize_tab_found = False
            for i, tab in enumerate(notebook.tabs()):
                if notebook.tab(tab, "text") == "Visualize":
                    notebook.select(i)
                    visualize_tab_found = True
                    break
                    
            # If tab not found by name, fall back to index (but log a warning)
            if not visualize_tab_found:
                print("Warning: Visualize tab not found by name, falling back to index")
                notebook.select(1)  # Switch to visualize tab (traditional index 1)
                
        except Exception as e:
            print(f"Error viewing benchmark visualizations: {e}")
            messagebox.showerror("Error", f"Error viewing visualizations: {e}")
    
    def prompt_add_to_leaderboard(self):
        """Prompt the user to add the benchmark results to the leaderboard"""
        if not hasattr(self, 'analysis'):
            self.log("No analysis data available. Run a benchmark first.", level="warning")
            return
        
        # Show add to leaderboard dialog through controller
        self.controller.show_add_leaderboard_dialog(self.parent)