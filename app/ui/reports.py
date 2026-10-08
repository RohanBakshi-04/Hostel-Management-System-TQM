"""Q05 Feature #5: Paginated Reports View Component.

TQM Quality Goal: Q05 - Reduce Response Time.

Technical Optimization Strategy:
Renders large institutional datasets using server/database-side SQL LIMIT/OFFSET
pagination, preventing UI freezes and unbounded RAM growth.
"""

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, Any, List
from ..services.report_service import PaginatedReportService
from ..utils.helpers import LatencyTimer, format_currency, format_timestamp
from .styles import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADER,
    FONT_BODY_BOLD,
    FONT_MONO,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


class ReportView(ttk.Frame):
    """Paginated Master Audit & Reports Interface."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller
        self.report_service = PaginatedReportService()

        self.current_page = 1
        self.page_size = 10
        self.total_pages = 1
        self.total_records = 0
        self.active_report = "Allocations"

        self._build_ui()

    def _build_ui(self) -> None:
        main_pad = ttk.Frame(self)
        main_pad.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Header Bar
        top_bar = ttk.Frame(main_pad)
        top_bar.pack(fill="x", pady=(0, 15))

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")

        lbl_title = ttk.Label(title_box, text="Paginated Audit Reports", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Q05 Database-driven SQL LIMIT/OFFSET pagination for ultra-low latency record inspection",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        # 2. Report Selector & Config Card
        cfg_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=10)
        cfg_card.pack(fill="x", pady=(0, 12))

        lbl_rep = tk.Label(cfg_card, text="Select Report:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_rep.pack(side="left", padx=(0, 8))

        self.rep_var = tk.StringVar(value="Allocations")
        cb_rep = ttk.Combobox(
            cfg_card,
            textvariable=self.rep_var,
            values=["Allocations", "Students", "Complaints"],
            state="readonly",
            width=18,
        )
        cb_rep.pack(side="left", padx=(0, 20))
        cb_rep.bind("<<ComboboxSelected>>", self._on_report_type_changed)

        lbl_size = tk.Label(cfg_card, text="Rows Per Page:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_size.pack(side="left", padx=(0, 8))

        self.size_var = tk.StringVar(value="10")
        cb_size = ttk.Combobox(
            cfg_card,
            textvariable=self.size_var,
            values=["5", "10", "20", "50"],
            state="readonly",
            width=8,
        )
        cb_size.pack(side="left")
        cb_size.bind("<<ComboboxSelected>>", self._on_page_size_changed)

        self.lbl_latency = tk.Label(
            cfg_card,
            text="⚡ Q05 Limit/Offset Latency: Ready",
            font=FONT_MONO,
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
        )
        self.lbl_latency.pack(side="right")

        # 3. Table Container
        self.table_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1)
        self.table_card.pack(fill="both", expand=True, pady=(0, 10))

        self.tree = ttk.Treeview(self.table_card, show="headings", selectmode="browse")
        self.scrollbar = ttk.Scrollbar(self.table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        self.scrollbar.pack(side="right", fill="y", pady=2)

        # 4. Pagination Controls Bar
        pag_bar = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=8)
        pag_bar.pack(fill="x")

        self.btn_first = ttk.Button(pag_bar, text="⏮ First", style="Secondary.TButton", width=8, command=self._go_first)
        self.btn_first.pack(side="left", padx=3)

        self.btn_prev = ttk.Button(pag_bar, text="◀ Prev", style="Secondary.TButton", width=8, command=self._go_prev)
        self.btn_prev.pack(side="left", padx=3)

        self.lbl_page_info = tk.Label(
            pag_bar,
            text="Page 1 of 1 (Total: 0 records)",
            font=FONT_BODY_BOLD,
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
            padx=15,
        )
        self.lbl_page_info.pack(side="left")

        self.btn_next = ttk.Button(pag_bar, text="Next ▶", style="Secondary.TButton", width=8, command=self._go_next)
        self.btn_next.pack(side="left", padx=3)

        self.btn_last = ttk.Button(pag_bar, text="Last ⏭", style="Secondary.TButton", width=8, command=self._go_last)
        self.btn_last.pack(side="left", padx=3)

        self.lbl_mem_note = tk.Label(
            pag_bar,
            text="Memory Profile: O(1) constant memory (page sliced in SQLite)",
            font=("Segoe UI", 9, "italic"),
            bg=COLOR_CARD_BG,
            fg="#64748B",
        )
        self.lbl_mem_note.pack(side="right")

    def on_view_active(self) -> None:
        self.load_report_page()

    def _on_report_type_changed(self, event=None) -> None:
        self.active_report = self.rep_var.get()
        self.current_page = 1
        self._configure_tree_columns()
        self.load_report_page()

    def _on_page_size_changed(self, event=None) -> None:
        try:
            self.page_size = int(self.size_var.get())
        except ValueError:
            self.page_size = 10
        self.current_page = 1
        self.load_report_page()

    def _configure_tree_columns(self) -> None:
        """Dynamically configure Treeview headers for selected report type."""
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")

        if self.active_report == "Allocations":
            cols = ("id", "student_reg_no", "student_name", "student_branch", "room_number", "room_block", "room_type", "base_fee", "allocation_date", "fee_status", "allocation_status")
            self.tree["columns"] = cols
            self.tree.heading("id", text="Alloc ID")
            self.tree.heading("student_reg_no", text="Student Roll No")
            self.tree.heading("student_name", text="Name")
            self.tree.heading("student_branch", text="Branch")
            self.tree.heading("room_number", text="Room")
            self.tree.heading("room_block", text="Block")
            self.tree.heading("room_type", text="Room Type")
            self.tree.heading("base_fee", text="Fee")
            self.tree.heading("allocation_date", text="Date")
            self.tree.heading("fee_status", text="Payment")
            self.tree.heading("allocation_status", text="Status")

            self.tree.column("id", width=60, anchor="center")
            self.tree.column("student_reg_no", width=120, anchor="center")
            self.tree.column("student_name", width=150, anchor="w")
            self.tree.column("student_branch", width=80, anchor="center")
            self.tree.column("room_number", width=80, anchor="center")
            self.tree.column("room_block", width=90, anchor="center")
            self.tree.column("room_type", width=100, anchor="center")
            self.tree.column("base_fee", width=100, anchor="center")
            self.tree.column("allocation_date", width=100, anchor="center")
            self.tree.column("fee_status", width=90, anchor="center")
            self.tree.column("allocation_status", width=90, anchor="center")

        elif self.active_report == "Students":
            cols = ("id", "student_id", "name", "email", "phone", "gender", "branch", "year", "guardian_phone")
            self.tree["columns"] = cols
            self.tree.heading("id", text="PK ID")
            self.tree.heading("student_id", text="Student ID")
            self.tree.heading("name", text="Full Name")
            self.tree.heading("email", text="Email")
            self.tree.heading("phone", text="Phone")
            self.tree.heading("gender", text="Gender")
            self.tree.heading("branch", text="Branch")
            self.tree.heading("year", text="Year")
            self.tree.heading("guardian_phone", text="Guardian Phone")

            for c in cols:
                self.tree.column(c, width=110, anchor="center" if c not in ["name", "email"] else "w")

        elif self.active_report == "Complaints":
            cols = ("complaint_id", "student_reg_no", "student_name", "room_number", "category", "severity", "status", "created_at", "resolved_at")
            self.tree["columns"] = cols
            self.tree.heading("complaint_id", text="Ticket ID")
            self.tree.heading("student_reg_no", text="Student Roll No")
            self.tree.heading("student_name", text="Student Name")
            self.tree.heading("room_number", text="Room")
            self.tree.heading("category", text="Category")
            self.tree.heading("severity", text="Priority")
            self.tree.heading("status", text="Status")
            self.tree.heading("created_at", text="Filed On")
            self.tree.heading("resolved_at", text="Resolved On")

            for c in cols:
                self.tree.column(c, width=110, anchor="center" if c != "student_name" else "w")

    def load_report_page(self) -> None:
        """Fetch strictly the active page slice from database."""
        self._configure_tree_columns()

        if self.active_report == "Allocations":
            data, elapsed_ms = self.report_service.get_paginated_allocations(self.current_page, self.page_size)
        elif self.active_report == "Students":
            data, elapsed_ms = self.report_service.get_paginated_students(self.current_page, self.page_size)
        else:
            data, elapsed_ms = self.report_service.get_paginated_complaints(self.current_page, self.page_size)

        self.current_page = data["current_page"]
        self.total_pages = data["total_pages"]
        self.total_records = data["total_records"]
        records = data["records"]

        # Populate tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in records:
            if self.active_report == "Allocations":
                vals = (
                    r["id"],
                    r["student_reg_no"],
                    r["student_name"],
                    r["student_branch"],
                    r["room_number"],
                    r["room_block"],
                    r["room_type"],
                    format_currency(r["base_fee"]),
                    r["allocation_date"],
                    r["fee_status"],
                    r["allocation_status"],
                )
            elif self.active_report == "Students":
                vals = (
                    r["id"],
                    r["student_id"],
                    r["name"],
                    r["email"],
                    r["phone"],
                    r["gender"],
                    r["branch"],
                    r["year"],
                    r["guardian_phone"],
                )
            else:
                vals = (
                    r["complaint_id"],
                    r["student_reg_no"],
                    r["student_name"],
                    r["room_number"],
                    r["category"],
                    r["severity"],
                    r["status"],
                    format_timestamp(r["created_at"]),
                    format_timestamp(r["resolved_at"]),
                )
            self.tree.insert("", "end", values=vals)

        # Update controls state
        self.lbl_page_info.config(
            text=f"Page {self.current_page} of {self.total_pages} (Total: {self.total_records} records)"
        )
        self.lbl_latency.config(
            text=f"⚡ Page Sliced in {elapsed_ms:.2f} ms ({len(records)} rows)",
            fg=COLOR_SUCCESS,
        )

        self.btn_first.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < self.total_pages else "disabled")
        self.btn_last.config(state="normal" if self.current_page < self.total_pages else "disabled")

    def _go_first(self) -> None:
        self.current_page = 1
        self.load_report_page()

    def _go_prev(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.load_report_page()

    def _go_next(self) -> None:
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_report_page()

    def _go_last(self) -> None:
        self.current_page = self.total_pages
        self.load_report_page()
