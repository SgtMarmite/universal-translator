# Universal Translator - Design Document

## Overview

A dockerized translation service where users upload documents via a web UI, and get back translated files in the same format. Pluggable LLM backends (OpenAI, Azure OpenAI, Google). No login — session-based security. Queue-based processing with Celery + Redis.

## Architecture

### Services

| Service | Role |
|-|-|
| frontend | SvelteKit — drag-and-drop upload UI, job queue display |
| api | FastAPI — file upload, session management, job status, downloads |
| worker | Celery worker — translation processing |
| redis | Message broker + result backend |
| tests | Runs pytest suite against the backend |

### Data Flow

1. User opens frontend, backend sets HTTP-only secure cookie with session token
2. User drags file, selects source/target language, optionally adds custom instructions
3. Frontend POSTs to `/api/translate`, API saves file to `/data/<session>/<job_id>/`, enqueues Celery task
4. Frontend polls `/api/jobs` for status updates (every 2s)
5. Worker extracts text segments, batches them to LLM, writes translated file
6. User downloads file, backend deletes it

### Security

- Cryptographically random session token in HTTP-only secure cookie
- All file operations scoped to session token — paths constructed server-side only
- Input files deleted immediately after translation completes
- Output files deleted after download or after configurable TTL
- Redis not exposed to host network

## File Format System

Plugin-based registry pattern. Each format implements:

```python
class FormatHandler(ABC):
    @abstractmethod
    def extract_texts(self, file_path: Path) -> list[TextSegment]:
        """Extract translatable text with positional metadata."""

    @abstractmethod
    def replace_texts(self, file_path: Path, translated: list[TextSegment], output_path: Path):
        """Write new file with translated text, preserving formatting."""

class TextSegment:
    id: str
    text: str
    context: str
    metadata: dict
```

### Initial Handlers

| Handler | Library | Notes |
|-|-|-|
| PlainTextHandler | built-in | Split by paragraphs |
| CsvHandler | pandas | Configurable columns to translate |
| DocxHandler | python-docx | Preserve runs, styles, formatting |
| XlsxHandler | openpyxl | Preserve formulas, translate string cells only |
| PptxHandler | python-pptx | Preserve slide layouts, shapes, text frames |

Adding a new format = one class + `@register` decorator. No other changes needed.

## LLM Provider System

Same registry pattern:

```python
class LLMProvider(ABC):
    @abstractmethod
    async def translate(self, texts: list[TextSegment], source_lang: str, target_lang: str) -> list[str]:
        """Translate a batch of text segments."""
```

### Providers

| Provider | Config |
|-|-|
| OpenAIProvider | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| AzureOpenAIProvider | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT` |
| GoogleProvider | `GOOGLE_API_KEY`, `GOOGLE_MODEL` |

Active provider set via `LLM_PROVIDER` env var.

### Batching

Segments batched up to a token limit per API call. Prompt returns JSON array of translations in same order. Includes context from surrounding text for better quality.

### Prompt Structure

```
Translate from {source_lang} to {target_lang}.

Custom instructions: {user_instructions}

Glossary (use these exact translations):
- "Revenue" -> "Umsatz"

Texts to translate:
[1] "Welcome to our company"
[2] "Q3 Revenue Report"

Return ONLY a JSON array of translated strings in the same order.
Do not translate proper nouns, code, or formulas.
```

Retry with exponential backoff on rate limits.

## Custom Instructions

Two levels, both session-scoped:

1. **Free-text instructions** — persisted in `/data/<session>/instructions.txt`
   - Examples: "Use formal tone", "Keep technical terms in English"
2. **Glossary CSV** — uploaded to `/data/<session>/glossary.csv`
   - Format: `source_term,target_term`

Both injected into every LLM prompt for the session.

## API Endpoints

| Method | Path | Purpose |
|-|-|-|
| GET | `/api/session` | Create session, set cookie, return supported languages + formats |
| POST | `/api/translate` | Upload file + languages + optional instructions, returns job ID |
| GET | `/api/jobs` | List jobs for current session |
| GET | `/api/jobs/{job_id}` | Single job detail |
| GET | `/api/jobs/{job_id}/download` | Download translated file (triggers deletion) |
| DELETE | `/api/jobs/{job_id}` | Cancel/remove job |
| POST | `/api/glossary` | Upload/replace glossary CSV |

## Frontend

SvelteKit single-page app with three zones:

1. **Upload zone** — Drag-and-drop area, language dropdowns (with auto-detect), custom instructions textarea (collapsible), glossary upload
2. **Queue zone** — Job list with status (queued/processing/done), progress indication, download button, error states
3. **Info zone** — Active LLM provider (read-only), supported formats

## Project Structure

```
universal-translator/
├── docker-compose.yml
├── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   └── src/
│       ├── app.html
│       ├── lib/
│       │   ├── api.ts
│       │   ├── types.ts
│       │   └── components/
│       │       ├── DropZone.svelte
│       │       ├── JobList.svelte
│       │       ├── JobItem.svelte
│       │       ├── LanguageSelect.svelte
│       │       └── Instructions.svelte
│       └── routes/
│           └── +page.svelte
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   │   └── app/
│   │       ├── main.py
│   │       ├── config.py
│   │       ├── routes/
│   │       │   ├── session.py
│   │       │   ├── translate.py
│   │       │   └── jobs.py
│   │       ├── models/
│   │       │   ├── job.py
│   │       │   └── session.py
│   │       ├── formats/
│   │       │   ├── base.py
│   │       │   ├── plaintext.py
│   │       │   ├── csv.py
│   │       │   ├── docx.py
│   │       │   ├── xlsx.py
│   │       │   └── pptx.py
│   │       ├── llm/
│   │       │   ├── base.py
│   │       │   ├── openai.py
│   │       │   ├── azure_openai.py
│   │       │   └── google.py
│   │       ├── worker/
│   │       │   ├── celery_app.py
│   │       │   └── tasks.py
│   │       └── cleanup.py
│   └── tests/
│       ├── conftest.py
│       ├── test_formats/
│       ├── test_llm/
│       ├── test_routes/
│       └── test_worker/
└── docs/
    └── plans/
```

## Docker Compose

| Service | Image | Ports | Volumes |
|-|-|-|-|
| frontend | ./frontend Dockerfile | 5173:5173 | source code (dev mount) |
| api | ./backend Dockerfile | 8000:8000 | translation-data:/data |
| worker | same as api, entrypoint: celery | none | translation-data:/data |
| redis | redis:7-alpine | none (internal) | redis-data |
| tests | same as api, entrypoint: pytest | none | translation-data:/data |

## Configuration (.env)

```
LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=
GOOGLE_API_KEY=
GOOGLE_MODEL=gemini-2.0-flash
MAX_FILE_SIZE_MB=50
FILE_TTL_SECONDS=3600
REDIS_URL=redis://redis:6379/0
SESSION_SECRET=<random-generated>
```
