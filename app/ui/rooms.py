"""Room Management View Component with CRUD and Fast Filtering.

TQM Quality Goal: Q05 - Reduce Response Time.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Optional, List
from ..models.room import Room
from ..services.room_service import RoomService
from ..services.search_service import FastSearchService
from ..utils.helpers import LatencyTimer, format_currency
from .styles import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_HEADER,
    FONT_BODY_BOLD,
    FONT_MONO,
)

if TYPE_CHECKING:
    from .main_window import MainWindow


class RoomView(ttk.Frame):
    """Room Inventory & CRUD Interface with Q05 Fast Search."""

    def __init__(self, parent: tk.Widget, controller: "MainWindow"):
        super().__init__(parent)
        self.controller = controller
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

        lbl_title = ttk.Label(title_box, text="Room Inventory & Capacity", style="Title.TLabel")
        lbl_title.pack(anchor="w")

        lbl_sub = ttk.Label(
            title_box,
            text="Manage room allotments, track bed occupancies, and execute Q05 fast room queries",
            style="Muted.TLabel",
        )
        lbl_sub.pack(anchor="w")

        # Top Action Buttons
        btn_box = ttk.Frame(top_bar)
        btn_box.pack(side="right")

        btn_add = ttk.Button(
            btn_box,
            text="➕ Add Room",
            style="Primary.TButton",
            command=self._open_add_dialog,
        )
        btn_add.pack(side="left", padx=5)

        btn_refresh = ttk.Button(
            btn_box,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self.load_rooms,
        )
        btn_refresh.pack(side="left", padx=5)

        # 2. Q05 Fast Search Toolbar Card
        search_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1, padx=15, pady=10)
        search_card.pack(fill="x", pady=(0, 12))

        lbl_search = tk.Label(search_card, text="🔍 Fast Search Rooms:", font=FONT_HEADER, bg=COLOR_CARD_BG)
        lbl_search.pack(side="left", padx=(0, 10))

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(search_card, textvariable=self.search_var, width=30)
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

        # 3. Rooms Table
        table_card = tk.Frame(main_pad, bg=COLOR_CARD_BG, relief="solid", borderwidth=1)
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        columns = ("id", "room_number", "block", "floor", "room_type", "capacity", "occupancy", "base_fee", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="PK ID")
        self.tree.heading("room_number", text="Room Number")
        self.tree.heading("block", text="Block / Wing")
        self.tree.heading("floor", text="Floor")
        self.tree.heading("room_type", text="Type")
        self.tree.heading("capacity", text="Capacity")
        self.tree.heading("occupancy", text="Occupancy / Beds")
        self.tree.heading("base_fee", text="Base Fee")
        self.tree.heading("status", text="Current Status")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("room_number", width=120, anchor="center")
        self.tree.column("block", width=120, anchor="center")
        self.tree.column("floor", width=80, anchor="center")
        self.tree.column("room_type", width=120, anchor="center")
        self.tree.column("capacity", width=90, anchor="center")
        self.tree.column("occupancy", width=150, anchor="center")
        self.tree.column("base_fee", width=120, anchor="center")
        self.tree.column("status", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

        # Action Bar
        action_bar = ttk.Frame(main_pad)
        action_bar.pack(fill="x")

        btn_edit = ttk.Button(action_bar, text="✏️ Edit Room", style="Secondary.TButton", command=self._open_edit_dialog)
        btn_edit.pack(side="left", padx=(0, 8))

        btn_del = ttk.Button(action_bar, text="🗑️ Delete Room", style="Danger.TButton", command=self._delete_selected)
        btn_del.pack(side="left", padx=8)

        self.lbl_record_count = ttk.Label(action_bar, text="Total Rooms: 0", style="Muted.TLabel")
        self.lbl_record_count.pack(side="right")

    def on_view_active(self) -> None:
        self.load_rooms()

    def load_rooms(self) -> None:
        """Load all rooms with occupancy details."""
        timer = LatencyTimer()
        timer.start()
        rooms = self.room_service.get_all_rooms()
        elapsed_ms = timer.stop()

        self._populate_tree(rooms)
        self.lbl_search_latency.config(
            text=f"Loaded {len(rooms)} rooms in {elapsed_ms:.2f} ms",
            fg=COLOR_SUCCESS,
        )

    def _populate_tree(self, rooms: List[Room]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for r in rooms:
            occ_info = self.room_service.get_room_occupancy_details(r.id)
            occ_str = f"{occ_info['occupied']} / {r.capacity} beds ({occ_info['available_beds']} free)"

            self.tree.insert(
                "",
                "end",
                iid=str(r.id),
                values=(
                    r.id,
                    r.room_number,
                    r.block,
                    f"Floor {r.floor}",
                    r.room_type,
                    f"{r.capacity} Beds",
                    occ_str,
                    format_currency(r.base_fee),
                    r.status,
                ),
            )
        self.lbl_record_count.config(text=f"Total Rooms: {len(rooms)}")

    def perform_search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            self.load_rooms()
            return

        results, elapsed_ms = self.search_service.search_rooms(query)
        self._populate_tree(results)
        self.lbl_search_latency.config(
            text=f"⚡ Q05 Fast Search: {len(results)} rooms matched in {elapsed_ms:.2f} ms",
            fg=COLOR_PRIMARY,
        )

    def _clear_search(self) -> None:
        self.search_var.set("")
        self.load_rooms()

    def _get_selected_room_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a room from the table.")
            return None
        return int(selected[0])

    def _open_add_dialog(self) -> None:
        self._show_room_form(title="Add New Room", room=None)

    def _open_edit_dialog(self) -> None:
        pk_id = self._get_selected_room_id()
        if not pk_id:
            return
        room = self.room_service.get_room_by_id(pk_id)
        if not room:
            messagebox.showerror("Error", "Room record could not be found.")
            return
        self._show_room_form(title="Edit Room Details", room=room)

    def _show_room_form(self, title: str, room: Optional[Room]) -> None:
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("480x540")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        pad_f = ttk.Frame(dialog)
        pad_f.pack(fill="both", expand=True, padx=24, pady=20)

        lbl_head = ttk.Label(pad_f, text=title, style="Subtitle.TLabel")
        lbl_head.pack(anchor="w", pady=(0, 15))

        form_f = ttk.Frame(pad_f)
        form_f.pack(fill="x", expand=True)

        entries = {}

        def add_field(row, label_text, var_name, default="", values=None):
            lbl = ttk.Label(form_f, text=label_text, font=FONT_BODY_BOLD)
            lbl.grid(row=row, column=0, sticky="w", pady=6, padx=(0, 10))

            if values:
                cb = ttk.Combobox(form_f, values=values, state="readonly", width=28)
                cb.set(default if default else values[0])
                cb.grid(row=row, column=1, sticky="w", pady=6)
                entries[var_name] = cb
            else:
                ent = ttk.Entry(form_f, width=30)
                ent.insert(0, str(default))
                ent.grid(row=row, column=1, sticky="w", pady=6)
                entries[var_name] = ent

        add_field(0, "Room Number *:", "room_number", room.room_number if room else "")
        add_field(1, "Block / Wing *:", "block", room.block if room else "Block A", values=["Block A", "Block B", "Block C", "PG Wing"])
        add_field(2, "Floor (0-20) *:", "floor", room.floor if room else "1")
        add_field(3, "Room Type *:", "room_type", room.room_type if room else "Double", values=["Single", "Double", "Triple", "Dormitory"])
        add_field(4, "Capacity (Beds) *:", "capacity", room.capacity if room else "2", values=["1", "2", "3", "4", "6"])
        add_field(5, "Base Fee (Rs.) *:", "base_fee", room.base_fee if room else "5000")
        add_field(6, "Status *:", "status", room.status if room else "Available", values=["Available", "Partially Occupied", "Full", "Maintenance"])

        btn_box = ttk.Frame(pad_f)
        btn_box.pack(fill="x", pady=(20, 0))

        def save():
            try:
                r_obj = Room(
                    room_number=entries["room_number"].get().strip(),
                    block=entries["block"].get().strip(),
                    floor=int(entries["floor"].get()),
                    room_type=entries["room_type"].get().strip(),
                    capacity=int(entries["capacity"].get()),
                    base_fee=float(entries["base_fee"].get()),
                    status=entries["status"].get().strip(),
                    id=room.id if room else None,
                )

                if room is None:
                    success, msg, _ = self.room_service.create_room(r_obj)
                else:
                    success, msg = self.room_service.update_room(r_obj)

                if success:
                    messagebox.showinfo("Success", msg)
                    dialog.destroy()
                    self.load_rooms()
                else:
                    messagebox.showerror("Validation Error", msg)
            except ValueError as e:
                messagebox.showerror("Input Error", f"Please ensure numerical fields are formatted correctly: {e}")

        btn_save = ttk.Button(btn_box, text="💾 Save Room", style="Primary.TButton", command=save)
        btn_save.pack(side="right", padx=(8, 0))

        btn_cancel = ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dialog.destroy)
        btn_cancel.pack(side="right")

    def _delete_selected(self) -> None:
        pk_id = self._get_selected_room_id()
        if not pk_id:
            return

        room = self.room_service.get_room_by_id(pk_id)
        if not room:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete Room {room.room_number} ({room.block})?\n\n"
            f"This action cannot be undone.",
        )
        if confirm:
            success, msg = self.room_service.delete_room(pk_id)
            if success:
                messagebox.showinfo("Deleted", msg)
                self.load_rooms()
            else:
                messagebox.showerror("Error", msg)
