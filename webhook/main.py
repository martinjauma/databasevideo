
import datetime
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
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
    MONGO_URI = config("MONGO_URI")
    MERCADOPAGO_ACCESS_TOKEN = config("MERCADOPAGO_ACCESS_TOKEN")
    
    client = MongoClient(MONGO_URI)
    db = client.login_logs
    suscripciones_collection = db.suscripciones
    
    sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
except Exception as e:
    logger.error(f"Error al inicializar los clientes: {e}")
    raise

def process_payment(payment_id: str):
    """
    Esta función se ejecuta en segundo plano para procesar el pago.
    """
    logger.info(f"Procesando pago {payment_id} en segundo plano.")
    try:
        payment_info = sdk.payment().get(payment_id)
        payment = payment_info.get("response")

        if not payment:
            logger.error(f"No se pudo obtener información para el pago ID: {payment_id}")
            return

        if payment.get("status") == "approved":
            user_email = payment.get("payer", {}).get("email")
            if not user_email:
                logger.error(f"Pago {payment_id} aprobado pero sin email del pagador.")
                return

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
        else:
            logger.info(f"Pago {payment_id} recibido pero no está aprobado (estado: {payment.get('status')}).")

    except Exception as e:
        logger.error(f"Error procesando el pago ID {payment_id} en segundo plano: {e}")


@app.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para recibir notificaciones de Webhook de Mercado Pago.
    Responde inmediatamente y procesa el pago en segundo plano.
    """
    body = await request.json()
    logger.info(f"Webhook recibido: {body}")

    if body.get("type") == "payment":
        payment_id = body.get("data", {}).get("id")
        if payment_id:
            # Añade la tarea de procesamiento a la cola de fondo
            background_tasks.add_task(process_payment, payment_id)
            logger.info(f"Pago {payment_id} encolado para procesamiento.")
            # Responde inmediatamente a Mercado Pago
            return {"status": "notification received"}

    return {"status": "notification ignored"}

@app.get("/")
def read_root():
    return {"Hello": "World"}
