"""
Controller for the settings tab functionality.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import shutil
from pathlib import Path
import time
from typing import Dict, Any, Optional

class SettingsController:
    """Controller for settings operations"""
    
    def __init__(self, state):
        """
        Initialize the settings controller.
        
        Args:
            state: Shared application state
        """
        self.state = state
        self.config_dir = Path.home() / ".lm-studio-benchmark"
        self.config_file = self.config_dir / "config.json"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Default config
        self.default_config = {
            "endpoint": "http://localhost:1234/v1/chat/completions",
            "output_dir": "benchmark_results",
            "leaderboard_dir": "benchmark_results/leaderboard",
            "timeout": 120,
            "execute_code": True,
            "monitor_resources": True,
            "parallel": 1,
            "runs": 1,
            "report_format": "markdown",
            "theme": "dark"
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file.
        
        Returns:
            Settings dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    # Load and merge with defaults for any missing keys
                    return {**self.default_config, **json.load(f)}
            except (json.JSONDecodeError, OSError):
                print(f"Error loading config file: {self.config_file}")
                return self.default_config
        
        return self.default_config
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save settings to file.
        
        Args:
            settings: Settings dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directories if they don't exist
            if "output_dir" in settings:
                Path(settings["output_dir"]).mkdir(exist_ok=True, parents=True)
            
            if "leaderboard_dir" in settings:
                Path(settings["leaderboard_dir"]).mkdir(exist_ok=True, parents=True)
            
            # Save to config file
            with open(self.config_file, "w") as f:
                json.dump(settings, f, indent=2)
            
            # Update state with new settings
            for key, value in settings.items():
                self.state[key] = value
            
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
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
    
    def reset_leaderboard(self) -> bool:
        """
        Reset the leaderboard database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get leaderboard directory from state or config
            leaderboard_dir = self.state.get("leaderboard_dir", "benchmark_results/leaderboard")
            leaderboard_path = Path(leaderboard_dir)
            
            # If the directory exists
            if leaderboard_path.exists():
                # Get the path to the database file
                db_file = leaderboard_path / "leaderboard_db.json"
                
                # If the database file exists, remove it
                if db_file.exists():
                    os.remove(db_file)
                
                # Create a new empty database file
                with open(db_file, "w") as f:
                    json.dump({
                        "version": 1,
                        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "entries": [],
                        "models": {}
                    }, f, indent=2)
                
                # Reinitialize the leaderboard in the application state
                if "leaderboard" in self.state:
                    from leaderboard import Leaderboard
                    self.state["leaderboard"] = Leaderboard(leaderboard_path=leaderboard_dir)
                
                return True
            else:
                # Create the directory
                leaderboard_path.mkdir(exist_ok=True, parents=True)
                
                # Create a new empty database file
                with open(leaderboard_path / "leaderboard_db.json", "w") as f:
                    json.dump({
                        "version": 1,
                        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "entries": [],
                        "models": {}
                    }, f, indent=2)
                
                return True
                
        except Exception as e:
            print(f"Error resetting leaderboard: {e}")
            return False
    
    def save_configuration_to_file(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Save configuration to a separate file for export.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Path to the saved file or None if canceled/failed
        """
        try:
            # Ask for file path
            filename = filedialog.asksaveasfilename(
                title="Save Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile="benchmark_config.json"
            )
            
            if filename:
                # Save configuration
                with open(filename, "w") as f:
                    json.dump(config, f, indent=2)
                
                return filename
            
            return None
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            return None
    
    def load_configuration_from_file(self) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a file.
        
        Returns:
            Configuration dictionary or None if canceled/failed
        """
        try:
            # Ask for file path
            filename = filedialog.askopenfilename(
                title="Load Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not filename:
                return None
            
            # Load configuration
            with open(filename, "r") as f:
                config = json.load(f)
            
            return config
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            return None