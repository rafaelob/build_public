"""Montagem dinamica do system prompt da Bia a partir do banco de dados."""

import aiosqlite


async def _get_configs(db: aiosqlite.Connection) -> dict[str, str]:
    """Carrega todas as configuracoes de prompt."""
    cursor = await db.execute(
        "SELECT config_key, config_value FROM prompt_config ORDER BY sort_order"
    )
    rows = await cursor.fetchall()
    return {row["config_key"]: row["config_value"] for row in rows}


async def _get_active_products(db: aiosqlite.Connection) -> list[dict]:
    """Carrega produtos ativos ordenados."""
    cursor = await db.execute(
        "SELECT name, price_display, description, target_audience "
        "FROM products WHERE is_active = 1 ORDER BY sort_order"
    )
    return [dict(row) for row in await cursor.fetchall()]


async def _get_active_skills(db: aiosqlite.Connection) -> list[dict]:
    """Carrega skills ativas ordenadas por categoria e ordem."""
    cursor = await db.execute(
        "SELECT name, category, prompt_instruction "
        "FROM skills WHERE is_active = 1 ORDER BY category, sort_order"
    )
    return [dict(row) for row in await cursor.fetchall()]


async def build_system_prompt(db: aiosqlite.Connection) -> str:
    """Monta o system prompt completo a partir do banco."""
    configs = await _get_configs(db)
    products = await _get_active_products(db)
    skills = await _get_active_skills(db)

    sections: list[str] = []

    # Identidade
    if identity := configs.get("identity"):
        sections.append(identity)

    # Personalidade
    if personality := configs.get("personality"):
        sections.append(personality)

    # Produtos
    if products:
        sections.append("\n## Produtos\n")
        for i, p in enumerate(products, 1):
            sections.append(f"### {i}. {p['name']} — {p['price_display']}")
            sections.append(p["description"])
            if p["target_audience"]:
                sections.append(f"- Ideal para: {p['target_audience']}")
            sections.append("")

    # Skills agrupadas por categoria
    category_labels = {
        "objective": "Seu objetivo",
        "rule": "Regras",
        "behavior": "Comportamentos",
    }
    for category, label in category_labels.items():
        cat_skills = [s for s in skills if s["category"] == category]
        if cat_skills:
            sections.append(f"\n## {label}\n")
            for s in cat_skills:
                sections.append(s["prompt_instruction"])

    # Restricoes
    if restrictions := configs.get("restrictions"):
        sections.append(f"\n{restrictions}")

    # Formato
    if format_rules := configs.get("format_rules"):
        sections.append(f"\n{format_rules}")

    return "\n".join(sections)
