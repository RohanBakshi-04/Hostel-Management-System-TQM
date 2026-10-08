"""Q05 Feature #3: Cached Dashboard View Component.

TQM Quality Goal: Q05 - Reduce Response Time.

Displays real-time hostel operational statistics with sub-millisecond
in-memory caching and reactive invalidation.
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, Any
from ..services.cache_service import DashboardCache
from .styles import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADER,
    FONT_METRIC_VALUE,
    FONT_METRIC_LABEL,
    FONT_SMALL,
    FONT_MONO,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


class DashboardView(ttk.Frame):
    """Executive Dashboard with Q05 Aggregate Caching."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct dashboard visual cards and controls."""
        # Main padding container
        main_pad = ttk.Frame(self)
        main_pad.pack(fill="both", expand=True, padx=25, pady=20)

        # Header Title + Refresh Action Bar
        top_bar = ttk.Frame(main_pad)
        top_bar.pack(fill="x", pady=(0, 15))

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")

        lbl_title = ttk.Label(title_box, text="System Overview & Analytics", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Real-time hostel management telemetry with Q05 in-memory response time caching",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        # Top Right: Cache Status Indicator + Refresh
        action_box = ttk.Frame(top_bar)
        action_box.pack(side="right")

        self.btn_refresh = ttk.Button(
            action_box,
            text="🔄 Force DB Recalculation",
            style="Secondary.TButton",
            command=lambda: self.load_metrics(force_refresh=True),
        )
        self.btn_refresh.pack(side="right", padx=(10, 0))

        # Latency & Cache Badge Card
        self.cache_card = tk.Frame(main_pad, bg="#EFF6FF", relief="solid", borderwidth=1, padx=12, pady=8)
        self.cache_card.pack(fill="x", pady=(0, 15))

        self.lbl_cache_status = tk.Label(
            self.cache_card,
            text="⚡ Q05 Cache Engine: Initializing...",
            font=FONT_MONO,
            bg="#EFF6FF",
            fg=COLOR_PRIMARY,
        )
        self.lbl_cache_status.pack(side="left")

        # Metric Cards Grid Frame
        self.cards_frame = ttk.Frame(main_pad)
        self.cards_frame.pack(fill="x", pady=5)
        for i in range(4):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="card")

        # Define 4 KPI Cards in Row 0
        self.card_students = self._create_card(self.cards_frame, 0, 0, "TOTAL STUDENTS", "0", COLOR_PRIMARY, "👨‍🎓")
        self.card_rooms = self._create_card(self.cards_frame, 0, 1, "TOTAL ROOMS", "0", "#0D9488", "🛏️")
        self.card_occupancy = self._create_card(self.cards_frame, 0, 2, "OCCUPANCY RATE", "0.0%", COLOR_SUCCESS, "📈")
        self.card_complaints = self._create_card(self.cards_frame, 0, 3, "PENDING ISSUES", "0", COLOR_WARNING, "⚠️")

        # Secondary Detailed Stats Grid in Row 1
        self.sec_frame = ttk.Frame(main_pad)
        self.sec_frame.pack(fill="x", pady=15)
        for i in range(3):
            self.sec_frame.grid_columnconfigure(i, weight=1, uniform="sec_card")

        self.card_beds = self._create_card_detail(
            self.sec_frame, 0, 0, "Bed Capacity Status", [("Occupied Beds:", "0"), ("Available Beds:", "0"), ("Total Beds:", "0")]
        )
        self.card_complaint_flow = self._create_card_detail(
            self.sec_frame, 0, 1, "Grievance Redressal Status", [("Pending:", "0"), ("In-Progress:", "0"), ("Resolved:", "0")]
        )
        self.card_quick_actions = self._create_quick_actions_card(self.sec_frame, 0, 2)

    def _create_card(
        self, parent: tk.Widget, row: int, col: int, label: str, init_val: str, color: str, icon: str
    ) -> Dict[str, Any]:
        """Create a prominent metric KPI card."""
        frame = tk.Frame(parent, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=16, pady=14)
        frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        top_f = tk.Frame(frame, bg=COLOR_CARD_BG)
        top_f.pack(fill="x")

        lbl_icon = tk.Label(top_f, text=icon, font=("Segoe UI", 16), bg=COLOR_CARD_BG)
        lbl_icon.pack(side="right")

        lbl_tag = tk.Label(top_f, text=label, font=FONT_METRIC_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG)
        lbl_tag.pack(side="left", anchor="w")

        lbl_value = tk.Label(frame, text=init_val, font=FONT_METRIC_VALUE, fg=color, bg=COLOR_CARD_BG)
        lbl_value.pack(anchor="w", pady=(8, 0))

        return {"frame": frame, "value": lbl_value}

    def _create_card_detail(
        self, parent: tk.Widget, row: int, col: int, title: str, items: list
    ) -> Dict[str, Any]:
        """Create a detailed multi-row metric card."""
        frame = tk.Frame(parent, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=16, pady=14)
        frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        lbl_title = tk.Label(frame, text=title, font=FONT_HEADER, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w", pady=(0, 10))

        val_labels = {}
        for item_lbl, init_val in items:
            row_f = tk.Frame(frame, bg=COLOR_CARD_BG)
            row_f.pack(fill="x", pady=3)

            lbl = tk.Label(row_f, text=item_lbl, font=FONT_SMALL, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD_BG)
            lbl.pack(side="left")

            val = tk.Label(row_f, text=init_val, font=("Segoe UI", 10, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG)
            val.pack(side="right")
            val_labels[item_lbl] = val

        return {"frame": frame, "labels": val_labels}

    def _create_quick_actions_card(self, parent: tk.Widget, row: int, col: int) -> Dict[str, Any]:
        """Create quick action shortcut panel."""
        frame = tk.Frame(parent, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=16, pady=14)
        frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        lbl_title = tk.Label(frame, text="⚡ Quick Shortcuts", font=FONT_HEADER, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD_BG)
        lbl_title.pack(anchor="w", pady=(0, 10))

        btn_grid = tk.Frame(frame, bg=COLOR_CARD_BG)
        btn_grid.pack(fill="both", expand=True)

        b1 = ttk.Button(btn_grid, text="➕ Add Student", style="Secondary.TButton", command=lambda: self.controller.navigate_to("students"))
        b1.pack(fill="x", pady=2)

        b2 = ttk.Button(btn_grid, text="📋 Allocate Bed", style="Secondary.TButton", command=lambda: self.controller.navigate_to("allocations"))
        b2.pack(fill="x", pady=2)

        b3 = ttk.Button(btn_grid, text="🛠️ Log Complaint", style="Secondary.TButton", command=lambda: self.controller.navigate_to("complaints"))
        b3.pack(fill="x", pady=2)

        return {"frame": frame}

    def on_view_active(self) -> None:
        """Called automatically by Quick Navigation when tab is selected."""
        self.load_metrics(force_refresh=False)

    def load_metrics(self, force_refresh: bool = False) -> None:
        """Fetch and render metrics through the Q05 Cache Engine."""
        metrics, is_hit, elapsed_ms = DashboardCache.get_dashboard_metrics(force_refresh=force_refresh)

        # Update KPI Cards
        self.card_students["value"].config(text=str(metrics.get("total_students", 0)))
        self.card_rooms["value"].config(text=str(metrics.get("total_rooms", 0)))
        self.card_occupancy["value"].config(text=f"{metrics.get('occupancy_rate', 0.0)}%")
        self.card_complaints["value"].config(text=str(metrics.get("pending_complaints", 0)))

        # Update Detailed Breakdown
        beds_lbls = self.card_beds["labels"]
        beds_lbls["Occupied Beds:"].config(text=str(metrics.get("occupied_beds", 0)))
        beds_lbls["Available Beds:"].config(text=str(metrics.get("available_beds", 0)))
        beds_lbls["Total Beds:"].config(text=str(metrics.get("total_capacity", 0)))

        comp_lbls = self.card_complaint_flow["labels"]
        comp_lbls["Pending:"].config(text=str(metrics.get("pending_complaints", 0)))
        comp_lbls["In-Progress:"].config(text=str(metrics.get("inprogress_complaints", 0)))
        comp_lbls["Resolved:"].config(text=str(metrics.get("resolved_complaints", 0)))

        # Update Cache Status Banner
        stats = DashboardCache.get_stats()
        if is_hit:
            status_text = (
                f"⚡ Q05 CACHE HIT: In-Memory snapshot loaded in {elapsed_ms:.2f} ms | "
                f"Total Hits: {stats['hits']} | Avoided DB queries: 8"
            )
            self.cache_card.config(bg="#F0FDF4")
            self.lbl_cache_status.config(text=status_text, bg="#F0FDF4", fg=COLOR_SUCCESS)
        else:
            status_text = (
                f"🔄 Q05 CACHE MISS / REFRESH: Recalculated from SQLite in {elapsed_ms:.2f} ms | "
                f"Cache repopulated"
            )
            self.cache_card.config(bg="#FFFBEB")
            self.lbl_cache_status.config(text=status_text, bg="#FFFBEB", fg=COLOR_WARNING)
