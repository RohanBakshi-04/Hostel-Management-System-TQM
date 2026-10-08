"""Allocation data model."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Allocation:
    """Represents a student room allocation entity."""
    student_id: int  # Foreign Key to students.id
    room_id: int     # Foreign Key to rooms.id
    allocation_date: str
    fee_status: str = "Pending"  # Paid, Pending, Overdue
    status: str = "Active"       # Active, Vacated
    remarks: str = ""
    id: Optional[int] = None
    created_at: Optional[str] = None
    # Joined metadata fields for presentation
    student_name: Optional[str] = None
    student_reg_no: Optional[str] = None
    room_number: Optional[str] = None
    room_block: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert allocation entity to dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row) -> "Allocation":
        """Create Allocation instance from SQLite Row."""
        keys = row.keys()
        return cls(
            id=row["id"] if "id" in keys else None,
            student_id=row["student_id"],
            room_id=row["room_id"],
            allocation_date=row["allocation_date"],
            fee_status=row["fee_status"],
            status=row["status"],
            remarks=row["remarks"] if "remarks" in keys else "",
            created_at=row["created_at"] if "created_at" in keys else None,
            student_name=row["student_name"] if "student_name" in keys else None,
            student_reg_no=row["student_reg_no"] if "student_reg_no" in keys else None,
            room_number=row["room_number"] if "room_number" in keys else None,
            room_block=row["room_block"] if "room_block" in keys else None,
        )
