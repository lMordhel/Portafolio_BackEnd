from fastapi import APIRouter, Depends, HTTPException
from app.models.contact import ContactRequest
from app.db.mongo import collection
from app.services.email_service import send_resend_email
from app.dependencies.auth import verify_admin_token
from app.core.logging_config import logger  # Importamos nuestro logger

router = APIRouter()

@router.post("/contact")
async def contact(req: ContactRequest):
    try:
        # Log de información: útil para seguimiento normal
        logger.info(f"Intento de contacto recibido desde: {req.email}")
        
        new_message = req.model_dump()
        result = await collection.insert_one(new_message)
        
        logger.info(f"Mensaje guardado en MongoDB con ID: {result.inserted_id}")

        # Intentar enviar el email
        try:
            email_sent = send_resend_email(new_message)
            if email_sent:
                logger.info("Notificación de email enviada exitosamente via Resend")
            else:
                logger.warning("Resend aceptó la petición pero el envío pudo no completarse")
        except Exception as e:
            # Log de error: algo falló en un servicio externo
            logger.error(f"Fallo crítico en el servicio de email: {str(e)}")

        return {"ok": True, "message": "Mensaje guardado"}

    except Exception as e:
        # Log crítico: error de base de datos o fallo total del servidor
        logger.critical(f"Fallo total en endpoint /contact: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el contacto")

@router.get("/messages", dependencies=[Depends(verify_admin_token)])
async def get_messages():
    try:
        logger.info("Acceso autorizado al panel de mensajes")
        cursor = collection.find({}, {"_id": 0})
        messages = await cursor.to_list(length=100)
        return messages
    except Exception as e:
        logger.error(f"Error al recuperar mensajes de la DB: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudieron obtener los mensajes")