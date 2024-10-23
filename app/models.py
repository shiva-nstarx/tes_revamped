import re
import uuid
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional


class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ZonePartner(BaseModel):
    plan_only: bool = Field(default=True)
    account_id: Optional[str] = Field(default=None)
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    location: str = Field(..., min_length=1, max_length=50)
    cloud: str = Field(...)
    partner_id: str = Field(...)
    user_id: str = Field(...)

    variables: dict = Field(
        default={
            "region": "us-east-1",
            "deployment_name": "edge-test",
            "subnet_count": 2,
            "instance_types": ["m5.2xlarge", "t3.large"],
            "min_nodes": 2,
            "max_nodes": 5,
            "desired_nodes": 3,
        }
    )

    @field_validator("cloud")
    def validate_cloud(cls, v):
        valid_clouds = ["aws", "azure", "google"]
        if v not in valid_clouds:
            raise ValueError(f"Cloud must be one of {', '.join(valid_clouds)}")
        return v

    @field_validator("partner_id")
    def validate_partner_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Partner ID must be a valid UUID")
        return v

    @field_validator("variables")
    def validate_variables(cls, v):
        if "region" not in v:
            raise ValueError("Region must be specified in variables")

        if "deployment_name" not in v:
            raise ValueError("Deployment name must be specified in variables")

        deployment_name = v["deployment_name"]
        if not 1 <= len(deployment_name) <= 14:
            raise ValueError("Deployment name must be between 1 and 14 characters long")
        if not deployment_name.replace("-", "").isalnum():
            raise ValueError(
                "Deployment name can only contain alphanumeric characters and hyphens"
            )
        if "--" in deployment_name:
            raise ValueError("Deployment name cannot contain consecutive hyphens")
        if deployment_name[0] == "-" or deployment_name[-1] == "-":
            raise ValueError("Deployment name cannot start or end with a hyphen")

        if (
            "subnet_count" not in v
            or not isinstance(v["subnet_count"], int)
            or v["subnet_count"] < 1
        ):
            raise ValueError("Subnet count must be a positive integer")

        if (
            "instance_types" not in v
            or not isinstance(v["instance_types"], list)
            or len(v["instance_types"]) == 0
        ):
            raise ValueError("At least one instance type must be specified")

        for key in ["min_nodes", "max_nodes", "desired_nodes"]:
            if key not in v or not isinstance(v[key], int) or v[key] < 0:
                raise ValueError(f"{key} must be a non-negative integer")

        if v["min_nodes"] > v["max_nodes"]:
            raise ValueError("min_nodes cannot be greater than max_nodes")
        if v["desired_nodes"] < v["min_nodes"] or v["desired_nodes"] > v["max_nodes"]:
            raise ValueError("desired_nodes must be between min_nodes and max_nodes")

        return v

    @model_validator(mode="after")
    def validate_model(self):
        if self.cloud == "aws":
            if not self.account_id:
                raise ValueError("Account ID is required for AWS")
            if not re.match(r"^\d{12}$", self.account_id):
                raise ValueError("AWS Account ID must be exactly 12 digits")
            if not re.match(r"^[a-z]{2}-[a-z]+-\d$", self.variables["region"]):
                raise ValueError("Invalid AWS region format")
        else:
            if self.account_id:
                raise ValueError("Account ID should be empty for non-AWS clouds")
        return self


class DeployMLWorkbench(BaseModel):
    jenkins_job_status: str = "string"
    jenkins_job_id: str = "string"
    deployment_name: str = "string"
    user_id: str = "string"
    partner_id: str = "string"
    account_id: str = "string"
    sftp_bucket_name_dev: str = "string"
    metadata_bucket_name_dev: str = "string"
    sftp_bucket_name_production: str = "string"
    metadata_bucket_name_production: str = "string"
    sftp_bucket_name_staging: str = "string"
    metadata_bucket_name_staging: str = "string"
    telesign_certificate_arn: str = "string"
    autoscaler_role_arn: str = "string"
    fsx_iam_role_arn: str = "string"
    eks_cluster_name: str = "string"
    cluster_subnet_id: str = "string"
    cluster_security_group_id: str = "string"
    vpc_id: str = "string"
    region: str = "string"


class Operation(str, Enum):
    create = "create"
    delete = "delete"


class Role(str, Enum):
    edit = "edit"
    view = "view"


class ProfileAccessRequest(BaseModel):
    partner_id: str
    email_id: EmailStr
    requested_access_profile: str
    role: str
    operation: str

    @model_validator(mode="after")
    def validate_fields(self) -> "ProfileAccessRequest":
        if self.role not in Role.__members__:
            raise ValueError(f"Invalid role option. Must be either 'edit' or 'view'.")
        if self.operation not in Operation.__members__:
            raise ValueError(
                f"Invalid operation option. Must be either 'create' or 'delete'."
            )
        return self

    def get_role_enum(self) -> Role:
        return Role[self.role]

    def get_operation_enum(self) -> Operation:
        return Operation[self.operation]
