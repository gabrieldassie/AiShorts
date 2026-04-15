"""
affiliate/link_generator.py — Gera links de afiliado para produtos do Mercado Livre.
"""

import logging

from aishorts.config import ML_AFFILIATE_TAG

logger = logging.getLogger(__name__)


def gerar_link_afiliado(permalink: str, tag: str = ML_AFFILIATE_TAG) -> str:
    """
    Recebe a URL original do produto e retorna a URL com parâmetros de afiliado.

    Parâmetros UTM adicionados:
      - utm_source=aishorts
      - utm_medium=youtube
      - ref=<ML_AFFILIATE_TAG>
    """
    if not permalink:
        logger.warning("Permalink vazio — link de afiliado não será gerado.")
        return ""

    # Monta a URL com parâmetros de rastreamento
    link = (
        f"{permalink}"
        f"?utm_source=aishorts"
        f"&utm_medium=youtube"
        f"&ref={tag}"
    )
    logger.info("Link de afiliado gerado: %s", link)
    return link
