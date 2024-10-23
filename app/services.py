import os
import threading
import time
from app.core.logging import setup_logger
from app.core.config import log_level
from app.core.constants import USE_ASSUMED_ROLES
from app.models import ZonePartner, DeployMLWorkbench
from app.schemas.auth import AWSCredentialsPayload, AWSCredentialsResponse
from app.utils.utils import get_cloud_provider, set_aws_session
from app.core.fs_utils import save_zone_partner_payload, update_status, load_zone_partner_json

logger = setup_logger(__name__, log_level)

credentials_thread = None


def expire_aws_credentials(expiration_time=7200):
    time.sleep(expiration_time)
    os.environ.pop("AWS_ACCESS_KEY_ID", None)
    os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
    os.environ.pop("AWS_SESSION_TOKEN", None)
    logger.info("AWS credentials expired")


def start_expiration_thread(expiration_time=7200):
    thread = threading.Thread(
        target=expire_aws_credentials,
        args=(expiration_time,),
        daemon=True
    )
    thread.start()
    return thread


async def create_zone_partner_service(zone_partner: ZonePartner):
    try:
        save_zone_partner_payload(zone_partner)
        if zone_partner.cloud != 'aws':
            raise ValueError(f"Unsupported cloud provider: {zone_partner.cloud}")

        provider = get_cloud_provider(zone_partner)

        if not zone_partner.plan_only:
            update_status(zone_partner.partner_id, "Terraform", "Creating")
            result = provider.create_zone_partner()
            update_status(zone_partner.partner_id, "Terraform", "Complete")
            return {"message": f"Zone partner created successfully. {result}"}

        return {"message": f"Zone partner creation plan completed for partner_id: {zone_partner.partner_id}"}
    except ValueError as ve:
        logger.error(str(ve))
        raise
    except Exception as e:
        logger.error(f"An error occurred during zone partner creation: {str(e)}")
        update_status(zone_partner.partner_id, "Terraform", "Error")
        raise


async def delete_zone_partner_service(partner_id: str):
    try:
        zone_partner = load_zone_partner_json(partner_id)
        if zone_partner is None:
            raise ValueError(f"No Zone Partner found with id: {partner_id}")

        if zone_partner.cloud != 'aws':
            raise ValueError(f"Unsupported cloud provider: {zone_partner.cloud}")

        update_status(partner_id, "Terraform", "Deleting")

        if USE_ASSUMED_ROLES:
            set_aws_session(partner_id)

        provider = get_cloud_provider(zone_partner)
        result = provider.delete_zone_partner()

        update_status(partner_id, "Terraform", "Deleted")
        return {"message": f"Zone partner deletion completed for partner_id: {partner_id}. {result}"}
    except ValueError as ve:
        logger.error(str(ve))
        update_status(partner_id, "Terraform", "Delete Error")
        raise
    except Exception as e:
        logger.error(f"An error occurred during zone partner deletion: {str(e)}")
        update_status(partner_id, "Terraform", "Delete Error")
        raise


async def redeploy_zone_partner_service(partner_id: str):
    try:
        zone_partner = load_zone_partner_json(partner_id)
        if zone_partner is None:
            raise ValueError(f"No Zone Partner found with id: {partner_id}")

        if zone_partner.cloud != 'aws':
            raise ValueError(f"Unsupported cloud provider: {zone_partner.cloud}")

        update_status(partner_id, "Terraform", "Redeploying")

        if USE_ASSUMED_ROLES:
            set_aws_session(partner_id)

        provider = get_cloud_provider(zone_partner)
        result = provider.redeploy_zone_partner()

        update_status(partner_id, "Terraform", "Redeployed")
        return {"message": f"Zone partner redeployment completed for partner_id: {partner_id}. {result}"}
    except ValueError as ve:
        logger.error(str(ve))
        update_status(partner_id, "Terraform", "Redeploy Error")
        raise
    except Exception as e:
        logger.error(f"An error occurred during zone partner redeployment: {str(e)}")
        update_status(partner_id, "Terraform", "Redeploy Error")
        raise


async def deploy_ml_workbench_service(deploy_payload: DeployMLWorkbench):
    # Implementation here
    pass



async def set_aws_credentials_service(credentials: AWSCredentialsPayload) -> AWSCredentialsResponse:
    if not USE_ASSUMED_ROLES:
        os.environ["AWS_ACCESS_KEY_ID"] = credentials.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.aws_secret_access_key
        os.environ["AWS_SESSION_TOKEN"] = credentials.aws_session_token
        logger.info(f"AWS credentials set successfully {credentials.aws_session_token}")

        start_expiration_thread()

        return AWSCredentialsResponse(message="AWS credentials set successfully")
    else:
        logger.error("Endpoint is disabled")
        raise ValueError("Endpoint is disabled")


def get_status_service(partner_id: str):
    # Implementation here
    pass
