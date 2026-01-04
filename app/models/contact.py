from pydantic import BaseModel, EmailStr, Field

class ContactRequest(BaseModel):
# El nombre debe tener entre 2 y 50 caracteres
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nombre del remitente"
    )
    
    # EmailStr ya valida el formato, pero podemos ser extra precavidos
    email: EmailStr
    
    # El mensaje no puede estar vacío y máximo 1000 caracteres
    message: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Contenido del mensaje de contacto"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Pérez",
                "email": "juan@ejemplo.com",
                "message": "Hola, me gustaría contactarte para un proyecto."
            }
        }