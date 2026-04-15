"""
uploader/youtube.py — Faz upload de vídeos para o YouTube via Data API v3 (OAuth2).
"""

import logging
import os
from typing import Any

from aishorts.config import YOUTUBE_CLIENT_SECRET_PATH

logger = logging.getLogger(__name__)

# Escopos necessários para upload de vídeos
_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Arquivo de token OAuth2 salvo localmente após primeira autenticação
_TOKEN_PATH = "youtube_token.json"

# Categoria padrão: "28" = Science & Technology
_CATEGORY_ID = "28"


def _autenticar_youtube() -> Any:
    """
    Realiza autenticação OAuth2 com o YouTube e retorna o objeto de serviço.
    Na primeira execução, abre o navegador para autorização.
    Nas execuções seguintes, usa o token salvo.
    """
    try:
        from google.auth.transport.requests import Request  # type: ignore[import]
        from google.oauth2.credentials import Credentials  # type: ignore[import]
        from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
        from googleapiclient.discovery import build  # type: ignore[import]
    except ImportError:
        logger.error(
            "Bibliotecas do Google não instaladas. "
            "Execute: pip install google-api-python-client google-auth-oauthlib"
        )
        raise

    creds = None

    # Carrega token salvo se disponível
    if os.path.exists(_TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(_TOKEN_PATH, _SCOPES)
        except Exception as exc:
            logger.warning("Token salvo inválido, será necessária nova autenticação: %s", exc)

    # Renova ou solicita novo token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Token do YouTube renovado com sucesso.")
            except Exception as exc:
                logger.warning("Falha ao renovar token: %s — iniciando novo fluxo OAuth2", exc)
                creds = None

        if not creds:
            if not os.path.exists(YOUTUBE_CLIENT_SECRET_PATH):
                raise FileNotFoundError(
                    f"Arquivo de credenciais não encontrado: {YOUTUBE_CLIENT_SECRET_PATH}. "
                    "Baixe o client_secret.json no Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_PATH, _SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva token para uso futuro
        with open(_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
        logger.info("Token do YouTube salvo em: %s", _TOKEN_PATH)

    return build("youtube", "v3", credentials=creds)


def fazer_upload(
    conteudo: dict[str, Any],
    link_afiliado: str,
    caminho_video: str,
) -> str:
    """
    Faz o upload do vídeo para o YouTube com metadados gerados pela IA.

    Retorna a URL do vídeo publicado.
    """
    try:
        from googleapiclient.http import MediaFileUpload  # type: ignore[import]
    except ImportError:
        logger.error("Biblioteca google-api-python-client não instalada.")
        raise

    # Substitui placeholder do link afiliado na descrição
    descricao = conteudo.get("description", "").replace("{link_afiliado}", link_afiliado)

    # Garante que a descrição e o título contêm #Shorts
    titulo = conteudo.get("title", "YouTube Short #Shorts")
    if "#Shorts" not in titulo:
        titulo = f"{titulo} #Shorts"
    if "#Shorts" not in descricao:
        descricao = f"{descricao}\n\n#Shorts"

    # Prepara as tags: combina hashtags geradas + tag fixa #Shorts
    hashtags = conteudo.get("hashtags", [])
    tags = [tag.lstrip("#") for tag in hashtags] + ["Shorts"]

    body = {
        "snippet": {
            "title": titulo[:100],  # Limite do YouTube: 100 caracteres
            "description": descricao,
            "tags": tags,
            "categoryId": _CATEGORY_ID,
            "defaultLanguage": "pt",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    try:
        logger.info("Autenticando no YouTube...")
        youtube = _autenticar_youtube()

        logger.info("Iniciando upload do vídeo: %s", caminho_video)
        media = MediaFileUpload(caminho_video, chunksize=-1, resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info("Upload: %.1f%%", status.progress() * 100)

        video_id = response.get("id", "")
        url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info("✅ Vídeo publicado com sucesso: %s", url)
        return url

    except Exception as exc:
        logger.error("Erro ao fazer upload para o YouTube: %s", exc)
        raise
