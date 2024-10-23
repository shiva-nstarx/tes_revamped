from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import api_router
from app.core.config import config, log_level
from app.core.logging import setup_logger
from app.utils.utils import check_tools

logger = setup_logger(__name__, log_level)

description = """
Partner Zone Management Service API 🚀

This API allows you to manage partner zones, including:

* Create new partner zones
* Delete existing partner zones
* Deploy ML workbenches
* Manage profile access
* Retrieve status information

For more information, please refer to the provided documentation.
"""

tags_metadata = [
    {
        "name": "zone-partners",
        "description": "Operations with zone partners. Includes creation, deletion, and redeployment.",
    },
    {
        "name": "ml-workbench",
        "description": "Manage ML workbench deployments.",
    },
    {
        "name": "profile-access",
        "description": "Manage user profile access within partner zones.",
    },
    {
        "name": "status",
        "description": "Retrieve status information for partner zones.",
    },
    {
        "name": "auth",
        "description": "Operations related to authentication.",
    },
    {
        "name": "health-checks",
        "description": "Operations related to health checks, liveness, readiness etc.",
    },
]

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup
    check_tools()
    logger.info("Application startup complete.")
    yield
    # Shutdown
    logger.warning("Application shutting down.")

app = FastAPI(
    title="Partner Zone Management API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.include_router(api_router)