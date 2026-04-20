from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IDME Cost System"
    app_env: str = "dev"
    app_debug: bool = True
    database_url: str = (
        "mysql+pymysql://root:123456@127.0.0.1:3306/idme?charset=utf8mb4"
    )
    llm_enabled: bool = True
    llm_base_url: str = "https://api.openai.com"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4.1-mini"
    llm_api_style: str = "openai"
    llm_timeout_seconds: int = 60
    llm_temperature: float = 0.2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
