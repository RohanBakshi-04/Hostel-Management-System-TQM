"""Complaint Management View Component with Resolution Workflow.

TQM Quality Goal: Q05 - Reduce Response Time.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional, List
from ..models.complaint import Complaint
from ..services.complaint_service import ComplaintService
from ..services.student_service import StudentService
from ..services.room_service import RoomService
from ..services.search_service import FastSearchService
from ..utils.helpers import LatencyTimer, format_timestamp
from .styles import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADER,
    FONT_BODY_BOLD,
    FONT_MONO,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


class ComplaintView(ttk.Frame):
    """Grievance Redressal and Maintenance Ticketing Interface."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller
        self.complaint_service = ComplaintService()
        self.student_service = StudentService()
        self.room_service = RoomService()
        self.search_service = FastSearchService()

        self._build_ui()

    def _build_ui(self) -> None:
        main_pad = ttk.Frame(self)
        main_pad.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Header Bar
        top_bar = ttk.Frame(main_pad)
        top_bar.pack(fill="x", pady=(0, 15))

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")

        lbl_title = ttk.Label(title_box, text="Complaint & Grievance Redressal", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Log maintenance tickets, advance resolution lifecycle, and execute Q05 fast searches",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        btn_box = ttk.Frame(top_bar)
        btn_box.pack(side="right")

        btn_add = ttk.Button(
            btn_box,
            text="➕ Log Complaint",
            style="Primary.TButton",
            command=self._open_create_dialog,
        )
        btn_add.pack(side="left", padx=5)

        btn_refresh = ttk.Button(
            btn_box,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self.load_complaints,
        )
        btn_refresh.pack(side="left", padx=5)

        # 2. Search & Filter Bar
        search_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=10)
        search_card.pack(fill="x", pady=(0, 12))

        lbl_search = tk.Label(search_card, text="🔍 Fast Search:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_search.pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(search_card, textvariable=self.search_var, width=24)
        self.entry_search.pack(side="left", padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.perform_search())

        ttk.Button(search_card, text="Search", style="Primary.TButton", command=self.perform_search).pack(side="left", padx=4)
        ttk.Button(search_card, text="Clear", style="Secondary.TButton", command=self._clear_search).pack(side="left", padx=4)

        # Status Filter Combobox
        lbl_filter = tk.Label(search_card, text="Filter:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_filter.pack(side="left", padx=(15, 6))

        self.filter_var = tk.StringVar(value="All")
        cb_filter = ttk.Combobox(
            search_card,
            textvariable=self.filter_var,
            values=["All", "Pending", "In-Progress", "Resolved", "Closed"],
            state="readonly",
            width=14,
        )
        cb_filter.pack(side="left")
        cb_filter.bind("<<ComboboxSelected>>", lambda e: self.load_complaints())

        self.lbl_search_latency = tk.Label(
            search_card,
            text="Q05 Query Latency: Ready",
            font=FONT_MONO,
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
        )
        self.lbl_search_latency.pack(side="right")

        # 3. Complaints Table
        table_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1)
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        columns = (
            "complaint_id",
            "student_reg_no",
            "student_name",
            "room_number",
            "category",
            "severity",
            "status",
            "description",
            "resolution_notes",
            "created_at",
        )
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("complaint_id", text="Ticket ID")
        self.tree.heading("student_reg_no", text="Student Roll No")
        self.tree.heading("student_name", text="Student Name")
        self.tree.heading("room_number", text="Room")
        self.tree.heading("category", text="Category")
        self.tree.heading("severity", text="Priority")
        self.tree.heading("status", text="Current Status")
        self.tree.heading("description", text="Issue Description")
        self.tree.heading("resolution_notes", text="Resolution Action")
        self.tree.heading("created_at", text="Date Logged")

        self.tree.column("complaint_id", width=100, anchor="center")
        self.tree.column("student_reg_no", width=120, anchor="center")
        self.tree.column("student_name", width=140, anchor="w")
        self.tree.column("room_number", width=80, anchor="center")
        self.tree.column("category", width=110, anchor="center")
        self.tree.column("severity", width=90, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("description", width=220, anchor="w")
        self.tree.column("resolution_notes", width=200, anchor="w")
        self.tree.column("created_at", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

        # Action Bar
        action_bar = ttk.Frame(main_pad)
        action_bar.pack(fill="x")

        btn_action = ttk.Button(
            action_bar,
            text="⚡ Resolve / Update Ticket",
            style="Primary.TButton",
            command=self._open_update_dialog,
        )
        btn_action.pack(side="left", padx=(0, 8))

        btn_del = ttk.Button(
            action_bar,
            text="🗑️ Delete Ticket",
            style="Danger.TButton",
            command=self._delete_selected,
        )
        btn_del.pack(side="left", padx=8)

        self.lbl_record_count = ttk.Label(action_bar, text="Total Complaints: 0", style="Muted.TLabel")
        self.lbl_record_count.pack(side="right")

    def on_view_active(self) -> None:
        self.load_complaints()

    def load_complaints(self) -> None:
        """Fetch and populate complaints."""
        timer = LatencyTimer()
        timer.start()

        filter_val = self.filter_var.get()
        complaints = self.complaint_service.get_all_complaints(status_filter=filter_val)
        elapsed_ms = timer.stop()

        self._populate_tree(complaints)
        self.lbl_search_latency.config(
            text=f"Loaded {len(complaints)} complaints in {elapsed_ms:.2f} ms",
            fg=COLOR_SUCCESS,
        )

    def _populate_tree(self, complaints: List[Complaint]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in complaints:
            self.tree.insert(
                "",
                "end",
                iid=c.complaint_id,
                values=(
                    c.complaint_id,
                    c.student_reg_no,
                    c.student_name,
                    c.room_number,
                    c.category,
                    c.severity,
                    c.status,
                    c.description,
                    c.resolution_notes or "-",
                    format_timestamp(c.created_at),
                ),
            )

        self.lbl_record_count.config(text=f"Total: {len(complaints)} tickets")

    def perform_search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            self.load_complaints()
            return

        results, elapsed_ms = self.search_service.search_complaints(query)
        self._populate_tree(results)
        self.lbl_search_latency.config(
            text=f"⚡ Q05 Fast Search: {len(results)} matches in {elapsed_ms:.2f} ms",
            fg=COLOR_PRIMARY,
        )

    def _clear_search(self) -> None:
        self.search_var.set("")
        self.load_complaints()

    def _get_selected_complaint_id(self) -> Optional[str]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a complaint ticket from the table.")
            return None
        return str(selected[0])

    def _open_create_dialog(self) -> None:
        students = self.student_service.get_all_students()
        rooms = self.room_service.get_all_rooms()

        if not students or not rooms:
            messagebox.showwarning("Prerequisites Missing", "Students and Rooms must exist before registering complaints.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Log Maintenance Complaint")
        dialog.geometry("520x520")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=24, pady=20)

        lbl_head = ttk.Label(pad_f, text="Register Grievance Ticket", style="Subtitle.TLabel")
        lbl_head.pack(anchor="w", pady=(0, 15))

        form_f = ttk.Frame(pad_f)
        form_f.pack(fill="x", expand=True)

        # Student
        lbl_s = ttk.Label(form_f, text="Filing Student *:", font=FONT_BODY_BOLD)
        lbl_s.grid(row=0, column=0, sticky="w", pady=8, padx=(0, 10))
        s_opts = [f"{s.student_id} - {s.name}" for s in students]
        cb_student = ttk.Combobox(form_f, values=s_opts, state="readonly", width=34)
        cb_student.current(0)
        cb_student.grid(row=0, column=1, sticky="w", pady=8)

        # Room
        lbl_r = ttk.Label(form_f, text="Affected Room *:", font=FONT_BODY_BOLD)
        lbl_r.grid(row=1, column=0, sticky="w", pady=8, padx=(0, 10))
        r_opts = [f"{r.room_number} ({r.block})" for r in rooms]
        cb_room = ttk.Combobox(form_f, values=r_opts, state="readonly", width=34)
        cb_room.current(0)
        cb_room.grid(row=1, column=1, sticky="w", pady=8)

        # Category
        lbl_c = ttk.Label(form_f, text="Category *:", font=FONT_BODY_BOLD)
        lbl_c.grid(row=2, column=0, sticky="w", pady=8, padx=(0, 10))
        cb_cat = ttk.Combobox(
            form_f,
            values=["Electrical", "Plumbing", "Cleanliness", "Carpentry", "Internet", "Other"],
            state="readonly",
            width=34,
        )
        cb_cat.set("Electrical")
        cb_cat.grid(row=2, column=1, sticky="w", pady=8)

        # Severity
        lbl_sev = ttk.Label(form_f, text="Severity / Priority *:", font=FONT_BODY_BOLD)
        lbl_sev.grid(row=3, column=0, sticky="w", pady=8, padx=(0, 10))
        cb_sev = ttk.Combobox(form_f, values=["Low", "Medium", "High", "Critical"], state="readonly", width=34)
        cb_sev.set("Medium")
        cb_sev.grid(row=3, column=1, sticky="w", pady=8)

        # Description
        lbl_d = ttk.Label(form_f, text="Description *:", font=FONT_BODY_BOLD)
        lbl_d.grid(row=4, column=0, sticky="nw", pady=8, padx=(0, 10))
        txt_desc = tk.Text(form_f, width=32, height=4, font=("Segoe UI", 9))
        txt_desc.grid(row=4, column=1, sticky="w", pady=8)

        btn_box = ttk.Frame(pad_f)
        btn_box.pack(fill="x", pady=(20, 0))

        def save():
            desc_val = txt_desc.get("1.0", "end-1c").strip()
            s_idx = cb_student.current()
            r_idx = cb_room.current()

            if s_idx < 0 or r_idx < 0:
                messagebox.showerror("Error", "Please select valid student and room records.")
                return

            chosen_student = students[s_idx]
            chosen_room = rooms[r_idx]

            success, msg, ticket_id = self.complaint_service.create_complaint(
                student_id=chosen_student.id,
                room_id=chosen_room.id,
                category=cb_cat.get(),
                description=desc_val,
                severity=cb_sev.get(),
            )

            if success:
                messagebox.showinfo("Ticket Logged", f"{msg}\nTracking ID: {ticket_id}")
                dialog.destroy()
                self.load_complaints()
            else:
                messagebox.showerror("Validation Error", msg)

        ttk.Button(btn_box, text="💾 Submit Complaint", style="Primary.TButton", command=save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="right")

    def _open_update_dialog(self) -> None:
        ticket_id = self._get_selected_complaint_id()
        if not ticket_id:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Update Ticket {ticket_id}")
        dialog.geometry("450x320")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = ttk.Label(pad_f, text=f"Update Complaint Status ({ticket_id})", style="Subtitle.TLabel")
        lbl.pack(anchor="w", pady=(0, 15))

        lbl_s = ttk.Label(pad_f, text="Workflow Status *:", font=FONT_BODY_BOLD)
        lbl_s.pack(anchor="w", pady=4)

        cb_status = ttk.Combobox(
            pad_f,
            values=["Pending", "In-Progress", "Resolved", "Closed"],
            state="readonly",
            width=28,
        )
        cb_status.set("Resolved")
        cb_status.pack(anchor="w", pady=4)

        lbl_r = ttk.Label(pad_f, text="Resolution / Maintenance Notes:", font=FONT_BODY_BOLD)
        lbl_r.pack(anchor="w", pady=4)

        txt_notes = tk.Text(pad_f, width=42, height=4, font=("Segoe UI", 9))
        txt_notes.insert("1.0", "Issue inspected and repaired by hostel maintenance staff.")
        txt_notes.pack(anchor="w", pady=4)

        def save():
            notes_val = txt_notes.get("1.0", "end-1c").strip()
            success, msg = self.complaint_service.update_complaint_status(
                complaint_id_str=ticket_id,
                new_status=cb_status.get(),
                resolution_notes=notes_val,
            )
            if success:
                messagebox.showinfo("Ticket Updated", msg)
                dialog.destroy()
                self.load_complaints()
            else:
                messagebox.showerror("Error", msg)

        btn_b = ttk.Frame(pad_f)
        btn_b.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_b, text="💾 Update Ticket", style="Primary.TButton", command=save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_b, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="right")

    def _delete_selected(self) -> None:
        ticket_id = self._get_selected_complaint_id()
        if not ticket_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete complaint ticket {ticket_id}?",
        )
        if confirm:
            success, msg = self.complaint_service.delete_complaint(ticket_id)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.load_complaints()
            else:
                messagebox.showerror("Error", msg)
