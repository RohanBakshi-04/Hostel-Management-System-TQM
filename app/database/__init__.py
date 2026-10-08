"""Database package for Hostel Management System."""
from .connection import DatabaseConnection, get_db_connection

__all__ = ["DatabaseConnection", "get_db_connection"]
