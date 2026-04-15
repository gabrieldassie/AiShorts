# AiShorts 🎬🤖

Automatiza a criação e postagem de **YouTube Shorts** de produtos afiliados do **Mercado Livre**, rodando 100% local com LLM (Ollama) e TTS (Coqui TTS).

## Funcionalidades

- 🔍 Busca produtos mais vendidos do Mercado Livre via API pública
- 🔗 Gera links de afiliado automaticamente
- 🤖 Cria roteiro/narração com LLM local (Ollama)
- 🎙️ Gera narração em PT-BR com Coqui TTS local
- 🎬 Monta o vídeo no formato Shorts 9:16 (1080x1920) com MoviePy + FFmpeg
- 📤 Faz upload automático no YouTube com título, descrição e link afiliado
- ⏱️ Respeita limite de **3 postagens por dia**

## Requisitos

- **Python 3.10+**
- **[Ollama](https://ollama.ai)** instalado e rodando localmente
- **FFmpeg** instalado no sistema
- Conta no **Mercado Livre** com acesso à API
- Projeto no **Google Cloud Console** com YouTube Data API v3 habilitada

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/AiShorts.git
cd AiShorts

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Baixe o modelo Ollama (ex: llama3)
ollama pull llama3

# 5. Instale o modelo TTS em PT-BR
tts --list_models  # para verificar disponibilidade
```

## Configuração

### 1. Variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
ML_APP_ID=seu_app_id_aqui          # App ID do Mercado Livre
ML_SECRET=seu_secret_aqui          # Secret do Mercado Livre
ML_AFFILIATE_TAG=sua_tag_afiliado  # Tag de afiliado

YOUTUBE_CLIENT_SECRET_PATH=client_secret.json  # Caminho para credenciais OAuth2
OLLAMA_MODEL=llama3                # Modelo Ollama a usar
DAILY_LIMIT=3                      # Máximo de posts por dia
NICHE=eletrônicos                  # Nicho de produtos
```

### 2. Autenticação no YouTube API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto (ou use um existente)
3. Ative a **YouTube Data API v3**
4. Crie credenciais **OAuth 2.0** do tipo "Aplicativo desktop"
5. Baixe o arquivo `client_secret.json` e coloque na raiz do projeto
6. Na primeira execução, um navegador será aberto para autorizar o acesso

### 3. Estrutura de pastas

```
aishorts/
├── main.py                  # Entry point
├── config.py                # Configurações
├── crawler/
│   └── mercadolivre.py      # Busca produtos via API ML
├── affiliate/
│   └── link_generator.py    # Gera links de afiliado
├── content/
│   ├── script_generator.py  # Roteiro via Ollama
│   └── tts.py               # Narração com Coqui TTS
├── video/
│   ├── generator.py         # Prepara imagens do produto
│   └── editor.py            # Monta o Short com MoviePy
├── uploader/
│   └── youtube.py           # Upload via YouTube Data API v3
├── scheduler/
│   └── daily_limit.py       # Limite de 3 posts/dia
├── data/
│   └── posts_log.json       # Log de postagens
├── output/                  # Vídeos gerados temporariamente
├── requirements.txt
├── .env.example
└── README.md
```

## Como rodar

```bash
python main.py
```

O pipeline executará automaticamente:

1. Verifica se o limite diário foi atingido
2. Busca os produtos mais vendidos do nicho configurado
3. Seleciona o próximo produto ainda não postado hoje
4. Gera link de afiliado
5. Gera roteiro com Ollama
6. Gera narração com Coqui TTS
7. Monta o Short (1080x1920, 30-59s) com MoviePy
8. Faz upload para o YouTube com título, tags e descrição gerados por IA
9. Registra a postagem no log `data/posts_log.json`

## Log de postagens

O arquivo `data/posts_log.json` mantém o histórico de postagens:

```json
{
  "2026-04-15": {
    "count": 2,
    "posts": [
      {
        "product_id": "MLB123456789",
        "video_path": "output/final_short.mp4",
        "youtube_url": "https://www.youtube.com/shorts/abc123"
      }
    ]
  }
}
```

## Observações

- Todo processamento de LLM e TTS é **100% local** (sem custos com APIs externas)
- Produtos já postados no dia são automaticamente ignorados
- O token OAuth2 do YouTube é salvo em `youtube_token.json` e renovado automaticamente
- Logs detalhados são exibidos durante a execução
