from app.core.config import log_level
from app.core.logging import setup_logger
from fastapi import APIRouter, HTTPException
from app.schemas.auth import AWSCredentialsPayload, AWSCredentialsResponse
from app.schemas.common import ErrorResponse
from app.services.aws_auth_service import AWSCredentialsService

logger = setup_logger(__name__, log_level)

router = APIRouter()
aws_service = AWSCredentialsService()


@router.post("/set_aws_credentials",
             summary="Sets AWS credentials to the Environment",
             response_model=AWSCredentialsResponse,
             responses={
                 200: {"model": AWSCredentialsResponse, "description": "Credentials set successfully"},
                 403: {"model": ErrorResponse, "description": "Forbidden"},
                 500: {"model": ErrorResponse, "description": "Internal server error"}
             })
async def set_aws_credentials(credentials: AWSCredentialsPayload) -> AWSCredentialsResponse:
    """
        Set AWS credentials in environment variables

        Parameters:
            credentials (AWSCredentials): AWS credentials to set

        Returns:
            AWSCredentialsResponse: Success message
        """
    message = aws_service.set_credentials(credentials)
    return AWSCredentialsResponse(message=message)
