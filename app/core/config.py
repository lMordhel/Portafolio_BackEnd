import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI = os.getenv("MONGO_URI")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    TO_EMAIL = os.getenv("TO_EMAIL")
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    CORS_ORIGINS = [
        "http://localhost:5173",
        "https://portafolio-eta-opal.vercel.app",
    ]

settings = Settings()
