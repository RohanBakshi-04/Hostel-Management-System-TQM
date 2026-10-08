"""Room Service - Handles room inventory CRUD operations and occupancy calculations."""

import sqlite3
from typing import List, Optional, Tuple, Dict, Any
from ..database.connection import get_db_connection
from ..models.room import Room
from ..utils.validators import validate_room_data


class RoomService:
    """Provides CRUD operations and capacity management for Hostel Rooms."""

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.db_conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self.db_conn:
            return self.db_conn
        return get_db_connection()

    def create_room(self, room: Room) -> Tuple[bool, str, Optional[int]]:
        """CREATE: Register a new room record with validation."""
        is_valid, err_msg = validate_room_data(
            room.room_number,
            room.block,
            room.floor,
            room.room_type,
            room.capacity,
            room.base_fee,
        )
        if not is_valid:
            return False, err_msg, None

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rooms (
                    room_number, block, floor, room_type, capacity, base_fee, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    room.room_number.strip().upper(),
                    room.block.strip().upper(),
                    int(room.floor),
                    room.room_type.strip(),
                    int(room.capacity),
                    float(room.base_fee),
                    room.status.strip(),
                ),
            )
            new_id = cursor.lastrowid
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Room added successfully.", new_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: rooms.room_number" in str(e):
                return False, f"Room '{room.room_number.upper()}' already exists.", None
            return False, f"Database constraint error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
        finally:
            if not self.db_conn:
                conn.close()

    def get_room_by_id(self, pk_id: int) -> Optional[Room]:
        """READ: Retrieve single room by primary key."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms WHERE id = ?;", (pk_id,))
            row = cursor.fetchone()
            if row:
                return Room.from_row(row)
            return None
        finally:
            if not self.db_conn:
                conn.close()

    def get_room_by_number(self, room_number: str) -> Optional[Room]:
        """READ: Retrieve room by unique room number (Uses Q05 Index)."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms WHERE room_number = ?;", (room_number.strip().upper(),))
            row = cursor.fetchone()
            if row:
                return Room.from_row(row)
            return None
        finally:
            if not self.db_conn:
                conn.close()

    def get_all_rooms(self) -> List[Room]:
        """READ: Retrieve all rooms ordered by block and room number."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rooms ORDER BY block ASC, room_number ASC;")
            rows = cursor.fetchall()
            return [Room.from_row(r) for r in rows]
        finally:
            if not self.db_conn:
                conn.close()

    def get_available_rooms(self) -> List[Room]:
        """READ: Retrieve only rooms that have available capacity for allocation."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Fast query leveraging composite index
            cursor.execute(
                """
                SELECT r.*,
                       COUNT(a.id) as occupied_count
                FROM rooms r
                LEFT JOIN allocations a ON r.id = a.room_id AND a.status = 'Active'
                WHERE r.status != 'Maintenance'
                GROUP BY r.id
                HAVING occupied_count < r.capacity
                ORDER BY r.block ASC, r.room_number ASC;
                """
            )
            rows = cursor.fetchall()
            return [Room.from_row(r) for r in rows]
        finally:
            if not self.db_conn:
                conn.close()

    def get_room_occupancy_details(self, room_id: int) -> Dict[str, Any]:
        """READ: Get real-time occupancy counts for a specific room."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT r.capacity,
                       COUNT(a.id) as active_allocations
                FROM rooms r
                LEFT JOIN allocations a ON r.id = a.room_id AND a.status = 'Active'
                WHERE r.id = ?
                GROUP BY r.id;
                """,
                (room_id,),
            )
            row = cursor.fetchone()
            if not row:
                return {"capacity": 0, "occupied": 0, "available_beds": 0}
            cap = row["capacity"]
            occ = row["active_allocations"]
            return {"capacity": cap, "occupied": occ, "available_beds": max(0, cap - occ)}
        finally:
            if not self.db_conn:
                conn.close()

    def update_room(self, room: Room) -> Tuple[bool, str]:
        """UPDATE: Modify room specifications."""
        if not room.id:
            return False, "Room ID is required for update."

        is_valid, err_msg = validate_room_data(
            room.room_number,
            room.block,
            room.floor,
            room.room_type,
            room.capacity,
            room.base_fee,
        )
        if not is_valid:
            return False, err_msg

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Verify capacity is not lowered below current active occupancy
            cursor.execute(
                "SELECT COUNT(*) FROM allocations WHERE room_id = ? AND status = 'Active';",
                (room.id,),
            )
            current_active = cursor.fetchone()[0]
            if int(room.capacity) < current_active:
                return (
                    False,
                    f"Cannot reduce capacity to {room.capacity}; room currently has {current_active} active students.",
                )

            cursor.execute(
                """
                UPDATE rooms
                SET room_number = ?, block = ?, floor = ?, room_type = ?,
                    capacity = ?, base_fee = ?, status = ?
                WHERE id = ?;
                """,
                (
                    room.room_number.strip().upper(),
                    room.block.strip().upper(),
                    int(room.floor),
                    room.room_type.strip(),
                    int(room.capacity),
                    float(room.base_fee),
                    room.status.strip(),
                    room.id,
                ),
            )
            if cursor.rowcount == 0:
                return False, "Room not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Room updated successfully."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: rooms.room_number" in str(e):
                return False, f"Another room with number '{room.room_number.upper()}' already exists."
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()

    def delete_room(self, pk_id: int) -> Tuple[bool, str]:
        """DELETE: Delete a vacant room record."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM allocations WHERE room_id = ? AND status = 'Active';",
                (pk_id,),
            )
            active_count = cursor.fetchone()[0]
            if active_count > 0:
                return False, "Cannot delete room with active student allocations."

            cursor.execute("DELETE FROM rooms WHERE id = ?;", (pk_id,))
            if cursor.rowcount == 0:
                return False, "Room record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Room deleted successfully."
        except Exception as e:
            return False, f"Error deleting room: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()
