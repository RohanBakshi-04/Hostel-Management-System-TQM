"""Database schema definition and table initialization.

Course: BBAT104 - Fundamentals of TQM
Student: Rohan Bakshi (2410301057)
Quality Goal: Q05 - Reduce Response Time
"""

import sqlite3
from typing import Optional
from .connection import get_db_connection


SCHEMA_SQL = """
-- 1. Students Table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    gender TEXT NOT NULL,
    branch TEXT NOT NULL,
    year TEXT NOT NULL,
    guardian_phone TEXT NOT NULL,
    address TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT NOT NULL UNIQUE,
    block TEXT NOT NULL,
    floor INTEGER NOT NULL CHECK(floor >= 0),
    room_type TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity BETWEEN 1 AND 6),
    base_fee REAL NOT NULL CHECK(base_fee >= 0),
    status TEXT NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Room Allocations Table
CREATE TABLE IF NOT EXISTS allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    allocation_date TEXT NOT NULL,
    fee_status TEXT NOT NULL DEFAULT 'Pending',
    status TEXT NOT NULL DEFAULT 'Active',
    remarks TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT NOT NULL UNIQUE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'Medium',
    status TEXT NOT NULL DEFAULT 'Pending',
    resolution_notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL
);
"""


def initialize_schema(conn: Optional[sqlite3.Connection] = None) -> None:
    """Initialize all database tables if they do not already exist.

    Args:
        conn: Optional SQLite connection. If None, default connection is used.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        if should_close:
            conn.close()


if __name__ == "__main__":
    print("Initializing Database Schema...")
    initialize_schema()
    print("Database Schema initialized successfully.")
