from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/warehouse_db"
    
    # Database connection pool settings (PRODUCTION CRITICAL)
    db_pool_size: int = 20  # Number of connections to maintain
    db_max_overflow: int = 10  # Additional connections when pool exhausted
    db_pool_timeout: int = 30  # Seconds to wait for connection
    db_pool_recycle: int = 3600  # Recycle connections after 1 hour

    # Application settings
    debug: bool = False
    title: str = "Warehouse Management API"
    version: str = "1.0.0"
    description: str = "A FastAPI application for warehouse management"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    # API Rate limiting
    rate_limit_per_minute: int = 60
    
    # Security settings
    secret_key: str = "your-secret-key-here"  # CHANGE IN PRODUCTION!
    api_key_header: str = "X-API-Key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 7 * 24 * 60
    
    # CORS settings
    cors_origins: list[str] = ["*"]  # Configure specific origins in production
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key-here":
            import warnings
            warnings.warn(
                "Using default secret key! Set SECRET_KEY environment variable in production.",
                UserWarning
            )
        return v

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


# Create a global settings instance
settings = Settings()
