from pydantic import BaseModel

class AWSCredentialsPayload(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str

class AWSCredentialsResponse(BaseModel):
    message: str