"""Complaint Service - Handles grievance registration and resolution workflow."""

import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from ..database.connection import get_db_connection
from ..models.complaint import Complaint
from ..utils.validators import validate_complaint_data
from ..utils.helpers import generate_complaint_id


class ComplaintService:
    """Provides complete complaint management and resolution tracking."""

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.db_conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self.db_conn:
            return self.db_conn
        return get_db_connection()

    def create_complaint(
        self,
        student_id: int,
        room_id: int,
        category: str,
        description: str,
        severity: str = "Medium",
    ) -> Tuple[bool, str, Optional[str]]:
        """CREATE: Register a new grievance ticket with Poka-Yoke checks."""
        is_valid, err_msg = validate_complaint_data(
            student_id, room_id, category, description, severity
        )
        if not is_valid:
            return False, err_msg, None

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Generate next sequential ticket ID
            cursor.execute("SELECT COUNT(*) FROM complaints;")
            seq = cursor.fetchone()[0] + 1001
            complaint_id = generate_complaint_id(seq)

            # Ensure uniqueness
            cursor.execute(
                """
                INSERT INTO complaints (
                    complaint_id, student_id, room_id, category, description, severity, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'Pending');
                """,
                (
                    complaint_id,
                    int(student_id),
                    int(room_id),
                    category.strip(),
                    description.strip(),
                    severity.strip(),
                ),
            )
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, f"Complaint {complaint_id} logged successfully.", complaint_id
        except Exception as e:
            return False, f"Failed to log complaint: {str(e)}", None
        finally:
            if not self.db_conn:
                conn.close()

    def get_all_complaints(self, status_filter: Optional[str] = None) -> List[Complaint]:
        """READ: Retrieve complaints joined with student & room details."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            params = []
            where_sql = ""
            if status_filter and status_filter != "All":
                where_sql = "WHERE c.status = ?"
                params.append(status_filter)

            query = f"""
                SELECT c.*,
                       s.name as student_name,
                       s.student_id as student_reg_no,
                       r.room_number as room_number
                FROM complaints c
                JOIN students s ON c.student_id = s.id
                JOIN rooms r ON c.room_id = r.id
                {where_sql}
                ORDER BY c.id DESC;
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Complaint.from_row(r) for r in rows]
        finally:
            if not self.db_conn:
                conn.close()

    def update_complaint_status(
        self,
        complaint_id_str: str,
        new_status: str,
        resolution_notes: str = "",
    ) -> Tuple[bool, str]:
        """UPDATE: Advance grievance workflow status and save resolution notes."""
        valid_statuses = ["Pending", "In-Progress", "Resolved", "Closed"]
        if new_status not in valid_statuses:
            return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            resolved_at = datetime.now().isoformat() if new_status in ["Resolved", "Closed"] else None

            cursor.execute(
                """
                UPDATE complaints
                SET status = ?, resolution_notes = ?, resolved_at = ?
                WHERE complaint_id = ?;
                """,
                (new_status, resolution_notes.strip(), resolved_at, complaint_id_str.strip()),
            )
            if cursor.rowcount == 0:
                return False, "Complaint record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, f"Complaint {complaint_id_str} status updated to '{new_status}'."
        except Exception as e:
            return False, f"Error updating complaint: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()

    def delete_complaint(self, complaint_id_str: str) -> Tuple[bool, str]:
        """DELETE: Remove an erroneous complaint ticket."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM complaints WHERE complaint_id = ?;", (complaint_id_str.strip(),))
            if cursor.rowcount == 0:
                return False, "Complaint record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Complaint deleted successfully."
        except Exception as e:
            return False, f"Failed to delete complaint: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()
