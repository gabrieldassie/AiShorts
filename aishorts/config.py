"""
config.py — Carrega configurações e variáveis de ambiente do projeto AiShorts.
"""

import os
import logging
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# ── Mercado Livre ──────────────────────────────────────────────────────────────
ML_APP_ID: str = os.getenv("ML_APP_ID", "")
ML_SECRET: str = os.getenv("ML_SECRET", "")
ML_AFFILIATE_TAG: str = os.getenv("ML_AFFILIATE_TAG", "")

# ── YouTube ────────────────────────────────────────────────────────────────────
YOUTUBE_CLIENT_SECRET_PATH: str = os.getenv(
    "YOUTUBE_CLIENT_SECRET_PATH", "client_secret.json"
)

# ── Ollama (LLM local) ─────────────────────────────────────────────────────────
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Scheduler ─────────────────────────────────────────────────────────────────
DAILY_LIMIT: int = int(os.getenv("DAILY_LIMIT", "3"))

# ── Nicho de produtos ─────────────────────────────────────────────────────────
NICHE: str = os.getenv("NICHE", "eletrônicos")

# ── Caminhos de saída ─────────────────────────────────────────────────────────
OUTPUT_DIR: str = os.path.join(os.path.dirname(__file__), "..", "output")
DATA_DIR: str = os.path.join(os.path.dirname(__file__), "..", "data")
POSTS_LOG_PATH: str = os.path.join(DATA_DIR, "posts_log.json")
NARRATION_PATH: str = os.path.join(OUTPUT_DIR, "narration.wav")
FINAL_VIDEO_PATH: str = os.path.join(OUTPUT_DIR, "final_short.mp4")

# ── Logging padrão ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
