import os
import shutil
from fastapi import HTTPException
from app.core.logging import setup_logger
from app.core.config import log_level
from app.models import ZonePartner
from app.providers.aws_provider import AWSCloudProvider
from app.providers.azure_provider import AzureCloudProvider
from app.providers.google_provider import GoogleCloudProvider
from app.core.boto3_utils import Boto3STSService
from app.core.fs_utils import load_zone_partner_json

logger = setup_logger(__name__, log_level)


def get_cloud_provider(zone_partner: ZonePartner):
    switcher = {
        'aws': AWSCloudProvider,
        'azure': AzureCloudProvider,
        'google': GoogleCloudProvider
    }
    provider_class = switcher.get(zone_partner.cloud)
    if provider_class is None:
        raise ValueError(f"Invalid cloud provider: {zone_partner.cloud}")
    return provider_class(zone_partner)


def check_tools():
    """
    Check if all required tools are installed and available in the system PATH.
    """
    required_tools = ["kustomize", "jq", "git", "kubectl", "helm", "aws"]

    for tool in required_tools:
        if shutil.which(tool) is None:
            logger.error(f"{tool} is not installed or not found in PATH.")


def set_aws_session(partner_id: str):
    try:
        zone_partner = load_zone_partner_json(partner_id)
        if zone_partner.cloud != 'aws':
            raise ValueError(f"Unsupported cloud provider: {zone_partner.cloud}")

        aws_manager = Boto3STSService(zone_partner)
        aws_manager.set_aws_credentials()
    except Exception as e:
        logger.error(f"Error setting AWS session: {str(e)}")
        raise


def check_aws_credentials():
    if (
        not os.environ.get("AWS_ACCESS_KEY_ID")
        or not os.environ.get("AWS_SECRET_ACCESS_KEY")
        or not os.environ.get("AWS_SESSION_TOKEN")
    ):
        raise HTTPException(status_code=400, detail="AWS credentials not set")
