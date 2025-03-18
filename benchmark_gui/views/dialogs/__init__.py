"""
Dialog modules for LM Studio Benchmark GUI.

This package contains dialog window components used throughout
the application for various purposes like displaying details,
configuration, and visualizations.
"""

from views.dialogs.add_leaderboard_entry import AddLeaderboardEntryDialog
from views.dialogs.entry_details import EntryDetailsDialog
from views.dialogs.model_compare import ModelCompareDialog
from views.dialogs.model_history import ModelHistoryDialog
from views.dialogs.resource_viz import ResourceMetricsDialog
from views.dialogs.generate_report_dialog import GenerateReportDialog

# Define exported modules
__all__ = [
    'AddLeaderboardEntryDialog',
    'EntryDetailsDialog',
    'ModelCompareDialog',
    'ModelHistoryDialog',
    'ResourceMetricsDialog',
    'GenerateReportDialog'
]