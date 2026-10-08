"""Database connection manager for SQLite3 with foreign keys and WAL mode enabled.

TQM Quality Objective: Q05 - Reduce Response Time.
Enabling WAL (Write-Ahead Logging) mode significantly improves read/write concurrency
and reduces transaction overhead.
"""

import os
import sqlite3
from typing import Optional

# Default database directory and path
DEFAULT_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "hostel.db")


class DatabaseConnection:
    """Manages SQLite database connections with optimized settings."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Ensure parent directory for database exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a new SQLite connection with performance PRAGMAs.

        Returns:
            sqlite3.Connection: Configured SQLite connection.
        """
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row  # Return dict-like row access

        # Performance & Integrity Pragmas
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")  # Fast concurrent reads/writes
        cursor.execute("PRAGMA synchronous = NORMAL;") # Faster disk sync while maintaining durability
        cursor.execute("PRAGMA temp_store = MEMORY;")  # Store temp tables in RAM for fast search/sort
        cursor.close()

        return conn


# Singleton-like helper for standard access
_default_db = DatabaseConnection()


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Convenience function to get an active database connection."""
    if db_path:
        return DatabaseConnection(db_path).get_connection()
    return _default_db.get_connection()
