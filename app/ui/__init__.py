"""UI Package for Hostel Management System."""

from .main_window import MainWindow
from .dashboard import DashboardView
from .students import StudentView
from .rooms import RoomView
from .allocations import AllocationView
from .complaints import ComplaintView
from .reports import ReportView

__all__ = [
    "MainWindow",
    "DashboardView",
    "StudentView",
    "RoomView",
    "AllocationView",
    "ComplaintView",
    "ReportView",
]
