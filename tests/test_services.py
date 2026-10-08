"""Integration tests for CRUD Services and transactional workflows."""

import unittest
import sqlite3
from app.database.schema import SCHEMA_SQL
from app.database.indexes import create_indexes
from app.models.student import Student
from app.models.room import Room
from app.services.student_service import StudentService
from app.services.room_service import RoomService
from app.services.allocation_service import AllocationService
from app.services.complaint_service import ComplaintService


class TestServices(unittest.TestCase):
    """Test full CRUD operations on isolated in-memory SQLite database."""

    def setUp(self):
        # Create dedicated in-memory database with full schema and indexes
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        create_indexes(self.conn)

        self.student_service = StudentService(self.conn)
        self.room_service = RoomService(self.conn)
        self.allocation_service = AllocationService(self.conn)
        self.complaint_service = ComplaintService(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_student_crud(self):
        # 1. CREATE
        s = Student(
            student_id="2410301057",
            name="Rohan Bakshi",
            email="rohan@student.edu",
            phone="9876543210",
            gender="Male",
            branch="CSE",
            year="2nd Year",
            guardian_phone="9812345678",
            address="Campus Block",
        )
        success, msg, new_id = self.student_service.create_student(s)
        self.assertTrue(success, msg)
        self.assertIsNotNone(new_id)

        # 2. READ
        fetched = self.student_service.get_student_by_id(new_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Rohan Bakshi")

        # 3. UPDATE
        fetched.name = "Rohan Bakshi (Senior)"
        success, msg = self.student_service.update_student(fetched)
        self.assertTrue(success, msg)

        updated = self.student_service.get_student_by_id(new_id)
        self.assertEqual(updated.name, "Rohan Bakshi (Senior)")

        # 4. DELETE
        success, msg = self.student_service.delete_student(new_id)
        self.assertTrue(success, msg)
        self.assertIsNone(self.student_service.get_student_by_id(new_id))

    def test_room_crud(self):
        # 1. CREATE
        r = Room(
            room_number="A-101",
            block="Block A",
            floor=1,
            room_type="Single",
            capacity=1,
            base_fee=6000.0,
        )
        success, msg, r_id = self.room_service.create_room(r)
        self.assertTrue(success, msg)

        # 2. READ
        room = self.room_service.get_room_by_id(r_id)
        self.assertIsNotNone(room)
        self.assertEqual(room.room_number, "A-101")

        # 3. UPDATE
        room.base_fee = 6500.0
        success, msg = self.room_service.update_room(room)
        self.assertTrue(success, msg)

        # 4. DELETE
        success, msg = self.room_service.delete_room(r_id)
        self.assertTrue(success, msg)

    def test_allocation_workflow_and_capacity_guard(self):
        # Setup student & single room
        _, _, s1_id = self.student_service.create_student(
            Student("2410301057", "Rohan Bakshi", "r@edu.com", "9876543210", "Male", "CSE", "2nd Year", "9812345678")
        )
        _, _, s2_id = self.student_service.create_student(
            Student("2410301001", "Aarav Sharma", "a@edu.com", "9876543211", "Male", "CSE", "1st Year", "9812345679")
        )
        _, _, r_id = self.room_service.create_room(
            Room("A-101", "Block A", 1, "Single", 1, 6000.0)
        )

        # 1. First Allocation should succeed
        success, msg, a1_id = self.allocation_service.allocate_room(
            student_id=s1_id,
            room_id=r_id,
            allocation_date="2026-08-01",
            fee_status="Paid",
        )
        self.assertTrue(success, msg)

        # 2. Second Allocation to full room should fail (Poka-Yoke capacity guard)
        success, msg, _ = self.allocation_service.allocate_room(
            student_id=s2_id,
            room_id=r_id,
            allocation_date="2026-08-01",
        )
        self.assertFalse(success)
        self.assertIn("full capacity", msg.lower())

        # 3. Vacate allocation
        success, msg = self.allocation_service.vacate_allocation(a1_id)
        self.assertTrue(success, msg)

        # Room should now be available again for s2
        success, msg, _ = self.allocation_service.allocate_room(
            student_id=s2_id,
            room_id=r_id,
            allocation_date="2026-08-02",
        )
        self.assertTrue(success, msg)

    def test_complaint_lifecycle(self):
        _, _, s_id = self.student_service.create_student(
            Student("2410301057", "Rohan Bakshi", "r@edu.com", "9876543210", "Male", "CSE", "2nd Year", "9812345678")
        )
        _, _, r_id = self.room_service.create_room(
            Room("A-101", "Block A", 1, "Single", 1, 6000.0)
        )

        # 1. Create Complaint
        success, msg, ticket_id = self.complaint_service.create_complaint(
            student_id=s_id,
            room_id=r_id,
            category="Electrical",
            description="Switchboard spark issue",
            severity="High",
        )
        self.assertTrue(success, msg)
        self.assertIsNotNone(ticket_id)

        # 2. Update Status to Resolved
        success, msg = self.complaint_service.update_complaint_status(
            ticket_id, "Resolved", "Replaced wiring and fuse."
        )
        self.assertTrue(success, msg)


if __name__ == "__main__":
    unittest.main()
