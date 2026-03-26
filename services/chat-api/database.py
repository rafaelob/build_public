"""Banco de dados SQLite para conversas, leads e admin."""

import aiosqlite
from config import DB_PATH


# ---------------------------------------------------------------------------
# Init & connection
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Cria as tabelas se nao existirem e faz seed dos dados default."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA_SQL)
        await _seed_defaults(db)


async def get_db() -> aiosqlite.Connection:
    """Retorna conexao ao banco."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
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

    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        price_display TEXT NOT NULL,
        price_cents INTEGER,
        description TEXT NOT NULL,
        target_audience TEXT,
        sort_order INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL DEFAULT 'behavior',
        description TEXT NOT NULL,
        prompt_instruction TEXT NOT NULL,
        sort_order INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS prompt_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_key TEXT NOT NULL UNIQUE,
        config_value TEXT NOT NULL,
        label TEXT NOT NULL,
        description TEXT,
        sort_order INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT DEFAULT (datetime('now'))
    );
"""


# ---------------------------------------------------------------------------
# Seed defaults
# ---------------------------------------------------------------------------

async def _seed_defaults(db: aiosqlite.Connection) -> None:
    """Insere dados default apenas se as tabelas estiverem vazias."""
    # Admin user
    cur = await db.execute("SELECT COUNT(*) as c FROM admin_users")
    row = await cur.fetchone()
    if row["c"] == 0:
        from auth import hash_password
        await db.execute(
            "INSERT INTO admin_users (username, password_hash, display_name) VALUES (?, ?, ?)",
            ("admin", hash_password("vibecoding2024"), "Administrador"),
        )

    # Products
    cur = await db.execute("SELECT COUNT(*) as c FROM products")
    row = await cur.fetchone()
    if row["c"] == 0:
        for p in _DEFAULT_PRODUCTS:
            await db.execute(
                "INSERT INTO products (name, slug, price_display, price_cents, description, target_audience, sort_order) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (p["name"], p["slug"], p["price_display"], p["price_cents"],
                 p["description"], p["target_audience"], p["sort_order"]),
            )

    # Skills
    cur = await db.execute("SELECT COUNT(*) as c FROM skills")
    row = await cur.fetchone()
    if row["c"] == 0:
        for s in _DEFAULT_SKILLS:
            await db.execute(
                "INSERT INTO skills (name, slug, category, description, prompt_instruction, sort_order) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (s["name"], s["slug"], s["category"], s["description"],
                 s["prompt_instruction"], s["sort_order"]),
            )

    # Prompt config
    cur = await db.execute("SELECT COUNT(*) as c FROM prompt_config")
    row = await cur.fetchone()
    if row["c"] == 0:
        for c in _DEFAULT_PROMPT_CONFIG:
            await db.execute(
                "INSERT INTO prompt_config (config_key, config_value, label, description, sort_order) "
                "VALUES (?, ?, ?, ?, ?)",
                (c["config_key"], c["config_value"], c["label"],
                 c["description"], c["sort_order"]),
            )

    await db.commit()


_DEFAULT_PRODUCTS = [
    {
        "name": "Comunidade VibeCoding",
        "slug": "comunidade",
        "price_display": "R$ 3.000/ano",
        "price_cents": 300000,
        "description": "- Para quem quer COMECAR com vibe coding\n- Acesso a comunidade com outros alunos\n- Conteudo gravado + atualizacoes\n- Melhor custo-beneficio para comecar",
        "target_audience": "Iniciantes e curiosos",
        "sort_order": 1,
    },
    {
        "name": "Mentoria VibeCoding",
        "slug": "mentoria",
        "price_display": "R$ 20.000",
        "price_cents": 2000000,
        "description": "- Para quem quer ACELERAR resultados\n- Acompanhamento proximo e personalizado\n- Sessoes ao vivo com o mentor\n- Para quem leva a serio e quer resultado rapido",
        "target_audience": "Profissionais e empreendedores com projeto",
        "sort_order": 2,
    },
    {
        "name": "Consultoria VibeCoding",
        "slug": "consultoria",
        "price_display": "R$ 100.000",
        "price_cents": 10000000,
        "description": "- Para EMPRESAS que querem implementar IA nos processos\n- Projeto sob medida para a empresa\n- Acompanhamento executivo\n- Investimento com retorno direto no negocio",
        "target_audience": "Empresas e times",
        "sort_order": 3,
    },
]

_DEFAULT_SKILLS = [
    # Objectives
    {"name": "Acolher", "slug": "acolher", "category": "objective",
     "description": "Bia cumprimenta e entende o que a pessoa procura",
     "prompt_instruction": "1. ACOLHER: Cumprimentar e entender o que a pessoa procura", "sort_order": 1},
    {"name": "Qualificar", "slug": "qualificar", "category": "objective",
     "description": "Bia faz perguntas para entender o perfil do visitante",
     "prompt_instruction": "2. QUALIFICAR: Fazer perguntas para entender o perfil (nivel tecnico, objetivo, urgencia, orcamento)", "sort_order": 2},
    {"name": "Recomendar", "slug": "recomendar", "category": "objective",
     "description": "Bia sugere o produto mais adequado",
     "prompt_instruction": "3. RECOMENDAR: Sugerir o produto mais adequado com base no perfil", "sort_order": 3},
    {"name": "Capturar Lead", "slug": "capturar-lead", "category": "objective",
     "description": "Bia pede contato quando ha interesse",
     "prompt_instruction": "4. CAPTURAR: Quando a pessoa demonstrar interesse, pedir nome e WhatsApp/email para o time entrar em contato", "sort_order": 4},
    # Rules
    {"name": "Regra de Qualificacao", "slug": "regra-qualificacao", "category": "rule",
     "description": "Regras para mapear perfil ao produto certo",
     "prompt_instruction": "## Regras de qualificacao\n- Iniciante curioso, sem urgencia, orcamento limitado -> Comunidade\n- Profissional/empreendedor com projeto, quer resultado rapido -> Mentoria\n- Empresa, time, orcamento corporativo -> Consultoria\n- Se nao conseguir qualificar, pergunte mais antes de recomendar", "sort_order": 5},
    {"name": "Regra de Captura", "slug": "regra-captura", "category": "rule",
     "description": "Quando e como pedir contato",
     "prompt_instruction": "## Regras de captura de lead\n- NAO peca contato logo de cara. Primeiro entenda a pessoa.\n- Quando a pessoa demonstrar interesse claro (\"quero saber mais\", \"como faco pra entrar\", \"quanto custa\", \"me interessei\"), ai peca o contato de forma natural:\n  \"Massa! Pra gente dar o proximo passo, me passa seu nome e WhatsApp (ou email) que o time entra em contato rapidinho?\"\n- Se a pessoa fornecer dados de contato, responda confirmando e agradecendo.", "sort_order": 6},
    {"name": "Nao Inventar", "slug": "nao-inventar", "category": "rule",
     "description": "Bia nunca inventa informacoes",
     "prompt_instruction": "- NUNCA inventa informacoes que nao estao aqui", "sort_order": 7},
    {"name": "Nao Prometer Resultados", "slug": "nao-prometer", "category": "rule",
     "description": "Bia nao promete resultados financeiros",
     "prompt_instruction": "- NAO promete resultados financeiros especificos", "sort_order": 8},
    {"name": "Nao Processar Pagamento", "slug": "nao-pagamento", "category": "rule",
     "description": "Bia nao processa pagamentos",
     "prompt_instruction": "- NAO processa pagamentos ou matriculas", "sort_order": 9},
    {"name": "Fallback", "slug": "fallback", "category": "rule",
     "description": "O que fazer quando nao sabe responder",
     "prompt_instruction": "- Se perguntarem algo que voce nao sabe, diga: \"Essa e uma otima pergunta! Vou pedir pro time te responder com mais detalhes. Me passa seu contato?\"", "sort_order": 10},
    # Behaviors
    {"name": "Tom Informal", "slug": "tom-informal", "category": "behavior",
     "description": "Portugues brasileiro informal mas profissional",
     "prompt_instruction": "- Fala portugues brasileiro natural, informal mas profissional", "sort_order": 11},
    {"name": "Emojis Moderados", "slug": "emojis-moderados", "category": "behavior",
     "description": "Usa 1-2 emojis por mensagem no maximo",
     "prompt_instruction": "- Usa emojis com moderacao (1-2 por mensagem, no maximo)", "sort_order": 12},
    {"name": "Respostas Curtas", "slug": "respostas-curtas", "category": "behavior",
     "description": "Mensagens de 2-4 frases",
     "prompt_instruction": "- Respostas curtas e objetivas (2-4 frases por mensagem)", "sort_order": 13},
    {"name": "Terminar com Pergunta", "slug": "terminar-pergunta", "category": "behavior",
     "description": "Sempre termina com pergunta ou CTA",
     "prompt_instruction": "- Sempre termine com uma pergunta ou chamada pra acao", "sort_order": 14},
    {"name": "Simpatica e Entusiasmada", "slug": "simpatica", "category": "behavior",
     "description": "Personalidade acolhedora",
     "prompt_instruction": "- Simpatica, direta e entusiasmada com vibe coding", "sort_order": 15},
]

_DEFAULT_PROMPT_CONFIG = [
    {
        "config_key": "identity",
        "config_value": "Voce e a Bia, atendente virtual da VibeCoding — empresa especializada em ensinar vibe coding (construir software com IA, sem precisar saber programar).",
        "label": "Identidade",
        "description": "Quem a Bia e. Primeira linha do prompt.",
        "sort_order": 1,
    },
    {
        "config_key": "personality",
        "config_value": "## Sua personalidade\nSimpatica, direta e entusiasmada com vibe coding. Fala portugues brasileiro natural, informal mas profissional.",
        "label": "Personalidade",
        "description": "Tracos de personalidade e tom de voz da Bia.",
        "sort_order": 2,
    },
    {
        "config_key": "restrictions",
        "config_value": "## O que voce NAO faz\n- NAO processa pagamentos ou matriculas\n- NAO promete resultados financeiros especificos\n- NAO inventa informacoes que nao estao aqui\n- NAO fala mal de concorrentes\n- NAO da consultoria tecnica gratuita (direcione para os produtos)",
        "label": "Restricoes",
        "description": "O que a Bia nao deve fazer em hipotese alguma.",
        "sort_order": 3,
    },
    {
        "config_key": "format_rules",
        "config_value": "## Formato das respostas\n- Respostas curtas (2-4 frases)\n- Sempre termine com uma pergunta ou chamada pra acao\n- Use quebras de linha para facilitar leitura",
        "label": "Formato de Respostas",
        "description": "Regras de formatacao das mensagens da Bia.",
        "sort_order": 4,
    },
]


# ---------------------------------------------------------------------------
# Chat helpers (existentes)
# ---------------------------------------------------------------------------

async def ensure_session(db: aiosqlite.Connection, session_id: str) -> None:
    """Cria sessao se nao existe."""
    await db.execute("INSERT OR IGNORE INTO sessions (id) VALUES (?)", (session_id,))
    await db.commit()


async def save_message(db: aiosqlite.Connection, session_id: str, role: str, content: str) -> None:
    """Salva uma mensagem na conversa."""
    await db.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    await db.execute(
        "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?", (session_id,),
    )
    await db.commit()


async def get_history(db: aiosqlite.Connection, session_id: str) -> list[dict[str, str]]:
    """Retorna historico de mensagens da sessao."""
    cursor = await db.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
        (session_id,),
    )
    rows = await cursor.fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


async def save_lead(db: aiosqlite.Connection, session_id: str, **kwargs) -> int:
    """Salva um lead capturado."""
    fields = ["name", "email", "whatsapp", "product_interest", "notes"]
    values = [kwargs.get(f) for f in fields]
    cursor = await db.execute(
        f"INSERT INTO leads (session_id, {', '.join(fields)}) VALUES (?, {', '.join('?' * len(fields))})",
        (session_id, *values),
    )
    await db.commit()
    return cursor.lastrowid  # type: ignore[return-value]


async def get_leads(db: aiosqlite.Connection, page: int = 1, per_page: int = 20) -> tuple[list[dict], int]:
    """Retorna leads paginados e total."""
    cur = await db.execute("SELECT COUNT(*) as c FROM leads")
    total = (await cur.fetchone())["c"]
    offset = (page - 1) * per_page
    cursor = await db.execute(
        "SELECT l.*, s.created_at as session_start FROM leads l "
        "LEFT JOIN sessions s ON l.session_id = s.id "
        "ORDER BY l.created_at DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows], total


# ---------------------------------------------------------------------------
# Admin helpers
# ---------------------------------------------------------------------------

async def get_admin_by_username(db: aiosqlite.Connection, username: str) -> dict | None:
    """Busca admin por username."""
    cursor = await db.execute(
        "SELECT * FROM admin_users WHERE username = ? AND is_active = 1", (username,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_admin_by_id(db: aiosqlite.Connection, user_id: int) -> dict | None:
    """Busca admin por ID."""
    cursor = await db.execute(
        "SELECT id, username, display_name FROM admin_users WHERE id = ? AND is_active = 1",
        (user_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_stats(db: aiosqlite.Connection) -> dict:
    """Retorna estatisticas do dashboard."""
    stats = {}
    for key, sql in [
        ("total_sessions", "SELECT COUNT(*) as c FROM sessions"),
        ("total_messages", "SELECT COUNT(*) as c FROM messages"),
        ("total_leads", "SELECT COUNT(*) as c FROM leads"),
        ("leads_today", "SELECT COUNT(*) as c FROM leads WHERE date(created_at) = date('now')"),
        ("leads_this_week", "SELECT COUNT(*) as c FROM leads WHERE created_at >= datetime('now', '-7 days')"),
    ]:
        cur = await db.execute(sql)
        stats[key] = (await cur.fetchone())["c"]
    return stats


# ---------------------------------------------------------------------------
# Products CRUD
# ---------------------------------------------------------------------------

async def list_products(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute("SELECT * FROM products ORDER BY sort_order")
    return [dict(row) for row in await cursor.fetchall()]


async def create_product(db: aiosqlite.Connection, data: dict) -> dict:
    cursor = await db.execute(
        "INSERT INTO products (name, slug, price_display, price_cents, description, target_audience, sort_order, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING *",
        (data["name"], data["slug"], data["price_display"], data.get("price_cents"),
         data["description"], data.get("target_audience"), data.get("sort_order", 0),
         data.get("is_active", 1)),
    )
    await db.commit()
    return dict(await cursor.fetchone())


async def update_product(db: aiosqlite.Connection, product_id: int, data: dict) -> dict | None:
    allowed = {"name", "slug", "price_display", "price_cents", "description", "target_audience", "sort_order", "is_active"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return None
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [product_id]
    await db.execute(
        f"UPDATE products SET {set_clause}, updated_at = datetime('now') WHERE id = ?", values,
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def delete_product(db: aiosqlite.Connection, product_id: int) -> bool:
    cursor = await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    await db.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Skills CRUD
# ---------------------------------------------------------------------------

async def list_skills(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute("SELECT * FROM skills ORDER BY category, sort_order")
    return [dict(row) for row in await cursor.fetchall()]


async def create_skill(db: aiosqlite.Connection, data: dict) -> dict:
    cursor = await db.execute(
        "INSERT INTO skills (name, slug, category, description, prompt_instruction, sort_order, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING *",
        (data["name"], data["slug"], data.get("category", "behavior"),
         data["description"], data["prompt_instruction"],
         data.get("sort_order", 0), data.get("is_active", 1)),
    )
    await db.commit()
    return dict(await cursor.fetchone())


async def update_skill(db: aiosqlite.Connection, skill_id: int, data: dict) -> dict | None:
    allowed = {"name", "slug", "category", "description", "prompt_instruction", "sort_order", "is_active"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return None
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [skill_id]
    await db.execute(
        f"UPDATE skills SET {set_clause}, updated_at = datetime('now') WHERE id = ?", values,
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def delete_skill(db: aiosqlite.Connection, skill_id: int) -> bool:
    cursor = await db.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    await db.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Prompt Config
# ---------------------------------------------------------------------------

async def list_prompt_configs(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute("SELECT * FROM prompt_config ORDER BY sort_order")
    return [dict(row) for row in await cursor.fetchall()]


async def update_prompt_config(db: aiosqlite.Connection, config_key: str, config_value: str) -> dict | None:
    await db.execute(
        "UPDATE prompt_config SET config_value = ?, updated_at = datetime('now') WHERE config_key = ?",
        (config_value, config_key),
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM prompt_config WHERE config_key = ?", (config_key,))
    row = await cursor.fetchone()
    return dict(row) if row else None
