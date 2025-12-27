from fastapi_sso.sso.google import GoogleSSO

from app.core.config import settings

sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=settings.GOOGLE_REDIRECT_URI,
    allow_insecure_http=True,
)
