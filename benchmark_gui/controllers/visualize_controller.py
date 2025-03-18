"""
Controller for the visualization tab functionality.
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import time
import json
import shutil
from typing import List, Optional

from enhanced_benchmark import EnhancedLMStudioBenchmark

class VisualizeController:
    """Controller for visualization operations"""
    
    def __init__(self, state):
        """
        Initialize the visualization controller.
        
        Args:
            state: Shared application state
        """
        self.state = state
    
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
    
    def generate_visualizations(self, analysis_file: str, output_dir: str, 
                              selected_types: List[str]) -> List[Path]:
        """
        Generate visualizations from an analysis file.
        
        Args:
            analysis_file: Path to the analysis file
            output_dir: Directory to save visualizations
            selected_types: List of selected visualization types
            
        Returns:
            List of paths to generated visualization files
        """
        try:
            # Load the analysis file
            with open(analysis_file, "r") as f:
                analysis = json.load(f)
            
            # Create output directory if it doesn't exist
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(exist_ok=True, parents=True)
            
            # Create a benchmark instance for visualization
            benchmark = EnhancedLMStudioBenchmark(
                results_dir=output_dir,
                title=analysis.get("title", "Visualization")
            )
            
            # Set the run directory
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
            viz_dir = benchmark.results_dir / f"{safe_title}_viz_{timestamp}"
            viz_dir.mkdir(exist_ok=True, parents=True)
            benchmark.run_dir = viz_dir
            
            # Generate visualizations
            benchmark.visualize_results(analysis, output_dir=viz_dir)
            
            # Get visualization files
            viz_files = list(viz_dir.glob("*.png"))
            
            return viz_files
        
        except Exception as e:
            print(f"Error generating visualizations: {e}")
            return []
    
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