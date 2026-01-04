from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI) if settings.MONGO_URI else AsyncIOMotorClient()
db = client.get_database("portafolio_db")
collection = db.get_collection("mensajes")
