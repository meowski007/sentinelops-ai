import os
from typing import List


class Settings:
    PROJECT_NAME: str = "SentinelOps AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinelops.db")

    # CORS
    _cors_env: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self._cors_env.split(",") if origin.strip()]

    # AI Engine Configuration: "LOCAL_DETERMINISTIC" or "EXTERNAL_LLM"
    AI_INVESTIGATION_MODE: str = os.getenv("AI_INVESTIGATION_MODE", "LOCAL_DETERMINISTIC")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Data generation
    DATA_SEED: int = int(os.getenv("DATA_SEED", "42"))

settings = Settings()
