"""
Theme and styling definitions for the LM Studio Benchmark GUI.
Simplified version for the dashboard application.
"""

def apply_modern_styles(style):
    """
    Apply modern styling to the application widgets.
    
    Args:
        style: ttk.Style instance
    """
    # Define colors based on the current theme
    is_dark = style.theme.name == "darkly"
    
    # Card styling
    style.configure(
        "TFrame", 
        background=style.colors.bg
    )
    
    # Button styling - making them more modern with padding
    style.configure(
        "TButton",
        font=("Inter", 11),
        padding=(16, 8)
    )
    
    # Success button
    style.configure(
        "success.TButton",
        background=style.colors.success,
        foreground="#ffffff"
    )
    
    # Secondary button
    style.configure(
        "secondary.TButton",
        background=style.colors.secondary if is_dark else "#f1f5f9",
        foreground=style.colors.fg
    )
    
    # Label styling
    style.configure(
        "TLabel",
        font=("Inter", 11),
        background=style.colors.bg,
        foreground=style.colors.fg
    )
    
    # Dark text for labels
    style.configure(
        "dark.TLabel",
        foreground="#0f172a" if not is_dark else style.colors.fg
    )
    
    # Secondary text for labels
    style.configure(
        "secondary.TLabel",
        foreground="#64748b"
    )