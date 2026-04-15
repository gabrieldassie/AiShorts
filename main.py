"""
main.py — Entry point do AiShorts. Orquestra o pipeline completo de criação e
postagem de YouTube Shorts de produtos afiliados do Mercado Livre.
"""

import logging
import sys

from aishorts.config import FINAL_VIDEO_PATH, NICHE
from aishorts.affiliate.link_generator import gerar_link_afiliado
from aishorts.content.script_generator import gerar_script
from aishorts.content.tts import gerar_narracao
from aishorts.crawler.mercadolivre import buscar_produtos_mais_vendidos
from aishorts.scheduler.daily_limit import (
    can_post_today,
    ja_foi_postado,
    register_post,
)
from aishorts.uploader.youtube import fazer_upload
from aishorts.video.editor import montar_short
from aishorts.video.generator import criar_imagem_produto

logger = logging.getLogger(__name__)


def run() -> None:
    """
    Executa o pipeline completo:
    1. Verifica o limite diário
    2. Busca produtos do Mercado Livre
    3. Seleciona o próximo produto não postado
    4. Gera link de afiliado
    5. Gera roteiro com Ollama
    6. Gera narração com Coqui TTS
    7. Baixa imagem do produto
    8. Monta o Short com MoviePy
    9. Faz upload para o YouTube
    10. Registra a postagem no log
    """
    # ── Verifica limite diário ─────────────────────────────────────────────────
    if not can_post_today():
        logger.info("⛔ Limite diário de postagens atingido. Tente novamente amanhã.")
        return

    # ── Busca produtos mais vendidos ──────────────────────────────────────────
    logger.info("🔍 Buscando produtos mais vendidos no Mercado Livre (nicho: %s)...", NICHE)
    produtos = buscar_produtos_mais_vendidos(NICHE)

    if not produtos:
        logger.error("❌ Nenhum produto encontrado. Verifique a configuração do nicho.")
        sys.exit(1)

    # ── Seleciona o primeiro produto ainda não postado hoje ───────────────────
    produto = None
    for p in produtos:
        if not ja_foi_postado(p["id"]):
            produto = p
            break

    if produto is None:
        logger.info("ℹ️ Todos os produtos do top 10 já foram postados hoje.")
        return

    logger.info("📦 Produto selecionado: %s (id=%s)", produto["title"], produto["id"])

    # ── Gera link de afiliado ─────────────────────────────────────────────────
    link_afiliado = gerar_link_afiliado(produto["permalink"])
    logger.info("🔗 Link de afiliado: %s", link_afiliado)

    # ── Gera roteiro com Ollama ───────────────────────────────────────────────
    logger.info("🤖 Gerando roteiro com Ollama...")
    conteudo = gerar_script(produto)

    # ── Gera narração com Coqui TTS ───────────────────────────────────────────
    logger.info("🎙️ Gerando narração em PT-BR...")
    gerar_narracao(conteudo["narration"])

    # ── Prepara imagem do produto ─────────────────────────────────────────────
    logger.info("🖼️ Preparando imagem do produto...")
    caminho_imagem = criar_imagem_produto(produto)

    # ── Monta o Short ─────────────────────────────────────────────────────────
    logger.info("🎬 Montando o YouTube Short...")
    montar_short(caminho_imagem, conteudo)

    # ── Faz upload para o YouTube ─────────────────────────────────────────────
    logger.info("📤 Fazendo upload para o YouTube...")
    url = fazer_upload(conteudo, link_afiliado, FINAL_VIDEO_PATH)

    # ── Registra a postagem ───────────────────────────────────────────────────
    register_post(produto["id"], url, FINAL_VIDEO_PATH)
    logger.info("✅ Short postado com sucesso: %s", url)


if __name__ == "__main__":
    run()
