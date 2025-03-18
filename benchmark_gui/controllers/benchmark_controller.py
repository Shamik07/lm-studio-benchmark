"""
Controller for the benchmark tab functionality.
"""

import os
import platform
import time
from typing import Tuple, List, Dict, Any

import tkinter as tk
from tkinter import messagebox

from enhanced_benchmark import EnhancedLMStudioBenchmark
from views.dialogs.add_leaderboard_entry import AddLeaderboardEntryDialog

class BenchmarkController:
    """Controller for benchmark operations"""
    
    def __init__(self, state):
        """
        Initialize the benchmark controller.
        
        Args:
            state: Shared application state
        """
        self.state = state
        self.benchmark = None
        self.init_benchmark()
    
    def init_benchmark(self):
        """Initialize the benchmark instance"""
        try:
            output_dir = self.state.get("output_dir", "benchmark_results")
            title = f"benchmark_{int(time.time())}"
            
            self.benchmark = EnhancedLMStudioBenchmark(
                model_endpoint="http://localhost:1234/v1/chat/completions",
                timeout=120,
                results_dir=output_dir,
                title=title,
                execute_code=True,
                monitor_resources=True
            )
            
            # Store benchmark in state
            self.state["benchmark"] = self.benchmark
            
            return True
        except Exception as e:
            print(f"Error initializing benchmark: {e}")
            return False
    
    def get_available_options(self) -> Tuple[List[str], List[str], List[str]]:
        """
        Get available categories, difficulties, and languages.
        
        Returns:
            Tuple of (categories, difficulties, languages)
        """
        if not self.benchmark:
            if not self.init_benchmark():
                # Default values if benchmark initialization fails
                return (
                    ["syntax", "algorithms", "data_structures", "debugging", "api_usage", 
                     "web_dev", "concurrency", "testing", "error_handling", "oop"],
                    ["easy", "medium", "hard"],
                    ["python", "javascript", "typescript", "java", "cpp", "csharp", "php", 
                     "go", "rust", "swift", "kotlin", "dart"]
                )
        
        # Extract unique categories, difficulties, and languages
        categories = sorted(set(task["category"] for task in self.benchmark.tasks))
        difficulties = sorted(set(task["difficulty"] for task in self.benchmark.tasks),
                             key=lambda x: ["easy", "medium", "hard"].index(x) 
                             if x in ["easy", "medium", "hard"] else 999)
        
        # Collect all languages across all tasks
        languages = set()
        for task in self.benchmark.tasks:
            languages.update(task["languages"])
        languages = sorted(languages)
        
        return categories, difficulties, languages
    
    def configure_benchmark(self, config):
        """
        Configure the benchmark instance with new settings.
        
        Args:
            config: Dictionary with benchmark configuration
        """
        try:
            # Create a new benchmark instance with the provided configuration
            self.benchmark = EnhancedLMStudioBenchmark(
                model_endpoint=config["endpoint"],
                timeout=config["timeout"],
                results_dir=self.state.get("output_dir", "benchmark_results"),
                title=config["title"],
                execute_code=config["execute_code"],
                monitor_resources=config["monitor_resources"]
            )
            
            # Store benchmark in state
            self.state["benchmark"] = self.benchmark
            
            return True
        except Exception as e:
            print(f"Error configuring benchmark: {e}")
            return False
    
    def run_benchmark(self, categories, difficulties, languages):
        """
        Run the benchmark with the specified settings.
        
        Args:
            categories: Selected categories
            difficulties: Selected difficulty levels
            languages: Selected programming languages
            
        Returns:
            Benchmark results dictionary
        """
        # Get additional parameters from configuration
        runs = self.benchmark.num_runs if hasattr(self.benchmark, "num_runs") else 1
        
        # Run the benchmark
        results = self.benchmark.run_benchmark(
            categories=categories,
            difficulties=difficulties,
            languages=languages,
            num_runs=runs
        )
        
        return results
    
    def analyze_results(self, results):
        """
        Analyze benchmark results.
        
        Args:
            results: Benchmark results dictionary
            
        Returns:
            Analysis dictionary
        """
        return self.benchmark.analyze_results(results)
    
    def open_analysis_file(self):
        """Open the analysis file in the default application"""
        if hasattr(self, 'benchmark') and hasattr(self.benchmark, 'run_dir'):
            # Get the path to the analysis file
            safe_title = "".join(c if c.isalnum() else "_" for c in self.benchmark.title)
            analysis_file = self.benchmark.run_dir / f"analysis_{safe_title}.json"
            
            if analysis_file.exists():
                try:
                    # Open the file with the default application
                    if platform.system() == 'Windows':
                        os.startfile(str(analysis_file))
                    elif platform.system() == 'Darwin':  # macOS
                        os.system(f'open "{analysis_file}"')
                    else:  # Linux
                        os.system(f'xdg-open "{analysis_file}"')
                        
                    return True
                except Exception as e:
                    print(f"Error opening analysis file: {e}")
                    return False
            else:
                print(f"Analysis file not found: {analysis_file}")
                return False
        else:
            print("No benchmark run available.")
            return False
    
    def get_visualization_files(self):
        """
        Get paths to visualization files from the benchmark run.
        
        Returns:
            List of Path objects for visualization files
        """
        if hasattr(self, 'benchmark') and hasattr(self.benchmark, 'run_dir'):
            # Get visualization files from the run directory
            viz_files = list(self.benchmark.run_dir.glob("*.png"))
            
            if viz_files:
                return viz_files
            else:
                print("No visualizations found in the benchmark run directory.")
                return []
        else:
            print("No benchmark run available.")
            return []
    
    def show_add_leaderboard_dialog(self, parent):
        """
        Show dialog to add benchmark results to leaderboard.
        
        Args:
            parent: Parent widget for the dialog
        """
        if not self.state.get("leaderboard"):
            messagebox.showerror("Error", "Leaderboard not available.")
            return
        
        # Get the path to the analysis file
        safe_title = "".join(c if c.isalnum() else "_" for c in self.benchmark.title)
        analysis_file = self.benchmark.run_dir / f"analysis_{safe_title}.json"
        
        if not analysis_file.exists():
            messagebox.showerror("Error", "Analysis file not found.")
            return
        
        # Show dialog
        dialog = AddLeaderboardEntryDialog(
            parent, 
            self.state["leaderboard"], 
            str(analysis_file), 
            self.benchmark.title
        )