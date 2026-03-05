# Universal Translator

Translate documents while preserving formatting. Upload files via a web UI, pick source/target languages, and download the translated result in the same format.

## Supported Formats

| Format | Extensions |
|-|-|
| Plain text | `.txt` |
| CSV | `.csv` |
| Word | `.docx` |
| Excel | `.xlsx` |
| PowerPoint | `.pptx` |

## LLM Providers

Configure via `LLM_PROVIDER` in `.env`:

- **`openai`** — OpenAI API (`OPENAI_API_KEY`, `OPENAI_MODEL`)
- **`azure_openai`** — Azure OpenAI (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_CHAT_MODEL_DEPLOYMENT_NAME`, `AZURE_OPENAI_API_VERSION`)
- **`google`** — Google Gemini (`GOOGLE_API_KEY`, `GOOGLE_MODEL`)

## Architecture

```
Frontend (SvelteKit) → API (FastAPI) → Redis → Celery Worker → LLM
```

- **Frontend** — SvelteKit 5 SPA with drag-and-drop multi-file upload, language selectors, custom instructions
- **API** — FastAPI handling uploads, session management (HTTP-only cookies, no login), job status
- **Worker** — Celery task queue processing translations asynchronously
- **Redis** — Message broker and result backend

Files are isolated per session and auto-deleted after processing.

## Quick Start

```bash
cp .env.example .env
# Fill in your LLM provider credentials

docker compose up
```

Frontend: http://localhost:5174
API: http://localhost:8000

## Configuration

| Variable | Default | Description |
|-|-|-|
| `LLM_PROVIDER` | `openai` | `openai`, `azure_openai`, or `google` |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size |
| `FILE_TTL_SECONDS` | `3600` | Auto-delete translated files after this |
| `SESSION_SECRET` | — | Secret for signing session cookies |

## Tests

```bash
docker compose run --rm tests
```

## Development

The frontend dev server supports HMR via volume mounts in `docker-compose.yml`. Edit files in `frontend/src/` and changes reflect immediately.
