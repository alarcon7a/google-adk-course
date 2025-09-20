import os
import json
import requests
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
from fastapi import FastAPI, Request, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from google import auth as google_auth
from google.auth.transport import requests as google_requests
import logging
from dotenv import load_dotenv
# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========= ENV REQUERIDAS =========
#  - D360_API_KEY: tu API key de 360dialog (D360-API-KEY)
#  - GCP_PROJECT:    ID de tu proyecto GCP
#  - GCP_LOCATION:   region (p.ej. "us-central1")
#  - REASONING_ENGINE_ID: ID del Reasoning Engine (solo el id numérico o nombre)
#  - WHATSAPP_VERIFY_TOKEN: token que tú inventas para verificación del webhook (opcional pero recomendado)

#D360_API_KEY = os.getenv("D360_API_KEY")
#GCP_PROJECT = os.getenv("GCP_PROJECT")
#GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
#ENGINE_BASE = os.getenv("ENGINE_BASE")
D360_API_KEY='khSBsCpyk1Ex4xDO6bMvwAnSAK'
GCP_PROJECT="gde-access"
GCP_LOCATION="us-central1"
ENGINE_BASE="projects/gde-access/locations/us-central1/reasoningEngines/5004194077357375488"
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "cambia_esto")

assert D360_API_KEY, "Falta D360_API_KEY"
assert GCP_PROJECT, "Falta GCP_PROJECT"
assert ENGINE_BASE, "Falta ENGINE_BASE"

app = FastAPI()

# Cache para evitar procesar mensajes duplicados
class MessageCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, datetime] = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def is_duplicate(self, message_id: str) -> bool:
        """Verifica si un mensaje ya fue procesado."""
        now = datetime.now()
        
        # Limpiar entradas antiguas
        self.cache = {k: v for k, v in self.cache.items() 
                     if now - v < self.ttl}
        
        if message_id in self.cache:
            return True
        
        self.cache[message_id] = now
        return False
    
    def generate_hash(self, from_wa: str, text: str, timestamp: str) -> str:
        """Genera un hash único para el mensaje."""
        content = f"{from_wa}:{text}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

# Instancia global del cache
message_cache = MessageCache(ttl_seconds=300)

# Set para rastrear mensajes en proceso
processing_messages: Set[str] = set()

def gcp_access_token() -> str:
    """Obtiene el token de acceso de GCP."""
    try:
        credentials, _ = google_auth.default()
        auth_request = google_requests.Request()
        credentials.refresh(auth_request)
        return credentials.token
    except Exception as e:
        logger.error(f"Error obteniendo token GCP: {e}")
        raise

def agent_query_stream(user_text: str, user_id: str, session_id: Optional[str] = None) -> str:
    """Llama al Agent Engine de Vertex AI (modo streaming: stream_query)."""
    url = f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/{ENGINE_BASE}:streamQuery"
    
    payload = {
        "class_method": "stream_query",
        "input": {
            "message": user_text,
            "user_id": user_id,
            "session_id": session_id
        }
    }
    
    headers = {
        "Authorization": f"Bearer {gcp_access_token()}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(payload), 
            stream=True, 
            timeout=60
        )
        response.raise_for_status()
        
        final_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        data = json.loads(line_str)
                        if 'content' in data and 'parts' in data['content']:
                            for part in data['content']['parts']:
                                print(part, flush=True)
                                if 'text' in part and data['content'].get('role') == 'model':
                                    final_response = part['text']
                                    print(part['text'], end='', flush=True)
                except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as e:
                    logger.debug(f"Error procesando línea del stream: {e}")
                    continue
        
        return final_response or "Lo siento, no pude procesar tu mensaje. Por favor, intenta de nuevo."
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error llamando a Vertex AI: {e}")
        return "Disculpa, estoy teniendo problemas técnicos. Por favor, intenta más tarde."
    except Exception as e:
        logger.error(f"Error inesperado en agent_query_stream: {e}")
        return "Ha ocurrido un error. Por favor, intenta de nuevo."

def send_whatsapp_text_360dialog(to: str, text: str) -> dict:
    """Envía texto por 360dialog."""
    url = "https://waba-v2.360dialog.io/messages"
    headers = {
        "D360-API-KEY": D360_API_KEY,
        "Content-Type": "application/json",
    }
    
    # Truncar mensaje si es muy largo
    if len(text) > 4096:
        text = text[:4093] + "..."
    
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enviando mensaje WhatsApp: {e}")
        raise RuntimeError(f"360dialog send error: {e}")

def mark_as_read(message_id: str) -> None:
    """Marca un mensaje como leído en WhatsApp."""
    url = "https://waba-v2.360dialog.io/messages"
    headers = {
        "D360-API-KEY": D360_API_KEY,
        "Content-Type": "application/json",
    }
    
    body = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    try:
        requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
    except Exception as e:
        logger.warning(f"No se pudo marcar mensaje como leído: {e}")

async def process_message_async(from_wa: str, user_text: str, message_id: str):
    """Procesa el mensaje de forma asíncrona."""
    try:
        # Marcar como leído primero
        mark_as_read(message_id)
        
        # Enviar indicador de "escribiendo"
        send_typing_indicator(from_wa, "typing_on")
        
        # Consultar al agente
        logger.info(f"Procesando mensaje de {from_wa}: {user_text[:50]}...")
        reply = agent_query_stream(user_text=user_text, user_id=from_wa)
        
        # Enviar respuesta
        send_typing_indicator(from_wa, "typing_off")
        send_whatsapp_text_360dialog(from_wa, reply)
        
        logger.info(f"Respuesta enviada a {from_wa}")
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        try:
            send_whatsapp_text_360dialog(
                from_wa, 
                "Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
            )
        except:
            pass
    finally:
        # Remover de mensajes en proceso
        processing_messages.discard(message_id)

def send_typing_indicator(to: str, action: str = "typing_on"):
    """Envía indicador de escritura (typing indicator)."""
    url = "https://waba-v2.360dialog.io/messages"
    headers = {
        "D360-API-KEY": D360_API_KEY,
        "Content-Type": "application/json",
    }
    
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "action",
        "action": {
            "type": action  # typing_on o typing_off
        }
    }
    
    try:
        requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
    except Exception as e:
        logger.debug(f"No se pudo enviar typing indicator: {e}")

# ===== Verificación del webhook (GET) =====
@app.get("/webhook")
async def verify(
    mode: Optional[str] = None, 
    challenge: Optional[str] = None, 
    verify_token: Optional[str] = None,
    hub_mode: Optional[str] = None, 
    hub_challenge: Optional[str] = None, 
    hub_verify_token: Optional[str] = None
):
    """Verificación del webhook de WhatsApp."""
    mode = mode or hub_mode
    challenge = challenge or hub_challenge
    verify_token = verify_token or hub_verify_token
    
    logger.info(f"Verificación webhook: mode={mode}, token={verify_token}")
    
    if mode == "subscribe" and verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verificado exitosamente")
        # Devolver el challenge tal cual lo envía WhatsApp
        if challenge and challenge.isdigit():
            return Response(content=challenge, media_type="text/plain")
        return Response(content=str(challenge or "OK"), media_type="text/plain")
    
    logger.warning("Verificación de webhook fallida")
    return JSONResponse(
        status_code=403,
        content={"status": "verification_failed"}
    )

# ===== Recepción del webhook (POST) =====
@app.post("/webhook")
async def receive(request: Request, background_tasks: BackgroundTasks):
    """Recibe y procesa mensajes de WhatsApp."""
    try:
        body = await request.json()
        
        # Log para debugging
        logger.debug(f"Webhook recibido: {json.dumps(body, indent=2)}")
        
        # Extraer información del mensaje
        entry = body.get("entry", [])
        if not entry:
            return JSONResponse(content={"status": "no_entry"}, status_code=200)
        
        changes = entry[0].get("changes", [])
        if not changes:
            return JSONResponse(content={"status": "no_changes"}, status_code=200)
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        # Si no hay mensajes, podría ser un status update
        if not messages:
            statuses = value.get("statuses", [])
            if statuses:
                logger.debug(f"Status update recibido: {statuses[0].get('status', 'unknown')}")
            return JSONResponse(content={"status": "no_message"}, status_code=200)
        
        msg = messages[0]
        message_id = msg.get("id")
        from_wa = msg.get("from")
        timestamp = msg.get("timestamp", "")
        mtype = msg.get("type")
        
        # Verificar si es un mensaje duplicado usando el ID del mensaje
        if message_id and message_id in processing_messages:
            logger.info(f"Mensaje {message_id} ya está siendo procesado, ignorando duplicado")
            return JSONResponse(content={"status": "duplicate_processing"}, status_code=200)
        
        # Verificar duplicados por contenido
        user_text = None
        
        if mtype == "text":
            user_text = msg.get("text", {}).get("body", "").strip()
        elif mtype == "interactive":
            inter = msg.get("interactive", {})
            if "list_reply" in inter:
                user_text = inter["list_reply"].get("title") or inter["list_reply"].get("id")
            elif "button_reply" in inter:
                user_text = inter["button_reply"].get("title") or inter["button_reply"].get("id")
        elif mtype == "button":
            user_text = msg.get("button", {}).get("text", "")
        elif mtype == "image":
            user_text = "(Imagen recibida)"
        elif mtype == "audio":
            user_text = "(Audio recibido)"
        elif mtype == "video":
            user_text = "(Video recibido)"
        elif mtype == "document":
            user_text = "(Documento recibido)"
        elif mtype == "location":
            user_text = "(Ubicación recibida)"
        else:
            user_text = f"(Mensaje tipo {mtype} no soportado)"
        
        if not user_text:
            return JSONResponse(content={"status": "empty_message"}, status_code=200)
        
        # Generar hash único para el mensaje
        msg_hash = message_cache.generate_hash(from_wa, user_text, timestamp)
        
        # Verificar si es duplicado
        if message_cache.is_duplicate(msg_hash):
            logger.info(f"Mensaje duplicado detectado de {from_wa}, ignorando")
            return JSONResponse(content={"status": "duplicate"}, status_code=200)
        
        # Agregar a mensajes en proceso
        if message_id:
            processing_messages.add(message_id)
        
        logger.info(f"Nuevo mensaje de {from_wa}: {mtype} - {user_text[:50]}...")
        
        # Procesar el mensaje en background para responder rápido al webhook
        background_tasks.add_task(
            process_message_async,
            from_wa,
            user_text,
            message_id
        )
        
        # Responder inmediatamente con 200 OK para evitar reintentos
        return JSONResponse(content={"status": "processing"}, status_code=200)
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        # Aún así devolver 200 para evitar reintentos
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=200)

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "WhatsApp-Vertex-Bot"}

@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "service": "WhatsApp Bot with Vertex AI",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)