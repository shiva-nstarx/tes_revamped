import time
import uuid
import base64
import jwt
import requests
from fastapi import HTTPException
from app.core.logging import setup_logger
from app.core.config import config, log_level


SCOPE = "okta.apps.read"

logger = setup_logger(__name__, log_level)

def validate_okta_token(token_to_validate: str) -> bool:
    try:
        # Get Okta credentials
        okta_config = config.get_okta_config()

        if "client_id" not in okta_config or "private_key" not in okta_config:
            raise KeyError("Missing required Okta configuration")

        # Decode the private key
        try:
            decoded_key = base64.b64decode(
                okta_config["private_key"].encode("utf-8")
            ).decode("utf-8")
        except ValueError as ve:
            # If regular decoding fails, try adding padding
            logger.warning(
                f"Initial base64 decode failed: {str(ve)}. Attempting with padding."
            )
            padded_key = okta_config["private_key"] + "=" * (
                    -len(okta_config["private_key"]) % 4
            )
            decoded_key = base64.b64decode(padded_key).decode("utf-8")

        # Create the JWT assertion
        now = int(time.time())
        claims = {
            "iss": okta_config["client_id"],
            "sub": okta_config["client_id"],
            "aud": f"https://{okta_config['okta_domain']}/oauth2/v1/introspect",
            "iat": now,
            "exp": now + 600,  # JWT expiration time
            "jti": str(uuid.uuid4()),
        }

        jwt_assertion = jwt.encode(claims, decoded_key, algorithm="RS256")

        # Introspection request
        introspect_url = f"https://{okta_config['okta_domain']}/oauth2/v1/introspect"
        payload = {
            "token": token_to_validate,
            "token_type_hint": "access_token",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_assertion,
        }

        response = requests.post(introspect_url, data=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        introspection_result = response.json()
        result = introspection_result.get("active", False)
        if result:
            return True
        else:
            logger.error(f"Invalid token: {token_to_validate}")
            raise HTTPException(status_code=401, detail="Invalid Token")
    except KeyError as ke:
        logger.error(f"Configuration error: {str(ke)}")
        raise HTTPException(status_code=500, detail="Invalid configuration")
    except ValueError as ve:
        logger.error(f"Base64 decoding error: {str(ve)}")
        raise HTTPException(status_code=500, detail="Error decoding private key")
    except requests.RequestException as req_ex:
        logger.error(f"Request error: {str(req_ex)}")
        raise HTTPException(status_code=500, detail="Unable to validate token")
    except jwt.PyJWTError as jwt_ex:
        logger.error(f"JWT error: {str(jwt_ex)}")
        raise HTTPException(status_code=500, detail="Unable to create or validate JWT")
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions (including our 401 for invalid tokens)
        raise
    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}")
        raise HTTPException(
            status_code=500, detail=f"Unable to validate token: {str(ex)}"
        )