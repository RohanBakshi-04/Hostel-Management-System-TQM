# Viva Voce Examination & Defense Manual

**Course:** BBAT104 – Fundamentals of Total Quality Management (TQM)  
**Academic Session:** 2026–27  
**Student Name:** Rohan Bakshi  
**Roll / Registration Number:** 2410301057  
**Branch:** B.Tech CSE (Section A)  
**Assigned Baseline System:** Hostel Management System (Topic Digit: 7)  
**Assigned Quality Goal:** **Q05 – REDUCE RESPONSE TIME**  

---

## 🎯 25 Core Viva Questions and Model Answers

### Q1: What is Total Quality Management (TQM)?
**Answer:**  
Total Quality Management (TQM) is an organization-wide management approach aimed at continuously improving the quality of products, processes, and services to achieve customer satisfaction. In software engineering, TQM involves designing defect-free systems (Poka-Yoke), establishing measurable Critical-to-Quality (CTQ) parameters, optimizing operational performance, and systematically analyzing defects using Statistical Quality Control (SQC) tools.

---

### Q2: What is your project and what problem does it solve?
**Answer:**  
My project is a **Hostel Management System (HMS)** designed to streamline hostel administrative operations—including student boarding, room inventory control, bed allocations, and maintenance grievance handling. It replaces slow, error-prone manual spreadsheets with an automated, responsive desktop software system.

---

### Q3: Why were you assigned the Hostel Management System?
**Answer:**  
According to the BBAT104 project guidelines, baseline software systems are allotted based on the last digit of the university roll number. My roll number is **2410301057**, which ends in **`7`**, corresponding to the **Hostel Management System**.

---

### Q4: What is your assigned Quality Goal and what does it mean?
**Answer:**  
My assigned Quality Goal is **Q05 – REDUCE RESPONSE TIME**.  
Response time is the elapsed duration between a user initiating an action (such as searching a student, clicking a tab, or loading dashboard statistics) and the system displaying the complete result. The goal of Q05 is to minimize latency across all frequent administrative interactions.

---

### Q5: What are the five mandatory features you implemented for Q05?
**Answer:**  
1. **Fast Search:** Parameterized indexed search queries using SQL `WHERE` and `LIKE`.
2. **Quick Navigation:** Persistent in-memory frame switching (`tkraise()`) with zero redraw overhead.
3. **Cached Dashboard:** In-memory aggregate metric caching with reactive state invalidation.
4. **Database Indexing:** 8 dedicated B-Tree indexes on high-frequency search and join columns.
5. **Paginated Reports:** Server-side SQL `LIMIT` / `OFFSET` pagination ensuring constant memory consumption.

---

### Q6: How does Fast Search reduce response time?
**Answer:**  
Instead of loading thousands of database rows into Python memory and iterating through loops in Python code, Fast Search delegates filtering directly to SQLite’s compiled C-engine using parameterized SQL predicates (`WHERE student_id LIKE ?`). When combined with B-Tree indexes, SQLite inspects only matching nodes, completing searches in under **$0.5\text{ ms}$**.

---

### Q7: What is a Database Index and why did you use B-Tree indexing?
**Answer:**  
A database index is a specialized data structure that allows SQLite to locate rows without scanning the entire table. SQLite uses balanced B-Trees (B+ Trees). Without an index, search time complexity is linear $O(N)$ (Full Table Scan). With a B-Tree index, search complexity drops to logarithmic $O(\log N)$, reducing disk I/O from hundreds of page reads down to 2 or 3 page reads.

---

### Q8: Which database columns did you index and why?
**Answer:**  
1. `students(student_id)` and `students(name)`: For instant student identification.
2. `rooms(room_number)` and `rooms(status)`: For rapid room availability filtering.
3. `allocations(room_id, status)`: A composite index for calculating live room bed occupancy.
4. `complaints(complaint_id)` and `complaints(status)`: For quick ticket tracking and dashboard grievance counts.

---

### Q9: How does Dashboard Caching work in your project?
**Answer:**  
The dashboard computes 8 aggregate metrics (total students, total rooms, occupancy percentage, pending complaints, etc.).  
- On first launch (Cold Cache), the system runs the SQL queries and stores the snapshot in an in-memory dictionary.
- Subsequent visits read directly from memory (Hot Cache Hit) in **$0.04\text{ ms}$**.
- When any write mutation occurs (adding a student, allocating a bed, updating a complaint), the system calls `DashboardCache.invalidate()`. The next dashboard request automatically recalculates fresh data.

---

### Q10: What is Pagination and why does it improve performance?
**Answer:**  
Pagination divides a large dataset into discrete, numbered pages. Instead of fetching 10,000 records into memory and creating 10,000 GUI table rows (which freezes the interface), our `PaginatedReportService` uses SQL `LIMIT :page_size OFFSET :offset` to fetch strictly 10 or 20 rows at a time. This keeps memory usage at $O(1)$ constant space and query time under **$2\text{ ms}$**.

---

### Q11: What is Quick Navigation and how does it prevent UI lag?
**Answer:**  
Traditional applications destroy and recreate windows or frames when navigating tabs. Quick Navigation pre-instantiates all 6 module views (`DashboardView`, `StudentView`, `RoomView`, `AllocationView`, `ComplaintView`, `ReportView`) at startup inside a centralized frame container. When the user clicks a navigation button, it brings the frame to the front using `frame.tkraise()`. Switching takes less than **$0.3\text{ ms}$** with zero UI flicker.

---

### Q12: What CRUD operations are implemented in your system?
**Answer:**  
1. **Students:** CREATE (register), READ (view directory), UPDATE (modify profile), DELETE (de-register).
2. **Rooms:** CREATE (add room), READ (view capacity & occupancy), UPDATE (modify specs), DELETE (remove vacant room).
3. **Allocations:** CREATE (allot bed), READ (audit allocations), UPDATE (fee status/remarks), DELETE (vacate/check out).
4. **Complaints:** CREATE (log ticket), READ (view grievances), UPDATE (advance workflow to Resolved/Closed), DELETE (remove invalid ticket).

---

### Q13: What is Poka-Yoke and how did you apply it in this software?
**Answer:**  
Poka-Yoke is a Japanese TQM term meaning "mistake-proofing" or error prevention at the source. In our system:
- Input validators check phone numbers (10-13 digits) and email syntax before touching the database.
- Room capacity guards prevent allocating a student to a room that has already reached maximum bed capacity.
- Referential integrity guards prevent deleting a student who currently holds an active room allocation.

---

### Q14: Why did you choose SQLite3 instead of MySQL or MongoDB?
**Answer:**  
SQLite3 is serverless, zero-configuration, ACID-compliant, and embedded directly into the Python standard library. It avoids external server connection latency and network overhead, running at in-process C-speed with support for WAL (Write-Ahead Logging) and B-Tree indexes.

---

### Q15: Why did you choose Python and Tkinter for the GUI?
**Answer:**  
Python offers rapid development and high maintainability. Tkinter with TTK is lightweight, runs natively on the OS without requiring heavy browser runtimes (like Electron), and consumes less than 40 MB of RAM.

---

### Q16: What is the system architecture of your project?
**Answer:**  
It follows a **Layered Service-Repository Architecture**:
1. **Presentation Layer:** Tkinter/TTK UI views and Quick Navigation controller.
2. **Business & Validation Layer:** Input validators and service classes.
3. **Q05 Optimization Layer:** Fast Search, Cache Manager, Indexing, and Pagination engines.
4. **Data Persistence Layer:** SQLite3 with WAL mode and foreign key constraints.

---

### Q17: What are the main Functional Requirements of your system?
**Answer:**  
- Student registration and record maintenance.
- Room inventory and capacity monitoring.
- Student-to-room allocation with vacancy updates.
- Maintenance complaint ticketing and resolution tracking.
- Paginated reporting and audit logs.

---

### Q18: What are the Non-Functional Requirements of your system?
**Answer:**  
- **Performance (Q05):** Sub-10ms search queries and sub-1ms cached dashboard rendering.
- **Reliability:** ACID database transactions and foreign key integrity.
- **Usability:** High-contrast layout, responsive controls, friendly error dialogs.
- **Maintainability:** Modular, PEP-8 compliant code structure.

---

### Q19: What automated testing did you perform?
**Answer:**  
We created an automated test suite with 18 unit, integration, and performance tests using Python's standard `unittest` framework:
- `test_models.py`: Verifies entity serialization.
- `test_validators.py`: Verifies Poka-Yoke error prevention on invalid inputs.
- `test_services.py`: Tests full CRUD workflows, capacity checks, and check-out logic.
- `test_performance_q05.py`: Verifies that B-Tree indexes exist, searches execute under 15ms, and cache hits run in under 5ms.

---

### Q20: What bugs did you encounter during development and how did you resolve them?
**Answer:**  
1. *Student Name Validation Bug:* Initial regex disallowed parentheses and numbers (e.g. "Rohan Bakshi (Senior)" or "Student Number 1"). Fixed by updating the regex to `^[A-Za-z0-9\s.'\-()]+$`.
2. *Allocation Concurrency & Rollback:* If an allocation query failed midway, the database state needed to remain atomic. Resolved by wrapping transactions with explicit `conn.rollback()` exception handlers.

---

### Q21: What is Write-Ahead Logging (WAL) and why is it enabled?
**Answer:**  
WAL is an SQLite journaling mode enabled via `PRAGMA journal_mode = WAL;`. Instead of locking the entire database during a write, writes are appended to a separate WAL file. This allows concurrent readers to continue querying without blocking writers, significantly improving concurrency and throughput.

---

### Q22: How does your Git commit history reflect TQM principles?
**Answer:**  
Our repository contains over 35 conventional, incremental commits (e.g., `feat:`, `fix:`, `test:`, `docs:`). This provides full traceability, demonstrating step-by-step engineering progression rather than a single monolithic dump.

---

### Q23: What are the limitations of the current implementation?
**Answer:**  
Currently, the system is designed for single-workstation desktop administrative offices. It does not include automated online bank payment gateway APIs or mobile apps, which are intentionally out of scope for Reviews 1 and 2.

---

### Q24: What work is planned for Review 3 and Review 4?
**Answer:**  
- **Review 3:** Process Mapping & Risk Audit (FMEA Matrix with RPN scores, SIPOC Process Map, CTQ Tree).
- **Review 4:** Statistical Quality Control & Continuous Improvement (Pareto 80/20 Charts for complaint root causes, Fishbone Ishikawa Diagrams, and PDCA cycle logs).

---

### Q25: How would you summarize your project in one sentence?
**Answer:**  
*"This project is a fully functional Hostel Management System built with Python and SQLite that applies TQM principles to achieve Quality Goal Q05 by reducing operational response times by over 95% through indexing, caching, fast search, quick navigation, and pagination."*
