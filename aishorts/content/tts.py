"""
content/tts.py — Gera narração em PT-BR com Coqui TTS (100% local).
"""

import logging
import os

from aishorts.config import NARRATION_PATH, OUTPUT_DIR

logger = logging.getLogger(__name__)

# Modelo TTS em português do Coqui
_TTS_MODEL = "tts_models/pt/cv/vits"


def gerar_narracao(texto: str, caminho_saida: str = NARRATION_PATH) -> str:
    """
    Gera um arquivo de áudio WAV com a narração do texto fornecido.

    Utiliza o modelo Coqui TTS local (tts_models/pt/cv/vits).
    Retorna o caminho do arquivo gerado.
    """
    # Garante que o diretório de saída existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        # Importação lazy para evitar lentidão no carregamento do módulo
        from TTS.api import TTS  # type: ignore[import]

        logger.info("Inicializando Coqui TTS com modelo '%s'...", _TTS_MODEL)
        tts = TTS(model_name=_TTS_MODEL, progress_bar=False, gpu=False)

        logger.info("Gerando narração em PT-BR (%d caracteres)...", len(texto))
        tts.tts_to_file(text=texto, file_path=caminho_saida)
        logger.info("Narração salva em: %s", caminho_saida)

    except ImportError:
        logger.error(
            "Coqui TTS não está instalado. Execute: pip install TTS"
        )
        raise
    except Exception as exc:
        logger.error("Erro ao gerar narração com Coqui TTS: %s", exc)
        raise

    return caminho_saida
