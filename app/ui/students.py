"""Student Management View Component with CRUD and Q05 Fast Search.

TQM Quality Goal: Q05 - Reduce Response Time.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional, List
from ..models.student import Student
from ..services.student_service import StudentService
from ..services.search_service import FastSearchService
from ..utils.helpers import LatencyTimer
from .styles import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADER,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_MONO,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


class StudentView(ttk.Frame):
    """Student Directory & CRUD Interface with Q05 Fast Search."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller
        self.student_service = StudentService()
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

        lbl_title = ttk.Label(title_box, text="Student Management", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Manage student profiles, registrations, and execute Q05 indexed fast searches",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        # Top Action Buttons
        btn_box = ttk.Frame(top_bar)
        btn_box.pack(side="right")

        btn_add = ttk.Button(
            btn_box,
            text="➕ Register Student",
            style="Primary.TButton",
            command=self._open_add_dialog,
        )
        btn_add.pack(side="left", padx=5)

        btn_refresh = ttk.Button(
            btn_box,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self.load_students,
        )
        btn_refresh.pack(side="left", padx=5)

        # 2. Q05 Fast Search Toolbar Card
        search_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=10)
        search_card.pack(fill="x", pady=(0, 12))

        lbl_search = tk.Label(search_card, text="🔍 Fast Search:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_search.pack(side="left", padx=(0, 10))

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(search_card, textvariable=self.search_var, width=32)
        self.entry_search.pack(side="left", padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.perform_search())

        btn_search = ttk.Button(
            search_card,
            text="Search",
            style="Primary.TButton",
            command=self.perform_search,
        )
        btn_search.pack(side="left", padx=4)

        btn_clear = ttk.Button(
            search_card,
            text="Clear",
            style="Secondary.TButton",
            command=self._clear_search,
        )
        btn_clear.pack(side="left", padx=4)

        self.lbl_search_latency = tk.Label(
            search_card,
            text="Q05 Query Latency: Ready",
            font=FONT_MONO,
            bg=COLOR_CARD_BG,
            fg=COLOR_PRIMARY,
        )
        self.lbl_search_latency.pack(side="right")

        # 3. Students Data Table (Treeview)
        table_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1)
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("id", "student_id", "name", "gender", "branch", "year", "phone", "email", "guardian_phone")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="PK ID")
        self.tree.heading("student_id", text="Student ID / Roll No")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("branch", text="Branch")
        self.tree.heading("year", text="Year")
        self.tree.heading("phone", text="Contact")
        self.tree.heading("email", text="Email")
        self.tree.heading("guardian_phone", text="Guardian Phone")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("student_id", width=140, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("gender", width=80, anchor="center")
        self.tree.column("branch", width=90, anchor="center")
        self.tree.column("year", width=80, anchor="center")
        self.tree.column("phone", width=120, anchor="center")
        self.tree.column("email", width=200, anchor="w")
        self.tree.column("guardian_phone", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

        # Row Action Buttons (Edit / Delete)
        action_bar = ttk.Frame(main_pad)
        action_bar.pack(fill="x")

        btn_edit = ttk.Button(action_bar, text="✏️ Edit Selected", style="Secondary.TButton", command=self._open_edit_dialog)
        btn_edit.pack(side="left", padx=(0, 8))

        btn_del = ttk.Button(action_bar, text="🗑️ Delete Selected", style="Danger.TButton", command=self._delete_selected)
        btn_del.pack(side="left", padx=8)

        self.lbl_record_count = ttk.Label(action_bar, text="Total Students: 0", style="Muted.TLabel")
        self.lbl_record_count.pack(side="right")

    def on_view_active(self) -> None:
        self.load_students()

    def load_students(self) -> None:
        """Load all student records with timing benchmark."""
        timer = LatencyTimer()
        timer.start()
        students = self.student_service.get_all_students()
        elapsed_ms = timer.stop()

        self._populate_tree(students)
        self.lbl_search_latency.config(
            text=f"Loaded {len(students)} records in {elapsed_ms:.2f} ms",
            fg=COLOR_SUCCESS,
        )

    def _populate_tree(self, students: List[Student]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for s in students:
            self.tree.insert(
                "",
                "end",
                iid=str(s.id),
                values=(
                    s.id,
                    s.student_id,
                    s.name,
                    s.gender,
                    s.branch,
                    s.year,
                    s.phone,
                    s.email,
                    s.guardian_phone,
                ),
            )
        self.lbl_record_count.config(text=f"Total Students: {len(students)}")

    def perform_search(self) -> None:
        """Execute Q05 Fast Search on student records."""
        query = self.search_var.get().strip()
        if not query:
            self.load_students()
            return

        results, elapsed_ms = self.search_service.search_students(query)
        self._populate_tree(results)
        self.lbl_search_latency.config(
            text=f"⚡ Q05 Fast Search: {len(results)} matches in {elapsed_ms:.2f} ms",
            fg=COLOR_PRIMARY,
        )

    def _clear_search(self) -> None:
        self.search_var.set("")
        self.load_students()

    def _get_selected_student_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student record from the table.")
            return None
        return int(selected[0])

    def _open_add_dialog(self) -> None:
        self._show_student_form(title="Register New Student", student=None)

    def _open_edit_dialog(self) -> None:
        pk_id = self._get_selected_student_id()
        if not pk_id:
            return
        student = self.student_service.get_student_by_id(pk_id)
        if not student:
            messagebox.showerror("Error", "Student record could not be found.")
            return
        self._show_student_form(title="Edit Student Details", student=student)

    def _show_student_form(self, title: str, student: Optional[Student]) -> None:
        """Modal dialog for Student Create and Update."""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("520x620")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=24, pady=20)

        lbl_head = ttk.Label(pad_f, text=title, style="Subtitle.TLabel")
        lbl_head.pack(anchor="w", pady=(0, 15))

        form_f = ttk.Frame(pad_f)
        form_f.pack(fill="x", expand=True)

        # Fields
        entries = {}

        def add_field(row, label_text, var_name, default="", values=None):
            lbl = ttk.Label(form_f, text=label_text, font=FONT_BODY_BOLD)
            lbl.grid(row=row, column=0, sticky="w", pady=6, padx=(0, 10))

            if values:
                cb = ttk.Combobox(form_f, values=values, state="readonly", width=32)
                cb.set(default if default else values[0])
                cb.grid(row=row, column=1, sticky="w", pady=6)
                entries[var_name] = cb
            else:
                ent = ttk.Entry(form_f, width=35)
                ent.insert(0, default)
                ent.grid(row=row, column=1, sticky="w", pady=6)
                entries[var_name] = ent

        add_field(0, "Student ID / Roll No *:", "student_id", student.student_id if student else "")
        add_field(1, "Full Name *:", "name", student.name if student else "")
        add_field(2, "Email Address *:", "email", student.email if student else "")
        add_field(3, "Student Phone *:", "phone", student.phone if student else "")
        add_field(4, "Gender *:", "gender", student.gender if student else "Male", values=["Male", "Female", "Other"])
        add_field(5, "Branch *:", "branch", student.branch if student else "CSE", values=["CSE", "ECE", "MECH", "CIVIL", "IT", "AI/ML"])
        add_field(6, "Academic Year *:", "year", student.year if student else "1st Year", values=["1st Year", "2nd Year", "3rd Year", "4th Year"])
        add_field(7, "Guardian Phone *:", "guardian_phone", student.guardian_phone if student else "")
        add_field(8, "Permanent Address:", "address", student.address if student else "")

        btn_box = ttk.Frame(pad_f)
        btn_box.pack(fill="x", pady=(20, 0))

        def save():
            s_obj = Student(
                student_id=entries["student_id"].get().strip(),
                name=entries["name"].get().strip(),
                email=entries["email"].get().strip(),
                phone=entries["phone"].get().strip(),
                gender=entries["gender"].get(),
                branch=entries["branch"].get(),
                year=entries["year"].get(),
                guardian_phone=entries["guardian_phone"].get().strip(),
                address=entries["address"].get().strip(),
                id=student.id if student else None,
            )

            if student is None:
                success, msg, _ = self.student_service.create_student(s_obj)
            else:
                success, msg = self.student_service.update_student(s_obj)

            if success:
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.load_students()
            else:
                messagebox.showerror("Validation / Database Error", msg)

        btn_save = ttk.Button(btn_box, text="💾 Save Student", style="Primary.TButton", command=save)
        btn_save.pack(side="right", padx=(8, 0))

        btn_cancel = ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dialog.destroy)
        btn_cancel.pack(side="right")

    def _delete_selected(self) -> None:
        pk_id = self._get_selected_student_id()
        if not pk_id:
            return

        student = self.student_service.get_student_by_id(pk_id)
        if not student:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete student record:\n\n"
            f"Name: {student.name}\nRoll No: {student.student_id}\n\n"
            f"This action cannot be undone.",
        )
        if confirm:
            success, msg = self.student_service.delete_student(pk_id)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.load_students()
            else:
                messagebox.showerror("Error", msg)
