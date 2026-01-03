from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/warehouse_db"

    # Application settings
    debug: bool = False
    title: str = "Warehouse Management API"
    version: str = "1.0.0"
    description: str = "A FastAPI application for warehouse management"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Security settings (for future use)
    secret_key: str = "your-secret-key-here"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()
