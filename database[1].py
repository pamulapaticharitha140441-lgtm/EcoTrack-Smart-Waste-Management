import sqlite3
import hashlib
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("ecotrack.db")

def _hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt, digest

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS waste_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                quantity REAL NOT NULL CHECK(quantity > 0),
                collection_date TEXT NOT NULL,
                location TEXT NOT NULL,
                recyclable INTEGER NOT NULL CHECK(recyclable IN (0, 1)),
                notes TEXT DEFAULT ''
            )
        """)
        user = conn.execute("SELECT id FROM users WHERE username = ?", ("admin",)).fetchone()
        if user is None:
            salt, digest = _hash_password("EcoTrack@123")
            conn.execute(
                "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
                ("admin", salt, digest)
            )

def verify_login(username: str, password: str) -> bool:
    with get_connection() as conn:
        user = conn.execute(
            "SELECT salt, password_hash FROM users WHERE username = ?",
            (username.strip(),)
        ).fetchone()
    if user is None:
        return False
    _, digest = _hash_password(password, user["salt"])
    return digest == user["password_hash"]

def add_waste_record(category, quantity, collection_date, location, recyclable, notes):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO waste_records
            (category, quantity, collection_date, location, recyclable, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category, quantity, collection_date, location, int(recyclable), notes))

def get_waste_records():
    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM waste_records
            ORDER BY collection_date DESC, id DESC
        """).fetchall()

def delete_waste_record(record_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM waste_records WHERE id = ?", (record_id,))

def get_summary():
    with get_connection() as conn:
        totals = conn.execute("""
            SELECT
                COALESCE(SUM(quantity), 0) AS total,
                COALESCE(SUM(CASE WHEN recyclable = 1 THEN quantity ELSE 0 END), 0) AS recyclable,
                COALESCE(SUM(CASE WHEN recyclable = 0 THEN quantity ELSE 0 END), 0) AS non_recyclable,
                COUNT(*) AS records
            FROM waste_records
        """).fetchone()
        categories = conn.execute("""
            SELECT category, SUM(quantity) AS quantity
            FROM waste_records
            GROUP BY category
            ORDER BY quantity DESC
        """).fetchall()
    return totals, categories
