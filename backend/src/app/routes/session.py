import secrets

from fastapi import APIRouter, Request, Response

from app.models.session import SUPPORTED_FORMATS, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/api")

SESSION_COOKIE = "session_token"


def get_session_token(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE)


def ensure_session_token(request: Request, response: Response) -> str:
    token = get_session_token(request)
    if not token:
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            httponly=True,
            samesite="strict",
            max_age=86400 * 30,
        )
    return token


@router.get("/session")
def get_session(request: Request, response: Response):
    token = ensure_session_token(request, response)
    return {
        "session_active": True,
        "formats": SUPPORTED_FORMATS,
        "languages": SUPPORTED_LANGUAGES,
        "has_session": get_session_token(request) is not None,
    }
