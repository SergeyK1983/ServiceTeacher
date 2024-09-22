from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings, case_sensitive=True):
    # case_sensitive=True все имена переменных теперь чувствительны к регистру

    # database
    DB_NAME: str = Field(alias="DB_NAME")
    DB_USER: str = Field(alias="DB_USER")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: int = Field(alias="DB_PORT")

    # auth
    SECRET_KEY: str = Field(alias="SECRET_KEY")
    ALGORITHM: str = Field(alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # class Config:
    #     secrets_dir = BASE_DIR / "secrets"  # директория, где хранится файл с паролем.

    @property
    def postgresql_url(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

