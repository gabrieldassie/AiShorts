"""
video/editor.py — Monta o YouTube Short final em formato 9:16 (1080x1920) com MoviePy.
"""

import logging
import os
from typing import Any

from aishorts.config import FINAL_VIDEO_PATH, NARRATION_PATH, OUTPUT_DIR

logger = logging.getLogger(__name__)

# Dimensões do Short (9:16 vertical)
LARGURA = 1080
ALTURA = 1920

# Duração mínima e máxima do Short em segundos
DURACAO_MIN = 30
DURACAO_MAX = 59


def montar_short(
    caminho_imagem: str,
    conteudo: dict[str, Any],
    caminho_audio: str = NARRATION_PATH,
    caminho_saida: str = FINAL_VIDEO_PATH,
) -> str:
    """
    Monta o vídeo final no formato 9:16 com:
      - Fundo preto
      - Imagem do produto centralizada com efeito de zoom suave
      - Narração como áudio
      - Watermark "AiShorts" no canto inferior
    Retorna o caminho do vídeo gerado.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        from moviepy.editor import (  # type: ignore[import]
            AudioFileClip,
            ColorClip,
            CompositeVideoClip,
            ImageClip,
            TextClip,
        )
    except ImportError:
        logger.error("MoviePy não está instalado. Execute: pip install moviepy")
        raise

    try:
        # ── Carrega o áudio de narração ───────────────────────────────────────
        logger.info("Carregando áudio de narração: %s", caminho_audio)
        audio_clip = AudioFileClip(caminho_audio)
        duracao = min(max(audio_clip.duration, DURACAO_MIN), DURACAO_MAX)

        # ── Fundo preto ───────────────────────────────────────────────────────
        fundo = ColorClip(size=(LARGURA, ALTURA), color=(0, 0, 0), duration=duracao)

        # ── Imagem do produto ─────────────────────────────────────────────────
        clipes = [fundo]

        if caminho_imagem and os.path.exists(caminho_imagem):
            img_clip = (
                ImageClip(caminho_imagem)
                .resize(width=LARGURA - 80)          # margem lateral de 40px cada lado
                .set_position("center")
                .set_duration(duracao)
            )

            # Efeito de zoom suave: escala vai de 1.0 a 1.05
            img_clip = img_clip.resize(
                lambda t: 1.0 + 0.05 * (t / duracao)
            )
            clipes.append(img_clip)
        else:
            logger.warning("Imagem do produto não encontrada: %s", caminho_imagem)

        # ── Watermark "AiShorts" ──────────────────────────────────────────────
        try:
            watermark = (
                TextClip(
                    "AiShorts",
                    fontsize=36,
                    color="white",
                    font="DejaVu-Sans-Bold",
                    stroke_color="black",
                    stroke_width=2,
                )
                .set_position(("center", ALTURA - 100))
                .set_duration(duracao)
                .set_opacity(0.8)
            )
            clipes.append(watermark)
        except Exception as exc:
            logger.warning("Não foi possível adicionar watermark: %s", exc)

        # ── Composição final ──────────────────────────────────────────────────
        video_final = CompositeVideoClip(clipes, size=(LARGURA, ALTURA))
        video_final = video_final.set_audio(audio_clip)
        video_final = video_final.set_duration(duracao)

        logger.info(
            "Renderizando vídeo final (%.1fs) em: %s", duracao, caminho_saida
        )
        video_final.write_videofile(
            caminho_saida,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(OUTPUT_DIR, "temp_audio.m4a"),
            remove_temp=True,
            logger=None,  # Suprime output verboso do MoviePy
        )

        logger.info("Vídeo gerado com sucesso: %s", caminho_saida)
        return caminho_saida

    except Exception as exc:
        logger.error("Erro ao montar o Short: %s", exc)
        raise
