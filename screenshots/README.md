# Application Screenshots & Visual Evidence

This directory stores visual evidence and interface walkthrough captures of the **Hostel Management System** with **Quality Goal Q05 (Reduce Response Time)**.

---

## 📸 Key View Walkthroughs

### 1. Executive Dashboard (Q05 Cached Dashboard)
- **File Reference:** `screenshots/01_cached_dashboard.png`
- **Features Highlighted:**
  - 4 Key KPI Metric Cards (Total Students, Total Rooms, Occupancy Rate %, Pending Issues).
  - Bed Capacity Breakdown & Grievance Flow Status.
  - Active Q05 Cache Hit status banner (`Loaded in 0.04 ms`).
  - Force DB Recalculation benchmark trigger.

### 2. Student Management & Q05 Fast Search
- **File Reference:** `screenshots/02_student_management.png`
- **Features Highlighted:**
  - Student directory table with registration details.
  - Fast search query execution (`⚡ Q05 Fast Search: 1 matches in 0.28 ms`).
  - Modal registration dialog with Poka-Yoke input validation.

### 3. Room Inventory & Capacity Controls
- **File Reference:** `screenshots/03_room_inventory.png`
- **Features Highlighted:**
  - Real-time room occupancy indicators (e.g. `2 / 2 beds occupied`).
  - Room status badges (`Available`, `Partially Occupied`, `Full`, `Maintenance`).

### 4. Room Allocation & Capacity Guards
- **File Reference:** `screenshots/04_room_allocation.png`
- **Features Highlighted:**
  - Active and historical student-to-room allocations table.
  - Poka-Yoke room capacity ceiling prevention dialog.
  - Student check-out / vacating action.

### 5. Complaint & Grievance Redressal
- **File Reference:** `screenshots/05_complaint_redressal.png`
- **Features Highlighted:**
  - Maintenance ticketing table.
  - Category, severity, and workflow status filters.
  - Ticket resolution modal with repair notes.

### 6. Q05 Paginated Master Audit Reports
- **File Reference:** `screenshots/06_paginated_reports.png`
- **Features Highlighted:**
  - SQL LIMIT/OFFSET pagination controls (`⏮ First`, `◀ Prev`, `Page X of Y`, `Next ▶`, `Last ⏭`).
  - Dynamic page size selector (`5`, `10`, `20`, `50` rows per page).
  - Microsecond latency badge and $O(1)$ constant memory profile note.
