from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NetWatch"
    
    # Database
    POSTGRES_USER: str = "netwatch_user"
    POSTGRES_PASSWORD: str = "netwatch_password"
    POSTGRES_DB: str = "netwatch"
    POSTGRES_SERVER: str = "127.0.0.1" # Forces IPv4 loopback instead of localhost
    POSTGRES_PORT: str = "5433"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    
    # Emulated dataset path
    DATASET_PATH: str = "../ml_pipeline/sample_dataset.csv"

settings = Settings()
