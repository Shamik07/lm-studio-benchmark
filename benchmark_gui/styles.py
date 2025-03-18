"""
Theme and styling definitions for the LM Studio Benchmark GUI.
Modern aesthetic inspired by shadcn and Buridan UI.
"""

# Modern shadcn-inspired theme colors
THEME_LIGHT = {
    "type": "light",
    "colors": {
        "primary": "#0f172a",       # Slate 900
        "primary_hover": "#1e293b", # Slate 800
        "secondary": "#f8fafc",     # Slate 50
        "success": "#10b981",       # Emerald 500
        "success_hover": "#059669", # Emerald 600
        "info": "#3b82f6",          # Blue 500
        "info_hover": "#2563eb",    # Blue 600
        "warning": "#f59e0b",       # Amber 500
        "warning_hover": "#d97706", # Amber 600
        "danger": "#ef4444",        # Red 500
        "danger_hover": "#dc2626",  # Red 600
        "bg": "#ffffff",            # White
        "card": "#f8fafc",          # Slate 50
        "card_hover": "#f1f5f9",    # Slate 100
        "fg": "#0f172a",            # Slate 900
        "fg_muted": "#64748b",      # Slate 500
        "border": "#e2e8f0",        # Slate 200
        "border_focus": "#94a3b8",  # Slate 400
        "input_bg": "#ffffff",      # White
        "input_fg": "#0f172a",      # Slate 900
        "input_placeholder": "#94a3b8", # Slate 400
        "ring": "rgba(59, 130, 246, 0.5)" # Blue 500 with alpha
    }
}

THEME_DARK = {
    "type": "dark",
    "colors": {
        "primary": "#f8fafc",       # Slate 50
        "primary_hover": "#e2e8f0", # Slate 200
        "secondary": "#1e293b",     # Slate 800
        "success": "#10b981",       # Emerald 500
        "success_hover": "#059669", # Emerald 600
        "info": "#3b82f6",          # Blue 500
        "info_hover": "#2563eb",    # Blue 600
        "warning": "#f59e0b",       # Amber 500
        "warning_hover": "#d97706", # Amber 600
        "danger": "#ef4444",        # Red 500
        "danger_hover": "#dc2626",  # Red 600
        "bg": "#0f172a",            # Slate 900
        "card": "#1e293b",          # Slate 800
        "card_hover": "#334155",    # Slate 700
        "fg": "#f8fafc",            # Slate 50
        "fg_muted": "#94a3b8",      # Slate 400
        "border": "#334155",        # Slate 700
        "border_focus": "#64748b",  # Slate 500
        "input_bg": "#1e293b",      # Slate 800
        "input_fg": "#f8fafc",      # Slate 50
        "input_placeholder": "#64748b", # Slate 500
        "ring": "rgba(59, 130, 246, 0.5)" # Blue 500 with alpha
    }
}

def configure_styles(style):
    """Configure custom styles for widgets"""
    colors = style.colors
    
    # General padding and margins
    PADDING = 16  # Base padding

    # Card styles
    style.configure("Card.TFrame", background=colors.card, borderwidth=1, 
                   relief="solid", bordercolor=colors.border)
    
    # Make card content have proper spacing
    style.configure("CardContent.TFrame", background=colors.card, 
                   padding=(PADDING, PADDING, PADDING, PADDING))
    
    # Modern typography
    style.configure("TLabel", font=("Inter", 11))
    style.configure("Title.TLabel", font=("Inter", 20, "bold"), 
                   foreground=colors.fg)
    style.configure("Subtitle.TLabel", font=("Inter", 14), 
                   foreground=colors.fg_muted)
    style.configure("Header.TLabel", font=("Inter", 16, "bold"), 
                   foreground=colors.fg)
    
    # Color-coded labels with modern styling
    style.configure("Info.TLabel", foreground=colors.info, font=("Inter", 11))
    style.configure("Success.TLabel", foreground=colors.success, font=("Inter", 11))
    style.configure("Warning.TLabel", foreground=colors.warning, font=("Inter", 11))
    style.configure("Danger.TLabel", foreground=colors.danger, font=("Inter", 11))
    
    # Modern button styles
    style.configure("TButton", font=("Inter", 11), padding=(PADDING, 8))
    
    # Primary button - more padding, rounded corners
    style.configure("success.TButton", 
                   background=colors.success,
                   foreground="#ffffff",
                   borderwidth=0,
                   focusthickness=0,
                   padding=(PADDING, 8))
    style.map("success.TButton",
             background=[('pressed', colors.success_hover), 
                         ('active', colors.success_hover)])
    
    # Secondary button
    style.configure("secondary.TButton", 
                   background=colors.secondary,
                   foreground=colors.fg,
                   borderwidth=1,
                   bordercolor=colors.border,
                   focusthickness=0,
                   padding=(PADDING, 8))
    style.map("secondary.TButton",
             background=[('pressed', colors.card_hover), 
                         ('active', colors.card_hover)])
    
    # Danger button
    style.configure("danger.TButton", 
                   background=colors.danger,
                   foreground="#ffffff",
                   borderwidth=0,
                   focusthickness=0,
                   padding=(PADDING, 8))
    style.map("danger.TButton",
             background=[('pressed', colors.danger_hover), 
                         ('active', colors.danger_hover)])
             
    # Separator style
    style.configure("TSeparator", background=colors.border)
    
    # Progress bar - thicker, rounded
    style.configure("Horizontal.TProgressbar", 
                   background=colors.info,
                   troughcolor=colors.card,
                   borderwidth=0,
                   thickness=8)
    
    # Entry fields
    style.configure("TEntry",
                   fieldbackground=colors.input_bg,
                   foreground=colors.input_fg,
                   bordercolor=colors.border,
                   lightcolor=colors.border,
                   darkcolor=colors.border,
                   insertcolor=colors.fg,
                   padding=(PADDING//2, 6))
    style.map("TEntry",
             bordercolor=[('focus', colors.border_focus)])
             
    # Combobox styling
    style.configure("TCombobox",
                   fieldbackground=colors.input_bg,
                   foreground=colors.input_fg,
                   selectbackground=colors.primary,
                   selectforeground=colors.bg,
                   bordercolor=colors.border,
                   arrowcolor=colors.fg,
                   padding=(PADDING//2, 6))
    
    # Treeview (for tables) styling
    style.configure("Treeview", 
                   fieldbackground=colors.bg,
                   background=colors.bg,
                   foreground=colors.fg,
                   bordercolor=colors.border,
                   padding=(PADDING//4, 4))
    style.configure("Treeview.Heading", 
                   font=("Inter", 10, "bold"),
                   background=colors.card,
                   foreground=colors.fg,
                   padding=(PADDING//2, 6))
    style.map("Treeview", 
             background=[('selected', colors.info)],
             foreground=[('selected', "#ffffff")])
             
    # Notebook tab styling
    style.configure("TNotebook", 
                   background=colors.bg,
                   borderwidth=0)
    style.configure("TNotebook.Tab", 
                   background=colors.bg,
                   foreground=colors.fg_muted,
                   bordercolor=colors.border,
                   padding=(PADDING, 8),
                   font=("Inter", 11))
    style.map("TNotebook.Tab", 
             background=[('selected', colors.bg)],
             foreground=[('selected', colors.fg)],
             bordercolor=[('selected', colors.info)])
             
    # Checkbutton styling
    style.configure("TCheckbutton", 
                   background=colors.bg,
                   foreground=colors.fg,
                   indicatorcolor=colors.card,
                   indicatorbackground=colors.card,
                   padding=(0, 2))
    style.map("TCheckbutton",
             indicatorcolor=[('selected', colors.info)])
             
    # Radiobutton styling
    style.configure("TRadiobutton", 
                   background=colors.bg,
                   foreground=colors.fg,
                   indicatorcolor=colors.card,
                   indicatorbackground=colors.card,
                   padding=(0, 2))
    style.map("TRadiobutton",
             indicatorcolor=[('selected', colors.info)])
             
    # Scrollbar styling - thinner, modern look
    style.configure("TScrollbar", 
                   background=colors.bg,
                   troughcolor=colors.bg,
                   bordercolor=colors.bg,
                   arrowcolor=colors.fg_muted,
                   width=10)
    style.map("TScrollbar",
             background=[('pressed', colors.card_hover), 
                         ('active', colors.card_hover)])