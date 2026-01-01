from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
import os, smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Header

load_dotenv()

# --- CONFIGURACIÓN BASE DE DATOS ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ContactModel(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(Text)

Base.metadata.create_all(bind=engine)

# --- APP FASTAPI ---
app = FastAPI()
@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a la API de Contacto de Matías",
        "estado": "Online",
        "docs": "/docs"
    }
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://portafolio-eta-opal.vercel.app", # Tu URL de Vercel
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Usamos la lista de arriba
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

def send_email_notification(data: dict):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"NUEVO CONTACTO: {data['name']}"
        msg["From"] = os.getenv("SMTP_USER")
        msg["To"] = os.getenv("TO_EMAIL")
        msg.set_content(f"Nombre: {data['name']}\nEmail: {data['email']}\n\nMensaje:\n{data['message']}")

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            # Para puerto 587 o similares
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

@app.post("/contact")
async def contact(req: ContactRequest):
    # 1. Guardar en Base de Datos
    db = SessionLocal()
    new_msg = ContactModel(name=req.name, email=req.email, message=req.message)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    db.close()

    # 2. Enviar Email
    email_sent = send_email_notification(req.model_dump())

    return {
        "ok": True, 
        "message": "Recibido y guardado", 
        "email_status": email_sent
    }
@app.get("/messages")
async def get_messages(x_token: str = Header(None)):
    if x_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esto")
    
    db = SessionLocal()
    try:
        return db.query(ContactModel).all()
    finally:
        db.close()