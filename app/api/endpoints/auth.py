from app.core.config import log_level
from app.core.logging import setup_logger
from fastapi import APIRouter, HTTPException
from app.schemas.auth import AWSCredentialsPayload, AWSCredentialsResponse
from app.schemas.common import ErrorResponse
from app.services import set_aws_credentials_service

logger = setup_logger(__name__, log_level)

router = APIRouter()


@router.post("/set_aws_credentials",
             summary="Sets AWS credentials to the Environment",
             response_model=AWSCredentialsResponse,
             responses={
                 200: {"model": AWSCredentialsResponse, "description": "Credentials set successfully"},
                 403: {"model": ErrorResponse, "description": "Forbidden"},
                 500: {"model": ErrorResponse, "description": "Internal server error"}
             })
async def set_aws_credentials(credentials: AWSCredentialsPayload):
    try:
        result = await set_aws_credentials_service(credentials)
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting AWS credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
