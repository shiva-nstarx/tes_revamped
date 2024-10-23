import logging
import time
import os
from kubernetes import config, client
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


def load_kube_config(config_file):
    if os.path.exists(config_file):
        config.load_kube_config(config_file=config_file)
    else:
        config.load_kube_config(os.path.expanduser("~/.kube/config"))


def wait_for_pod_initialization(kube_config_out, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            pods = v1.list_pod_for_all_namespaces(watch=False)
            pods_ready = all(
                pod.status.phase == "Running" and all(cs.ready for cs in (pod.status.container_statuses or []))
                for pod in pods.items
            )
            if pods_ready:
                logger.info("All pods are ready.")
                return True
            logger.info("Waiting for pods to be ready...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"An error occurred while checking pods: {e}")
    else:
        logger.error("Timeout waiting for pods to initialize.")
        return False


def return_lb_dns_name(kube_config_out, service_name, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            services = v1.list_service_for_all_namespaces(watch=False)
            for service in services.items:
                if service.metadata.name == service_name and service.status.load_balancer:
                    if service.status.load_balancer.ingress:
                        hostname = service.status.load_balancer.ingress[0].hostname
                        logger.info(f"LoadBalancer hostname found for service '{service_name}': {hostname}")
                        return hostname
            logger.info(f"Waiting for LoadBalancer IP for service '{service_name}'...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"An error occurred while retrieving service IP: {e}")
            return None
    else:
        logger.error(f"Timeout waiting for LoadBalancer IP for service '{service_name}'.")
        return None


def update_configmap(kube_config_out, namespace, configmap_name, new_data, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            current_configmap = v1.read_namespaced_config_map(configmap_name, namespace)
            current_configmap.data = {'authorized_keys': new_data}
            v1.replace_namespaced_config_map(configmap_name, namespace, current_configmap)
            logger.info(f"ConfigMap {configmap_name} updated successfully.")
            return True
        except ApiException as e:
            logger.error(f"An error occurred while updating the configmap: {e}")
            time.sleep(10)
    else:
        logger.error(f"Timeout waiting for the configmap {configmap_name} to be updated.")
        return False


def force_delete_pod(kube_config_out, namespace, label_selector, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            v1.delete_collection_namespaced_pod(namespace, label_selector=label_selector, grace_period_seconds=0)
            logger.info(f"Pods with label selector {label_selector} deleted successfully.")
            return True
        except ApiException as e:
            logger.error(f"An error occurred while deleting the pod: {e}")
            time.sleep(10)
    else:
        logger.error(f"Timeout waiting for the pods with label selector {label_selector} to be deleted.")
        return False


def wait_for_pod_ready(kube_config_out, namespace, label_selector, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            pods = v1.list_namespaced_pod(namespace, label_selector=label_selector)
            pods_ready = all(
                pod.status.phase == "Running" and all(cs.ready for cs in (pod.status.container_statuses or []))
                for pod in pods.items
            )
            if pods_ready:
                logger.info(f"All pods with label selector {label_selector} are ready.")
                return True
            logger.info(f"Waiting for pods with label selector {label_selector} to be ready...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"An error occurred while checking pods: {e}")
    else:
        logger.error(f"Timeout waiting for pods with label selector {label_selector} to be ready.")
        return False


def patch_service_type(kube_config_out, namespace, service_name, service_type, timeout=300):
    load_kube_config(kube_config_out)
    v1 = client.CoreV1Api()
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            patch = [{"op": "replace", "path": "/spec/type", "value": service_type}]
            v1.patch_namespaced_service(name=service_name, namespace=namespace, body=patch)
            logger.info(
                f"Service '{service_name}' in namespace '{namespace}' patched successfully as '{service_type}'.")
            return True
        except ApiException as e:
            logger.error(f"An error occurred while patching the service: {e}")
            time.sleep(10)
    else:
        logger.error(f"Timeout waiting for service '{service_name}' to be patched.")
        return False
