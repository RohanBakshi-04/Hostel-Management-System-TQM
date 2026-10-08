"""Student data model."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Student:
    """Represents a student entity in the Hostel Management System."""
    student_id: str
    name: str
    email: str
    phone: str
    gender: str
    branch: str
    year: str
    guardian_phone: str
    address: str = ""
    id: Optional[int] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert student entity to dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row) -> "Student":
        """Create Student instance from SQLite Row."""
        return cls(
            id=row["id"] if "id" in row.keys() else None,
            student_id=row["student_id"],
            name=row["name"],
            email=row["email"],
            phone=row["phone"],
            gender=row["gender"],
            branch=row["branch"],
            year=row["year"],
            guardian_phone=row["guardian_phone"],
            address=row["address"] if "address" in row.keys() else "",
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )
