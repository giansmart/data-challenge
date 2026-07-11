from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    backup_dir: str = "backups"
    log_dir: str = "logs"
    max_batch_size: int = 1000
    csv_delimiter: str = ","


settings = Settings()
