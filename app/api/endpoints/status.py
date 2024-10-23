from fastapi import APIRouter, HTTPException
from app.core.config import config, log_level
from app.core.logging import setup_logger
from app.core.fs_utils import load_status_json
from app.schemas.status import StatusResponse
from app.schemas.common import ErrorResponse

logger = setup_logger(__name__, log_level)

router = APIRouter()


@router.get("/{partner_id}")
async def get_status(partner_id: str):
    data = get_status_service(partner_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Status file not found")
    return data
