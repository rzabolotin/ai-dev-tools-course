from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "mysql+aiomysql://root:secret@db:3306/code_interview"


settings = Settings()
