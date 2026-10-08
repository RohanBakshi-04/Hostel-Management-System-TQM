# System Architecture Document

**Course:** BBAT104 – Fundamentals of Total Quality Management  
**Academic Session:** 2026–27  
**Project:** Hostel Management System (HMS)  
**Student Name:** Rohan Bakshi  
**Roll / Registration Number:** 2410301057  
**Assigned Quality Goal:** **Q05 – Reduce Response Time**  

---

## 1. High-Level Architectural Overview

The Hostel Management System is engineered using a **Layered Service-Repository Architecture** with an embedded **Q05 Performance Optimization Layer**. This decoupling ensures high maintainability, strict separation of concerns, data integrity (Poka-Yoke), and minimal execution latency.

```mermaid
flowchart TD
    subgraph UI_Layer ["1. Presentation Layer (Tkinter / TTK GUI)"]
        UI_Nav["Quick Navigation Controller (Persistent Shell)"]
        UI_Dash["Dashboard View (Metrics Cards)"]
        UI_Stud["Student Management View"]
        UI_Room["Room Management View"]
        UI_Alloc["Room Allocation View"]
        UI_Comp["Complaint Management View"]
        UI_Rep["Paginated Reports View"]
    end

    subgraph Service_Layer ["2. Business Logic & Validation Layer"]
        Val["Poka-Yoke Input Validators"]
        S_Stud["Student Service"]
        S_Room["Room Service"]
        S_Alloc["Allocation Service (Capacity Guard)"]
        S_Comp["Complaint Service"]
    end

    subgraph Q05_Layer ["3. Q05 Performance Optimization Layer"]
        Q_Nav["Q05-2: Quick Navigation (In-Memory View Switching)"]
        Q_Cache["Q05-3: In-Memory Dashboard Cache (Smart Invalidation)"]
        Q_Search["Q05-1: Fast Search Engine (Parameterized WHERE/LIKE)"]
        Q_Page["Q05-5: Limit/Offset Pagination Engine"]
        Q_Index["Q05-4: B-Tree Database Indexes"]
    end

    subgraph DB_Layer ["4. Data Persistence Layer (SQLite3 Engine)"]
        DB_Conn["Thread-Safe Connection Pool & WAL Mode"]
        T_Stud[("students table")]
        T_Room[("rooms table")]
        T_Alloc[("allocations table")]
        T_Comp[("complaints table")]
    end

    UI_Nav --> UI_Dash & UI_Stud & UI_Room & UI_Alloc & UI_Comp & UI_Rep
    UI_Nav -.-> Q_Nav

    UI_Stud --> Val --> S_Stud
    UI_Room --> Val --> S_Room
    UI_Alloc --> Val --> S_Alloc
    UI_Comp --> Val --> S_Comp
    UI_Rep --> Q_Page

    UI_Dash <--> Q_Cache
    Q_Search <--> S_Stud & S_Room & S_Comp

    S_Stud & S_Room & S_Alloc & S_Comp -.->|Invalidate on Write| Q_Cache
    S_Stud & S_Room & S_Alloc & S_Comp --> DB_Conn
    Q_Search & Q_Page --> DB_Conn

    DB_Conn --> Q_Index
    Q_Index --> T_Stud & T_Room & T_Alloc & T_Comp
```

---

## 2. Core Architectural Layers Explained

### 2.1 Presentation Layer (GUI)
- **Role:** Renders the user interface, captures user actions, and displays data cleanly without freezing.
- **Technology:** Python `tkinter` & `ttk` with cohesive visual styling (modern typography, contrasting cards, status badges).
- **Key Modules:**
  - `MainWindow`: Orchestrates the sidebar navigation and view swapping.
  - `DashboardView`: Displays quick statistics and system health.
  - `StudentView`, `RoomView`, `AllocationView`, `ComplaintView`: Handle complete CRUD workflows.
  - `ReportView`: Delivers paginated data auditing.

### 2.2 Business Logic & Validation Layer
- **Role:** Enforces institutional business rules, validates incoming data (Poka-Yoke error prevention), and coordinates transactions.
- **Key Features:**
  - Automatic validation of phone formats, unique student IDs, and non-empty mandatory fields.
  - Capacity bounds checking: Ensures a room cannot be over-allocated beyond its configured capacity ceiling.
  - Cascading cleanup: Checks student allocation status before permitting record deletion.

### 2.3 Q05 Performance Optimization Layer (Assigned Quality Goal)
This dedicated layer sits between the business services and database to guarantee minimal response time:
1. **Fast Search:** Directs search requests through indexed SQL queries rather than fetching full tables into Python memory.
2. **Quick Navigation:** Maintains pre-instantiated frame references in memory, switching views instantaneously via `tkraise()`.
3. **Cached Dashboard:** Stores aggregated metrics in memory and only recalculates when write mutations trigger cache invalidation.
4. **Database Indexing:** Enforces B-Tree search indexes on high-frequency columns to achieve $O(\log N)$ retrieval complexity.
5. **Paginated Reports:** Fetches precise row slices via `LIMIT` and `OFFSET`, keeping RAM consumption minimal and constant.

### 2.4 Data Persistence Layer
- **Role:** Manages SQLite database connections, transaction commits, rollbacks, and schema integrity.
- **Features:** Foreign keys enabled (`PRAGMA foreign_keys = ON`), Write-Ahead Logging (`PRAGMA journal_mode = WAL`) for concurrent read/write throughput.

---

## 3. Data Flow & CRUD Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant UI as GUI View
    participant Val as Input Validator (Poka-Yoke)
    participant Svc as Service Layer
    participant Cache as Q05 Cache Engine
    participant DB as SQLite Database (with Indexes)

    Admin->>UI: Submit Form (e.g. New Student Registration)
    UI->>Val: Validate Inputs (ID, Name, Phone, Email)
    alt Validation Fails
        Val-->>UI: Return Validation Error
        UI-->>Admin: Show Friendly Error Alert Dialog
    else Validation Succeeds
        Val-->>Svc: Pass Clean Domain Object
        Svc->>DB: Execute Parameterized INSERT Query
        DB-->>Svc: Success (Record ID)
        Svc->>Cache: Invalidate Relevant Cache Keys
        Svc-->>UI: Return Success Confirmation
        UI-->>Admin: Show Success Feedback & Refresh Table View
    end
```

---

## 4. Q05 Cache Lifecycle & Smart Invalidation Architecture

```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    Uninitialized --> ColdCache: App Starts / First Request
    ColdCache --> DatabaseQuery: Fetch Aggregates from SQLite
    DatabaseQuery --> Cached: Cache Populated in Memory
    
    state Cached {
        [*] --> ServingCache: Dashboard Navigation Request
        ServingCache --> ServingCache: Instant Memory Return (<0.5ms)
    }

    Cached --> InvalidationTrigger: Write Mutation Occurs (Add/Update/Delete)
    InvalidationTrigger --> DirtyState: Mark Cache as Invalidate/Dirty
    DirtyState --> DatabaseQuery: Recalculate on Next Demand
```
