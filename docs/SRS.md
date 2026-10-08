# Software Requirements Specification (SRS)
## Hostel Management System (HMS) with Latency Optimization (Q05)

**Course Code:** BBAT104 – Fundamentals of Total Quality Management (TQM)  
**Academic Session:** 2026–27  
**Student Name:** Rohan Bakshi  
**Registration / Roll Number:** 2410301057  
**Branch & Section:** B.Tech Computer Science and Engineering (Section A)  
**Assigned Baseline System:** Hostel Management System (Digit 7)  
**Assigned Quality Goal:** **Q05 – Reduce Response Time**  

---

## 1. Title
**High-Performance Hostel Management System with Quality Engineering for Reduced Operational Latency (Q05).**

## 2. Student & Academic Information
- **Author:** Rohan Bakshi
- **University Roll Number:** 2410301057
- **Course:** BBAT104: Fundamentals of TQM
- **Submission Milestone:** Review 1 (Setup & SRS) & Review 2 (Base System & CRUD with Q05 Features)

---

## 3. Project Overview
The Hostel Management System is a specialized desktop management software designed to automate hostel administration processes including student boarding, room inventory control, student-room allocation, and grievance/complaint redressal. By integrating Total Quality Management (TQM) principles into the software engineering lifecycle, this system specifically targets **Quality Goal Q05 (Reduce Response Time)** through parameterized indexed searching, in-memory aggregation caching, persistent UI routing, B-Tree database indexing, and limit/offset pagination.

---

## 4. Problem Statement
Traditional hostel management systems in collegiate institutions suffer from notable performance bottlenecks:
1. **Slow Query Times:** As student records grow, unindexed full-table scans cause searching and filtering to become noticeably sluggish.
2. **Repetitive Dashboard Latency:** Every navigation to the dashboard recalculates total counts, occupancy percentages, and pending complaints via costly full database aggregations.
3. **UI Freezes on Large Datasets:** Loading entire tables containing hundreds or thousands of historical allocation records and complaint tickets causes noticeable frame drops and memory spikes.
4. **Disorganized Navigation:** Fragmented multi-window interfaces force administrators to click through multiple dialogs, wasting user time.
5. **Data Entry Errors:** Lack of input validation (Poka-Yoke) leads to inconsistent data formats, duplicate room numbers, and over-allocation beyond room capacity.

---

## 5. Objectives
1. Build a fully functional, reliable, and user-friendly Hostel Management System with complete CRUD operations for Students, Rooms, Allocations, and Complaints.
2. Formally implement and verify the five mandatory **Q05 (Reduce Response Time)** quality features.
3. Eliminate UI lag and achieve sub-10ms query and rendering response times for administrative tasks.
4. Enforce strict data integrity and Poka-Yoke error prevention on all user inputs.
5. Provide a clean, maintainable architecture suitable for viva defense and subsequent Review 3 (FMEA) and Review 4 (SQC) expansions.

---

## 6. Scope
- **Included in Reviews 1 & 2:** Student Management, Room Management, Allocation Engine, Complaint Tracking, Cached Metrics Dashboard, Fast Search Engine, Quick Navigation System, Database B-Tree Indexing, Paginated Reports, Unit/Performance Testing, and Complete Documentation.
- **Excluded:** Online payment integration, biometric hardware interfaces, mobile applications, and advanced Review 3/4 SQC tools (FMEA/Pareto/Fishbone).

---

## 7. Stakeholders & User Roles
1. **Hostel Warden / Chief Administrator:** Superintends hostel operations, monitors occupancy ratios, audits grievance resolution rates, and generates paginated analytical summaries.
2. **Hostel Caretaker / Administrative Clerk:** Handles daily student registration, allocates vacant beds, updates room maintenance status, and registers student complaints.
3. **Academic Evaluator / TQM Faculty:** Audits software compliance against TQM benchmarks, inspects Git commit history, verifies Q05 response time improvements, and conducts viva assessment.

---

## 8. Functional Requirements (FR)

### FR1: Student Management
- **FR1.1 (Create):** The system shall allow administrators to register new students with fields: Student ID (Unique), Full Name, Email, Phone, Gender, Branch, Year, Guardian Contact, and Address.
- **FR1.2 (Read):** The system shall display all registered students in a structured, sortable data table.
- **FR1.3 (Update):** The system shall allow modification of student contact details, branch, and guardian information.
- **FR1.4 (Delete):** The system shall allow de-registration of a student, verifying that active room allocations are cleanly terminated.

### FR2: Room Management
- **FR2.1 (Create):** The system shall enable creating room records with Room Number (Unique), Block/Wing, Floor, Room Type (Single/Double/Triple), Capacity (1-4), and Monthly/Annual Fee.
- **FR2.2 (Read):** The system shall display rooms along with current occupied beds and dynamic status (`Available`, `Partially Occupied`, `Full`, `Maintenance`).
- **FR2.3 (Update):** The system shall allow editing room capacity, fee rates, and maintenance flags.
- **FR2.4 (Delete):** The system shall prevent deletion of rooms currently holding active student allocations.

### FR3: Room Allocation Engine
- **FR3.1 (Allocate):** The system shall allow assigning an unallocated student to an available room, automatically verifying that room capacity is not exceeded.
- **FR3.2 (Read):** The system shall display active room allocations with student name, room number, allotment date, and fee status.
- **FR3.3 (Update):** The system shall allow updating allocation metadata, fee payment status (`Paid`, `Pending`), and administrative remarks.
- **FR3.4 (Deallocate):** The system shall support student check-out / vacating, updating the room's occupancy status instantaneously.

### FR4: Complaint & Grievance Management
- **FR4.1 (Create):** The system shall log student complaints with Complaint ID, Student ID, Room Number, Category (`Electrical`, `Plumbing`, `Carpentry`, `Cleanliness`, `Internet`, `Other`), Description, and Severity.
- **FR4.2 (Read):** The system shall display all complaint tickets with status indicators.
- **FR4.3 (Update):** The system shall allow updating complaint status (`Pending` $\to$ `In Progress` $\to$ `Resolved` $\to$ `Closed`) and recording resolution notes.
- **FR4.4 (Delete):** The system shall support deleting invalid or duplicate complaint entries.

---

## 9. Non-Functional Requirements (NFR)

### NFR1: Performance & Response Time (Primary CTQ - Q05)
- **NFR1.1:** Single-record lookups and searches shall execute in under 10 milliseconds.
- **NFR1.2:** Dashboard view transitions shall render in under 5 milliseconds when metrics are cached.
- **NFR1.3:** Report pagination shall load any 20-record slice in under 15 milliseconds regardless of overall table volume.

### NFR2: Reliability & Data Integrity
- **NFR2.1:** All database modifications shall follow ACID transaction guarantees using SQLite.
- **NFR2.2:** Foreign key relationships between Students, Rooms, Allocations, and Complaints shall be strictly enforced.

### NFR3: Usability & Human Factors
- **NFR3.1:** The GUI layout shall be intuitive, adhering to consistent typography, padding, color feedback, and error messaging.
- **NFR3.2:** Destructive actions (deletions, checkouts) shall require explicit user confirmation dialogs.

### NFR4: Portability & Maintainability
- **NFR4.1:** The application shall run out-of-the-box on standard Python 3.8+ environments without external binary compilations.
- **NFR4.2:** Codebase shall maintain a clean, modular Service-Repository architecture separating GUI logic from database transactions.

---

## 10. Hardware & Software Requirements

### Hardware Requirements:
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **Memory (RAM):** Minimum 2 GB (4 GB recommended).
- **Disk Storage:** Minimum 100 MB free hard disk space.
- **Display Resolution:** Minimum 1024x768 (1280x800 or higher recommended).

### Software Requirements:
- **Operating System:** Windows 10/11, macOS 11+, or modern Linux distribution.
- **Runtime Environment:** Python 3.8 to 3.14.
- **Database Engine:** SQLite 3 (bundled with Python).
- **IDE:** Visual Studio Code / GitHub Desktop.

---

## 11. Technology Stack
- **Programming Language:** Python 3.x
- **GUI Toolkit:** Python Tkinter / TTK with custom modern styling
- **Database Engine:** SQLite3 with WAL mode and custom B-Tree Indexes
- **Testing Framework:** Python standard `unittest`
- **Version Control:** Git & GitHub

---

## 12. Database Requirements
- Relational schema consisting of 4 core tables: `students`, `rooms`, `allocations`, `complaints`.
- Foreign key cascading/protection constraints.
- Automated schema bootstrap upon first application launch.

---

## 13. GUI Requirements
- Modern desktop sidebar layout with dedicated operational tabs:
  - 🏠 **Dashboard** (Summary statistics & quick status)
  - 👨‍🎓 **Students** (Student directory & CRUD forms)
  - 🛏️ **Rooms** (Room inventory & occupancy trackers)
  - 📋 **Allocations** (Student-bed assignments)
  - 🛠️ **Complaints** (Maintenance ticketing)
  - 📊 **Reports** (Paginated master table with audit tools)

---

## 14. Assigned Quality Goal Q05 Requirements

The project specifically optimizes for **Quality Goal Q05: Reduce Response Time**. The system must implement and demonstrate the following five required features:

### 15. Q05 Feature #1: Fast Search Requirement
- **Requirement:** Provide instant keyword searching across Students, Rooms, and Complaints.
- **Implementation:** Parameterized SQLite queries utilizing indexed `WHERE` conditions and leading-wildcard optimized `LIKE` patterns. Avoids full memory extraction.
- **Verification Metric:** Query execution time $< 5\text{ ms}$.

### 16. Q05 Feature #2: Quick Navigation Requirement
- **Requirement:** Ensure seamless switching between system views with zero lag.
- **Implementation:** Pre-instantiated view frames hosted within a centralized controller (`MainWindow`). Switching frames occurs in-memory via geometry management (`tkraise()`), eliminating window teardown and redraw delays.
- **Verification Metric:** Tab switch latency $< 2\text{ ms}$.

### 17. Q05 Feature #3: Cached Dashboard Requirement
- **Requirement:** Prevent repetitive, costly aggregate calculations on every dashboard visit.
- **Implementation:** A thread-safe `CacheService` stores statistical counters (Total Students, Total Rooms, Occupied Beds, Available Beds, Pending Complaints, Resolved Complaints). A reactive invalidation mechanism flags the cache dirty only when mutation services (Create/Update/Delete) execute.
- **Verification Metric:** Cached dashboard fetch time $< 0.5\text{ ms}$ (vs $> 15\text{ ms}$ for cold queries).

### 18. Q05 Feature #4: Database Indexing Requirement
- **Requirement:** Accelerate frequent lookup queries across large tables.
- **Implementation:** Dedicated B-Tree indexes constructed on:
  - `idx_students_id` ON `students(student_id)`
  - `idx_students_name` ON `students(name)`
  - `idx_rooms_number` ON `rooms(room_number)`
  - `idx_rooms_status` ON `rooms(status)`
  - `idx_allocations_student` ON `allocations(student_id)`
  - `idx_allocations_room` ON `allocations(room_id)`
  - `idx_complaints_student` ON `complaints(student_id)`
  - `idx_complaints_status` ON `complaints(status)`
- **Verification Metric:** Index scan reduces search time complexity from $O(N)$ linear scans to $O(\log N)$ logarithmic tree lookups.

### 19. Q05 Feature #5: Paginated Reports Requirement
- **Requirement:** Prevent UI freezing and memory degradation when viewing extensive historical logs.
- **Implementation:** SQL-driven `LIMIT :limit OFFSET :offset` query generator returning strictly the requested page slice (e.g., 20 records) along with real-time total count and page counters.
- **Verification Metric:** Memory footprint remains constant regardless of whether database contains 100 or 100,000 records.

---

## 20. System Constraints
- Single-user desktop environment suitable for college hostel administrative offices.
- Local SQLite database file storage.

## 21. Assumptions
- User has basic computer literacy.
- Host machine has write access to the project directory for SQLite file generation.

## 22. Future Enhancements (Review 3, Review 4 & Beyond)
- Integration of SQC tools: Pareto charts for complaint root-causes, Fishbone diagrams for allocation bottlenecks, and FMEA risk matrices.
- Automated SMS/Email alerts for fee dues and complaint resolution notices.
- Exporting paginated reports to PDF and Excel formats.
