"""Complaint data model."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Complaint:
    """Represents a complaint / grievance ticket entity."""
    complaint_id: str
    student_id: int    # Foreign Key to students.id
    room_id: int       # Foreign Key to rooms.id
    category: str      # Electrical, Plumbing, Cleanliness, Carpentry, Internet, Other
    description: str
    severity: str = "Medium"  # Low, Medium, High, Critical
    status: str = "Pending"   # Pending, In-Progress, Resolved, Closed
    resolution_notes: str = ""
    id: Optional[int] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
    # Joined metadata fields for presentation
    student_name: Optional[str] = None
    student_reg_no: Optional[str] = None
    room_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert complaint entity to dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row) -> "Complaint":
        """Create Complaint instance from SQLite Row."""
        keys = row.keys()
        return cls(
            id=row["id"] if "id" in keys else None,
            complaint_id=row["complaint_id"],
            student_id=row["student_id"],
            room_id=row["room_id"],
            category=row["category"],
            description=row["description"],
            severity=row["severity"],
            status=row["status"],
            resolution_notes=row["resolution_notes"] if "resolution_notes" in keys else "",
            created_at=row["created_at"] if "created_at" in keys else None,
            resolved_at=row["resolved_at"] if "resolved_at" in keys else None,
            student_name=row["student_name"] if "student_name" in keys else None,
            student_reg_no=row["student_reg_no"] if "student_reg_no" in keys else None,
            room_number=row["room_number"] if "room_number" in keys else None,
        )
