import os
import threading
import time
from typing import Tuple

from fastapi import HTTPException

from app.core.logging import setup_logger
from app.core.config import log_level, config
from app.core.constants import USE_ASSUMED_ROLES
from app.schemas.auth import AWSCredentialsPayload

logger = setup_logger(__name__, log_level)


class AWSCredentialsService:
    def __init__(self):
        self._credentials_thread = None

    @staticmethod
    def _expire_aws_credentials(expiration_time: int = 7200) -> None:
        """
        Expire AWS credentials after specified time

        Args:
            expiration_time: Time in seconds after which credentials expire (default 2 hours)
        """
        time.sleep(expiration_time)
        os.environ.pop("AWS_ACCESS_KEY_ID", None)
        os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
        os.environ.pop("AWS_SESSION_TOKEN", None)
        logger.info("AWS credentials expired and removed from environment")

    def _start_expiration_thread(self, expiration_time: int = 7200) -> threading.Thread:
        """
        Start a thread to handle credential expiration

        Args:
            expiration_time: Time in seconds after which credentials expire

        Returns:
            threading.Thread: The started expiration thread
        """
        thread = threading.Thread(
            target=self._expire_aws_credentials,
            args=(expiration_time,),
            daemon=True
        )
        thread.start()
        return thread

    def set_credentials(self, credentials: AWSCredentialsPayload) -> str:
        """
        Set AWS credentials in environment variables

        Args:
            credentials: AWS credentials model

        Returns:
            str: Success message

        Raises:
            HTTPException: If USE_ASSUMED_ROLES is enabled or credentials are invalid
        """
        if USE_ASSUMED_ROLES:
            logger.error("Endpoint is disabled due to USE_ASSUMED_ROLES being enabled")
            raise HTTPException(
                status_code=403,
                detail="Endpoint is disabled when using assumed roles"
            )

        try:
            os.environ["AWS_ACCESS_KEY_ID"] = credentials.aws_access_key_id
            os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.aws_secret_access_key
            os.environ["AWS_SESSION_TOKEN"] = credentials.aws_session_token

            logger.info(f"AWS credentials set successfully {credentials.aws_session_token}")

            # Start expiration thread
            self._credentials_thread = self._start_expiration_thread()

            return "AWS credentials set successfully"

        except Exception as e:
            logger.error(f"Error setting AWS credentials: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error setting AWS credentials: {str(e)}"
            )

    @staticmethod
    def check_aws_credentials() -> None:
        """
        Check if AWS credentials are set in environment

        Raises:
            HTTPException: If AWS credentials are not set
        """
        if (
                not os.environ.get("AWS_ACCESS_KEY_ID")
                or not os.environ.get("AWS_SECRET_ACCESS_KEY")
                or not os.environ.get("AWS_SESSION_TOKEN")
        ):
            raise HTTPException(
                status_code=400,
                detail="AWS credentials not set"
            )