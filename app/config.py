from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./izin.db"
    jwt_secret_key: str = "change-this-in-production"
    jwt_expire_minutes: int = 480
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
