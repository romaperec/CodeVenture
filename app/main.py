from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.redis import lifespan
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router

app = FastAPI(title="CodeVenture API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
async def root():
    return {"API": "Working!"}


instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app)
