from fastapi import APIRouter
from starlette.responses import RedirectResponse

router = APIRouter()


@router.get("/")
async def root():
    return RedirectResponse(url='/docs')