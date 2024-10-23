from pydantic import BaseModel

class AWSCredentialsPayload(BaseModel):
    """AWS credentials model"""
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str

class AWSCredentialsResponse(BaseModel):
    """Response model for AWS credentials"""
    message: str