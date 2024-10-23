import jenkins
import logging
from app.core.config import config

logger = logging.getLogger(__name__)


def get_jenkins_server():
    jenkins_config = config.get_jenkins_config()
    return jenkins.Jenkins(
        jenkins_config['url'],
        username=jenkins_config['username'],
        password=jenkins_config['api_token']
    )


def trigger_pipeline(params):
    jenkins_config = config.get_jenkins_config()
    server = get_jenkins_server()

    logger.info(f"Triggering pipeline '{jenkins_config['pipeline_name']}' with parameters {params}")
    try:
        server.build_job(jenkins_config['pipeline_name'], parameters=params)
        logger.info(f"Pipeline '{jenkins_config['pipeline_name']}' triggered successfully")
    except Exception as e:
        logger.error(f"Error triggering pipeline: {str(e)}")
        raise


def convert_zone_partner_to_params(zone_partner, variables):
    converted = ','.join([f'"{instance_type}"' for instance_type in variables['instance_types']])

    return {
        'PZ_ACCOUNT_ID': str(zone_partner.account_id),
        'PZ_REGION': variables['region'],
        'PZ_DEPLOYMENT_NAME': variables['deployment_name'],
        'PZ_PARTNER_ID': str(zone_partner.partner_id),
        'PZ_SUBNET_COUNT': variables['subnet_count'],
        'PZ_INSTANCE_TYPES': converted,
        'PZ_MIN_NODES': variables['min_nodes'],
        'PZ_MAX_NODES': variables['max_nodes'],
        'PZ_DESIRED_NODES': variables['desired_nodes']
    }


def trim_parameters(parameters):
    return {
        'PZ_TARGET_BRANCH': f"{parameters['PZ_DEPLOYMENT_NAME']}-{parameters['PZ_REGION']}",
        'PZ_ACCOUNT_ID': parameters['PZ_ACCOUNT_ID']
    }


def add_destroy_env(parameters):
    trimmed_parameters = trim_parameters(parameters)
    trimmed_parameters['PZ_DESTROY_ENV'] = True
    return trimmed_parameters


def trigger_pipeline_create_aws(zone_partner, parameters: dict):
    params = convert_zone_partner_to_params(zone_partner, parameters)
    trigger_pipeline(params)


def trigger_pipeline_redeploy_aws(zone_partner, variables):
    parameters = convert_zone_partner_to_params(zone_partner, variables)
    required_parameters = trim_parameters(parameters)
    trigger_pipeline(required_parameters)


def trigger_pipeline_destroy_aws(zone_partner, variables):
    parameters = convert_zone_partner_to_params(zone_partner, variables)
    required_parameters = add_destroy_env(parameters)
    trigger_pipeline(required_parameters)