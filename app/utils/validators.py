"""Poka-Yoke Input Validation Utilities.

TQM Principle: Error Prevention (Poka-Yoke) - Stop defects before they enter the database.
"""

import re
from typing import Tuple


def validate_student_data(
    student_id: str,
    name: str,
    email: str,
    phone: str,
    gender: str,
    branch: str,
    year: str,
    guardian_phone: str,
) -> Tuple[bool, str]:
    """Validate student registration and update payload.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not student_id or not student_id.strip():
        return False, "Student ID / Roll Number is required."

    if not re.match(r"^[A-Za-z0-9\-_/]{3,20}$", student_id.strip()):
        return False, "Student ID must be 3-20 alphanumeric characters (symbols allowed: - _ /)."

    if not name or len(name.strip()) < 2:
        return False, "Full Name must be at least 2 characters long."

    if not re.match(r"^[A-Za-z\s.'-]+$", name.strip()):
        return False, "Student Name contains invalid characters."

    # Email validation
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not email or not re.match(email_regex, email.strip()):
        return False, "Please provide a valid email address (e.g. name@university.edu)."

    # Phone validation (10 digits)
    phone_clean = re.sub(r"[\s\-\(\)\+]", "", phone.strip())
    if not phone_clean.isdigit() or len(phone_clean) < 10 or len(phone_clean) > 13:
        return False, "Student contact number must be a valid 10-13 digit phone number."

    # Guardian phone validation
    gphone_clean = re.sub(r"[\s\-\(\)\+]", "", guardian_phone.strip())
    if not gphone_clean.isdigit() or len(gphone_clean) < 10 or len(gphone_clean) > 13:
        return False, "Guardian contact number must be a valid 10-13 digit phone number."

    if not gender or gender not in ["Male", "Female", "Other"]:
        return False, "Please select a valid gender."

    if not branch or not branch.strip():
        return False, "Academic branch is required."

    if not year or not year.strip():
        return False, "Academic year is required."

    return True, ""


def validate_room_data(
    room_number: str,
    block: str,
    floor: any,
    room_type: str,
    capacity: any,
    base_fee: any,
) -> Tuple[bool, str]:
    """Validate room creation/update inputs.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not room_number or not room_number.strip():
        return False, "Room Number is required (e.g. A-101)."

    if not re.match(r"^[A-Za-z0-9\-]{2,15}$", room_number.strip()):
        return False, "Room Number should be 2-15 alphanumeric characters (e.g. A-101, B202)."

    if not block or not block.strip():
        return False, "Hostel Block / Wing is required."

    try:
        floor_int = int(floor)
        if floor_int < 0 or floor_int > 25:
            return False, "Floor must be an integer between 0 and 25."
    except (ValueError, TypeError):
        return False, "Floor must be a valid integer number."

    if not room_type or room_type not in ["Single", "Double", "Triple", "Dormitory"]:
        return False, "Room type must be Single, Double, Triple, or Dormitory."

    try:
        capacity_int = int(capacity)
        if capacity_int < 1 or capacity_int > 6:
            return False, "Capacity must be between 1 and 6 beds."
    except (ValueError, TypeError):
        return False, "Capacity must be a valid positive integer."

    try:
        fee_float = float(base_fee)
        if fee_float < 0:
            return False, "Base fee cannot be negative."
    except (ValueError, TypeError):
        return False, "Base fee must be a valid numeric amount."

    return True, ""


def validate_complaint_data(
    student_id: int,
    room_id: int,
    category: str,
    description: str,
    severity: str,
) -> Tuple[bool, str]:
    """Validate complaint ticket submission.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not student_id or int(student_id) <= 0:
        return False, "Valid Student reference is required."

    if not room_id or int(room_id) <= 0:
        return False, "Valid Room reference is required."

    valid_cats = ["Electrical", "Plumbing", "Cleanliness", "Carpentry", "Internet", "Other"]
    if not category or category not in valid_cats:
        return False, f"Category must be one of: {', '.join(valid_cats)}"

    if not description or len(description.strip()) < 5:
        return False, "Description must be at least 5 characters long."

    valid_sevs = ["Low", "Medium", "High", "Critical"]
    if not severity or severity not in valid_sevs:
        return False, f"Severity must be one of: {', '.join(valid_sevs)}"

    return True, ""
