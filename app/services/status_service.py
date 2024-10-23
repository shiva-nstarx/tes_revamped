from typing import Optional
from fastapi import HTTPException

from app.core.logging import setup_logger
from app.core.config import log_level
from app.core.fs_utils import load_status_json
from app.schemas.status import StatusResponse

logger = setup_logger(__name__, log_level)


class StatusService:
    @staticmethod
    def get_status(partner_id: str) -> StatusResponse:
        """
        Get the status information for a partner zone

        Args:
            partner_id: The ID of the partner zone

        Returns:
            StatusResponse: Status information

        Raises:
            HTTPException: If status file not found
        """
        data = load_status_json(partner_id)
        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"No status file found for partner_id: {partner_id}"
            )

        try:
            return StatusResponse(**data)
        except Exception as e:
            logger.error(f"Error parsing status data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing status data"
            )