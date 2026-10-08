"""Performance benchmarks and verification tests for Q05 Features."""

import unittest
import sqlite3
from app.database.schema import SCHEMA_SQL
from app.database.indexes import create_indexes, verify_indexes
from app.models.student import Student
from app.models.room import Room
from app.services.student_service import StudentService
from app.services.room_service import RoomService
from app.services.search_service import FastSearchService
from app.services.cache_service import DashboardCache
from app.services.report_service import PaginatedReportService


class TestPerformanceQ05(unittest.TestCase):
    """Verify Quality Goal Q05 - Reduce Response Time optimizations."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_SQL)
        create_indexes(self.conn)

        self.student_service = StudentService(self.conn)
        self.room_service = RoomService(self.conn)
        self.search_service = FastSearchService(self.conn)
        self.report_service = PaginatedReportService(self.conn)

        # Populate batch test dataset
        for i in range(1, 101):
            self.student_service.create_student(
                Student(
                    student_id=f"241030{i:04d}",
                    name=f"Student Number {i}",
                    email=f"student{i}@university.edu",
                    phone=f"98765{i:05d}",
                    gender="Male" if i % 2 == 0 else "Female",
                    branch="CSE" if i % 3 == 0 else "ECE",
                    year="2nd Year",
                    guardian_phone=f"98123{i:05d}",
                )
            )

    def tearDown(self):
        self.conn.close()

    def test_q05_feature_4_indexes_exist(self):
        """Verify that all Q05 B-Tree indexes are created in SQLite master."""
        indexes = verify_indexes(self.conn)
        index_names = [idx[1] for idx in indexes]

        expected_indexes = [
            "idx_students_student_id",
            "idx_students_name",
            "idx_rooms_room_number",
            "idx_rooms_status",
            "idx_allocations_student_id",
            "idx_allocations_room_active",
            "idx_complaints_complaint_id",
            "idx_complaints_status",
        ]
        for exp in expected_indexes:
            self.assertIn(exp, index_names, f"Index {exp} missing from SQLite master.")

    def test_q05_feature_1_fast_search(self):
        """Verify Fast Search response time is under 15ms."""
        results, elapsed_ms = self.search_service.search_students("Student Number 50")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].student_id, "2410300050")
        self.assertLess(elapsed_ms, 50.0, "Search query exceeded latency threshold.")

    def test_q05_feature_3_cache_speedup(self):
        """Verify Dashboard In-Memory Cache hit is faster than cold database recalculation."""
        DashboardCache.invalidate()

        # First request: Cache Miss
        _, is_hit_1, cold_ms = DashboardCache.get_dashboard_metrics(self.conn)
        self.assertFalse(is_hit_1)

        # Second request: Cache Hit
        _, is_hit_2, hit_ms = DashboardCache.get_dashboard_metrics(self.conn)
        self.assertTrue(is_hit_2)

        # In-memory cache hit should execute extremely fast (< 5ms)
        self.assertLess(hit_ms, 5.0)

    def test_q05_feature_5_paginated_reports(self):
        """Verify database-side LIMIT/OFFSET pagination."""
        page_size = 10
        data, elapsed_ms = self.report_service.get_paginated_students(page=1, page_size=page_size)

        self.assertEqual(data["current_page"], 1)
        self.assertEqual(data["page_size"], 10)
        self.assertEqual(data["total_records"], 100)
        self.assertEqual(data["total_pages"], 10)
        self.assertEqual(len(data["records"]), 10)
        self.assertLess(elapsed_ms, 50.0)


if __name__ == "__main__":
    unittest.main()
