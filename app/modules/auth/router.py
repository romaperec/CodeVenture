from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.get("/")
async def root():
    return {"Module": "Working!"}
