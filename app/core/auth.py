from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.logging import setup_logger
from app.core.config import log_level
from app.utils.okta_utils import validate_okta_token

logger = setup_logger(__name__, log_level)

security = HTTPBearer()

def token_dependency(auth: HTTPAuthorizationCredentials = Security(security)) -> bool:
    token = auth.credentials
    if not validate_okta_token(token):
        logger.warning(f"Invalid token attempt: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid token")
    return True