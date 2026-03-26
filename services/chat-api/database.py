"""Banco de dados SQLite para conversas e leads."""

import aiosqlite
from config import DB_PATH


async def init_db() -> None:
    """Cria as tabelas se nao existirem."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                role TEXT NOT NULL CHECK (role IN ('user', 'model')),
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT REFERENCES sessions(id),
                name TEXT,
                email TEXT,
                whatsapp TEXT,
                product_interest TEXT,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, created_at);
        """)


async def get_db() -> aiosqlite.Connection:
    """Retorna conexao ao banco."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def ensure_session(db: aiosqlite.Connection, session_id: str) -> None:
    """Cria sessao se nao existe."""
    await db.execute(
        "INSERT OR IGNORE INTO sessions (id) VALUES (?)",
        (session_id,),
    )
    await db.commit()


async def save_message(
    db: aiosqlite.Connection, session_id: str, role: str, content: str
) -> None:
    """Salva uma mensagem na conversa."""
    await db.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    await db.execute(
        "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?",
        (session_id,),
    )
    await db.commit()


async def get_history(
    db: aiosqlite.Connection, session_id: str
) -> list[dict[str, str]]:
    """Retorna historico de mensagens da sessao."""
    cursor = await db.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
        (session_id,),
    )
    rows = await cursor.fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


async def save_lead(
    db: aiosqlite.Connection,
    session_id: str,
    name: str | None = None,
    email: str | None = None,
    whatsapp: str | None = None,
    product_interest: str | None = None,
    notes: str | None = None,
) -> int:
    """Salva um lead capturado."""
    cursor = await db.execute(
        """INSERT INTO leads (session_id, name, email, whatsapp, product_interest, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session_id, name, email, whatsapp, product_interest, notes),
    )
    await db.commit()
    return cursor.lastrowid  # type: ignore[return-value]


async def get_leads(db: aiosqlite.Connection) -> list[dict]:
    """Retorna todos os leads."""
    cursor = await db.execute(
        """SELECT l.*, s.created_at as session_start
           FROM leads l
           LEFT JOIN sessions s ON l.session_id = s.id
           ORDER BY l.created_at DESC"""
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
