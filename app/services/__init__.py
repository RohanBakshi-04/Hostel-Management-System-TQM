"""Services package for Hostel Management System."""

from .student_service import StudentService
from .room_service import RoomService
from .allocation_service import AllocationService
from .complaint_service import ComplaintService
from .search_service import FastSearchService
from .cache_service import DashboardCache
from .report_service import PaginatedReportService

__all__ = [
    "StudentService",
    "RoomService",
    "AllocationService",
    "ComplaintService",
    "FastSearchService",
    "DashboardCache",
    "PaginatedReportService",
]
