"""
Main application class for LM Studio Benchmark GUI.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.messagebox as messagebox

from styles import configure_styles
from views.benchmark_view import BenchmarkView
from views.visualize_view import VisualizeView
from views.leaderboard_view import LeaderboardView
from views.settings_view import SettingsView
from controllers.settings_controller import SettingsController

class BenchmarkApp:
    """Main application class for LM Studio Benchmark GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Load theme settings
        settings_controller = SettingsController({})
        settings = settings_controller.load_settings()
        
        # Create theme variable with saved value
        self.theme_var = tk.StringVar(value=settings.get("theme", "dark"))
        
        # Apply theme immediately 
        self.style = ttk.Style()
        if self.theme_var.get() == "dark":
            self.style.theme_use("darkly")
        else:
            self.style.theme_use("cosmo")
        
        configure_styles(self.style)
        
        # Create shared state dictionary
        self.state = {
            "is_running": False,
            "benchmark": None,
            "leaderboard": None,
            "theme_var": self.theme_var,
            "output_dir": settings.get("output_dir", "benchmark_results")
        }
        
        # Create UI components
        self.create_menu()
        self.create_notebook()
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Results", command=self.open_results_file)
        file_menu.add_command(label="Save Configuration", command=self.save_configuration)
        file_menu.add_command(label="Load Configuration", command=self.load_configuration)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_radiobutton(label="Light Theme", variable=self.theme_var, value="light", command=self.toggle_theme)
        theme_menu.add_radiobutton(label="Dark Theme", variable=self.theme_var, value="dark", command=self.toggle_theme)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu
        self.root.config(menu=menubar)
    
    def create_notebook(self):
        """Create the main notebook interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Create tab views
        self.benchmark_view = BenchmarkView(self.notebook, self.state)
        self.visualize_view = VisualizeView(self.notebook, self.state)
        self.leaderboard_view = LeaderboardView(self.notebook, self.state)
        self.settings_view = SettingsView(self.notebook, self.state)
        
        # Add tabs to notebook
        self.notebook.add(self.benchmark_view.frame, text="Benchmark")
        self.notebook.add(self.visualize_view.frame, text="Visualize")
        self.notebook.add(self.leaderboard_view.frame, text="Leaderboard")
        self.notebook.add(self.settings_view.frame, text="Settings")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.theme_var.get() == "dark":
            self.style.theme_use("darkly")
        else:
            self.style.theme_use("cosmo")  # Use 'cosmo' as the light theme
        
        # Reconfigure styles
        configure_styles(self.style)
    
    def open_results_file(self):
        """Open a benchmark results file"""
        # Delegate to benchmark view
        if hasattr(self, 'benchmark_view'):
            self.benchmark_view.open_results_file()
    
    def save_configuration(self):
        """Save current configuration"""
        # Delegate to settings view
        if hasattr(self, 'settings_view'):
            self.settings_view.save_configuration()
    
    def load_configuration(self):
        """Load configuration"""
        # Delegate to settings view
        if hasattr(self, 'settings_view'):
            self.settings_view.load_configuration()
    
    def show_documentation(self):
        """Show documentation"""
        import webbrowser
        # Replace with actual documentation URL
        webbrowser.open("https://github.com/yourusername/lm-studio-benchmark")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About LM Studio Coding Benchmark",
            "LM Studio Coding Benchmark GUI\n\n"
            "A comprehensive tool for evaluating LM Studio models on coding tasks.\n\n"
            "Version 1.0.0\n"
            "© 2025 Your Name"
        )
    
    def on_close(self):
        """Handle window close event"""
        # Check if benchmark is running
        if self.state.get("is_running", False):
            if not messagebox.askyesno(
                "Confirm Exit",
                "A benchmark is currently running. Are you sure you want to exit?"
            ):
                return
        
        # Save settings only if settings_view exists
        if hasattr(self, 'settings_view'):
            try:
                self.settings_view.save_settings()
            except Exception as e:
                print(f"Error saving settings: {e}")
        
        # Destroy the window
        self.root.destroy()