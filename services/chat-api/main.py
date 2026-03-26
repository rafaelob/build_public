"""VibeCoding Chat Atendente — API principal."""

import sys
from pathlib import Path

# Garante que o diretorio do servico esta no path
_service_dir = str(Path(__file__).resolve().parent)
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google import genai
from google.genai import types
from pydantic import BaseModel

from config import GEMINI_API_KEY, GEMINI_MODEL, APP_HOST, APP_PORT, ADMIN_TOKEN
from database import (
    init_db,
    get_db,
    ensure_session,
    save_message,
    get_history,
    save_lead,
    get_leads,
)
from prompts import SYSTEM_PROMPT


# --- Gemini client ---
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# --- Lifespan ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


# --- App ---
app = FastAPI(
    title="VibeCoding Chat Atendente",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str


class LeadRequest(BaseModel):
    session_id: str
    name: str | None = None
    email: str | None = None
    whatsapp: str | None = None
    product_interest: str | None = None
    notes: str | None = None


# --- Endpoints ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Envia mensagem e recebe resposta da IA."""
    session_id = req.session_id or str(uuid.uuid4())

    db = await get_db()
    try:
        await ensure_session(db, session_id)
        await save_message(db, session_id, "user", req.message)

        # Monta historico para o Gemini
        history = await get_history(db, session_id)
        contents = [
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["content"])],
            )
            for msg in history
        ]

        # Chama Gemini
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=500,
            ),
            contents=contents,
        )

        ai_text = response.text or "Desculpe, nao consegui gerar uma resposta. Tente novamente!"

        await save_message(db, session_id, "model", ai_text)

        return ChatResponse(session_id=session_id, response=ai_text)
    finally:
        await db.close()


@app.post("/api/leads")
async def create_lead(req: LeadRequest):
    """Registra um lead capturado."""
    db = await get_db()
    try:
        lead_id = await save_lead(
            db,
            session_id=req.session_id,
            name=req.name,
            email=req.email,
            whatsapp=req.whatsapp,
            product_interest=req.product_interest,
            notes=req.notes,
        )
        return {"id": lead_id, "status": "captured"}
    finally:
        await db.close()


@app.get("/api/leads")
async def list_leads(authorization: str = Header(default="")):
    """Lista leads capturados (protegido por token)."""
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Token invalido")
    db = await get_db()
    try:
        leads = await get_leads(db)
        return {"leads": leads, "total": len(leads)}
    finally:
        await db.close()


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok", "model": GEMINI_MODEL}


# --- Serve frontend ---
_web_dir = str(
    __import__("pathlib").Path(__file__).resolve().parent.parent.parent / "apps" / "web"
)
app.mount("/static", StaticFiles(directory=_web_dir), name="static")


@app.get("/")
async def serve_index():
    """Serve a pagina principal do chat."""
    return FileResponse(f"{_web_dir}/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=APP_HOST, port=int(APP_PORT))
