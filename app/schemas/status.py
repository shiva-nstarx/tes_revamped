from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Response model for status endpoint"""
    Last_Updated: datetime = Field(description="Last updated timestamp")
    Terraform: Optional[str] = Field(None, description="Terraform deployment status")
    MLWorkbench: Optional[str] = Field(None, description="MLWorkbench deployment status")
    cluster_name: Optional[str] = Field(None, description="EKS cluster name")

    # DynamoDB tables
    dynamotable_dev: Optional[str] = Field(None, description="Development environment DynamoDB table")
    dynamotable_production: Optional[str] = Field(None, description="Production environment DynamoDB table")
    dynamotable_staging: Optional[str] = Field(None, description="Staging environment DynamoDB table")

    # SFTP buckets
    s3_sftp_bucket_dev: Optional[str] = Field(None, description="Development environment SFTP bucket")
    s3_sftp_bucket_production: Optional[str] = Field(None, description="Production environment SFTP bucket")
    s3_sftp_bucket_staging: Optional[str] = Field(None, description="Staging environment SFTP bucket")

    # Metadata buckets
    s3_metadata_bucket_dev: Optional[str] = Field(None, description="Development environment metadata bucket")
    s3_metadata_bucket_production: Optional[str] = Field(None, description="Production environment metadata bucket")
    s3_metadata_bucket_staging: Optional[str] = Field(None, description="Staging environment metadata bucket")

    # URLs
    Kubeflow_URL: Optional[str] = Field(None, description="Kubeflow dashboard URL")
    SFTP_URL: Optional[str] = Field(None, description="SFTP service URL")
    PZ_External_URL: Optional[str] = Field(None, description="Partner Zone external URL")

    class Config:
        json_schema_extra = {
            "example": {
                "Last_Updated": "2024-10-23T10:00:00",
                "Terraform": "Complete",
                "MLWorkbench": "Complete",
                "cluster_name": "eks-cluster-1",
                "dynamotable_dev": "partner_batch_results_dev",
                "dynamotable_production": "partner_batch_results_production",
                "dynamotable_staging": "partner_batch_results_staging",
                "s3_sftp_bucket_dev": "sftp-bucket-dev",
                "s3_sftp_bucket_production": "sftp-bucket-production",
                "s3_sftp_bucket_staging": "sftp-bucket-staging",
                "s3_metadata_bucket_dev": "metadata-bucket-dev",
                "s3_metadata_bucket_production": "metadata-bucket-production",
                "s3_metadata_bucket_staging": "metadata-bucket-staging",
                "Kubeflow_URL": "https://kubeflow.example.com",
                "SFTP_URL": "sftp://sftp.example.com",
                "PZ_External_URL": "https://pz.example.com"
            }
        }