"""
Views package initialization for LM Studio Benchmark GUI.

This package contains all the view components of the application,
including the main tab views and dialog windows.
"""

# Import from the package itself, not from the parent directory
from benchmark_gui.views.benchmark_view import BenchmarkView
from benchmark_gui.views.visualize_view import VisualizeView
from benchmark_gui.views.leaderboard_view import LeaderboardView
from benchmark_gui.views.settings_view import SettingsView

# Import dialogs
from benchmark_gui.views.dialogs.add_leaderboard_entry import AddLeaderboardEntryDialog
from benchmark_gui.views.dialogs.entry_details import EntryDetailsDialog
from benchmark_gui.views.dialogs.model_compare import ModelCompareDialog
from benchmark_gui.views.dialogs.model_history import ModelHistoryDialog
from benchmark_gui.views.dialogs.resource_viz import ResourceMetricsDialog

# Define exported modules
__all__ = [
    'BenchmarkView',
    'VisualizeView',
    'LeaderboardView',
    'SettingsView',
    'AddLeaderboardEntryDialog',
    'EntryDetailsDialog',
    'ModelCompareDialog',
    'ModelHistoryDialog',
    'ResourceMetricsDialog'
]