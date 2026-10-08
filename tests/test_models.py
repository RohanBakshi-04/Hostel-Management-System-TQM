"""Unit tests for domain models."""

import unittest
from app.models.student import Student
from app.models.room import Room
from app.models.allocation import Allocation
from app.models.complaint import Complaint


class TestModels(unittest.TestCase):
    """Test entity dataclasses and dictionary serialization."""

    def test_student_model(self):
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
        self.assertEqual(s.student_id, "2410301057")
        self.assertEqual(s.name, "Rohan Bakshi")
        d = s.to_dict()
        self.assertEqual(d["email"], "rohan@student.edu")

    def test_room_model(self):
        r = Room(
            room_number="A-101",
            block="Block A",
            floor=1,
            room_type="Single",
            capacity=1,
            base_fee=8000.0,
            status="Available",
        )
        self.assertEqual(r.room_number, "A-101")
        self.assertEqual(r.capacity, 1)
        self.assertEqual(r.base_fee, 8000.0)

    def test_allocation_model(self):
        a = Allocation(
            student_id=1,
            room_id=2,
            allocation_date="2026-08-01",
            fee_status="Paid",
            status="Active",
            remarks="Quality Lead",
        )
        self.assertEqual(a.student_id, 1)
        self.assertEqual(a.fee_status, "Paid")
        self.assertEqual(a.status, "Active")

    def test_complaint_model(self):
        c = Complaint(
            complaint_id="CMP-1001",
            student_id=1,
            room_id=2,
            category="Electrical",
            description="Fan not working",
            severity="High",
            status="Pending",
        )
        self.assertEqual(c.complaint_id, "CMP-1001")
        self.assertEqual(c.category, "Electrical")
        self.assertEqual(c.severity, "High")


if __name__ == "__main__":
    unittest.main()
