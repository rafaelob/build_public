"""Rotas administrativas — login, CRUD de produtos/skills/prompt, leads, stats."""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from auth import verify_password, create_token, decode_token
from database import (
    get_db,
    get_admin_by_username,
    get_admin_by_id,
    get_stats,
    list_products,
    create_product,
    update_product,
    delete_product,
    list_skills,
    create_skill,
    update_skill,
    delete_skill,
    list_prompt_configs,
    update_prompt_config,
    get_leads,
)
from prompt_builder import build_system_prompt

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

async def get_current_admin(authorization: str = Header(default="")):
    """Valida JWT e retorna dados do admin."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")
    db = await get_db()
    try:
        admin = await get_admin_by_id(db, int(payload["sub"]))
        if not admin:
            raise HTTPException(status_code=401, detail="Usuario nao encontrado")
        return admin
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(req: LoginRequest):
    db = await get_db()
    try:
        admin = await get_admin_by_username(db, req.username)
        if not admin or not verify_password(req.password, admin["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciais invalidas")
        token, expires_in = create_token(admin["id"], admin["username"])
        return {
            "token": token,
            "display_name": admin["display_name"],
            "expires_in": expires_in,
        }
    finally:
        await db.close()


@router.get("/me")
async def me(admin: dict = Depends(get_current_admin)):
    return admin


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/stats")
async def stats(admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        return await get_stats(db)
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Products CRUD
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    name: str
    slug: str
    price_display: str
    price_cents: int | None = None
    description: str
    target_audience: str | None = None
    sort_order: int = 0
    is_active: int = 1


class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    price_display: str | None = None
    price_cents: int | None = None
    description: str | None = None
    target_audience: str | None = None
    sort_order: int | None = None
    is_active: int | None = None


@router.get("/products")
async def products_list(admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        products = await list_products(db)
        return {"products": products, "total": len(products)}
    finally:
        await db.close()


@router.post("/products")
async def products_create(req: ProductCreate, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        product = await create_product(db, req.model_dump())
        return product
    finally:
        await db.close()


@router.put("/products/{product_id}")
async def products_update(product_id: int, req: ProductUpdate, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        data = {k: v for k, v in req.model_dump().items() if v is not None}
        product = await update_product(db, product_id, data)
        if not product:
            raise HTTPException(status_code=404, detail="Produto nao encontrado")
        return product
    finally:
        await db.close()


@router.delete("/products/{product_id}")
async def products_delete(product_id: int, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        if not await delete_product(db, product_id):
            raise HTTPException(status_code=404, detail="Produto nao encontrado")
        return {"status": "deleted"}
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Skills CRUD
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    name: str
    slug: str
    category: str = "behavior"
    description: str
    prompt_instruction: str
    sort_order: int = 0
    is_active: int = 1


class SkillUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    category: str | None = None
    description: str | None = None
    prompt_instruction: str | None = None
    sort_order: int | None = None
    is_active: int | None = None


@router.get("/skills")
async def skills_list(admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        skills = await list_skills(db)
        return {"skills": skills, "total": len(skills)}
    finally:
        await db.close()


@router.post("/skills")
async def skills_create(req: SkillCreate, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        skill = await create_skill(db, req.model_dump())
        return skill
    finally:
        await db.close()


@router.put("/skills/{skill_id}")
async def skills_update(skill_id: int, req: SkillUpdate, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        data = {k: v for k, v in req.model_dump().items() if v is not None}
        skill = await update_skill(db, skill_id, data)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill nao encontrada")
        return skill
    finally:
        await db.close()


@router.delete("/skills/{skill_id}")
async def skills_delete(skill_id: int, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        if not await delete_skill(db, skill_id):
            raise HTTPException(status_code=404, detail="Skill nao encontrada")
        return {"status": "deleted"}
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Prompt Config
# ---------------------------------------------------------------------------

class PromptConfigUpdate(BaseModel):
    config_value: str


@router.get("/prompt-config")
async def prompt_config_list(admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        configs = await list_prompt_configs(db)
        return {"configs": configs}
    finally:
        await db.close()


@router.put("/prompt-config/{config_key}")
async def prompt_config_update(config_key: str, req: PromptConfigUpdate, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        config = await update_prompt_config(db, config_key, req.config_value)
        if not config:
            raise HTTPException(status_code=404, detail="Config nao encontrada")
        return config
    finally:
        await db.close()


@router.get("/prompt-preview")
async def prompt_preview(admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        prompt = await build_system_prompt(db)
        return {"prompt": prompt, "char_count": len(prompt), "token_estimate": len(prompt) // 4}
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Leads (upgraded with pagination)
# ---------------------------------------------------------------------------

@router.get("/leads")
async def leads_list(page: int = 1, per_page: int = 20, admin: dict = Depends(get_current_admin)):
    db = await get_db()
    try:
        leads, total = await get_leads(db, page, per_page)
        return {
            "leads": leads,
            "total": total,
            "page": page,
            "pages": (total + per_page - 1) // per_page,
        }
    finally:
        await db.close()
