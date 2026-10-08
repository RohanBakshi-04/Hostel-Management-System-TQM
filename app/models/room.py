"""Room data model."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Room:
    """Represents a room inventory entity in the Hostel Management System."""
    room_number: str
    block: str
    floor: int
    room_type: str
    capacity: int
    base_fee: float
    status: str = "Available"  # Available, Partially Occupied, Full, Maintenance
    id: Optional[int] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert room entity to dictionary."""
        return asdict(self)

    @classmethod
    def from_row(cls, row) -> "Room":
        """Create Room instance from SQLite Row."""
        return cls(
            id=row["id"] if "id" in row.keys() else None,
            room_number=row["room_number"],
            block=row["block"],
            floor=int(row["floor"]),
            room_type=row["room_type"],
            capacity=int(row["capacity"]),
            base_fee=float(row["base_fee"]),
            status=row["status"],
            created_at=row["created_at"] if "created_at" in row.keys() else None,
        )
