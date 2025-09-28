# OLD
# from pydantic import BaseSettings

# NEW
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENWEATHER_KEY: str
    DEFAULT_CITY: str = "London"
    RAIN_THRESHOLD_MM: float = 1.0

    class Config:
        env_file = "../data_pipeline/.env"

settings = Settings()
