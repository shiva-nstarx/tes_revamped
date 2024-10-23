import os
import json
import boto3
from botocore.exceptions import ClientError
from app.core.logging import get_basic_json_logger, setup_logger

logger = get_basic_json_logger(__name__)

class Config:
    def __init__(self):
        self.jenkins_config = {}
        self.okta_config = {}
        self.sftp_mongo_config = {}
        self.okta_ds_config = {}
        self.log_level = "INFO"
        self.logger = None

    def initialize(self, app_config, secrets):
        try:
            # Set log level
            self.log_level = app_config["log_level"]

            # Set up logger
            self.logger = setup_logger(self.__class__.__name__, self.log_level)

            # Set Jenkins Config
            self.jenkins_config = {
                "url": app_config["jenkins_url"],
                "pipeline_name": app_config["jenkins_pipeline_name"],
                "r53_pipeline_name": app_config["jenkins_r53_pipeline_name"],
                "username": secrets["jenkins"]["username"],
                "api_token": secrets["jenkins"]["token"],
                "call_back_url": f"{app_config['partner_creation_api_url']}/deploy-ml-workbench",
                "portal_env": app_config["portal_env"],
            }

            # Set Okta PZ Config
            self.okta_config = {
                "client_id": secrets["okta_pz"]["CLIENT_ID"],
                "private_key": secrets["okta_pz"]["PRIVATE_KEY"],
                "okta_domain": app_config["okta_url"],
                "portal_url": app_config["partner_portal_url"],
            }

            # Set Okta DS Config
            self.okta_ds_config = {
                "client_id": secrets["okta_ds"]["DS_CLIENT_ID"],
                "client_secret": secrets["okta_ds"]["DS_CLIENT_SECRET"],
                "private_cert": secrets["okta_ds"]["PRIVATE_CERT"],
            }

            # Set SFTP and Mongo Config
            self.sftp_mongo_config = {
                "mongodb_username": secrets["sftp_mongo"]["mongodb_username"],
                "mongodb_password": secrets["sftp_mongo"]["mongodb_password"],
                "sftp_default_admin_user": secrets["sftp_mongo"][
                    "sftpgo_default_admin_username"
                ],
                "sftp_default_admin_password": secrets["sftp_mongo"][
                    "sftpgo_default_admin_password"
                ],
                "sftp_user": secrets["sftp_mongo"]["sftpgo_user"],
                "redis_password": secrets["sftp_mongo"]["redis_password"],
                "mlflow_user": secrets["sftp_mongo"]["mlflow_user"],
                "mlflow_password": secrets["sftp_mongo"]["mlflow_password"],
            }

        except Exception as e:
            self.logger.error(f"Error initializing configuration: {str(e)}")
            raise

    def get_jenkins_config(self):
        return self.jenkins_config

    def get_okta_config(self):
        return self.okta_config

    def get_okta_ds_config(self):
        return self.okta_ds_config

    def get_sftp_mongo_config(self):
        return self.sftp_mongo_config

    def get_log_level(self):
        return self.log_level

config = Config()


def create_session():
    return boto3.session.Session(region_name=os.environ.get("AWS_REGION", "us-east-1"))


def read_aws_appconfig():
    try:
        session = create_session()
        client = session.client(service_name="appconfig")
        response = client.get_configuration(
            Application=os.environ["AWS_APPCONFIG_APPLICATION"],
            Environment=os.environ["AWS_APPCONFIG_ENVIRONMENT"],
            Configuration=os.environ["AWS_APPCONFIG_CONFIGURATION"],
            ClientId=os.environ["AWS_APPCONFIG_CLIENT_ID"],
        )
        content = response["Content"].read()
        if response["ContentType"] == "application/json":
            return json.loads(content)
        else:
            logger.warning("Wrong AWS AppConfig configuration type")
            return {}
    except Exception as e:
        logger.error(f"Error reading AWS AppConfig: {e}")
        return {}


def get_aws_secrets(secret_arn):
    try:
        session = create_session()
        client = session.client(service_name="secretsmanager")
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
            return json.loads(secret)
        else:
            logger.warning("SecretString not found in response")
            return {}
    except ClientError as e:
        logger.error(f"Error getting AWS secret: {e}")
        return {}

def initialize_app():
    try:
        app_config = read_aws_appconfig()
        if not app_config:
            logger.warning("Failed to read AWS AppConfig, using default configuration")
            return config.get_log_level()
        secrets = {
            "jenkins": get_aws_secrets(app_config["jenkins_credentials_secret_manager_arn"]),
            "okta_pz": get_aws_secrets(app_config["okta_pz_credentials_secret_manager_arn"]),
            "okta_ds": get_aws_secrets(app_config["okta_ds_credentials_secret_manager_arn"]),
            "sftp_mongo": get_aws_secrets(app_config["sftp_mongo_credentials_secret_manager_arn"]),
        }
        config.initialize(app_config, secrets)
        return config.get_log_level()
    except Exception as e:
        logger.error(f"Failed to initialize app config: {e}")
        return config.get_log_level()

# Initialize the app configuration
log_level = initialize_app()