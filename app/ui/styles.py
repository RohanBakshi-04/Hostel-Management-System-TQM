"""UI Theme and Style Definitions.

Provides a clean, professional, high-contrast desktop aesthetic using standard Tkinter TTK.
"""

import tkinter as tk
from tkinter import ttk

# Color Palette (Modern Slate Blue & Clean Neutral Whites/Grays)
COLOR_PRIMARY = "#1E40AF"       # Deep Blue
COLOR_PRIMARY_HOVER = "#1D4ED8" # Hover Blue
COLOR_SECONDARY = "#0F172A"     # Dark Slate (Sidebar)
COLOR_ACCENT = "#0284C7"        # Sky Blue Accent
COLOR_SUCCESS = "#059669"       # Emerald Green
COLOR_WARNING = "#D97706"       # Amber
COLOR_DANGER = "#DC2626"        # Rose Red
COLOR_BG = "#F1F5F9"            # Clean Slate Light Background
COLOR_CARD_BG = "#FFFFFF"       # White Card
COLOR_TEXT_MAIN = "#0F172A"     # Dark Charcoal
COLOR_TEXT_MUTED = "#64748B"    # Slate Gray
COLOR_BORDER = "#CBD5E1"        # Light Border

# Font Definitions
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 13, "bold")
FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_METRIC_VALUE = ("Segoe UI", 24, "bold")
FONT_METRIC_LABEL = ("Segoe UI", 10, "bold")


def apply_theme_styles(root: tk.Tk) -> None:
    """Apply global TTK styling configuration."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Global TTK defaults
    style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT_MAIN, font=FONT_BODY)

    # Frame backgrounds
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD_BG, relief="solid", borderwidth=1)
    style.configure("Sidebar.TFrame", background=COLOR_SECONDARY)

    # Label styles
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MAIN, font=FONT_BODY)
    style.configure("Card.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MAIN, font=FONT_BODY)
    style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_PRIMARY, font=FONT_TITLE)
    style.configure("Subtitle.TLabel", background=COLOR_BG, foreground=COLOR_SECONDARY, font=FONT_SUBTITLE)
    style.configure("Muted.TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MUTED, font=FONT_SMALL)
    style.configure("CardMuted.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MUTED, font=FONT_SMALL)

    # Metric Card specific styles
    style.configure("MetricVal.TLabel", background=COLOR_CARD_BG, foreground=COLOR_PRIMARY, font=FONT_METRIC_VALUE)
    style.configure("MetricLbl.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MUTED, font=FONT_METRIC_LABEL)

    # Button styles
    style.configure(
        "Primary.TButton",
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=6,
    )
    style.map("Primary.TButton", background=[("active", COLOR_PRIMARY_HOVER)])

    style.configure(
        "Success.TButton",
        background=COLOR_SUCCESS,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=6,
    )
    style.map("Success.TButton", background=[("active", "#047857")])

    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        borderwidth=0,
        padding=6,
    )
    style.map("Danger.TButton", background=[("active", "#B91C1C")])

    style.configure(
        "Secondary.TButton",
        background="#E2E8F0",
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY,
        borderwidth=0,
        padding=6,
    )
    style.map("Secondary.TButton", background=[("active", "#CBD5E1")])

    # Sidebar Navigation Button Style
    style.configure(
        "Nav.TButton",
        background=COLOR_SECONDARY,
        foreground="#E2E8F0",
        font=("Segoe UI", 11),
        anchor="w",
        padding=10,
        borderwidth=0,
    )
    style.map(
        "Nav.TButton",
        background=[("active", "#1E293B"), ("selected", COLOR_PRIMARY)],
        foreground=[("active", "#FFFFFF"), ("selected", "#FFFFFF")],
    )

    # Treeview (Data Tables)
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        rowheight=28,
        fieldbackground="#FFFFFF",
        font=FONT_BODY,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground=COLOR_TEXT_MAIN,
        font=FONT_HEADER,
        padding=6,
    )
    style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", "#1E3A8A")])

    # Entry & Combobox
    style.configure("TEntry", fieldbackground="#FFFFFF", padding=5)
    style.configure("TCombobox", fieldbackground="#FFFFFF", padding=5)
