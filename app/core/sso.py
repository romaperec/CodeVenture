# app/core/sso.py
"""Конфигурация OAuth2 провайдеров (Google и GitHub)."""

from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.github import GithubSSO

from app.core.config import settings

# Google OAuth2 конфигурация
google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=settings.GOOGLE_REDIRECT_URI,
    allow_insecure_http=True,
)

# GitHub OAuth2 конфигурация
github_sso = GithubSSO(
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    redirect_uri=settings.GITHUB_REDIRECT_URI,
    allow_insecure_http=True,
)
