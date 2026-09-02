from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()