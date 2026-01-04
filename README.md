# Backend Python - FastAPI Modular Structure

Este documento describe la arquitectura del backend, organizado de manera modular para facilitar la escalabilidad y el mantenimiento.

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura por capas donde cada carpeta tiene una responsabilidad específica.

```
/ (root)
├── app/                  # Código fuente principal de la aplicación
│   ├── core/             # Configuraciones globales y seguridad
│   ├── db/               # Conexión y manejo de base de datos
│   ├── models/           # Esquemas de datos (Pydantic)
│   ├── services/         # Lógica de negocio externa (ej. Email)
│   ├── routers/          # Definición de rutas (Endpoints)
│   ├── dependencies/     # Dependencias reutilizables (ej. Auth)
│   └── main.py           # Inicialización de la App FastAPI
├── main.py               # Punto de entrada para Vercel (Shim)
├── requirements.txt      # Librerías y dependencias
├── vercel.json           # Configuración de despliegue en Vercel
└── .env                  # Variables de entorno (No subir a Git)
```

## 🧩 Descripción de Componentes

### 1. `app/core/` (Núcleo)
Contiene la configuración base que afecta a toda la app.
- **`config.py`**: Carga y valida las variables de entorno (como `MONGO_URI`, claves de API) usando `python-dotenv` y `os`. Centraliza la configuración para no tener `os.getenv` dispersos por el código.
- **`security.py`**: Utilidades de seguridad (hashing de contraseñas, generación de tokens). Actualmente incluye funciones básicas preparadas para expansión.

### 2. `app/db/` (Base de Datos)
Maneja la conexión con la persistencia de datos.
- **`mongo.py`**: Inicializa el cliente `AsyncIOMotorClient` (MongoDB asíncrono). Expone el objeto `db` y `collection` para que otros módulos los importen y usen.

### 3. `app/models/` (Modelos)
Define la estructura de los datos que entran y salen de la API.
- **`contact.py`**: Define `ContactRequest` usando Pydantic. Valida que el JSON recibido tenga `name`, `email` (válido) y `message` antes de procesarlo.

### 4. `app/services/` (Servicios)
Contiene la lógica de negocio pura o integraciones con terceros, separada de los controladores (routers).
- **`email_service.py`**: Contiene la función `send_resend_email`. Se encarga de llamar a la API de Resend para enviar notificaciones. Maneja sus propios errores para no bloquear el flujo principal.

### 5. `app/dependencies/` (Dependencias)
Funciones que se inyectan en las rutas para validaciones previas.
- **`auth.py`**: Contiene `get_admin_token`. Verifica que el header `x-token` coincida con el `ADMIN_TOKEN` definido en las variables de entorno. Protege rutas sensibles.

### 6. `app/routers/` (Rutas)
Define los endpoints HTTP (URLs) y orquesta la llamada a servicios y base de datos.
- **`contact.py`**:
    - `POST /contact`: Recibe el modelo, guarda en MongoDB y llama al servicio de email en segundo plano.
    - `GET /messages`: Lista los mensajes guardados. Usa la dependencia de auth para proteger el acceso.

### 7. `app/main.py` (App Principal)
- Inicializa `FastAPI`.
- Configura **CORS** (Orígenes permitidos).
- Incluye los `routers` definidos en otras carpetas.

### 8. `main.py` (Raíz)
- Archivo "shim" o adaptador necesario para entornos serverless como Vercel. Simplemente importa la `app` desde `app.main` para exponerla al servidor.

## 🚀 Cómo Ejecutar

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar entorno**:
   Crea un archivo `.env` en la raíz con:
   ```env
   MONGO_URI=...
   RESEND_API_KEY=...
   TO_EMAIL=...
   ADMIN_TOKEN=...
   ```

3. **Correr servidor**:
   ```bash
   uvicorn app.main:app --reload
   ```

Esta estructura permite que una IA (o un desarrollador) entienda rápidamente dónde buscar: si es un error de base de datos, ir a `db/`; si es una validación de datos, ir a `models/`; si es lógica de negocio, ir a `services/`.
