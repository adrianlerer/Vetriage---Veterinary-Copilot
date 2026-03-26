"""
SQLite-based storage for API keys and usage tracking.
Lightweight, no external DB dependency — upgrade to PostgreSQL/Supabase when needed.
"""

import sqlite3
import os
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from contextlib import contextmanager

from .models import Tier, APIKeyRecord, UsageRecord, TIER_CONFIG


DB_PATH = os.getenv("VETRIAGE_DB_PATH", "vetriage_billing.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                api_key_hash TEXT NOT NULL UNIQUE,
                owner_email TEXT NOT NULL,
                owner_name TEXT,
                tier TEXT NOT NULL DEFAULT 'free',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_time_ms INTEGER DEFAULT 0,
                status_code INTEGER DEFAULT 200,
                tokens_used INTEGER DEFAULT 0,
                estimated_cost_usd REAL DEFAULT 0.0,
                FOREIGN KEY (key_id) REFERENCES api_keys(key_id)
            );

            CREATE INDEX IF NOT EXISTS idx_usage_key_time
                ON usage_logs(key_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_usage_endpoint
                ON usage_logs(endpoint, timestamp);
            CREATE INDEX IF NOT EXISTS idx_api_key_hash
                ON api_keys(api_key_hash);
        """)


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key(owner_email: str, owner_name: str = None, tier: Tier = Tier.FREE) -> Tuple[str, str]:
    """Create a new API key. Returns (key_id, raw_api_key). The raw key is shown only once."""
    key_id = f"vtg_{secrets.token_hex(8)}"
    raw_key = f"vtg_live_{secrets.token_urlsafe(32)}"
    key_hash = _hash_key(raw_key)
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        conn.execute(
            """INSERT INTO api_keys (key_id, api_key_hash, owner_email, owner_name, tier, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, 1, ?)""",
            (key_id, key_hash, owner_email, owner_name, tier.value, now),
        )
    return key_id, raw_key


def validate_api_key(raw_key: str) -> Optional[APIKeyRecord]:
    """Validate an API key and return its record, or None if invalid."""
    key_hash = _hash_key(raw_key)
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM api_keys WHERE api_key_hash = ? AND is_active = 1",
            (key_hash,),
        ).fetchone()
        if not row:
            return None
        if row["expires_at"]:
            if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
                return None
        return APIKeyRecord(
            key_id=row["key_id"],
            api_key_hash=row["api_key_hash"],
            owner_email=row["owner_email"],
            owner_name=row["owner_name"],
            tier=Tier(row["tier"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None,
        )


def log_usage(key_id: str, endpoint: str, response_time_ms: int = 0,
              status_code: int = 200, tokens_used: int = 0, estimated_cost_usd: float = 0.0):
    """Log an API call."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO usage_logs (key_id, endpoint, timestamp, response_time_ms, status_code, tokens_used, estimated_cost_usd)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (key_id, endpoint, datetime.utcnow().isoformat(), response_time_ms, status_code, tokens_used, estimated_cost_usd),
        )


def get_monthly_usage(key_id: str) -> int:
    """Get total requests this calendar month."""
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM usage_logs WHERE key_id = ? AND timestamp >= ?",
            (key_id, start_of_month.isoformat()),
        ).fetchone()
        return row["cnt"] if row else 0


def get_minute_usage(key_id: str) -> int:
    """Get requests in the last 60 seconds."""
    one_minute_ago = (datetime.utcnow() - timedelta(seconds=60)).isoformat()
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM usage_logs WHERE key_id = ? AND timestamp >= ?",
            (key_id, one_minute_ago),
        ).fetchone()
        return row["cnt"] if row else 0


def get_usage_summary(key_id: str) -> dict:
    """Get usage summary for dashboard display."""
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) as cnt, SUM(estimated_cost_usd) as cost FROM usage_logs WHERE key_id = ? AND timestamp >= ?",
            (key_id, start_of_month.isoformat()),
        ).fetchone()

        by_endpoint = conn.execute(
            """SELECT endpoint, COUNT(*) as cnt, SUM(estimated_cost_usd) as cost, AVG(response_time_ms) as avg_ms
               FROM usage_logs WHERE key_id = ? AND timestamp >= ?
               GROUP BY endpoint ORDER BY cnt DESC""",
            (key_id, start_of_month.isoformat()),
        ).fetchall()

        daily = conn.execute(
            """SELECT DATE(timestamp) as day, COUNT(*) as cnt
               FROM usage_logs WHERE key_id = ? AND timestamp >= ?
               GROUP BY DATE(timestamp) ORDER BY day""",
            (key_id, start_of_month.isoformat()),
        ).fetchall()

    return {
        "period": f"{start_of_month.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}",
        "total_requests": total["cnt"] if total else 0,
        "total_cost_usd": round(total["cost"] or 0, 4),
        "by_endpoint": [{"endpoint": r["endpoint"], "requests": r["cnt"], "cost_usd": round(r["cost"] or 0, 4), "avg_response_ms": round(r["avg_ms"] or 0)} for r in by_endpoint],
        "daily": [{"date": r["day"], "requests": r["cnt"]} for r in daily],
    }


def deactivate_key(key_id: str):
    with get_db() as conn:
        conn.execute("UPDATE api_keys SET is_active = 0 WHERE key_id = ?", (key_id,))


def update_tier(key_id: str, new_tier: Tier):
    with get_db() as conn:
        conn.execute("UPDATE api_keys SET tier = ? WHERE key_id = ?", (new_tier.value, key_id))
