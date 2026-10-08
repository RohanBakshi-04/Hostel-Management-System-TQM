"""Q05 Feature #2: Quick Navigation Shell and Main Window Controller.

TQM Quality Goal: Q05 - Reduce Response Time.

Technical Optimization Strategy:
Instead of creating and destroying new Toplevel windows or rebuilding frames
on every tab click, the `MainWindow` pre-instantiates all core views at launch:
- DashboardView
- StudentView
- RoomView
- AllocationView
- ComplaintView
- ReportView

Switching between modules happens in-memory with zero overhead via `tkraise()`,
achieving sub-millisecond tab navigation transitions without UI redraw lag or memory leaks.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from .styles import (
    apply_theme_styles,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_BG,
    COLOR_CARD_BG,
    FONT_SUBTITLE,
    FONT_SMALL,
    FONT_HEADER,
)
from ..utils.helpers import LatencyTimer


class MainWindow(tk.Tk):
    """Main Application Window with Persistent Quick Navigation Sidebar."""

    def __init__(self):
        super().__init__()
        self.title("Hostel Management System (HMS) - TQM Quality Engineering [Q05: Reduce Response Time]")
        self.geometry("1180x740")
        self.minsize(1000, 650)
        self.configure(bg=COLOR_BG)

        # Apply styles
        apply_theme_styles(self)

        # Container for views
        self.views: Dict[str, ttk.Frame] = {}
        self.nav_buttons: Dict[str, tk.Button] = {}
        self.active_view_name: Optional[str] = None

        self._build_layout()
        self._initialize_views()
        self.navigate_to("dashboard")

    def _build_layout(self) -> None:
        """Construct the persistent two-column layout: Sidebar + Content Area."""
        # Top Header Bar
        self.header_frame = tk.Frame(self, bg=COLOR_PRIMARY, height=45)
        self.header_frame.pack(side="top", fill="x")

        title_lbl = tk.Label(
            self.header_frame,
            text="🏨 HOSTEL MANAGEMENT SYSTEM",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
        )
        title_lbl.pack(side="left", padx=15, pady=8)

        student_tag = tk.Label(
            self.header_frame,
            text="Student: Rohan Bakshi (2410301057) | Goal: Q05 Reduce Response Time",
            font=("Segoe UI", 9, "italic"),
            bg=COLOR_PRIMARY,
            fg="#E0E7FF",
        )
        student_tag.pack(side="right", padx=15, pady=8)

        # Main Workspace (Sidebar + Dynamic Container)
        self.workspace_frame = ttk.Frame(self)
        self.workspace_frame.pack(side="top", fill="both", expand=True)

        # Left Sidebar (Q05 Quick Navigation)
        self.sidebar_frame = tk.Frame(self.workspace_frame, bg=COLOR_SECONDARY, width=220)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Sidebar Header
        sb_head = tk.Label(
            self.sidebar_frame,
            text="QUICK NAVIGATION",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_SECONDARY,
            fg="#94A3B8",
        )
        sb_head.pack(anchor="w", padx=16, pady=(16, 10))

        # Nav Items
        nav_items = [
            ("dashboard", "🏠  Dashboard"),
            ("students", "👨‍🎓  Students"),
            ("rooms", "🛏️  Rooms"),
            ("allocations", "📋  Allocations"),
            ("complaints", "🛠️  Complaints"),
            ("reports", "📊  Paginated Reports"),
        ]

        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar_frame,
                text=label,
                font=("Segoe UI", 10),
                bg=COLOR_SECONDARY,
                fg="#F8FAFC",
                activebackground="#1E293B",
                activeforeground="#FFFFFF",
                bd=0,
                anchor="w",
                padx=16,
                pady=10,
                cursor="hand2",
                command=lambda k=key: self.navigate_to(k),
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # Bottom System Info in Sidebar
        sb_bottom = tk.Frame(self.sidebar_frame, bg=COLOR_SECONDARY)
        sb_bottom.pack(side="bottom", fill="x", padx=12, pady=16)

        ver_lbl = tk.Label(
            sb_bottom,
            text="TQM Baseline v1.0\nSQLite + Q05 Engine",
            font=("Segoe UI", 8),
            bg=COLOR_SECONDARY,
            fg="#64748B",
            justify="left",
        )
        ver_lbl.pack(anchor="w")

        # Right Content Viewport
        self.content_container = ttk.Frame(self.workspace_frame)
        self.content_container.pack(side="right", fill="both", expand=True)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Status / Latency Bar
        self.status_bar = tk.Frame(self, bg="#E2E8F0", height=24)
        self.status_bar.pack(side="bottom", fill="x")

        self.status_msg = tk.Label(
            self.status_bar,
            text="System Ready | Quality Goal Q05 Active",
            font=("Segoe UI", 8),
            bg="#E2E8F0",
            fg="#334155",
        )
        self.status_msg.pack(side="left", padx=10, pady=2)

        self.latency_lbl = tk.Label(
            self.status_bar,
            text="Q05 Navigation Latency: 0.00 ms",
            font=("Consolas", 8, "bold"),
            bg="#E2E8F0",
            fg=COLOR_PRIMARY,
        )
        self.latency_lbl.pack(side="right", padx=10, pady=2)

    def _initialize_views(self) -> None:
        """Pre-instantiate all view frames in-memory to enable instant navigation."""
        from .dashboard import DashboardView
        from .students import StudentView
        from .rooms import RoomView
        from .allocations import AllocationView
        from .complaints import ComplaintView
        from .reports import ReportView

        self.views["dashboard"] = DashboardView(self.content_container, self)
        self.views["students"] = StudentView(self.content_container, self)
        self.views["rooms"] = RoomView(self.content_container, self)
        self.views["allocations"] = AllocationView(self.content_container, self)
        self.views["complaints"] = ComplaintView(self.content_container, self)
        self.views["reports"] = ReportView(self.content_container, self)

        # Grid all views into same viewport cell for instantaneous tkraise
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def navigate_to(self, view_name: str) -> None:
        """Q05 Quick Navigation: Switch views in-memory with sub-millisecond latency."""
        if view_name not in self.views:
            return

        timer = LatencyTimer()
        timer.start()

        # Update button highlights
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.configure(bg=COLOR_PRIMARY, fg="#FFFFFF", font=("Segoe UI", 10, "bold"))
            else:
                btn.configure(bg=COLOR_SECONDARY, fg="#F8FAFC", font=("Segoe UI", 10))

        # Raise frame to top
        view = self.views[view_name]
        view.tkraise()
        self.active_view_name = view_name

        # Trigger view-specific data refresh if available
        if hasattr(view, "on_view_active"):
            view.on_view_active()

        elapsed_ms = timer.stop()
        self.latency_lbl.config(
            text=f"Q05 Quick Navigation: Switched to '{view_name}' in {elapsed_ms:.2f} ms"
        )

    def set_status(self, message: str) -> None:
        """Update the global status bar message."""
        self.status_msg.config(text=message)
