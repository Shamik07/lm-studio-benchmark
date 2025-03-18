"""
Views package initialization for LM Studio Benchmark GUI.

This package contains all the view components of the application,
including the main tab views and dialog windows.
"""

from views.benchmark_view import BenchmarkView
from views.visualize_view import VisualizeView
from views.leaderboard_view import LeaderboardView
from views.settings_view import SettingsView

# Import dialogs
from views.dialogs.add_leaderboard_entry import AddLeaderboardEntryDialog
from views.dialogs.entry_details import EntryDetailsDialog
from views.dialogs.model_compare import ModelCompareDialog
from views.dialogs.model_history import ModelHistoryDialog
from views.dialogs.resource_viz import ResourceMetricsDialog

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