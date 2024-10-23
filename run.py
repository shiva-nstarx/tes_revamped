import uvicorn
from app.core.config import config, log_level
from app.core.logging import get_uvicorn_log_config


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level=config.log_level.lower(),
        log_config=get_uvicorn_log_config(log_level),
        reload=True,
    )