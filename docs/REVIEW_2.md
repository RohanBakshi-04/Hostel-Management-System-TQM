# Review 2: Base System & CRUD with Q05 Execution Guide

**Course Code:** BBAT104 – Fundamentals of Total Quality Management (TQM)  
**Academic Session:** 2026–27  
**Max Raw Marks:** 15 Marks (Mapped COs: CO1, CO2)  
**Student Name:** Rohan Bakshi  
**University Roll Number:** 2410301057  
**Branch & Section:** B.Tech CSE (Section A)  
**Assigned Baseline System:** Hostel Management System (Topic Digit: 7)  
**Assigned Quality Goal:** **Q05 – REDUCE RESPONSE TIME**  

---

## 1. Review 2 Deliverables Checklist

| Review 2 Evaluation Criterion | Implementation Evidence | Status |
| :--- | :--- | :---: |
| **Application Launch & Bootstrapping** | Automated database creation, schema setup, index creation, and seeder | **PASS [✅]** |
| **Student Management (Full CRUD)** | Create, Read, Update, Delete with Poka-Yoke input validation | **PASS [✅]** |
| **Room Management (Full CRUD)** | Capacity controls, occupancy indicators, maintenance status flag | **PASS [✅]** |
| **Room Allocation Module** | Allocation workflow with automated capacity ceiling guards | **PASS [✅]** |
| **Complaint Management Module** | Maintenance ticketing with status lifecycle & resolution logging | **PASS [✅]** |
| **Q05 Feature #1: Fast Search** | Parameterized SQL WHERE/LIKE queries ($< 1\text{ ms}$) | **PASS [✅]** |
| **Q05 Feature #2: Quick Navigation** | Persistent in-memory frame switching ($< 0.5\text{ ms}$) | **PASS [✅]** |
| **Q05 Feature #3: Cached Dashboard** | In-memory metric caching with reactive write invalidation ($< 0.1\text{ ms}$) | **PASS [✅]** |
| **Q05 Feature #4: Database Indexing** | 8 dedicated B-Tree indexes accelerating lookups from $O(N)$ to $O(\log N)$ | **PASS [✅]** |
| **Q05 Feature #5: Paginated Reports** | Database-side SQL LIMIT/OFFSET pagination with constant $O(1)$ memory | **PASS [✅]** |
| **Automated Testing Suite** | 18 unit, integration, and latency benchmark tests (100% passing) | **PASS [✅]** |
| **Git Repository Health** | 35+ structured conventional commits | **PASS [✅]** |

---

## 2. Step-by-Step Live Demonstration Script for Review 2

Follow this sequence during your live software evaluation:

### Step 1: Launch Application
```bash
python -m app.main
```
*Point out to evaluators: The console displays the automated database initialization, B-Tree index verification, and sample dataset seeding.*

### Step 2: Demonstrate Q05 Cached Dashboard
1. Show the **Executive Dashboard**. Highlight the 4 KPI cards and capacity breakdown.
2. Point to the green status banner: `⚡ Q05 CACHE HIT: In-Memory snapshot loaded in 0.04 ms`.
3. Click **🔄 Force DB Recalculation**: Show how a cold query executes against SQLite ($\approx 3-5\text{ ms}$).
4. Switch tabs and switch back: Show that the system immediately serves from memory with zero database roundtrips.

### Step 3: Demonstrate Q05 Quick Navigation
1. Switch rapidly between **Students**, **Rooms**, **Allocations**, **Complaints**, and **Reports**.
2. Point to the bottom status bar: `Q05 Quick Navigation: Switched in 0.18 ms`.
3. Explain to evaluators: All views are pre-instantiated in memory, eliminating UI redraw delay.

### Step 4: Demonstrate Student CRUD & Q05 Fast Search
1. Click **➕ Register Student**: Fill in a new student (e.g., `2410301099`, `Kavya Sharma`). Show that entering an invalid phone or email triggers a friendly Poka-Yoke error dialog.
2. Save the valid record: Note how the table updates instantly.
3. In the **Fast Search** bar, type `Kavya` and hit Enter: Point to the latency timer: `⚡ Q05 Fast Search: 1 matches in 0.28 ms`.
4. Click **✏️ Edit Selected** to modify contact details.

### Step 5: Demonstrate Room Management & Allocation Guards
1. Navigate to **Rooms**: Show the room list with real-time bed occupancy (e.g., `2 / 2 beds occupied (0 free)`).
2. Navigate to **Allocations**: Click **➕ New Bed Allocation**.
3. Attempt to allocate a student to room `A-101` (which is already full): Show that the Poka-Yoke guard prevents over-allocation with an error message.
4. Allocate to an available room: Note that the room's occupancy status updates dynamically to `Full` or `Partially Occupied`.
5. Select an allocation and click **🚪 Vacate / Check-Out Student**: Show that the bed is restored immediately to `Available`.

### Step 6: Demonstrate Complaint Management
1. Navigate to **Complaints**: Show existing maintenance tickets.
2. Click **➕ Log Complaint** to file a ticket.
3. Select an open ticket and click **⚡ Resolve / Update Ticket**: Change status from `Pending` to `Resolved` and input repair notes.

### Step 7: Demonstrate Q05 Paginated Reports
1. Navigate to **Paginated Reports**.
2. Select report type: `Allocations`, `Students`, or `Complaints`.
3. Change rows per page between `5`, `10`, and `20`.
4. Click **Next ▶** and **Last ⏭**: Highlight the latency badge (`⚡ Page Sliced in 1.10 ms`). Explain that memory consumption remains constant regardless of total table rows.

### Step 8: Show Git Commit History & Test Suite
1. Run `python -m unittest discover tests` in terminal: Show all 18 automated tests passing in $< 0.05\text{ s}$.
2. Run `git log --oneline`: Show $\ge 35$ structured commits showing clear engineering progression.

---

## 3. Review 2 Viva Defense Quick-Sheet

- **Why does Fast Search improve response time?**  
  *It delegates pattern matching to SQLite's native C-engine using parameterized SQL `WHERE/LIKE` and B-Tree indexes, avoiding full memory extraction into Python lists.*
- **What is the cache invalidation strategy?**  
  *Write-through invalidation: whenever a CREATE, UPDATE, or DELETE operation succeeds in any module, `DashboardCache.invalidate()` marks the cache dirty so subsequent requests pull fresh data.*
- **How does B-Tree indexing change algorithmic complexity?**  
  *From linear scan $O(N)$ down to logarithmic tree search $O(\log N)$.*
- **Why is Limit/Offset pagination critical for TQM?**  
  *It eliminates UI thread freezing by fetching strictly the rows required for the visible page, ensuring consistent sub-5ms rendering times even as historical logs scale.*
