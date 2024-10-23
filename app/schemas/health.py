from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str

class ReadinessResponse(BaseModel):
    status: str
    message: str
    log_level: str