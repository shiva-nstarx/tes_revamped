from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StatusResponse(BaseModel):
    """Response model for status endpoint"""
    Last_Updated: datetime
    Terraform: Optional[str] = None
    MLWorkbench: Optional[str] = None
    cluster_name: Optional[str] = None
    dynamotable_dev: Optional[str] = None
    dynamotable_production: Optional[str] = None
    dynamotable_staging: Optional[str] = None
    s3_sftp_bucket_dev: Optional[str] = None
    s3_sftp_bucket_production: Optional[str] = None
    s3_sftp_bucket_staging: Optional[str] = None
    s3_metadata_bucket_dev: Optional[str] = None
    s3_metadata_bucket_production: Optional[str] = None
    s3_metadata_bucket_staging: Optional[str] = None
    Kubeflow_URL: Optional[str] = None
    SFTP_URL: Optional[str] = None
    PZ_External_URL: Optional[str] = None

    class Config:
        from_attributes = True