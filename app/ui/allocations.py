"""Room Allocation View Component with Poka-Yoke Capacity Enforcement.

TQM Quality Goal: Q05 - Reduce Response Time.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import TYPE_CHECKING, Optional, List
from ..models.allocation import Allocation
from ..services.allocation_service import AllocationService
from ..services.student_service import StudentService
from ..services.room_service import RoomService
from ..utils.helpers import LatencyTimer
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


class AllocationView(ttk.Frame):
    """Room Allocation and Bed Allotment Interface."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller
        self.allocation_service = AllocationService()
        self.student_service = StudentService()
        self.room_service = RoomService()

        self._build_ui()

    def _build_ui(self) -> None:
        main_pad = ttk.Frame(self)
        main_pad.pack(fill="both", expand=True, padx=25, pady=20)

        # 1. Header Bar
        top_bar = ttk.Frame(main_pad)
        top_bar.pack(fill="x", pady=(0, 15))

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")

        lbl_title = ttk.Label(title_box, text="Room Allotments & Bed Allocation", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Assign eligible students to available beds with automated capacity boundary enforcement",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        btn_box = ttk.Frame(top_bar)
        btn_box.pack(side="right")

        btn_alloc = ttk.Button(
            btn_box,
            text="➕ New Bed Allocation",
            style="Primary.TButton",
            command=self._open_allocation_dialog,
        )
        btn_alloc.pack(side="left", padx=5)

        btn_refresh = ttk.Button(
            btn_box,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self.load_allocations,
        )
        btn_refresh.pack(side="left", padx=5)

        # 2. Filter Bar
        filter_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=10)
        filter_card.pack(fill="x", pady=(0, 12))

        lbl_filter = tk.Label(filter_card, text="Filter Status:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_filter.pack(side="left", padx=(0, 10))

        self.filter_var = tk.StringVar(value="All Allocations")
        cb_filter = ttk.Combobox(
            filter_card,
            textvariable=self.filter_var,
            values=["All Allocations", "Active Only", "Vacated Only"],
            state="readonly",
            width=20,
        )
        cb_filter.pack(side="left", padx=(0, 10))
        cb_filter.bind("<<ComboboxSelected>>", lambda e: self.load_allocations())

        self.lbl_alloc_latency = tk.Label(
            filter_card,
            text="Query Latency: Ready",
            font=FONT_MONO,
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
        )
        self.lbl_alloc_latency.pack(side="right")

        # 3. Allocations Table
        table_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1)
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        columns = (
            "id",
            "student_reg_no",
            "student_name",
            "room_number",
            "room_block",
            "allocation_date",
            "fee_status",
            "status",
            "remarks",
        )
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="Alloc ID")
        self.tree.heading("student_reg_no", text="Student Roll No")
        self.tree.heading("student_name", text="Student Name")
        self.tree.heading("room_number", text="Room No")
        self.tree.heading("room_block", text="Block")
        self.tree.heading("allocation_date", text="Allotment Date")
        self.tree.heading("fee_status", text="Fee Status")
        self.tree.heading("status", text="Allotment Status")
        self.tree.heading("remarks", text="Remarks")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("student_reg_no", width=130, anchor="center")
        self.tree.column("student_name", width=180, anchor="w")
        self.tree.column("room_number", width=100, anchor="center")
        self.tree.column("room_block", width=110, anchor="center")
        self.tree.column("allocation_date", width=110, anchor="center")
        self.tree.column("fee_status", width=110, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("remarks", width=180, anchor="w")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

        # Action Bar
        action_bar = ttk.Frame(main_pad)
        action_bar.pack(fill="x")

        btn_vacate = ttk.Button(
            action_bar,
            text="🚪 Vacate / Check-Out Student",
            style="Danger.TButton",
            command=self._vacate_selected,
        )
        btn_vacate.pack(side="left", padx=(0, 8))

        btn_update_fee = ttk.Button(
            action_bar,
            text="💳 Update Fee Status",
            style="Secondary.TButton",
            command=self._update_fee_dialog,
        )
        btn_update_fee.pack(side="left", padx=8)

        self.lbl_record_count = ttk.Label(action_bar, text="Total Allocations: 0", style="Muted.TLabel")
        self.lbl_record_count.pack(side="right")

    def on_view_active(self) -> None:
        self.load_allocations()

    def load_allocations(self) -> None:
        """Fetch and populate allocations list."""
        timer = LatencyTimer()
        timer.start()

        filter_mode = self.filter_var.get()
        active_only = filter_mode == "Active Only"
        allocations = self.allocation_service.get_all_allocations(active_only=active_only)

        if filter_mode == "Vacated Only":
            allocations = [a for a in allocations if a.status == "Vacated"]

        elapsed_ms = timer.stop()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for a in allocations:
            self.tree.insert(
                "",
                "end",
                iid=str(a.id),
                values=(
                    a.id,
                    a.student_reg_no,
                    a.student_name,
                    a.room_number,
                    a.room_block,
                    a.allocation_date,
                    a.fee_status,
                    a.status,
                    a.remarks or "-",
                ),
            )

        self.lbl_record_count.config(text=f"Total: {len(allocations)} allocations")
        self.lbl_alloc_latency.config(
            text=f"Loaded in {elapsed_ms:.2f} ms",
            fg=COLOR_SUCCESS,
        )

    def _get_selected_allocation_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an allocation row from the table.")
            return None
        return int(selected[0])

    def _open_allocation_dialog(self) -> None:
        """Dialog to create new room allotment."""
        students = self.student_service.get_all_students()
        available_rooms = self.room_service.get_available_rooms()

        if not students:
            messagebox.showwarning("No Students", "Please register student records before allocating rooms.")
            return

        if not available_rooms:
            messagebox.showwarning("No Available Rooms", "All rooms are currently full or in maintenance.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Allocate Student to Room")
        dialog.geometry("520x460")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=24, pady=20)

        lbl_head = ttk.Label(pad_f, text="New Bed Allocation", style="Subtitle.TLabel")
        lbl_head.pack(anchor="w", pady=(0, 15))

        form_f = ttk.Frame(pad_f)
        form_f.pack(fill="x", expand=True)

        # Student Picker
        lbl_s = ttk.Label(form_f, text="Select Student *:", font=FONT_BODY_BOLD)
        lbl_s.grid(row=0, column=0, sticky="w", pady=8, padx=(0, 10))

        student_options = [f"{s.student_id} - {s.name} ({s.branch})" for s in students]
        cb_student = ttk.Combobox(form_f, values=student_options, state="readonly", width=36)
        cb_student.current(0)
        cb_student.grid(row=0, column=1, sticky="w", pady=8)

        # Room Picker
        lbl_r = ttk.Label(form_f, text="Select Room *:", font=FONT_BODY_BOLD)
        lbl_r.grid(row=1, column=0, sticky="w", pady=8, padx=(0, 10))

        room_options = [
            f"{r.room_number} ({r.block} - {r.room_type}, Cap: {r.capacity})" for r in available_rooms
        ]
        cb_room = ttk.Combobox(form_f, values=room_options, state="readonly", width=36)
        cb_room.current(0)
        cb_room.grid(row=1, column=1, sticky="w", pady=8)

        # Date Picker
        lbl_d = ttk.Label(form_f, text="Allotment Date *:", font=FONT_BODY_BOLD)
        lbl_d.grid(row=2, column=0, sticky="w", pady=8, padx=(0, 10))

        ent_date = ttk.Entry(form_f, width=38)
        ent_date.insert(0, date.today().isoformat())
        ent_date.grid(row=2, column=1, sticky="w", pady=8)

        # Fee Status
        lbl_f = ttk.Label(form_f, text="Fee Status *:", font=FONT_BODY_BOLD)
        lbl_f.grid(row=3, column=0, sticky="w", pady=8, padx=(0, 10))

        cb_fee = ttk.Combobox(form_f, values=["Paid", "Pending", "Overdue"], state="readonly", width=36)
        cb_fee.set("Paid")
        cb_fee.grid(row=3, column=1, sticky="w", pady=8)

        # Remarks
        lbl_rem = ttk.Label(form_f, text="Remarks:", font=FONT_BODY_BOLD)
        lbl_rem.grid(row=4, column=0, sticky="w", pady=8, padx=(0, 10))

        ent_remarks = ttk.Entry(form_f, width=38)
        ent_remarks.insert(0, "Regular Semester Allotment")
        ent_remarks.grid(row=4, column=1, sticky="w", pady=8)

        btn_box = ttk.Frame(pad_f)
        btn_box.pack(fill="x", pady=(20, 0))

        def save_allocation():
            s_idx = cb_student.current()
            r_idx = cb_room.current()
            if s_idx < 0 or r_idx < 0:
                messagebox.showerror("Error", "Please select valid student and room records.")
                return

            chosen_student = students[s_idx]
            chosen_room = available_rooms[r_idx]

            success, msg, _ = self.allocation_service.allocate_room(
                student_id=chosen_student.id,
                room_id=chosen_room.id,
                allocation_date=ent_date.get().strip(),
                fee_status=cb_fee.get(),
                remarks=ent_remarks.get().strip(),
            )

            if success:
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.load_allocations()
            else:
                messagebox.showerror("Allocation Guard Error", msg)

        btn_save = ttk.Button(btn_box, text="💾 Confirm Allocation", style="Primary.TButton", command=save_allocation)
        btn_save.pack(side="right", padx=(8, 0))

        btn_cancel = ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dialog.destroy)
        btn_cancel.pack(side="right")

    def _vacate_selected(self) -> None:
        alloc_id = self._get_selected_allocation_id()
        if not alloc_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Vacating",
            f"Are you sure you want to check out / vacate allocation #{alloc_id}?\n\n"
            f"This will free up the bed in the assigned room immediately.",
        )
        if confirm:
            success, msg = self.allocation_service.vacate_allocation(alloc_id)
            if success:
                messagebox.showinfo("Vacated", msg)
                self.load_allocations()
            else:
                messagebox.showerror("Error", msg)

    def _update_fee_dialog(self) -> None:
        alloc_id = self._get_selected_allocation_id()
        if not alloc_id:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Update Allocation #{alloc_id} Fee Status")
        dialog.geometry("380x240")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = ttk.Label(pad_f, text=f"Update Fee for Allocation #{alloc_id}", style="Subtitle.TLabel")
        lbl.pack(anchor="w", pady=(0, 15))

        lbl_s = ttk.Label(pad_f, text="Fee Status:", font=FONT_BODY_BOLD)
        lbl_s.pack(anchor="w", pady=4)

        cb_fee = ttk.Combobox(pad_f, values=["Paid", "Pending", "Overdue"], state="readonly", width=25)
        cb_fee.set("Paid")
        cb_fee.pack(anchor="w", pady=4)

        lbl_r = ttk.Label(pad_f, text="Remarks:", font=FONT_BODY_BOLD)
        lbl_r.pack(anchor="w", pady=4)

        ent_rem = ttk.Entry(pad_f, width=30)
        ent_rem.pack(anchor="w", pady=4)

        def save():
            success, msg = self.allocation_service.update_allocation(alloc_id, cb_fee.get(), ent_rem.get())
            if success:
                messagebox.showinfo("Updated", msg)
                dialog.destroy()
                self.load_allocations()
            else:
                messagebox.showerror("Error", msg)

        btn_b = ttk.Frame(pad_f)
        btn_b.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_b, text="Save", style="Primary.TButton", command=save).pack(side="right", padx=(8, 0))
        ttk.Button(btn_b, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="right")
