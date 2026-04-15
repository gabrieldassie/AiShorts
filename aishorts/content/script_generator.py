"""
content/script_generator.py — Gera roteiro do vídeo usando Ollama (LLM local).
"""

import json
import logging
from typing import Any

import requests

from aishorts.config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)

# Prompt base para geração do roteiro
_PROMPT_TEMPLATE = """
Você é um criador de conteúdo especializado em marketing de afiliados para o YouTube.
Crie um roteiro de YouTube Short para o seguinte produto:

Nome: {title}
Preço: R$ {price:.2f}

Responda APENAS com um JSON válido (sem markdown, sem texto antes ou depois) com exatamente estas chaves:
{{
  "narration": "<narração de 30-45 segundos em PT-BR, animada e persuasiva, sem mencionar preço>",
  "title": "<título do YouTube com emoji, máximo 100 caracteres, inclua #Shorts>",
  "description": "<descrição do YouTube com call-to-action e o texto exato {{link_afiliado}} onde o link deve aparecer>",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5", "hashtag6", "hashtag7", "hashtag8", "hashtag9", "hashtag10"],
  "visual_prompt": "<prompt em inglês para gerar imagem do produto, estilo publicitário>"
}}
"""


def gerar_script(produto: dict[str, Any]) -> dict[str, Any]:
    """
    Envia o produto ao Ollama e retorna um dicionário com o conteúdo gerado:
      - narration, title, description, hashtags, visual_prompt
    """
    prompt = _PROMPT_TEMPLATE.format(
        title=produto.get("title", "Produto incrível"),
        price=float(produto.get("price", 0)),
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        logger.info("Gerando roteiro via Ollama (modelo: %s)...", OLLAMA_MODEL)
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        raw = response.json().get("response", "{}")
    except requests.exceptions.RequestException as exc:
        logger.error("Erro ao conectar no Ollama: %s", exc)
        return _fallback_script(produto)

    try:
        conteudo = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Resposta do Ollama não é JSON válido: %s | Resposta: %s", exc, raw)
        return _fallback_script(produto)

    # Garante que todas as chaves necessárias existem
    conteudo.setdefault("narration", f"Conheça o incrível {produto.get('title', 'produto')}!")
    conteudo.setdefault("title", f"🔥 {produto.get('title', 'Produto')} #Shorts")
    conteudo.setdefault(
        "description",
        f"{produto.get('title', 'Produto')} — Compre agora: {{link_afiliado}}\n#Shorts",
    )
    conteudo.setdefault("hashtags", ["#Shorts", "#MercadoLivre", "#Afiliados"])
    conteudo.setdefault("visual_prompt", f"Product photo of {produto.get('title', 'product')}")

    logger.info("Roteiro gerado com sucesso para o produto: %s", produto.get("title"))
    return conteudo


def _fallback_script(produto: dict[str, Any]) -> dict[str, Any]:
    """Retorna um roteiro padrão em caso de falha no Ollama."""
    titulo = produto.get("title", "Produto incrível")
    return {
        "narration": (
            f"Olha que produto incrível! {titulo}. "
            "Você não pode perder essa oportunidade! "
            "Clique no link da descrição e garanta o seu agora!"
        ),
        "title": f"🔥 {titulo[:80]} #Shorts",
        "description": (
            f"Confira este produto incrível: {titulo}\n"
            "👉 Compre aqui: {link_afiliado}\n\n"
            "#Shorts #MercadoLivre #Afiliados"
        ),
        "hashtags": [
            "#Shorts",
            "#MercadoLivre",
            "#Afiliados",
            "#Produto",
            "#Oferta",
            "#Desconto",
            "#Compras",
            "#Brasil",
            "#Eletrônicos",
            "#TopProduto",
        ],
        "visual_prompt": f"Professional product photo of {titulo}, white background, studio lighting",
    }
