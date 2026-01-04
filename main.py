from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- CONFIGURACIÓN CORS ---
origins = [
    "http://localhost:5173",
    "https://portafolio-eta-opal.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONEXIÓN MONGODB ---
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("portafolio_db")
collection = db.get_collection("mensajes")

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

# --- FUNCIÓN DE EMAIL (Vía Resend API para evitar bloqueos) ---
def send_resend_email(data: dict):
    api_key = os.getenv("RESEND_API_KEY")
    try:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": "onboarding@resend.dev",
                "to": os.getenv("TO_EMAIL"),
                "subject": f"Nuevo contacto: {data['name']}",
                "html": f"<p>De: {data['name']} ({data['email']})</p><p>{data['message']}</p>"
            }
        )
        return res.status_code in [200, 201]
    except:
        return False

@app.post("/contact")
async def contact(req: ContactRequest):
    try:
        # 1. Guardar en MongoDB
        new_message = req.model_dump()
        await collection.insert_one(new_message)
        
        # 2. Intentar enviar email (pero no bloquear si falla)
        try:
            send_resend_email(new_message)
        except Exception as e:
            print(f"Error de Resend: {e}")

        return {"ok": True, "message": "Mensaje guardado"}
        
    except Exception as e:
        print(f"Error interno: {e}")
        # Esto ayudará a que Vercel te diga qué pasó en los logs
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages")
async def get_messages(x_token: str = Header(None)):
    if x_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=403)
    
    # Traer mensajes de MongoDB
    cursor = collection.find({}, {"_id": 0})
    messages = await cursor.to_list(length=100)
    return messages