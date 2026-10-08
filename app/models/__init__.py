"""Domain models package for Hostel Management System."""

from .student import Student
from .room import Room
from .allocation import Allocation
from .complaint import Complaint

__all__ = ["Student", "Room", "Allocation", "Complaint"]
