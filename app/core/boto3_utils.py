import os
import boto3
import json
import logging
from botocore.exceptions import ClientError
from app.models import ZonePartner

logger = logging.getLogger(__name__)


class Boto3STSService:
    def __init__(self, zone_partner: ZonePartner):
        self.session = None
        self.account_id = zone_partner.account_id
        self.partner_id = zone_partner.partner_id
        self.variables = zone_partner.variables
        self.region = self.variables['region']
        self.deployment_name = self.variables['deployment_name']
        self.assume_role_arn = f'arn:aws:iam::{self.account_id}:role/eks-access-role-{self.deployment_name}-{self.region}'

    def get_assumed_role_credentials(self):
        sts_client = boto3.client('sts')
        try:
            assumed_role = sts_client.assume_role(
                RoleArn=self.assume_role_arn,
                RoleSessionName='ECSCrossAccountSession'
            )
            logger.info(f"Successfully assumed role: {self.assume_role_arn}")
            return assumed_role['Credentials']
        except ClientError as e:
            logger.error(f"Error assuming role: {e}")
            raise

    def set_aws_credentials(self):
        try:
            credentials = self.get_assumed_role_credentials()
            os.environ["AWS_ACCESS_KEY_ID"] = credentials['AccessKeyId']
            os.environ["AWS_SECRET_ACCESS_KEY"] = credentials['SecretAccessKey']
            os.environ["AWS_SESSION_TOKEN"] = credentials['SessionToken']
            logger.info(f"AWS credentials set successfully for partner_id: {self.partner_id}")
        except ClientError as e:
            logger.error(f"Error setting environment variables: {e}")
            raise


def read_aws_appconfig():
    session = boto3.session.Session()
    client = session.client(service_name='appconfig')
    try:
        response = client.get_configuration(
            Application=os.environ.get('AWS_APPCONFIG_APPLICATION'),
            Environment=os.environ.get('AWS_APPCONFIG_ENVIRONMENT'),
            Configuration=os.environ.get('AWS_APPCONFIG_CONFIGURATION'),
            ClientId=os.environ.get('AWS_APPCONFIG_CLIENT_ID'),
        )
        content = response['Content'].read()
        if response['ContentType'] == 'application/json':
            config = json.loads(content)
            logger.info(f"AWS AppConfig read successfully. Config: {config}")
            return config
        else:
            raise ValueError('Wrong AWS AppConfig configuration type')
    except Exception as e:
        logger.error(f"Error reading AWS AppConfig: {str(e)}")
        raise


def get_aws_secrets(secret_arn):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            raise Exception("The requested secret " + secret_arn + " was not found")
        elif error_code == 'InvalidRequestException':
            raise Exception("The request was invalid due to: %s", e)
        elif error_code == 'InvalidParameterException':
            raise Exception("The request had invalid params: %s", e)
        elif error_code == 'DecryptionFailure':
            raise Exception("The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif error_code == 'InternalServiceError':
            raise Exception("An error occurred on the service side: %s", e)
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            raise ValueError("SecretString not found in response")
