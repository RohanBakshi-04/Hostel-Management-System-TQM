"""Q05 Performance Optimization: Database Indexing Manager.

TQM Quality Goal: Q05 - Reduce Response Time.

Purpose:
Without indexes, SQLite performs full table scans (O(N) time complexity),
reading every row sequentially from disk. By creating B-Tree indexes on
frequently searched and joined columns, query execution is accelerated
to O(log N) logarithmic lookup time.

Indexed Vectors:
1. students(student_id) -> Accelerates fast search by roll/reg number.
2. students(name) -> Accelerates keyword searches on student names.
3. rooms(room_number) -> Accelerates room allocation and room search.
4. rooms(status) -> Accelerates filtering available/occupied rooms.
5. allocations(student_id) -> Accelerates checking student allocation history.
6. allocations(room_id, status) -> Accelerates live occupancy calculation per room.
7. complaints(complaint_id) -> Accelerates complaint ticket tracking.
8. complaints(status) -> Accelerates dashboard pending/resolved complaint counts.
"""

import sqlite3
from typing import List, Optional, Tuple
from .connection import get_db_connection

INDEX_DEFINITIONS = [
    # Table, Index Name, Columns, Is Unique, Rationale
    (
        "students",
        "idx_students_student_id",
        "student_id",
        True,
        "Q05 Fast Search: O(log N) direct student registration lookup",
    ),
    (
        "students",
        "idx_students_name",
        "name",
        False,
        "Q05 Fast Search: Sub-millisecond name prefix and autocomplete queries",
    ),
    (
        "rooms",
        "idx_rooms_room_number",
        "room_number",
        True,
        "Q05 Fast Search: Instant room number lookups during allocation",
    ),
    (
        "rooms",
        "idx_rooms_status",
        "status",
        False,
        "Q05 Dashboard & Filter: Rapid filtering by room occupancy status",
    ),
    (
        "allocations",
        "idx_allocations_student_id",
        "student_id",
        False,
        "Q05 Relational Integrity: Fast verification of existing allocations",
    ),
    (
        "allocations",
        "idx_allocations_room_active",
        "room_id, status",
        False,
        "Q05 Capacity Check: Composite index for instant active bed counting",
    ),
    (
        "complaints",
        "idx_complaints_complaint_id",
        "complaint_id",
        True,
        "Q05 Fast Search: Instant ticket status retrieval by tracking code",
    ),
    (
        "complaints",
        "idx_complaints_status",
        "status",
        False,
        "Q05 Dashboard Caching & Metric aggregation by grievance status",
    ),
]


def create_indexes(conn: Optional[sqlite3.Connection] = None) -> List[str]:
    """Create all performance-optimizing B-Tree indexes.

    Args:
        conn: Optional SQLite connection.

    Returns:
        List[str]: List of successfully ensured index names.
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    created = []
    try:
        cursor = conn.cursor()
        for table, index_name, columns, is_unique, _ in INDEX_DEFINITIONS:
            unique_kw = "UNIQUE" if is_unique else ""
            sql = f"CREATE {unique_kw} INDEX IF NOT EXISTS {index_name} ON {table}({columns});"
            cursor.execute(sql)
            created.append(index_name)
        conn.commit()
    finally:
        if should_close:
            conn.close()

    return created


def verify_indexes(conn: Optional[sqlite3.Connection] = None) -> List[Tuple[str, str, str]]:
    """Verify and list all active indexes present in the SQLite catalog.

    Returns:
        List[Tuple[str, str, str]]: Tuples of (table_name, index_name, sql).
    """
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tbl_name, name, sql
            FROM sqlite_master
            WHERE type = 'index' AND name NOT LIKE 'sqlite_autoindex%'
            ORDER BY tbl_name, name;
            """
        )
        return cursor.fetchall()
    finally:
        if should_close:
            conn.close()


if __name__ == "__main__":
    print("Creating Q05 Performance Indexes...")
    indexes = create_indexes()
    print(f"Created {len(indexes)} indexes successfully:")
    for idx in indexes:
        print(f" - {idx}")
