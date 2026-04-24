import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

_DB_PATH: Path | None = None


def init(db_path: Path) -> None:
    global _DB_PATH
    _DB_PATH = db_path
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _conn() as conn:
        _migrate(conn)


@contextmanager
def _conn():
    assert _DB_PATH is not None, "history.manager.init() não foi chamado"
    conn = sqlite3.connect(str(_DB_PATH))
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


def _migrate(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            attached_files TEXT DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS rag_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
            source_file TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            score REAL DEFAULT 0
        );

        -- FTS5 standalone table (maintained manually for reliability)
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            content,
            conversation_id UNINDEXED
        );
    """)


def _now() -> str:
    return datetime.now(UTC).isoformat()


# ── Conversations ─────────────────────────────────────────────────────────────


def create_conversation(conversation_id: str, title: str) -> dict:
    now = _now()
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (conversation_id, title, now, now),
        )
    return {"id": conversation_id, "title": title, "created_at": now, "updated_at": now}


def list_conversations(limit: int = 50) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def delete_conversation(conversation_id: str) -> bool:
    with _conn() as conn:
        # Remove from FTS before cascade delete
        msg_ids = conn.execute(
            "SELECT id FROM messages WHERE conversation_id=?", (conversation_id,)
        ).fetchall()
        for row in msg_ids:
            conn.execute("DELETE FROM messages_fts WHERE rowid=?", (row["id"],))
        conn.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
    return True


def search_conversations(query_text: str, limit: int = 20) -> list[dict]:
    safe = query_text.replace('"', "").strip()
    if not safe:
        return []
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT c.id, c.title, c.updated_at
            FROM messages_fts f
            JOIN conversations c ON c.id = f.conversation_id
            WHERE messages_fts MATCH ?
            ORDER BY c.updated_at DESC
            LIMIT ?
            """,
            (safe + "*", limit),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Messages ──────────────────────────────────────────────────────────────────


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    attached_files: list | None = None,
) -> int:
    now = _now()
    files_json = json.dumps(attached_files or [])
    with _conn() as conn:
        cursor = conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at, attached_files) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, role, content, now, files_json),
        )
        msg_id = cursor.lastrowid
        conn.execute(
            "UPDATE conversations SET updated_at=? WHERE id=?",
            (now, conversation_id),
        )
        conn.execute(
            "INSERT INTO messages_fts(rowid, content, conversation_id) VALUES (?, ?, ?)",
            (msg_id, content, conversation_id),
        )
    return msg_id  # type: ignore[return-value]


def get_messages(conversation_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, role, content, created_at, attached_files FROM messages WHERE conversation_id=? ORDER BY id",
            (conversation_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["attached_files"] = json.loads(d.get("attached_files") or "[]")
        result.append(d)
    return result


# ── RAG sources ───────────────────────────────────────────────────────────────


def save_rag_sources(conversation_id: str, message_id: int, sources: list[dict]) -> None:
    if not sources:
        return
    with _conn() as conn:
        conn.executemany(
            "INSERT INTO rag_sources (conversation_id, message_id, source_file, chunk_text, score) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    conversation_id,
                    message_id,
                    s["source_file"],
                    s["chunk_text"],
                    s.get("score", 0.0),
                )
                for s in sources
            ],
        )


def get_rag_sources(conversation_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT source_file, chunk_text, score FROM rag_sources WHERE conversation_id=? ORDER BY score DESC",
            (conversation_id,),
        ).fetchall()
    return [dict(r) for r in rows]
