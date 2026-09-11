from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "WorkForce AI Pro"
    API_V1_STR: str = "/api/v1"

    # MySQL connection - update via .env in production
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "maadhavan2304"
    DB_NAME: str = "workforce_ai_pro"

    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
