
from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from decouple import config
import mercadopago
import logging

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Inicialización de la App FastAPI ---
app = FastAPI()

# --- Configuración de Clientes ---
try:
    # Usamos decouple para cargar las variables de entorno de forma segura
    MONGO_URI = config("MONGO_URI")
    MERCADOPAGO_ACCESS_TOKEN = config("MERCADOPAGO_ACCESS_TOKEN")
    
    client = MongoClient(MONGO_URI)
    db = client.login_logs
    suscripciones_collection = db.suscripciones
    
    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
except Exception as e:
    logger.error(f"Error al inicializar los clientes: {e}")
    # Si no podemos conectar, la aplicación no puede funcionar.
    # En un entorno real, esto debería alertar a los desarrolladores.
    raise

@app.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request):
    """
    Endpoint para recibir notificaciones de Webhook de Mercado Pago.
    """
    body = await request.json()
    logger.info(f"Webhook recibido: {body}")

    # 1. Validar que la notificación es del tipo correcto
    if body.get("type") == "payment":
        payment_id = body.get("data", {}).get("id")
        if not payment_id:
            logger.warning("Notificación de pago sin ID.")
            raise HTTPException(status_code=400, detail="ID de pago no encontrado en la notificación.")

        try:
            # 2. Obtener la información completa del pago desde Mercado Pago
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info.get("response")

            if not payment:
                logger.error(f"No se pudo obtener información para el pago ID: {payment_id}")
                raise HTTPException(status_code=404, detail="Pago no encontrado en Mercado Pago.")

            # 3. Verificar si el pago fue aprobado
            if payment.get("status") == "approved":
                # Asumiendo que el email del pagador está en el campo `payer.email`
                user_email = payment.get("payer", {}).get("email")
                if not user_email:
                    logger.error(f"Pago {payment_id} aprobado pero sin email del pagador.")
                    # Aún así, devolvemos 200 para que MP no reintente. El error ya está logueado.
                    return {"status": "error", "detail": "Email no encontrado en el pago"}

                # 4. Actualizar la base de datos para otorgar la suscripción
                suscripciones_collection.update_one(
                    {"user_email": user_email},
                    {
                        "$set": {
                            "status": "active",
                            "payment_date": datetime.datetime.now(),
                            "source": "mercadopago_webhook",
                            "last_payment_id": payment_id
                        },
                        "$setOnInsert": {
                            "user_email": user_email,
                            "signup_date": datetime.datetime.now()
                        }
                    },
                    upsert=True
                )
                logger.info(f"Suscripción activada para {user_email} a través del webhook.")
                return {"status": "success"}
            else:
                logger.info(f"Pago {payment_id} recibido pero no está aprobado (estado: {payment.get('status')}).")
                # No es un error, simplemente no hacemos nada.
                return {"status": "ignored", "reason": "payment_not_approved"}

        except Exception as e:
            logger.error(f"Error procesando el pago ID {payment_id}: {e}")
            # Devolvemos un error 500 para que Mercado Pago pueda reintentar si es un fallo temporal.
            raise HTTPException(status_code=500, detail="Error interno al procesar el pago.")

    return {"status": "notification_ignored"}

@app.get("/")
def read_root():
    return {"Hello": "World"}
