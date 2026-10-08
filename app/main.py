"""Main Application Entry Point for Hostel Management System (HMS).

Course: BBAT104 - Fundamentals of Total Quality Management (TQM)
Student: Rohan Bakshi
Roll No: 2410301057
Quality Goal: Q05 - Reduce Response Time
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import get_db_connection
from app.database.schema import initialize_schema
from app.database.indexes import create_indexes
from app.utils.seeder import seed_initial_data
from app.ui.main_window import MainWindow


def bootstrap_application():
    """Bootstrap database, apply schema, create indexes, and seed sample records."""
    print("==================================================================")
    print(" HOSTEL MANAGEMENT SYSTEM - TQM QUALITY ENGINEERING (Q05)")
    print(" Student: Rohan Bakshi | Roll No: 2410301057 | Academic: 2026-27")
    print("==================================================================")

    # 1. Initialize schema
    print("[1/3] Checking SQLite schema & tables...")
    initialize_schema()

    # 2. Ensure Q05 B-Tree Indexes
    print("[2/3] Ensuring Q05 Performance B-Tree Indexes...")
    indexes = create_indexes()
    print(f"      Active Indexes: {len(indexes)} verified.")

    # 3. Seed Realistic Data if empty
    print("[3/3] Checking dataset and seeding initial records...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_initial_data(conn)
            print("      Initial demo dataset seeded successfully.")
        else:
            print(f"      Database ready ({count} student records found).")
    finally:
        conn.close()

    print("------------------------------------------------------------------")
    print("[Q05] System Ready. Launching GUI Application...")
    print("------------------------------------------------------------------")


def main():
    """Launch the Tkinter desktop GUI."""
    try:
        bootstrap_application()
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Fatal Startup Error: {e}", file=sys.stderr)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
