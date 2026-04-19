from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IDME Cost System"
    app_env: str = "dev"
    app_debug: bool = True
    database_url: str = (
        "mysql+pymysql://root:123456@127.0.0.1:3306/idme?charset=utf8mb4"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

