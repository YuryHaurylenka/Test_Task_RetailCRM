from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application-wide settings.
    """

    # api
    api_prefix: str = "/api/v1"
    project_name: str = "Test Task: RetailCRM App"
    debug: bool = False

    # db
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    db_echo: bool = False

    # RetailCRM
    retailcrm_api_key: str

    @property
    def db_url(self) -> str:
        """
        Dynamically generate the database URL.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()