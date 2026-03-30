import sqlite3
import os

DB_NAME = "magxxic_knowledge.db"

def init_db():
    """Initializes the SQLite database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table for known domain-to-provider mappings (Learned/Feedback)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domain_map (
        domain TEXT PRIMARY KEY,
        provider TEXT NOT NULL,
        source TEXT DEFAULT 'auto', -- 'auto', 'user', 'ml'
        confidence REAL DEFAULT 1.0
    )
    """)

    # Table for fuzzy matching cache
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuzzy_cache (
        query TEXT PRIMARY KEY,
        match TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def get_cached_provider(domain):
    """Retrieves a provider for a domain if it exists in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT provider FROM domain_map WHERE domain = ?", (domain,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def save_domain_provider(domain, provider, source='auto'):
    """Saves or updates a domain-to-provider mapping."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO domain_map (domain, provider, source)
    VALUES (?, ?, ?)
    ON CONFLICT(domain) DO UPDATE SET provider=excluded.provider, source=excluded.source
    """, (domain, provider, source))
    conn.commit()
    conn.close()

def get_user_overrides():
    """Retrieves all user-defined overrides."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT domain, provider FROM domain_map WHERE source = 'user'")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

# Initialize on import
init_db()
