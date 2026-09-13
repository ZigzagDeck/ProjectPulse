"""Database Schema definitions for SIH PS26122 Intelligent Schedule-Linking Layer."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('L1', 'L2', 'L3', 'L4', 'L5', 'L6')),
    parent_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    discipline TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    planned_duration INTEGER DEFAULT 1,
    actual_duration INTEGER DEFAULT 0,
    planned_start TEXT,
    planned_end TEXT,
    progress_pct REAL DEFAULT 0.0,
    status TEXT DEFAULT 'NOT_STARTED' CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'DELAYED')),
    last_updated TEXT
);

CREATE INDEX IF NOT EXISTS idx_tasks_level ON tasks(level);
CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_discipline ON tasks(discipline);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT DEFAULT 'general',
    sender_name TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    message_text TEXT NOT NULL,
    is_field_update INTEGER DEFAULT 0,
    linked_task_id TEXT REFERENCES tasks(id),
    confidence_score REAL,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_messages(timestamp);

CREATE TABLE IF NOT EXISTS audit_trail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER REFERENCES chat_messages(id),
    raw_input TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    extracted_task TEXT,
    extracted_state TEXT,
    extracted_progress_pct REAL,
    matched_node_id TEXT REFERENCES tasks(id),
    matched_node_name TEXT,
    confidence_score REAL,
    status TEXT NOT NULL CHECK (status IN ('AUTO_APPROVED', 'PENDING_REVIEW', 'MANUALLY_APPROVED', 'REJECTED')),
    reviewed_by TEXT,
    review_notes TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_trail(status);
CREATE INDEX IF NOT EXISTS idx_audit_matched_node ON audit_trail(matched_node_id);

CREATE TABLE IF NOT EXISTS synthetic_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    record_count INTEGER NOT NULL,
    upload_timestamp TEXT NOT NULL
);
"""
