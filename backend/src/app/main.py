from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import session, translate, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Universal Translator", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(translate.router)
app.include_router(jobs.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
