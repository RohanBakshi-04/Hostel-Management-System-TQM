# Project Scope Document

**Course:** BBAT104 – Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Project Title:** Hostel Management System with Latency Reduction (Q05)  
**Student Name:** Rohan Bakshi  
**Roll / Registration Number:** 2410301057  
**Branch & Section:** B.Tech CSE (Section A)  
**Baseline System:** Hostel Management System (Topic Digit: 7)  
**Assigned Quality Goal:** **Q05 – Reduce Response Time**  

---

## 1. Executive Summary

This document establishes the official project boundaries, target deliverables, functional boundaries, operational constraints, and milestone timelines for the **Hostel Management System (HMS)** developed for course **BBAT104 (Fundamentals of TQM)**.

The primary objective is to implement a robust desktop-based management application that optimizes operational efficiency by directly addressing **Quality Goal Q05: Reduce Response Time** using software engineering and Total Quality Management (TQM) methodologies.

---

## 2. In-Scope Deliverables (Milestones: Review 1 & Review 2)

### 2.1 Core Hostel Management System Modules (Full CRUD)
1. **Student Management Module:**
   - Add new student records with validation (Student ID, Name, Gender, Branch, Year, Contact, Guardian Contact, Address).
   - Read and display students with formatted table views.
   - Update student profile and contact details.
   - Delete/De-register student records with referential integrity checks.
2. **Room Management Module:**
   - Add new room definitions (Room Number, Block/Wing, Floor, Room Type, Capacity, Base Fee).
   - View list of rooms with real-time occupancy and status indicators (Available, Partial, Full, Maintenance).
   - Update room attributes and maintenance status.
   - Delete vacant rooms with safety validations.
3. **Room Allocation Module:**
   - Allocate eligible students to available rooms with automated capacity enforcement (Poka-Yoke).
   - View active and historical room allocations.
   - Update room allotment dates, fee payment status, and remarks.
   - De-allocate / Check-out students and automatically restore room availability.
4. **Complaint Management Module:**
   - Register maintenance and disciplinary complaints tagged to student IDs and room numbers.
   - View complaint tickets with filterable categories (Electrical, Plumbing, Furniture, Cleanliness, Other).
   - Update complaint status (`Pending`, `In-Progress`, `Resolved`, `Closed`) with resolution notes.
   - Remove obsolete or duplicate complaint logs.

### 2.2 Assigned Quality Goal Q05 Features (Mandatory)
1. **Fast Search:**
   - Parameterized SQLite query engine utilizing `WHERE` and index-accelerated `LIKE` clauses.
   - Search across Students (ID, Name, Branch), Rooms (Number, Block, Status), Complaints (ID, Student ID, Status).
   - Zero-lag instant query execution avoiding in-memory Python list iteration.
2. **Quick Navigation:**
   - Unified persistent sidebar navigation system.
   - Single-click transition between Dashboard, Students, Rooms, Allocations, Complaints, and Reports.
   - State preservation and cached frame transitions with zero UI flicker.
3. **Cached Dashboard:**
   - In-memory metric caching for aggregated counts (Total Students, Total Rooms, Occupancy Rate, Active Allocations, Open Complaints).
   - Smart invalidation system: Cache refreshes only when database write mutations (Create/Update/Delete) occur.
   - Eliminates repetitive overhead of multiple `COUNT(*)` database roundtrips.
4. **Database Indexing:**
   - Explicit B-Tree database indexes created on high-frequency query columns (`students.student_id`, `students.name`, `rooms.room_number`, `rooms.status`, `complaints.student_id`, `complaints.status`).
   - Query execution acceleration from linear scan $O(N)$ to logarithmic time $O(\log N)$.
5. **Paginated Reports:**
   - SQL `LIMIT` / `OFFSET` pagination engine for reporting.
   - Prevents memory bloat and long UI load freezes when processing thousands of historical records.
   - Configurable page sizes (10, 25, 50 records/page) with intuitive Previous/Next/Jump controls.

### 2.3 Quality Assurance & TQM Components
- **Error Prevention (Poka-Yoke):** Strict input format validation (Contact numbers, valid email/IDs, capacity ceilings, uniqueness constraints).
- **Graceful Error Handling:** Safe exception trapping preventing application crashes and presenting user-friendly diagnostic dialogs.
- **Unit & Integration Testing:** Automated test suite verifying database integrity, CRUD operations, caching logic, and latency gains.

---

## 3. Out-of-Scope (Excluded for Review 1 & Review 2)

The following items are intentionally excluded from Reviews 1 & 2 to ensure architectural stability, academic clarity, and focus on core Quality Goal Q05:
- **Online Payment Gateways & Banking APIs:** Manual fee tracking is supported; live payment integrations (Razorpay/Stripe) are excluded.
- **Biometric Hardware Integration:** Physical hardware interfacing (fingerprint readers, RFID turnstiles) is excluded.
- **Cloud Microservices & Multi-Tenancy:** The application is built as a stable, single-tier / two-tier desktop system using Python and SQLite.
- **Mobile Applications:** No native Android or iOS client is included.
- **Advanced Statistical Quality Control (SQC) Audits:** FMEA matrices, SIPOC maps, Pareto 80/20 charts, and Fishbone diagrams belong specifically to **Review 3 and Review 4** and will be integrated in subsequent milestones.

---

## 4. Stakeholders and User Roles

| Stakeholder Role | Responsibilities & System Interactions |
| :--- | :--- |
| **Hostel Warden / Chief Administrator** | Reviews high-level dashboard metrics, manages room capacities, audits occupancy and resolved grievances. |
| **Hostel Caretaker / Clerk** | Executes daily CRUD operations: registers students, allots rooms, logs incoming complaints, updates repair status. |
| **TQM Course Evaluator / Examiner** | Assesses software engineering standards, verifies implementation of Q05 features, inspects Git commit history and code quality. |

---

## 5. Technical Constraints & Assumptions

### Constraints:
1. System runtime environment must be standard Python 3.8+ on Windows/Linux/macOS without proprietary dependencies.
2. Data storage must use lightweight, local SQLite3 without requiring external server installations (MySQL/PostgreSQL daemon setup).
3. GUI must operate smoothly without requiring high-end GPU acceleration.

### Assumptions:
1. The administrative user has read/write permissions on the local working directory.
2. The initial deployment manages single-institution hostel facilities with data volumes up to 100,000 records.
3. System clocks are synchronized for accurate timestamp logging.
