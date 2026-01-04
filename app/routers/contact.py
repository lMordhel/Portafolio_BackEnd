from fastapi import APIRouter, Depends
from app.models.contact import ContactRequest
from app.db.mongo import collection
from app.services.email_service import send_resend_email
from app.dependencies.auth import verify_admin_token

router = APIRouter()

@router.post("/contact")
async def contact(req: ContactRequest):
    new_message = req.model_dump()
    await collection.insert_one(new_message)
    try:
        send_resend_email(new_message)
    except Exception as e:
        print(f"Error de Resend: {e}")
    return {"ok": True, "message": "Mensaje guardado"}

@router.get("/messages", dependencies=[Depends(verify_admin_token)])
async def get_messages():
    cursor = collection.find({}, {"_id": 0})
    messages = await cursor.to_list(length=100)
    return messages
