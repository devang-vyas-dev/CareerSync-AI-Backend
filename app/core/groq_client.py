from groq import Groq
from app.core.config import settings

_client = None

def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

# Keep this also for backward compatibility
groq_client = get_groq_client()