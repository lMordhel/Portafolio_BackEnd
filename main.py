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
    # Obtenemos las variables del entorno primero
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port_raw = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("TO_EMAIL")

    # Verificamos que todas existan para evitar errores
    if not all([smtp_host, smtp_port_raw, smtp_user, smtp_pass, to_email]):
        print("Error: Faltan variables de entorno para el correo")
        return False

    try:
        # Convertimos el puerto a entero
        port = int(smtp_port_raw)
        
        msg = EmailMessage()
        msg["Subject"] = f"NUEVO CONTACTO: {data.get('name')}"
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg.set_content(f"Nombre: {data.get('name')}\nEmail: {data.get('email')}\n\nMensaje:\n{data.get('message')}")

        # Lógica de conexión según el puerto
        if port == 465:
            # SSL directo
            with smtplib.SMTP_SSL(smtp_host, port) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            # TLS (puerto 587 o similar)
            with smtplib.SMTP(smtp_host, port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        
        print("Email enviado exitosamente")
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