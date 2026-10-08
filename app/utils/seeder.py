"""Realistic Dataset Seeder for Demonstration and Testing.

Populates initial students, rooms, allocations, and grievance tickets.
"""

import sqlite3
from typing import Optional
from ..database.connection import get_db_connection


def seed_initial_data(conn: Optional[sqlite3.Connection] = None) -> None:
    """Populate realistic sample records across all 4 tables."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cursor = conn.cursor()

        # 1. Seed Rooms
        rooms_data = [
            ("A-101", "Block A", 1, "Single", 1, 8000.0, "Available"),
            ("A-102", "Block A", 1, "Double", 2, 5500.0, "Available"),
            ("A-103", "Block A", 1, "Double", 2, 5500.0, "Available"),
            ("A-201", "Block A", 2, "Triple", 3, 4000.0, "Available"),
            ("A-202", "Block A", 2, "Triple", 3, 4000.0, "Available"),
            ("B-101", "Block B", 1, "Single", 1, 8500.0, "Available"),
            ("B-102", "Block B", 1, "Double", 2, 6000.0, "Available"),
            ("B-201", "Block B", 2, "Double", 2, 6000.0, "Available"),
            ("B-202", "Block B", 2, "Dormitory", 4, 3000.0, "Available"),
            ("C-101", "Block C", 1, "Double", 2, 5000.0, "Maintenance"),
            ("C-102", "Block C", 1, "Double", 2, 5000.0, "Available"),
            ("PG-101", "PG Wing", 1, "Single", 1, 9500.0, "Available"),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO rooms (
                room_number, block, floor, room_type, capacity, base_fee, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            rooms_data,
        )

        # 2. Seed Students
        students_data = [
            ("2410301057", "Rohan Bakshi", "rohan.bakshi@student.edu", "9876543210", "Male", "CSE", "2nd Year", "9812345678", "Sector 14, Chandigarh"),
            ("2410301001", "Aarav Sharma", "aarav.s@student.edu", "9876500001", "Male", "CSE", "1st Year", "9812300001", "Civil Lines, Delhi"),
            ("2410301015", "Priya Verma", "priya.v@student.edu", "9876500002", "Female", "ECE", "2nd Year", "9812300002", "Indira Nagar, Lucknow"),
            ("2410301022", "Aditya Nair", "aditya.n@student.edu", "9876500003", "Male", "MECH", "3rd Year", "9812300003", "Kaloor, Kochi"),
            ("2410301034", "Sneha Patel", "sneha.p@student.edu", "9876500004", "Female", "IT", "1st Year", "9812300004", "Navrangpura, Ahmedabad"),
            ("2410301045", "Vikram Singh", "vikram.s@student.edu", "9876500005", "Male", "CIVIL", "4th Year", "9812300005", "Vaishali Nagar, Jaipur"),
            ("2410301060", "Ananya Roy", "ananya.r@student.edu", "9876500006", "Female", "AI/ML", "2nd Year", "9812300006", "Salt Lake, Kolkata"),
            ("2410301072", "Karan Mehta", "karan.m@student.edu", "9876500007", "Male", "CSE", "3rd Year", "9812300007", "Andheri West, Mumbai"),
            ("2410301088", "Tanvi Joshi", "tanvi.j@student.edu", "9876500008", "Female", "ECE", "1st Year", "9812300008", "Kothrud, Pune"),
            ("2410301099", "Rahul Deshmukh", "rahul.d@student.edu", "9876500009", "Male", "MECH", "2nd Year", "9812300009", "Viman Nagar, Pune"),
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO students (
                student_id, name, email, phone, gender, branch, year, guardian_phone, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            students_data,
        )

        # 3. Seed Allocations
        # Fetch IDs
        cursor.execute("SELECT id, student_id FROM students;")
        stud_map = {row["student_id"]: row["id"] for row in cursor.fetchall()}

        cursor.execute("SELECT id, room_number FROM rooms;")
        room_map = {row["room_number"]: row["id"] for row in cursor.fetchall()}

        allocations_data = [
            (stud_map["2410301057"], room_map["A-101"], "2026-08-01", "Paid", "Active", "Quality Lead Allotment"),
            (stud_map["2410301001"], room_map["A-102"], "2026-08-01", "Paid", "Active", "Regular Allotment"),
            (stud_map["2410301022"], room_map["A-102"], "2026-08-02", "Paid", "Active", "Roommate Pairing"),
            (stud_map["2410301015"], room_map["B-101"], "2026-08-01", "Paid", "Active", "Single Room Request"),
            (stud_map["2410301045"], room_map["B-202"], "2026-08-03", "Pending", "Active", "Fee installment pending"),
            (stud_map["2410301072"], room_map["A-201"], "2026-08-01", "Paid", "Active", "Triple sharing bed 1"),
        ]

        for s_id, r_id, alloc_date, fee_st, status, rem in allocations_data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO allocations (
                    student_id, room_id, allocation_date, fee_status, status, remarks
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (s_id, r_id, alloc_date, fee_st, status, rem),
            )

        # Update room statuses based on seeded allocations
        cursor.execute("UPDATE rooms SET status = 'Full' WHERE room_number IN ('A-101', 'A-102', 'B-101');")
        cursor.execute("UPDATE rooms SET status = 'Partially Occupied' WHERE room_number IN ('A-201', 'B-202');")

        # 4. Seed Complaints
        complaints_data = [
            ("CMP-1001", stud_map["2410301001"], room_map["A-102"], "Electrical", "Ceiling fan regulator not working on speed 3 and 4.", "Medium", "Resolved", "Regulator capacitor replaced on 05 Aug.", "2026-08-04 10:15:00", "2026-08-05 16:30:00"),
            ("CMP-1002", stud_map["2410301022"], room_map["A-102"], "Plumbing", "Bathroom tap leaking slowly.", "Low", "Closed", "Washer replaced.", "2026-08-10 11:00:00", "2026-08-11 14:00:00"),
            ("CMP-1003", stud_map["2410301045"], room_map["B-202"], "Internet", "Wi-Fi access point signal weak near balcony.", "Medium", "In-Progress", "Network team assigned ticket.", "2026-08-15 09:30:00", None),
            ("CMP-1004", stud_map["2410301057"], room_map["A-101"], "Carpentry", "Study desk drawer handle loose.", "Low", "Pending", "", "2026-08-18 14:20:00", None),
            ("CMP-1005", stud_map["2410301072"], room_map["A-201"], "Cleanliness", "Corridor water cooler tray needs cleaning.", "Low", "Resolved", "Sanitation team completed cleaning.", "2026-08-20 08:45:00", "2026-08-20 11:30:00"),
        ]

        for cid, sid, rid, cat, desc, sev, st, notes, c_at, r_at in complaints_data:
            cursor.execute(
                """
                INSERT OR IGNORE INTO complaints (
                    complaint_id, student_id, room_id, category, description, severity, status, resolution_notes, created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (cid, sid, rid, cat, desc, sev, st, notes, c_at, r_at),
            )

        conn.commit()
    finally:
        if should_close:
            conn.close()
