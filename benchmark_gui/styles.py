"""
Theme and styling definitions for the LM Studio Benchmark GUI.
"""

# Theme colors based on Shadcn style
THEME_LIGHT = {
    "type": "light",
    "colors": {
        "primary": "#0f172a",       # Slate 900
        "secondary": "#f8fafc",     # Slate 50
        "success": "#10b981",       # Emerald 500
        "info": "#3b82f6",          # Blue 500
        "warning": "#f59e0b",       # Amber 500
        "danger": "#ef4444",        # Red 500
        "bg": "#ffffff",            # White
        "fg": "#0f172a",            # Slate 900
        "selectbg": "#e2e8f0",      # Slate 200
        "selectfg": "#0f172a",      # Slate 900
        "border": "#e2e8f0",        # Slate 200
        "inputfg": "#0f172a",       # Slate 900
        "inputbg": "#f8fafc"        # Slate 50
    }
}

THEME_DARK = {
    "type": "dark",
    "colors": {
        "primary": "#f8fafc",       # Slate 50
        "secondary": "#1e293b",     # Slate 800
        "success": "#10b981",       # Emerald 500
        "info": "#3b82f6",          # Blue 500
        "warning": "#f59e0b",       # Amber 500
        "danger": "#ef4444",        # Red 500
        "bg": "#0f172a",            # Slate 900
        "fg": "#f8fafc",            # Slate 50
        "selectbg": "#334155",      # Slate 700
        "selectfg": "#f8fafc",      # Slate 50
        "border": "#334155",        # Slate 700
        "inputfg": "#f8fafc",       # Slate 50
        "inputbg": "#1e293b"        # Slate 800
    }
}

def configure_styles(style):
    """Configure custom styles for widgets"""
    # Card styles
    style.configure("Card.TFrame", background=style.colors.secondary)
    style.configure("CardContent.TFrame", padding=10)
    
    # Text styles
    style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
    style.configure("Subtitle.TLabel", font=("Helvetica", 12))
    style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
    
    # Color-coded labels
    style.configure("Info.TLabel", foreground=style.colors.info)
    style.configure("Success.TLabel", foreground=style.colors.success)
    style.configure("Warning.TLabel", foreground=style.colors.warning)
    style.configure("Danger.TLabel", foreground=style.colors.danger)
    
    # Button styles
    style.configure("Primary.TButton", font=("Helvetica", 11))
    style.configure("Secondary.TButton", font=("Helvetica", 11))
    style.configure("Outline.TButton", font=("Helvetica", 11))
    
    # Separator style
    style.configure("Separator.TSeparator", background=style.colors.border)