"""Student Service - Handles business logic and CRUD operations for students."""

import sqlite3
from typing import List, Optional, Tuple
from ..database.connection import get_db_connection
from ..models.student import Student
from ..utils.validators import validate_student_data


class StudentService:
    """Provides complete CRUD operations for Student records."""

    def __init__(self, db_conn: Optional[sqlite3.Connection] = None):
        self.db_conn = db_conn

    def _get_conn(self) -> sqlite3.Connection:
        if self.db_conn:
            return self.db_conn
        return get_db_connection()

    def create_student(self, student: Student) -> Tuple[bool, str, Optional[int]]:
        """CREATE: Register a new student into the database with Poka-Yoke validation.

        Returns:
            Tuple[bool, str, Optional[int]]: (success, message, new_record_id)
        """
        is_valid, err_msg = validate_student_data(
            student.student_id,
            student.name,
            student.email,
            student.phone,
            student.gender,
            student.branch,
            student.year,
            student.guardian_phone,
        )
        if not is_valid:
            return False, err_msg, None

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO students (
                    student_id, name, email, phone, gender, branch, year, guardian_phone, address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    student.student_id.strip(),
                    student.name.strip(),
                    student.email.strip().lower(),
                    student.phone.strip(),
                    student.gender,
                    student.branch.strip(),
                    student.year.strip(),
                    student.guardian_phone.strip(),
                    student.address.strip(),
                ),
            )
            new_id = cursor.lastrowid
            conn.commit()

            # Invalidate dashboard cache on data write
            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Student registered successfully.", new_id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: students.student_id" in str(e):
                return False, f"A student with ID '{student.student_id}' already exists.", None
            return False, f"Database integrity error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
        finally:
            if not self.db_conn:
                conn.close()

    def get_student_by_id(self, pk_id: int) -> Optional[Student]:
        """READ: Retrieve single student by primary key."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = ?;", (pk_id,))
            row = cursor.fetchone()
            if row:
                return Student.from_row(row)
            return None
        finally:
            if not self.db_conn:
                conn.close()

    def get_student_by_reg_no(self, student_id: str) -> Optional[Student]:
        """READ: Retrieve student by unique registration roll number (Uses Q05 Index)."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id.strip(),))
            row = cursor.fetchone()
            if row:
                return Student.from_row(row)
            return None
        finally:
            if not self.db_conn:
                conn.close()

    def get_all_students(self, limit: int = 1000) -> List[Student]:
        """READ: Retrieve all registered students ordered by newest first."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT ?;", (limit,))
            rows = cursor.fetchall()
            return [Student.from_row(r) for r in rows]
        finally:
            if not self.db_conn:
                conn.close()

    def update_student(self, student: Student) -> Tuple[bool, str]:
        """UPDATE: Modify existing student details."""
        if not student.id:
            return False, "Student Primary Key ID is missing for update."

        is_valid, err_msg = validate_student_data(
            student.student_id,
            student.name,
            student.email,
            student.phone,
            student.gender,
            student.branch,
            student.year,
            student.guardian_phone,
        )
        if not is_valid:
            return False, err_msg

        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE students
                SET student_id = ?, name = ?, email = ?, phone = ?, gender = ?,
                    branch = ?, year = ?, guardian_phone = ?, address = ?
                WHERE id = ?;
                """,
                (
                    student.student_id.strip(),
                    student.name.strip(),
                    student.email.strip().lower(),
                    student.phone.strip(),
                    student.gender,
                    student.branch.strip(),
                    student.year.strip(),
                    student.guardian_phone.strip(),
                    student.address.strip(),
                    student.id,
                ),
            )
            if cursor.rowcount == 0:
                return False, "Student record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Student updated successfully."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: students.student_id" in str(e):
                return False, f"Another student already has ID '{student.student_id}'.", None
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()

    def delete_student(self, pk_id: int) -> Tuple[bool, str]:
        """DELETE: Remove a student record after referential safety checks."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Safety check: Verify student does not have an active room allocation
            cursor.execute(
                "SELECT COUNT(*) FROM allocations WHERE student_id = ? AND status = 'Active';",
                (pk_id,),
            )
            active_allocations = cursor.fetchone()[0]
            if active_allocations > 0:
                return False, "Cannot delete student with an active room allocation. Please de-allocate first."

            cursor.execute("DELETE FROM students WHERE id = ?;", (pk_id,))
            if cursor.rowcount == 0:
                return False, "Student record not found."
            conn.commit()

            from .cache_service import DashboardCache
            DashboardCache.invalidate()

            return True, "Student deleted successfully."
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
        finally:
            if not self.db_conn:
                conn.close()
