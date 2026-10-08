"""Unit tests for Poka-Yoke input validators."""

import unittest
from app.utils.validators import (
    validate_student_data,
    validate_room_data,
    validate_complaint_data,
)


class TestValidators(unittest.TestCase):
    """Test boundary conditions and error prevention mechanisms."""

    def test_student_validator_success(self):
        valid, msg = validate_student_data(
            student_id="2410301057",
            name="Rohan Bakshi",
            email="rohan@student.edu",
            phone="9876543210",
            gender="Male",
            branch="CSE",
            year="2nd Year",
            guardian_phone="9812345678",
        )
        self.assertTrue(valid)
        self.assertEqual(msg, "")

    def test_student_validator_invalid_email(self):
        valid, msg = validate_student_data(
            student_id="2410301057",
            name="Rohan Bakshi",
            email="invalid-email-address",
            phone="9876543210",
            gender="Male",
            branch="CSE",
            year="2nd Year",
            guardian_phone="9812345678",
        )
        self.assertFalse(valid)
        self.assertIn("valid email", msg.lower())

    def test_student_validator_invalid_phone(self):
        valid, msg = validate_student_data(
            student_id="2410301057",
            name="Rohan Bakshi",
            email="rohan@student.edu",
            phone="12345",  # Too short
            gender="Male",
            branch="CSE",
            year="2nd Year",
            guardian_phone="9812345678",
        )
        self.assertFalse(valid)
        self.assertIn("phone", msg.lower())

    def test_room_validator_success(self):
        valid, msg = validate_room_data(
            room_number="A-101",
            block="Block A",
            floor=1,
            room_type="Single",
            capacity=1,
            base_fee=5000.0,
        )
        self.assertTrue(valid)

    def test_room_validator_invalid_capacity(self):
        valid, msg = validate_room_data(
            room_number="A-101",
            block="Block A",
            floor=1,
            room_type="Single",
            capacity=10,  # Exceeds max 6
            base_fee=5000.0,
        )
        self.assertFalse(valid)
        self.assertIn("capacity", msg.lower())

    def test_complaint_validator_empty_description(self):
        valid, msg = validate_complaint_data(
            student_id=1,
            room_id=1,
            category="Electrical",
            description="",  # Empty
            severity="Medium",
        )
        self.assertFalse(valid)
        self.assertIn("description", msg.lower())


if __name__ == "__main__":
    unittest.main()
