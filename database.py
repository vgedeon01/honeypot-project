import sqlite3

DB = "soc.db"


def get_connection():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()

    # ============================================================
    # RAW COWRIE EVENTS
    # ============================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_id TEXT,
            session TEXT,
            protocol TEXT,
            src_ip TEXT,
            src_port INTEGER,
            dst_ip TEXT,
            dst_port INTEGER,
            sensor TEXT,
            uuid TEXT,
            message TEXT
        )
    """)

    # ============================================================
    # SSH SESSIONS
    # ============================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            start_time TEXT,
            end_time TEXT,
            src_ip TEXT,
            username TEXT,
            password TEXT,
            protocol TEXT,
            duration INTEGER,
            successful_login INTEGER DEFAULT 0
        )
    """)

    # ============================================================
    # COMMANDS
    # ============================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            command TEXT,
            category TEXT,

            FOREIGN KEY (session_id)
                REFERENCES sessions(session_id)
                ON DELETE CASCADE
        )
    """)

    # ============================================================
    # DOWNLOADS
    # ============================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            url TEXT,
            filename TEXT,
            sha256 TEXT,
            size INTEGER,

            FOREIGN KEY (session_id)
                REFERENCES sessions(session_id)
                ON DELETE CASCADE
        )
    """)

    # ============================================================
    # ALERTS
    # ============================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            alert_type TEXT,
            severity TEXT,
            src_ip TEXT,
            session_id TEXT,
            description TEXT,

            FOREIGN KEY (session_id)
                REFERENCES sessions(session_id)
                ON DELETE SET NULL
        )
    """)

    # ============================================================
    # INDEXES
    # ============================================================

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_timestamp
        ON events(timestamp)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_src_ip
        ON events(src_ip)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_session
        ON events(session)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_event_id
        ON events(event_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_events_uuid
        ON events(uuid)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_src_ip
        ON sessions(src_ip)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_start_time
        ON sessions(start_time)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_commands_session
        ON commands(session_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_commands_category
        ON commands(category)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_commands_timestamp
        ON commands(timestamp)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_session
        ON downloads(session_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_downloads_sha256
        ON downloads(sha256)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_severity
        ON alerts(severity)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_src_ip
        ON alerts(src_ip)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_timestamp
        ON alerts(timestamp)
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
