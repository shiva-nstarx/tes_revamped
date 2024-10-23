from fastapi import APIRouter, HTTPException
from app.core.config import config, log_level
from app.core.logging import setup_logger
from app.schemas.health import HealthResponse, ReadinessResponse
from app.schemas.common import ErrorResponse

logger = setup_logger(__name__, log_level)

router = APIRouter()


@router.get("/health",
            summary="Health Check",
            description="Check if the API is up and running",
            response_model=HealthResponse,
            responses={
                200: {"model": HealthResponse, "description": "API is operational"}
            })
async def health_check():
    """
    Perform a health check on the API.

    This endpoint can be used to verify if the API is operational.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    return {"status": "UP"}


@router.get("/readiness",
            summary="Readiness Check",
            description="Check if the API is ready to accept requests",
            response_model=ReadinessResponse,
            responses={
                200: {"model": ReadinessResponse, "description": "API is ready to accept requests"},
                503: {"model": ErrorResponse, "description": "API is not ready"}
            })
async def readiness_check():
    """
    Perform a readiness check on the API.

    This endpoint checks if all necessary configurations are loaded and the API is ready to accept requests.

    Returns:
        dict: A dictionary containing the readiness status, a message, and the current log level.

    Raises:
        HTTPException: If the API is not ready to accept requests.
    """
    try:
        jenkins_config = config.get_jenkins_config()
        okta_config = config.get_okta_config()
        okta_ds_config = config.get_okta_ds_config()
        sftp_mongo_config = config.get_sftp_mongo_config()

        if not all([jenkins_config, okta_config, okta_ds_config, sftp_mongo_config]):
            raise ValueError("One or more configurations are missing")

        return {
            "status": "ready",
            "message": "All configurations loaded successfully",
            "log_level": config.get_log_level()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {str(e)}")