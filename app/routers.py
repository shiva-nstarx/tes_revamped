from fastapi import APIRouter, Depends

from app.api.endpoints import zone_partners, ml_workbench, status, auth, health, root
from app.core.auth import token_dependency

api_router = APIRouter()

api_router.include_router(root.router, include_in_schema=False)
api_router.include_router(zone_partners.router, prefix="/zone-partners", tags=["zone-partners"])
api_router.include_router(ml_workbench.router, prefix="/ml-workbench", tags=["ml-workbench"])
# api_router.include_router(profile_access.router, prefix="/profile-access", tags=["profile-access"], dependencies=[Depends(token_dependency)])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(zone_partners.router, prefix="/zone-partners", tags=["zone-partners"], dependencies=[Depends(token_dependency)])
# api_router.include_router(ml_workbench.router, prefix="/ml-workbench", tags=["ml-workbench"], dependencies=[Depends(token_dependency)])
# api_router.include_router(profile_access.router, prefix="/profile-access", tags=["profile-access"], dependencies=[Depends(token_dependency)])
# api_router.include_router(status.router, prefix="/status", tags=["status"], dependencies=[Depends(token_dependency)])
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"], dependencies=[Depends(token_dependency)])
api_router.include_router(health.router, tags=["health-checks"])