# Hostel Management System (HMS) - TQM Quality Engineering

**Course:** BBAT104 – Fundamentals of Total Quality Management (TQM)  
**Academic Session:** 2026–27  
**Student Name:** Rohan Bakshi  
**Roll / Registration Number:** 2410301057  
**Branch & Section:** B.Tech CSE (Section A)  
**Assigned Baseline Software System:** Hostel Management System (Digit: 7)  
**Assigned Quality Goal:** **Q05 – Reduce Response Time**  

---

## 🎯 Executive Summary & Quality Objective

In educational institutions, hostel administrative portals suffer from high latency during peak admission and room allotment periods. Administrators frequently experience delays when querying student records, searching room availability, navigating between operational tabs, and generating summary reports.

Applying Total Quality Management (TQM) principles—specifically **Customer Focus**, **Poka-Yoke (Defect Prevention)**, and **Statistical Quality Control for Latency Reduction**—this project builds a high-performance, responsive desktop Hostel Management System engineered from the ground up to achieve **Quality Goal Q05 (Reduce Response Time)**.

### Mandatory Q05 Features Implemented
1. **Fast Search:** Parameterized indexed search queries using SQLite `WHERE` and `LIKE` optimizations with sub-millisecond execution times.
2. **Quick Navigation:** Zero-lag responsive sidebar routing maintaining views in memory and eliminating redundant page-load redraws.
3. **Cached Dashboard:** In-memory metric caching with reactive state invalidation to eliminate repeated expensive aggregation queries on every view switch.
4. **Database Indexing:** B-Tree indexing on primary lookup vectors (`student_id`, `name`, `room_number`, `status`, `complaint_id`) reducing lookup time complexity from $O(N)$ to $O(\log N)$.
5. **Paginated Reports:** Server/database-side SQL `LIMIT` / `OFFSET` pagination ensuring instant rendering regardless of dataset growth.

---

## 🏗️ Architecture & Technology Stack

- **Language & Runtime:** Python 3.x (Standard Library)
- **GUI Framework:** Python Tkinter / TTK Modern Styled Desktop Architecture
- **Database Layer:** SQLite3 (ACID-compliant relational database with write-ahead indexing)
- **Design Pattern:** Layered Service-Repository Architecture (UI Layer $\to$ Service Layer $\to$ Q05 Optimization Layer $\to$ Database Access Layer)
- **Version Control:** Git & GitHub (Structured conventional commit history)

---

## 📂 Repository Structure

```
Hostel Management System TQM/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # Main application entry point
│   ├── database/                   # Database engine, schema & indexes
│   │   ├── __init__.py
│   │   ├── connection.py           # Thread-safe SQLite connection manager
│   │   ├── schema.py               # Table definitions & DDL scripts
│   │   └── indexes.py              # Q05 B-Tree indexes configuration
│   │
│   ├── models/                     # Strongly-typed domain models
│   │   ├── __init__.py
│   │   ├── student.py              # Student entity model
│   │   ├── room.py                 # Room entity model
│   │   ├── allocation.py           # Room allocation model
│   │   └── complaint.py            # Complaint resolution model
│   │
│   ├── services/                   # Business logic & Q05 optimizations
│   │   ├── __init__.py
│   │   ├── student_service.py      # Student CRUD operations
│   │   ├── room_service.py         # Room CRUD operations
│   │   ├── allocation_service.py   # Allocation management & capacity guards
│   │   ├── complaint_service.py    # Complaint lifecycle management
│   │   ├── search_service.py       # Q05 Fast Search engine
│   │   ├── cache_service.py        # Q05 In-Memory Cache Manager
│   │   └── report_service.py       # Q05 Paginated Reports engine
│   │
│   ├── ui/                         # User interface & visual presentation
│   │   ├── __init__.py
│   │   ├── styles.py               # Theme colors, fonts & ttk styles
│   │   ├── main_window.py          # Quick Navigation layout shell
│   │   ├── dashboard.py            # Cached Dashboard view
│   │   ├── students.py             # Student management CRUD interface
│   │   ├── rooms.py                # Room management interface
│   │   ├── allocations.py          # Room allocation interface
│   │   ├── complaints.py           # Complaint tracking interface
│   │   └── reports.py              # Paginated reports & audit table
│   │
│   └── utils/                      # Helper tools & quality assurance
│       ├── __init__.py
│       ├── validators.py           # Poka-Yoke input validation
│       ├── helpers.py              # Formatting & benchmark timers
│       └── seeder.py               # Realistic dataset seeder
│
├── docs/                           # Comprehensive Review Documentation
│   ├── SRS.md                      # Software Requirements Specification
│   ├── SCOPE.md                    # Project Scope Document (In/Out Scope)
│   ├── SYSTEM_ARCHITECTURE.md      # Architecture flowcharts & dataflow
│   ├── DATABASE_DESIGN.md          # ER schema & Indexing rationale
│   ├── Q05_FEATURES.md             # In-depth technical breakdown of Q05
│   ├── REVIEW_1.md                 # Review 1 submission & evaluation defense
│   ├── REVIEW_2.md                 # Review 2 submission & CRUD checklist
│   └── VIVA_PREPARATION.md         # Comprehensive viva Q&A guide
│
├── screenshots/                    # UI execution screenshots & evidence
├── tests/                          # Automated unit, integration & benchmarks
│   ├── __init__.py
│   ├── test_models.py              # Entity validation tests
│   ├── test_validators.py          # Poka-Yoke error prevention tests
│   ├── test_services.py            # Full CRUD verification suite
│   └── test_performance_q05.py     # Q05 latency & indexing benchmarks
│
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT License
├── README.md                       # Main project documentation
└── requirements.txt                # Dependencies specification
```

---

## ⚡ Quick Start & Installation

### Prerequisites
- Python 3.8 or higher installed on Windows, macOS, or Linux.
- Tkinter library support (included by default in standard Python distributions on Windows).

### 1. Clone or Open the Repository
```bash
git clone https://github.com/RohanBakshi/BBAT104_TQM_2410301057.git
cd BBAT104_TQM_2410301057
```

### 2. Run the Application
```bash
python -m app.main
```
*The application automatically creates the SQLite database (`data/hostel.db`), initializes all normalized tables, executes Q05 B-Tree indexes, and populates initial sample data if empty.*

### 3. Run Automated Tests & Performance Benchmarks
```bash
python -m unittest discover tests
```

---

## 📊 Evaluation Milestones Summary

| Milestone | Raw Marks | Status | Primary Artefacts |
| :--- | :--- | :--- | :--- |
| **Review 1: Setup & SRS** | 10 Marks | **READY (PASS)** | GitHub Repo, SRS Document, Scope Document, System Architecture Flowchart |
| **Review 2: Base System & CRUD** | 15 Marks | **READY (PASS)** | Functional GUI, Full CRUD on all 4 modules, 5 Q05 Quality Features |
| **Review 3: FMEA & Risk Audit** | 15 Marks | Scheduled | FMEA Matrix with RPN, SIPOC Process Map, CTQ Tree |
| **Review 4: SQC & Continuous Imp.** | 15 Marks | Scheduled | Pareto 80/20 Charts, Fishbone Root-Cause Diagram, PDCA Cycle |
| **Final Demo & Viva** | 10 Marks | Prepared | Live execution sequence, Viva defense manual |
| **Documentation & Git Health** | 5 Marks | **READY (PASS)** | Comprehensive manuals, $\ge 35$ structured Git commits |

---

## 👤 Author & Academic Details
- **Student Name:** Rohan Bakshi
- **Roll Number:** 2410301057
- **Course:** BBAT104 Fundamentals of TQM
- **Institution:** Department of Computer Science & Engineering
