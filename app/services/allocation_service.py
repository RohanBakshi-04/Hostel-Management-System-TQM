"""Allocation Service - Handles student room allotments with Poka-Yoke capacity enforcement."""

import sqlite3
from typing import List, Optional, Tuple
from ..database.connection import get_db_connection
from ..models.allocation import Allocation


class AllocationService:
    """Provides allocation CRUD operations, status transitions, and capacity guards."""

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.db_conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self.db_conn:
            return self.db_conn
        return get_db_connection()

    def allocate_room(
        self,
        student_id: int,
        room_id: int,
        allocation_date: str,
        fee_status: str = "Pending",
        remarks: str = "",
    ) -> Tuple[bool, str, Optional[int]]:
        """CREATE: Allocate an eligible student to an available room with capacity verification.

        Poka-Yoke Guards:
        1. Prevents allocating a student who already has an active room.
        2. Prevents allocating to a room under maintenance.
        3. Prevents exceeding configured room capacity.
        """
        if not student_id or not room_id or not allocation_date:
            return False, "Student, Room, and Allocation Date are required fields.", None

        conn = self._get_conn()
        try:
            cursor = conn.cursor()

            # Guard 1: Verify student exists and has no active allocation
            cursor.execute("SELECT id, name FROM students WHERE id = ?;", (student_id,))
            student_row = cursor.fetchone()
            if not student_row:
                return False, "Selected student record does not exist.", None

            cursor.execute(
                "SELECT id FROM allocations WHERE student_id = ? AND status = 'Active';",
                (student_id,),
            )
            if cursor.fetchone():
                return False, f"Student '{student_row['name']}' already holds an active room allocation.", None

            # Guard 2: Verify room exists and check capacity & maintenance status
            cursor.execute("SELECT id, room_number, capacity, status FROM rooms WHERE id = ?;", (room_id,))
            room_row = cursor.fetchone()
            if not room_row:
                return False, "Selected room does not exist.", None

            if room_row["status"] == "Maintenance":
                return False, f"Room {room_row['room_number']} is currently under Maintenance.", None

            # Guard 3: Check current occupancy using Q05 composite index
            cursor.execute(
                "SELECT COUNT(*) FROM allocations WHERE room_id = ? AND status = 'Active';",
                (room_id,),
            )
            current_occupancy = cursor.fetchone()[0]
            if current_occupancy >= room_row["capacity"]:
                return (
                    False,
                    f"Room {room_row['room_number']} is at full capacity ({room_row['capacity']}/{room_row['capacity']}).",
                    None,
                )

            # Perform Allocation
            cursor.execute(
                """
                INSERT INTO allocations (
                    student_id, room_id, allocation_date, fee_status, status, remarks
                ) VALUES (?, ?, ?, ?, 'Active', ?);
                """,
                (student_id, room_id, allocation_date.strip(), fee_status.strip(), remarks.strip()),
            )
            new_id = cursor.lastrowid

            # Update room status flag (Available, Partially Occupied, Full)
            new_occupancy = current_occupancy + 1
            if new_occupancy >= room_row["capacity"]:
                room_status = "Full"
            else:
                room_status = "Partially Occupied"

            cursor.execute("UPDATE rooms SET status = ? WHERE id = ?;", (room_status, room_id))
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, f"Room {room_row['room_number']} allocated to {student_row['name']} successfully.", new_id
        except Exception as e:
            return False, f"Allocation transaction failed: {str(e)}", None
        finally:
            if not self.db_conn:
                conn.close()

    def get_all_allocations(self, active_only: bool = False) -> List[Allocation]:
        """READ: Retrieve room allocations joined with student and room details."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            where_clause = "WHERE a.status = 'Active'" if active_only else ""
            query = f"""
                SELECT a.*,
                       s.name as student_name,
                       s.student_id as student_reg_no,
                       r.room_number as room_number,
                       r.block as room_block
                FROM allocations a
                JOIN students s ON a.student_id = s.id
                JOIN rooms r ON a.room_id = r.id
                {where_clause}
                ORDER BY a.id DESC;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Allocation.from_row(r) for r in rows]
        finally:
            if not self.db_conn:
                conn.close()

    def update_allocation(
        self,
        allocation_id: int,
        fee_status: str,
        remarks: str,
    ) -> Tuple[bool, str]:
        """UPDATE: Modify allocation fee status or remarks."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE allocations
                SET fee_status = ?, remarks = ?
                WHERE id = ?;
                """,
                (fee_status, remarks.strip(), allocation_id),
            )
            if cursor.rowcount == 0:
                return False, "Allocation record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Allocation details updated successfully."
        except Exception as e:
            return False, f"Error updating allocation: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()

    def vacate_allocation(self, allocation_id: int) -> Tuple[bool, str]:
        """DE-ALLOCATE: Mark allocation as Vacated and recalculate room capacity status."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT room_id, status FROM allocations WHERE id = ?;", (allocation_id,))
            alloc_row = cursor.fetchone()
            if not alloc_row:
                return False, "Allocation not found."

            if alloc_row["status"] == "Vacated":
                return False, "This allocation is already vacated."

            room_id = alloc_row["room_id"]
            cursor.execute("UPDATE allocations SET status = 'Vacated' WHERE id = ?;", (allocation_id,))

            # Recalculate room status
            cursor.execute("SELECT capacity, status FROM rooms WHERE id = ?;", (room_id,))
            room_row = cursor.fetchone()
            if room_row and room_row["status"] != "Maintenance":
                cursor.execute(
                    "SELECT COUNT(*) FROM allocations WHERE room_id = ? AND status = 'Active';",
                    (room_id,),
                )
                remaining_active = cursor.fetchone()[0]
                if remaining_active == 0:
                    new_status = "Available"
                elif remaining_active < room_row["capacity"]:
                    new_status = "Partially Occupied"
                else:
                    new_status = "Full"
                cursor.execute("UPDATE rooms SET status = ? WHERE id = ?;", (new_status, room_id))

            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Student checked out / allocation vacated successfully."
        except Exception as e:
            return False, f"Failed to vacate allocation: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()
