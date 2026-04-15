"""
scheduler/daily_limit.py — Controla o limite diário de postagens (persiste em JSON).
"""

import json
import logging
import os
from datetime import date
from typing import Any

from aishorts.config import DATA_DIR, DAILY_LIMIT, POSTS_LOG_PATH

logger = logging.getLogger(__name__)


def _carregar_log() -> dict[str, Any]:
    """Carrega o arquivo de log de postagens. Retorna dict vazio se não existir."""
    if not os.path.exists(POSTS_LOG_PATH):
        return {}
    try:
        with open(POSTS_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Erro ao ler o log de postagens: %s", exc)
        return {}


def _salvar_log(log: dict[str, Any]) -> None:
    """Salva o log de postagens no arquivo JSON."""
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(POSTS_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.error("Erro ao salvar o log de postagens: %s", exc)
        raise


def _hoje() -> str:
    """Retorna a data de hoje no formato YYYY-MM-DD."""
    return date.today().isoformat()


def can_post_today() -> bool:
    """
    Retorna True se o limite diário de postagens ainda não foi atingido.
    """
    count = get_today_count()
    pode = count < DAILY_LIMIT
    if not pode:
        logger.info(
            "Limite diário atingido: %d/%d postagens hoje.", count, DAILY_LIMIT
        )
    return pode


def get_today_count() -> int:
    """Retorna o número de postagens feitas hoje."""
    log = _carregar_log()
    hoje = _hoje()
    return log.get(hoje, {}).get("count", 0)


def get_posted_product_ids() -> list[str]:
    """Retorna todos os product_ids já postados hoje."""
    log = _carregar_log()
    hoje = _hoje()
    posts = log.get(hoje, {}).get("posts", [])
    return [p.get("product_id", "") for p in posts]


def ja_foi_postado(product_id: str) -> bool:
    """Verifica se um produto já foi postado hoje."""
    return product_id in get_posted_product_ids()


def register_post(
    product_id: str,
    youtube_url: str,
    video_path: str = "",
) -> None:
    """
    Registra uma nova postagem no log do dia.

    Estrutura do JSON:
    {
      "2026-04-15": {
        "count": 1,
        "posts": [
          {"product_id": "MLB123", "video_path": "output/...", "youtube_url": "https://..."}
        ]
      }
    }
    """
    log = _carregar_log()
    hoje = _hoje()

    if hoje not in log:
        log[hoje] = {"count": 0, "posts": []}

    log[hoje]["posts"].append(
        {
            "product_id": product_id,
            "video_path": video_path,
            "youtube_url": youtube_url,
        }
    )
    log[hoje]["count"] = len(log[hoje]["posts"])

    _salvar_log(log)
    logger.info(
        "Post registrado: produto=%s | url=%s | total hoje=%d",
        product_id,
        youtube_url,
        log[hoje]["count"],
    )
