# 🛢️ ProjectPulse
### SIH 2026 · Problem Statement PS26122 · Client: Oil India Limited

> **Connects informal site field reports to Oracle Primavera P6 WBS nodes using fuzzy string matching — no training required for ground crews.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Pytest](https://img.shields.io/badge/Tests-6%20Passing-10b981?logo=pytest&logoColor=white)](tests/test_engine.py)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](database/)

---

## 📌 Problem Statement

Large oil & gas infrastructure projects suffer from a critical information gap: **ground-level progress is invisible for weeks at a time.** Field supervisors post status updates in WhatsApp groups or handwritten logbooks, but linking those informal messages to official Oracle Primavera P6 WBS requires planning engineers to manually scroll through thousands of L5/L6 tasks — a process that takes 2–3 days per reporting cycle and is prone to transcription errors, omissions, and contractor billing disputes.

**The result:** Project directors make decisions on data that is 2 to 4 weeks stale.

---

## ✅ What This System Does

```
"Erected Line 24 spool at bay 1, completed 80% welding on Joint W-04"
                              ↓  (< 300ms)
  Matched → OIL-L6-07: Fit-up & Root Pass TIG Welding, Joint W-04 Line 24
  Confidence: 94.3%  →  AUTO_APPROVED  →  L6 → L5 → L4 → L3 → L2 → L1 rollup recalculated
```

| Capability | Status |
| :--- | :---: |
| Keyword-based detection of field progress updates | ✅ Live |
| Regex entity extraction (task code, %, state, discipline) | ✅ Live |
| Confidence-gated fuzzy matching (RapidFuzz) | ✅ Live |
| Auto-approval gate at ≥ 85% confidence | ✅ Live |
| Human-in-the-loop Review Queue (< 85%) | ✅ Live |
| Weighted L6 → L1 hierarchical progress rollup | ✅ Live |
| Immutable audit trail (sender, role, timestamp, score) | ✅ Live |
| Plotly analytics: Sunburst, Duration bars, Discipline bars | ✅ Live |
| Role simulation (Director, Lead, Supervisor) | ✅ Live |
| WBS Schedule Explorer with live filters | ✅ Live |
| CSV Master Schedule export | ✅ Live |
| CSV file ingestion (preview only, not yet merged to DB) | ⚠️ Partial |

---

## 🗂️ WBS Database Coverage

The bundled SQLite database (`oil_india_p6.db`) models a real Oil India gas gathering & compression project across 6 WBS levels:

| Level | Count | Represents | Example |
| :---: | :---: | :--- | :--- |
| **L1** | 1 | Macro Project | Duliajan Central Gas Gathering & Compression |
| **L2** | 3 | Plant / Sub-Project | Gas Dehydration Unit-3, Compressor Station |
| **L3** | 5 | Discipline Package | Civil & Structural Foundations — Compressor Area |
| **L4** | 5 | Work Package / Area | Pipe Rack 3 Spool Erection & Welding Package |
| **L5** | 5 | Work Activity | Joint-by-Joint TIG Welding & NDT Campaign |
| **L6** | 14 | Executable Daily Task | Fit-up & Root Pass Welding, Joint W-04, Line 24 |
| **Total** | **33** | **Full WBS hierarchy** | **19 matchable L5/L6 target tasks** |

**Disciplines:** Piping & Mechanical (12) · Civil & Structural (10) · Electrical & Instrumentation (7) · Quality & Testing (3) · Project Management (1)

---

## 🔄 System Architecture & Data Flow

### End-to-End Pipeline

```mermaid
flowchart TD
    A([👷 Site Supervisor\nFree-Text Field Message]) --> B

    subgraph INGESTION ["💬 Ingestion Layer (app.py)"]
        B[Streamlit Chat Interface\nor Direct Slider Input]
    end

    subgraph ENGINE ["🔍 Extraction Engine (engine/extractor.py)"]
        C[Keyword Scan\nIs this a progress update?]
        D{Update\nDetected?}
        E[Regex Extraction\nTask Code · Progress % · State · Discipline]
    end

    subgraph MATCH ["🎯 Fuzzy Matcher (engine/matcher.py)"]
        F[Normalize Text\nExpand Domain Synonyms]
        G[RapidFuzz Composite Scorer\n0.50×TokenSet + 0.35×WRatio + 0.15×Partial]
        H[Hardware Token Bonus\n+12% per matched tag: W-04 · Line 24 · C-101]
        I[Discipline Alignment Bonus\n+5% if discipline hint matches WBS task]
        J{Confidence ≥ 85%?}
    end

    subgraph DB ["🗃️ Database Layer (database/)"]
        K[(SQLite: oil_india_p6.db)]
        L[update_task_progress L6 Node]
        M[recalculate_rollup\nL6→L5→L4→L3→L2→L1]
        N[Audit: AUTO_APPROVED]
        O[Audit: PENDING_REVIEW]
    end

    subgraph REVIEW ["⚖️ Review Queue (Tab 4)"]
        P[Manager Reviews Card\nRaw Input + Best Match + Score]
        Q{Decision}
        R[Remap Task / Adjust %\nApprove → update_task_progress]
        S[Reject → status: REJECTED]
    end

    subgraph OUTPUT ["📊 Output Layer (ui/)"]
        T[KPI Cards: L1 Project %]
        U[Duration Bar Chart: Planned vs Actual]
        V[WBS Sunburst L1→L6]
        W[Discipline Progress Bars]
    end

    B --> C
    C --> D
    D -- No --> X([💬 General Chat\nNo WBS Update])
    D -- Yes --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J -- YES ≥ 85% --> L
    J -- NO < 85% --> O
    O --> P
    P --> Q
    Q -- Approve --> R
    Q -- Reject --> S
    R --> L
    L --> M
    L --> N
    M --> K
    N --> K
    K --> T
    K --> U
    K --> V
    K --> W
```

---

### Hierarchical WBS Rollup Logic

```mermaid
flowchart LR
    L6A["L6: Fit-up & Root Pass\nJoint W-04 · 80%\nWeight: 0.35"]
    L6B["L6: Spool Alignment\nLine 24 · 100%\nWeight: 0.25"]
    L6C["L6: NDE Radiograph\nJoint W-04 · 0%\nWeight: 0.25"]
    L6D["L6: Torque Flanges · 0%\nWeight: 0.15"]

    L5["L5: TIG Welding &\nNDT Campaign\n= 53% ← weighted avg"]
    L4["L4: Pipe Rack-3\nSpool Erection Package\n= 32%"]
    L3["L3: Piping & Mechanical\nFGCS-01\n= 24%"]
    L2["L2: Feed Gas Compressor\nStation FGCS-01\n= 18%"]
    L1["L1: Duliajan Gas\nGathering Facility\n= 12%"]

    L6A --> L5
    L6B --> L5
    L6C --> L5
    L6D --> L5
    L5 --> L4
    L4 --> L3
    L3 --> L2
    L2 --> L1
```

---

### Confidence Gate & Governance

```mermaid
flowchart LR
    IN([Raw Field Message]) --> SCORE{Composite\nConfidence Score}

    SCORE -->|"≥ 85% → AUTO_APPROVED"| AUTO["⚡ Write to DB\nRecalculate Rollup"]
    SCORE -->|"< 85% → PENDING_REVIEW"| QUEUE["📋 Review Queue\nHuman-in-the-Loop"]

    AUTO --> AUDIT1["🔒 Audit Log\nAUTO_APPROVED\nTimestamp · Score · Sender"]
    QUEUE --> LEAD["👔 Discipline Lead\nSees raw message\n+ best candidate + score"]
    LEAD -->|Approve / Override| APPLY["✅ Apply with\nReviewer Notes"]
    LEAD -->|Reject| DISCARD["❌ REJECTED\nAudit logged"]
    APPLY --> APPLY2["Write to DB\nRecalculate Rollup"]
    APPLY2 --> AUDIT2["🔒 Audit Log\nMANUALLY_APPROVED\nReviewer · Notes"]
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.9 – 3.14**
- `pip` package manager

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:** `streamlit>=1.35.0` · `rapidfuzz>=3.8.0` · `pandas>=2.0.0` · `plotly>=5.20.0` · `pytest>=8.0.0`

### 2. Launch the Dashboard
```bash
streamlit run app.py
```

> **Windows shortcut:** Double-click `run.bat` — it installs dependencies and launches automatically.

Open your browser at **http://localhost:8501**

### 3. Run the Test Suite
```bash
python -m pytest -v
```

Expected output: **6/6 tests passing** in < 2 seconds.

```
tests/test_engine.py::test_extractor_percentages_and_intent          PASSED
tests/test_engine.py::test_extractor_fraction_progress               PASSED
tests/test_engine.py::test_high_confidence_auto_approval_matching    PASSED
tests/test_engine.py::test_low_confidence_pending_review_matching    PASSED
tests/test_engine.py::test_hierarchical_rollup_math                  PASSED
tests/test_engine.py::test_review_queue_approval_workflow            PASSED
```

---

## 📂 Project Structure

```
ProjectPulse/
│
├── app.py                    # Main Streamlit application (6 dashboard tabs)
├── requirements.txt          # Python dependencies
├── run.bat                   # Windows one-click startup script
├── PS26-122.pdf              # Official SIH problem statement specification
├── oil_india_p6.db           # Pre-seeded SQLite database (33-node WBS hierarchy)
├── README.md                 # This file
├── .gitignore                # Excludes __pycache__, .pytest_cache, *.pyc, *.zip
│
├── database/                 # ── Data Layer ──────────────────────────────────────
│   ├── schema.py             # SQLite DDL: tasks, chat_messages, audit_trail, uploads
│   ├── seed_data.py          # Synthetic Primavera P6 WBS (33 tasks, L1–L6)
│   └── db_manager.py         # CRUD operations, rollup engine, review queue logic
│
├── engine/                   # ── Extraction & Matching Core ───────────────────────
│   ├── extractor.py          # Regex: keyword detection, % extraction, state parsing
│   └── matcher.py            # RapidFuzz scorer: Token-Set + WRatio + token bonuses
│
├── ui/                       # ── Presentation Layer ───────────────────────────────
│   ├── styles.py             # Dark-themed CSS: glassmorphism, Oil India palette
│   ├── components.py         # Chat bubbles, metric cards, audit table, WBS cards
│   └── analytics.py          # Plotly: Duration bars, Discipline bars, Sunburst, Donut
│
└── tests/                    # ── Quality Assurance ────────────────────────────────
    └── test_engine.py        # 6 pytest tests: extraction, matching, rollup, workflow
```

---

## 🎯 Dashboard Tabs

| Tab | What It Does |
| :--- | :--- |
| **💬 Field Updates & Chat** | Chat interface with quick-test sample buttons. Sends free-text through the full extraction → matching → DB pipeline in real time. Shows confidence score chips inline on each message. |
| **🏗️ WBS Schedule Hierarchy** | Filterable (Level + Discipline + keyword search) live view of all 33 WBS nodes with progress bars, weights, parent links, and planned vs. actual durations. |
| **📋 Live Audit Trail** | Searchable, filterable immutable log of every field update — auto-approved, pending, manually approved, or rejected — with full extraction metadata. |
| **⚖️ Review Queue** | Cards for all < 85% confidence matches. Leads can remap to the correct task, override the percentage, write justification notes, and approve or reject with 1 click. |
| **📊 Analytics & Bottlenecks** | 4-chart Plotly dashboard: Planned vs. Actual Duration bars, Discipline Progress horizontals, Status Distribution donut, WBS Sunburst. |
| **📁 Master Schedule & Export** | Full WBS table view with live CSV export of all 33 tasks. Accepts CSV upload for preview only (ingestion into DB not yet implemented). |

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
| :--- | :--- | :--- |
| **Frontend / Dashboard** | [Streamlit 1.35+](https://streamlit.io/) | Python-native rapid prototyping, no JS boilerplate |
| **Matching** | [RapidFuzz 3.8+](https://github.com/maxbachmann/RapidFuzz) | C-accelerated Levenshtein + token distance |
| **Extraction** | Python `re` (regex) | Deterministic, fast, zero dependencies |
| **Analytics** | [Plotly 5.20+](https://plotly.com/python/) | Interactive charts, consistent dark theme |
| **Data Wrangling** | [Pandas 2.0+](https://pandas.pydata.org/) | WBS filtering, CSV export, aggregations |
| **Storage** | SQLite3 (WAL mode, foreign keys) | Zero-config embedded DB |
| **Testing** | [Pytest 8.0+](https://pytest.org/) | Deterministic unit tests with temp DB fixture |

---

## 🏗️ How the Matching Score is Computed

Every incoming field message is scored against each of the **19 matchable L5/L6 WBS tasks**:

$$\text{Composite Score} = 0.50 \times \text{TokenSetRatio} + 0.35 \times \text{WRatio} + 0.15 \times \text{PartialRatio}$$

**Bonus boosts (applied after base score):**
- **+12 points per matching hardware token** (e.g. `W-04`, `Line 24`, `C-101`, `11kV`) — capped at 100
- **+5 points if inferred discipline matches the WBS task's discipline**

**Result routing:**
- Score **≥ 85%** → `AUTO_APPROVED` → instant database write + rollup
- Score **< 85%** → `PENDING_REVIEW` → enters Review Queue for human verification

---

## 📊 Verified Test Scenarios

| Test Case | Input | Expected Outcome | Result |
| :--- | :--- | :--- | :---: |
| **Explicit %** | "Spool erected on line 24 at Rack 3, completed 80% welding on Joint W-04" | `is_update=True`, `progress=80.0%`, `discipline=Piping & Mechanical` | ✅ |
| **Fraction progress** | "Cable pulling ongoing, pulled 3 out of 4 segments" | `progress=75.0%` | ✅ |
| **High-confidence match** | "Fit-up & Root Pass TIG Welding on Joint W-04 Line 24" | Matches `OIL-L6-07`, confidence ≥ 85%, `AUTO_APPROVED` | ✅ |
| **Low-confidence ambiguity** | "Worked on some equipment near the station" | Confidence < 85%, `PENDING_REVIEW` | ✅ |
| **Rollup math** | Update `OIL-L6-07` to 100% | L5 parent recalculates to 60% (weighted), L1 progress > 0% | ✅ |
| **Review queue workflow** | Submit 78% confidence → Lead approves at 70% | Task updates to 70%, removed from queue | ✅ |

---

## ⚠️ Current Limitations

| Feature | Status |
| :--- | :--- |
| Extraction engine | Rule-based regex — fails on complex/ambiguous phrasing without an explicit % or keyword |
| Matching scale | O(N) linear scan; works for 33 tasks, would need indexing for 10,000+ |
| CSV ingestion | Upload accepts file for preview only; DB merge not implemented |
| Role-based access | Role switcher is cosmetic — does not enforce permissions |
| Voice input | Not implemented |

---

## 🔮 Roadmap

- [ ] **LLM-backed extraction** — Gemini/LLaMA prompt for complex/multilingual field messages
- [ ] **Vector search** — FAISS/ChromaDB embeddings for enterprise-scale schedules
- [ ] **Full CSV ingestion** — Parse and merge Primavera export CSVs into the live DB
- [ ] **True RBAC** — Enforce role-level restrictions on review actions and admin controls
- [ ] **Actual duration tracking** — Auto-increment `actual_duration` from sequential updates
- [ ] **PostgreSQL backend** — Production-grade persistent storage

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for full terms.

---

*Built for Smart India Hackathon 2026 — Oil India Limited, Duliajan, Assam.*
