import logging
from app.core.jenkins_utils import trigger_pipeline_create_aws, trigger_pipeline_redeploy_aws, trigger_pipeline_destroy_aws
from app.utils.k8s_utils import patch_service_type

logger = logging.getLogger(__name__)


class AWSCloudProvider:
    def __init__(self, zone_partner):
        self.zone_partner = zone_partner
        self.variables = self.zone_partner.variables
        self.plan_only = self.zone_partner.plan_only
        self.partner_id = self.zone_partner.partner_id

    def create_zone_partner(self):
        try:
            trigger_pipeline_create_aws(self.zone_partner, self.variables)
            return "Creation pipeline triggered successfully"
        except Exception as e:
            logger.error(f"An error occurred during zone partner creation: {str(e)}")
            raise

    def delete_zone_partner(self):
        try:
            no_lb_services = self.pre_cleanup(self.partner_id)
            if no_lb_services:
                trigger_pipeline_destroy_aws(self.zone_partner, self.variables)
                return "Deletion pipeline triggered successfully"
            else:
                raise ValueError("LoadBalancer services could not be removed. Cannot proceed with deletion.")
        except Exception as e:
            logger.error(f"An error occurred during zone partner deletion: {str(e)}")
            raise

    def redeploy_zone_partner(self):
        try:
            trigger_pipeline_redeploy_aws(self.zone_partner, self.variables)
            return "Redeployment pipeline triggered successfully"
        except Exception as e:
            logger.error(f"An error occurred during zone partner redeployment: {str(e)}")
            raise

    def pre_cleanup(self, partner_id):
        services_to_patch = [
            ("istio-system", "istio-ingressgateway"),
            ("pz-external", "pz-external-service"),
            ("s3-sftp-server", "sftp-loadbalancer")
        ]

        all_patched = True
        for namespace, service_name in services_to_patch:
            try:
                if not patch_service_type(partner_id, namespace, service_name, "ClusterIP"):
                    logger.error(f"Failed to patch service '{service_name}' in namespace '{namespace}'.")
                    all_patched = False
            except Exception as e:
                logger.error(f"Exception while patching service '{service_name}' in namespace '{namespace}': {e}")
                all_patched = False

        return all_patched
