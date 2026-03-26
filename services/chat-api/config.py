"""Configuracao do aplicativo — carrega variaveis de ambiente."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega .env da raiz do projeto
_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_root / ".env")

GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "change-this-token")
ADMIN_JWT_SECRET: str = os.getenv("ADMIN_JWT_SECRET", "troque-este-segredo-jwt-agora")
ADMIN_JWT_EXPIRY_HOURS: int = int(os.getenv("ADMIN_JWT_EXPIRY_HOURS", "24"))
DB_PATH: Path = _root / "data" / "chat.db"
