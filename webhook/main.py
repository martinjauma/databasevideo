
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
    logger.info("Clientes de MongoDB y Mercado Pago inicializados correctamente.")
except Exception as e:
    logger.error(f"Error CRÍTICO al inicializar los clientes: {e}", exc_info=True)
    raise

def process_payment(payment_id: str):
    """
    Esta función se ejecuta en segundo plano para procesar el pago.
    """
    logger.info(f"[BG_TASK] Iniciando procesamiento para el pago ID: {payment_id}")
    try:
        logger.info(f"[BG_TASK] Obteniendo detalles del pago desde la API de Mercado Pago...")
        payment_info = sdk.payment().get(payment_id)
        payment = payment_info.get("response")
        logger.info(f"[BG_TASK] Respuesta de la API de MP recibida.")

        if not payment:
            logger.error(f"[BG_TASK] No se pudo obtener información para el pago ID: {payment_id}")
            return

        payment_status = payment.get("status")
        logger.info(f"[BG_TASK] El estado del pago es: {payment_status}")

        if payment_status == "approved":
            user_email = payment.get("payer", {}).get("email")
            logger.info(f"[BG_TASK] Email del pagador: {user_email}")

            if not user_email:
                logger.error(f"[BG_TASK] Pago {payment_id} aprobado pero sin email del pagador.")
                return

            logger.info(f"[BG_TASK] Intentando actualizar la base de datos para {user_email}...")
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
            logger.info(f"[BG_TASK] ¡ÉXITO! Base de datos actualizada para {user_email}.")
        else:
            logger.info(f"[BG_TASK] El pago no está aprobado. No se realiza ninguna acción.")

    except Exception as e:
        logger.error(f"[BG_TASK] EXCEPCIÓN DETALLADA durante el procesamiento del pago: {e}", exc_info=True)


@app.post("/webhook/mercadopago")
async def mercadopago_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para recibir notificaciones de Webhook de Mercado Pago.
    Responde inmediatamente y procesa el pago en segundo plano.
    """
    try:
        body = await request.json()
        logger.info(f"Webhook recibido: {body}")

        if body.get("type") == "payment":
            payment_id = body.get("data", {}).get("id")
            if payment_id:
                background_tasks.add_task(process_payment, payment_id)
                logger.info(f"Pago {payment_id} encolado para procesamiento. Respondiendo 200 OK a Mercado Pago.")
                return {"status": "notification received"}
        
        logger.warning("Notificación ignorada (no es de tipo 'payment' o no tiene ID).")
        return {"status": "notification ignored"}

    except Exception as e:
        logger.error(f"Error en el endpoint principal del webhook antes de procesar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno en el servidor de webhooks.")

@app.get("/")
def read_root():
    return {"Hello": "World"}
