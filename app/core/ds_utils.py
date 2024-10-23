import os
import logging
import shutil
from typing import Dict, List
from app.utils.bash_utils import execute_bash
from app.utils.k8s_utils import wait_for_pod_initialization, return_lb_dns_name, patch_service_type

logger = logging.getLogger(__name__)

class DSUtils:
    def __init__(self, terraform_dir: str, state_path: str):
        self.terraform_dir = terraform_dir
        self.state_path = state_path
        self.kube_config_out = ""

    def replace_placeholders(self, content: str, var_mapping: Dict[str, str]) -> str:
        for key, value in var_mapping.items():
            content = content.replace(f"${{{key}}}", value)
        return content

    def generate_files_from_templates(self, variables: Dict[str, str], files_to_generate: List[Dict]):
        try:
            for file_info in files_to_generate:
                with open(file_info["template"], 'r') as template_file:
                    template_content = template_file.read()

                var_mapping = {var: variables[var] for var in file_info["variables"]}
                updated_content = self.replace_placeholders(template_content, var_mapping)

                output_dir = os.path.dirname(file_info["output"])
                os.makedirs(output_dir, exist_ok=True)

                with open(file_info["output"], 'w') as output_file:
                    output_file.write(updated_content)

                logger.info(f"Generated file: {file_info['output']}")
        except Exception as e:
            logger.error(f"Error while generating the kubernetes manifest files: {e}")

    def deploy(self, deploy_vars):
        service_ips = {}
        k8s_manifests_dir = f"{self.terraform_dir}/k8s-services"

        variables = {
            "account_id": deploy_vars.account_id,
            "partner_id": deploy_vars.partner_id,
            "deployment_name": deploy_vars.deployment_name,
            "bucket_name": deploy_vars.sftp_bucket_name,
            "aws_region": deploy_vars.region,
            "autoscaler_IAM_role_arn": deploy_vars.autoscaler_role_arn,
            "fsx_IAM_role_arn": deploy_vars.fsx_iam_role_arn,
            "eks_cluster_name": deploy_vars.eks_cluster_name,
            "cluster_subnet_id": deploy_vars.cluster_subnet_id,
            "cluster_security_group_id": deploy_vars.cluster_security_group_id,
            "certArn": deploy_vars.telesign_certificate_arn,
            "vpc_id": deploy_vars.vpc_id,
        }

        lbc_role_arn = f"arn:aws:iam::{variables['account_id']}:role/{variables['eks_cluster_name']}-eks-alb-controller-role"
        assume_role = f"arn:aws:iam::{variables['account_id']}:role/eks-access-role-{variables['deployment_name']}-{variables['aws_region']}"

        k8s_manifests_partner_dir = os.path.join(self.state_path, f"{variables['partner_id']}", "manifests")
        os.makedirs(k8s_manifests_partner_dir, exist_ok=True)

        for item in os.listdir(os.path.join(k8s_manifests_dir, "manifests")):
            src_path = os.path.join(k8s_manifests_dir, "manifests", item)
            dst_path = os.path.join(k8s_manifests_partner_dir, item)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)

        logger.info(f"Copied contents from {k8s_manifests_dir}/manifests to {k8s_manifests_partner_dir}")

        files_to_generate = [
            {
                "template": f"{k8s_manifests_dir}/templates/s3-sftp.tpl",
                "output": f"{k8s_manifests_partner_dir}/s3-sftp.yaml",
                "variables": ["bucket_name", "aws_region"]
            },
            # ... (other template files)
        ]

        self.generate_files_from_templates(variables, files_to_generate)

        self.kube_config_out = os.path.join(self.state_path, f"{variables['partner_id']}", f"config_{variables['partner_id']}")
        ret = execute_bash(
            f"./get_kubeconfig.sh {variables['eks_cluster_name']} {variables['aws_region']} {assume_role} {self.kube_config_out}"
        )

        if ret == 0:
            logger.info("Deploy KF...")
            result = execute_bash(
                f"./deploy_kf.sh {self.kube_config_out} {k8s_manifests_partner_dir} {variables['eks_cluster_name']} {variables['certArn']} {variables['fsx_IAM_role_arn']} {variables['aws_region']} {variables['vpc_id']} {lbc_role_arn}")
            if result == 0:
                logger.info("Check for KF...")
                wait_for_pod_initialization(self.kube_config_out)
                services_to_query = [
                    ("istio-ingressgateway", "kf_ip"),
                    ("sftp-loadbalancer", "sftp_ip"),
                    ("pz-external-service", "pz_external_ip")
                ]
                for service_name, ip_key in services_to_query:
                    try:
                        service_ip = return_lb_dns_name(self.kube_config_out, service_name)
                        service_ips[ip_key] = service_ip
                        logger.info(f"{service_name} IP: {service_ip}")
                    except Exception as e:
                        logger.error(f"Exception occurred while retrieving IP for service '{service_name}': {e}")
                        service_ips[ip_key] = None
        else:
            logger.error(f"Error, cannot get kubeconfig for {self.kube_config_out}")
            return {"cannot get kubeconfig"}
        return service_ips

    def pre_cleanup(self, partner_id):
        services_to_patch = [
            ("istio-system", "istio-ingressgateway"),
            ("pz-external", "pz-external-service"),
            ("s3-sftp-server", "sftp-loadbalancer")
        ]

        self.kube_config_out = os.path.join(self.state_path, partner_id, f"config_{partner_id}")
        k8s_manifests_partner_dir = os.path.join(self.state_path, partner_id, "manifests")

        logger.info("Cleanup additional configurations in EKS...")

        if execute_bash(f"./destroy_kf.sh {self.kube_config_out} {k8s_manifests_partner_dir}") == 0:
            all_patched = True

            for namespace, service_name in services_to_patch:
                try:
                    if not patch_service_type(self.kube_config_out, namespace, service_name, "ClusterIP"):
                        logger.error(f"Failed to patch service '{service_name}' in namespace '{namespace}'.")
                        all_patched = False
                except Exception as e:
                    logger.error(f"Exception while patching service '{service_name}' in namespace '{namespace}': {e}")
                    all_patched = False

            if all_patched:
                logger.info("All LoadBalancer services successfully patched to ClusterIP. Safe to proceed with TF Destroy.")
                return True
            else:
                logger.error("Some LoadBalancer services could not be patched. Proceed with caution.")
                return False
        else:
            logger.error("Error during pre-cleanup activities.")
            return False