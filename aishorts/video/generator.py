"""
video/generator.py — Baixa e prepara imagens/clipes do produto para o Short.
"""

import logging
import os
from typing import Any

import requests

from aishorts.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def baixar_thumbnail(produto: dict[str, Any]) -> str | None:
    """
    Baixa a thumbnail do produto e salva em output/thumbnail.jpg.
    Retorna o caminho do arquivo ou None em caso de falha.
    """
    url_thumbnail = produto.get("thumbnail", "")
    if not url_thumbnail:
        logger.warning("Produto sem thumbnail: %s", produto.get("id"))
        return None

    # Melhora a resolução da imagem (substitui tamanho pequeno pelo grande)
    url_thumbnail = url_thumbnail.replace("-I.jpg", "-O.jpg").replace(
        "-I.webp", "-O.webp"
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caminho = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

    try:
        logger.info("Baixando thumbnail do produto: %s", url_thumbnail)
        response = requests.get(url_thumbnail, timeout=15)
        response.raise_for_status()
        with open(caminho, "wb") as f:
            f.write(response.content)
        logger.info("Thumbnail salva em: %s", caminho)
        return caminho
    except requests.exceptions.RequestException as exc:
        logger.error("Erro ao baixar thumbnail: %s", exc)
        return None


def criar_imagem_produto(produto: dict[str, Any]) -> str:
    """
    Prepara a imagem do produto para uso no vídeo.
    Tenta baixar a thumbnail; se falhar, cria uma imagem placeholder.
    Retorna o caminho da imagem.
    """
    caminho = baixar_thumbnail(produto)
    if caminho:
        return caminho

    # Cria imagem placeholder se thumbnail não estiver disponível
    return _criar_placeholder(produto.get("title", "Produto"))


def _criar_placeholder(titulo: str) -> str:
    """Cria uma imagem placeholder com o título do produto."""
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore[import]

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        caminho = os.path.join(OUTPUT_DIR, "thumbnail.jpg")

        # Cria imagem preta 1080x1080
        img = Image.new("RGB", (1080, 1080), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)

        # Adiciona texto centralizado
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except IOError:
            font = ImageFont.load_default()

        # Quebra o título em linhas
        palavras = titulo.split()
        linhas = []
        linha_atual = ""
        for palavra in palavras:
            if len(linha_atual + " " + palavra) <= 25:
                linha_atual = (linha_atual + " " + palavra).strip()
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)

        # Desenha o texto
        y = 1080 // 2 - len(linhas) * 30
        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=font)
            w = bbox[2] - bbox[0]
            draw.text(((1080 - w) // 2, y), linha, fill=(255, 255, 255), font=font)
            y += 70

        img.save(caminho, "JPEG")
        logger.info("Imagem placeholder criada: %s", caminho)
        return caminho

    except Exception as exc:
        logger.error("Erro ao criar placeholder: %s", exc)
        # Retorna caminho mesmo sem a imagem (editor vai tratar)
        return os.path.join(OUTPUT_DIR, "thumbnail.jpg")
