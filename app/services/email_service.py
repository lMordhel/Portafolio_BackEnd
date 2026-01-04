import requests
from app.core.config import settings

def send_resend_email(data: dict) -> bool:
    api_key = settings.RESEND_API_KEY
    try:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": "onboarding@resend.dev",
                "to": settings.TO_EMAIL,
                "subject": f"Nuevo contacto: {data['name']}",
                "html": f"<p>De: {data['name']} ({data['email']})</p><p>{data['message']}</p>",
            },
        )
        return res.status_code in (200, 201)
    except Exception:
        return False
