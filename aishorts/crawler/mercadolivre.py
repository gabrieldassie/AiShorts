"""
crawler/mercadolivre.py — Busca os produtos mais vendidos do Mercado Livre via API pública.
"""

import logging
from typing import Any

import requests

from aishorts.config import ML_APP_ID, NICHE

logger = logging.getLogger(__name__)

# URL base da API do Mercado Livre
_ML_API_BASE = "https://api.mercadolibre.com"

# Número máximo de produtos a retornar
_TOP_N = 10


def buscar_produtos_mais_vendidos(nicho: str = NICHE) -> list[dict[str, Any]]:
    """
    Busca os produtos mais vendidos do Mercado Livre para o nicho informado.

    Retorna uma lista com os top _TOP_N produtos, cada um contendo:
      - id, title, price, thumbnail, permalink
    """
    url = f"{_ML_API_BASE}/sites/MLB/search"
    params = {
        "q": nicho,
        "sort": "sold_quantity_desc",
        "limit": _TOP_N,
    }
    headers = {}

    # Adiciona credencial de app se disponível (aumenta limite de requisições)
    if ML_APP_ID:
        headers["Authorization"] = f"Bearer {ML_APP_ID}"

    try:
        logger.info("Buscando produtos do Mercado Livre para o nicho: '%s'", nicho)
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        logger.error("Erro ao buscar produtos no Mercado Livre: %s", exc)
        return []

    resultados = data.get("results", [])
    produtos = []

    for item in resultados[:_TOP_N]:
        produtos.append(
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "price": item.get("price", 0.0),
                "thumbnail": item.get("thumbnail", ""),
                "permalink": item.get("permalink", ""),
            }
        )

    logger.info("%d produtos encontrados para o nicho '%s'", len(produtos), nicho)
    return produtos


def buscar_produto_top(nicho: str = NICHE) -> dict[str, Any] | None:
    """
    Retorna o primeiro produto mais vendido do nicho (ou None se não encontrar).
    """
    produtos = buscar_produtos_mais_vendidos(nicho)
    if not produtos:
        logger.warning("Nenhum produto encontrado para o nicho '%s'", nicho)
        return None
    return produtos[0]
