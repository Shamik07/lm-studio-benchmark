"""
Controller for the leaderboard tab functionality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
from typing import List, Dict, Any, Tuple, Optional

from leaderboard import Leaderboard
from views.dialogs.entry_details import EntryDetailsDialog

class LeaderboardController:
    """Controller for leaderboard operations"""
    
    def __init__(self, state):
        """
        Initialize the leaderboard controller.
        
        Args:
            state: Shared application state
        """
        self.state = state
        self.leaderboard = None
        self.init_leaderboard()
    
    def init_leaderboard(self):
        """Initialize the leaderboard instance"""
        try:
            leaderboard_dir = self.state.get("leaderboard_dir", "benchmark_results/leaderboard")
            self.leaderboard = Leaderboard(leaderboard_path=leaderboard_dir)
            
            # Store in app state
            self.state["leaderboard"] = self.leaderboard
            
            return True
        except Exception as e:
            print(f"Error initializing leaderboard: {e}")
            return False
    
    def browse_for_file(self, title: str, filetypes: List[tuple]) -> Optional[str]:
        """
        Show file browser dialog.
        
        Args:
            title: Dialog title
            filetypes: List of file type tuples
            
        Returns:
            Selected file path or None if canceled
        """
        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )
        
        return filename if filename else None
    
    def browse_for_directory(self, title: str) -> Optional[str]:
        """
        Show directory browser dialog.
        
        Args:
            title: Dialog title
            
        Returns:
            Selected directory path or None if canceled
        """
        directory = filedialog.askdirectory(
            title=title
        )
        
        return directory if directory else None
    
    def add_to_leaderboard(self, analysis_file: str, model_name: str, 
                          model_info: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add benchmark results to the leaderboard.
        
        Args:
            analysis_file: Path to the analysis file
            model_name: Model name
            model_info: Optional model metadata
            
        Returns:
            True if added successfully, False otherwise
        """
        if not self.leaderboard:
            if not self.init_leaderboard():
                messagebox.showerror("Error", "Failed to initialize leaderboard.")
                return False
        
        if not Path(analysis_file).exists():
            messagebox.showerror("Error", f"Analysis file not found: {analysis_file}")
            return False
        
        try:
            # Add to leaderboard
            entry = self.leaderboard.add_entry(
                analysis_file=analysis_file,
                model_name=model_name,
                model_info=model_info if model_info else None
            )
            
            print(f"Added entry {entry['id']} for model {model_name} to leaderboard.")
            return True
            
        except Exception as e:
            print(f"Error adding to leaderboard: {e}")
            messagebox.showerror("Error", f"Failed to add to leaderboard: {e}")
            return False
    
    def refresh_leaderboard(self, metric: str = "test_pass_rate", 
                          limit: int = 10) -> Tuple[List[Dict], List[Dict]]:
        """
        Refresh leaderboard data.
        
        Args:
            metric: Metric to sort by
            limit: Maximum number of entries to return
            
        Returns:
            Tuple of (models, entries) lists
        """
        if not self.leaderboard:
            if not self.init_leaderboard():
                return [], []
        
        try:
            # Get models
            models = self.leaderboard.list_models(
                metric=metric,
                limit=limit
            )
            
            # Get entries
            entries = self.leaderboard.list_entries(
                metric=metric,
                limit=limit
            )
            
            return models, entries
            
        except Exception as e:
            print(f"Error refreshing leaderboard: {e}")
            return [], []
    
    def get_model_entries(self, model_name: str) -> List[Dict]:
        """
        Get entries for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of entries for the model
        """
        if not self.leaderboard:
            return []
        
        try:
            # Get entries for this model
            entries = self.leaderboard.list_entries(
                model_name=model_name,
                limit=100  # Get more entries for the selected model
            )
            
            return entries
            
        except Exception as e:
            print(f"Error getting model entries: {e}")
            return []
    
    def get_entry_by_id(self, entry_id: str) -> Optional[Dict]:
        """
        Get entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Entry dictionary or None if not found
        """
        if not self.leaderboard:
            return None
        
        try:
            # Find the entry in the leaderboard database
            for entry in self.leaderboard.db["entries"]:
                if entry["id"] == entry_id:
                    return entry
            
            return None
            
        except Exception as e:
            print(f"Error getting entry: {e}")
            return None
    
    def show_entry_details(self, entry_id: str, parent_widget):
        """
        Show dialog with entry details.
        
        Args:
            entry_id: Entry ID
            parent_widget: Parent widget for the dialog
        """
        entry = self.get_entry_by_id(entry_id)
        
        if not entry:
            messagebox.showerror("Error", f"Entry not found: {entry_id}")
            return
        
        # Show the entry details dialog
        dialog = EntryDetailsDialog(parent_widget, entry, self)
    
    def open_analysis_file(self, file_path: str) -> bool:
        """
        Open an analysis file with default application.
        
        Args:
            file_path: Path to the analysis file
            
        Returns:
            True if opened successfully, False otherwise
        """
        try:
            if not Path(file_path).exists():
                return False
                
            # Open the file with the default application
            import os
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')
                
            return True
        except Exception as e:
            print(f"Error opening analysis file: {e}")
            return False
    
    def generate_leaderboard_report(self, format_type: str, top_n: int, 
                                  output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a leaderboard report.
        
        Args:
            format_type: Report format (markdown, html, text)
            top_n: Number of top models to include
            output_path: Path to save the report (optional)
            
        Returns:
            Path to the generated report or None if failed
        """
        if not self.leaderboard:
            return None
        
        try:
            # Generate the report
            report_path = self.leaderboard.generate_leaderboard_report(
                output_path=output_path,
                top_n=top_n,
                format=format_type
            )
            
            return report_path
            
        except Exception as e:
            print(f"Error generating leaderboard report: {e}")
            return None
    
    def compare_models(self, model_names: List[str], metrics: List[str], 
                     resource_metrics: Optional[List[str]] = None, 
                     output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a comparison visualization of multiple models.
        
        Args:
            model_names: List of model names to compare
            metrics: List of metrics to compare
            resource_metrics: List of resource metrics to include (optional)
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization or None if failed
        """
        if not self.leaderboard:
            return None
        
        try:
            # Generate the comparison
            comparison_path = self.leaderboard.compare_models(
                model_names=model_names,
                metrics=metrics,
                resource_metrics=resource_metrics,
                output_path=output_path
            )
            
            return comparison_path
            
        except Exception as e:
            print(f"Error comparing models: {e}")
            return None
    
    def visualize_model_history(self, model_name: str, metrics: List[str], 
                              output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a history visualization for a model.
        
        Args:
            model_name: Model name
            metrics: List of metrics to include
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization or None if failed
        """
        if not self.leaderboard:
            return None
        
        try:
            # Generate the history visualization
            history_path = self.leaderboard.visualize_model_history(
                model_name=model_name,
                metrics=metrics,
                output_path=output_path
            )
            
            return history_path
            
        except Exception as e:
            print(f"Error visualizing model history: {e}")
            return None
    
    def visualize_resource_metrics(self, metric: str, top_n: int, 
                                 output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a resource metrics visualization.
        
        Args:
            metric: Resource metric to visualize
            top_n: Number of top models to include
            output_path: Path to save the visualization (optional)
            
        Returns:
            Path to the generated visualization or None if failed
        """
        if not self.leaderboard:
            return None
        
        try:
            # Generate the visualization
            resource_path = self.leaderboard.visualize_resource_metrics(
                metric=metric,
                top_n=top_n,
                output_path=output_path
            )
            
            return resource_path
            
        except Exception as e:
            print(f"Error visualizing resource metrics: {e}")
            return None
    
    def save_visualization(self, file_path: Path) -> bool:
        """
        Save a visualization to a user-selected location.
        
        Args:
            file_path: Path to the visualization file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ask for output file
            output_file = filedialog.asksaveasfilename(
                title="Save Visualization",
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("All files", "*.*")],
                initialfile=file_path.name
            )
            
            if output_file:
                # Copy the file
                shutil.copy2(file_path, output_file)
                return True
            
            return False
        
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return False
        
    def show_generate_report_dialog(self, parent_widget):
        """
        Show dialog for generating leaderboard reports.
        
        Args:
            parent_widget: Parent widget for the dialog
        """
        try:
            # Make sure the GenerateReportDialog module is available
            from views.dialogs.generate_report_dialog import GenerateReportDialog
            
            # Create and show the dialog
            dialog = GenerateReportDialog(parent_widget, self)
            
            # The dialog itself is modal, so we don't need to wait for it here
            
        except ImportError as e:
            print(f"Error importing GenerateReportDialog: {e}")
            messagebox.showerror("Error", "Could not open report dialog. Dialog module not found.")
        except Exception as e:
            print(f"Error showing report dialog: {e}")
            messagebox.showerror("Error", f"Could not open report dialog: {e}")