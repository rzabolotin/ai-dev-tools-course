from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+aiomysql://root:secret@db:3306/code_interview"

    class Config:
        env_file = ".env"


settings = Settings()
