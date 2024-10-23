from fastapi import APIRouter, HTTPException
from app.core.logging import setup_logger
from app.core.config import log_level
from app.schemas.status import StatusResponse
from app.schemas.common import ErrorResponse
from app.services.status_service import StatusService

router = APIRouter()
logger = setup_logger(__name__, log_level)


@router.get(
    "/{partner_id}",
    response_model=StatusResponse,
    responses={
        200: {"model": StatusResponse, "description": "Successfully retrieved status"},
        404: {"model": ErrorResponse, "description": "Status file not found"}
    }
)
async def get_status(partner_id: str) -> StatusResponse:
    """
    Get the current status of a partner zone deployment

    Parameters:
        partner_id (str): The unique identifier of the partner zone

    Returns:
        StatusResponse: The current status of the partner zone deployment
    """
    return StatusService.get_status(partner_id)