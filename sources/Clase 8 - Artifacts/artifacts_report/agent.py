"""
Clase 8: Artifacts Agent
Este agente demuestra el uso de Artifacts para generar y consumir archivos binarios (PDF, Imágenes).
"""

import os
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
# -------------------------
# Tools para el Agente
# -------------------------


async def guardar_archivo(tool_context: ToolContext, filename: str, data: str, mime_type: str) -> str:
    '''
    Guarda un archivo como Artifact en el contexto de la herramienta.
    Args:
        filename: Nombre del archivo a guardar.
        data: Contenido del archivo.
        mime_type: Tipo MIME del archivo. (e.g., 'application/pdf', 'image/png', 'audio/mp3')

    Returns:
        dict: Resultado de la operación con estado y mensaje.

    '''
    print(f"⚙️ [Tool] Guardando artifact: {filename}")
    if not mime_type:
        mime_type = "text/plain"

    try:
        data_bytes = data.encode('utf-8')
        artifact_part = types.Part(inline_data=types.Blob(data=data_bytes, mime_type=mime_type))
        version = await tool_context.save_artifact(filename, artifact_part)

        return {"version": version,
     "message": f"He guardado el artifact '{filename}' con éxito.",
     'status': 'success'}
    except Exception as e:
        return {"status": "error", "error": str(e)}



async def generar_pdf(tool_context: ToolContext, titulo: str, datos_texto: str) -> dict:
    '''
    Genera un reporte PDF con un título y una descripción de datos.
    
    Args:
        titulo: El título que aparecerá en el PDF.
        datos_texto: El contenido del reporte.
    '''
    print(f"   ⚙️ [Tool] Creando PDF: {titulo}")
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Estilo simple
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height - 50, titulo)
        
        c.setFont("Helvetica", 12)
        y_pos = height - 80
        for line in datos_texto.split('\\n'):
            c.drawString(50, y_pos, line)
            y_pos -= 15
            
        c.save()
        pdf_bytes = buffer.getvalue()
        
        # Guardar como Artifact
        filename = f"reporte_{datetime.now().strftime('%H%M%S')}.pdf"
        artifact_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        
        # El ADK maneja la persistencia del artifact
        version = await tool_context.save_artifact(filename, artifact_part)
        
        return {
            "status": "success",
            "filename": filename,
            "version": version,
            "message": f"He generado el PDF '{filename}'. Puedes descargarlo ahora."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def generar_grafico_simple(tool_context: ToolContext, etiqueta: str, valor: str) -> dict:
    '''    Genera una imagen PNG simple con una etiqueta y un valor estadístico.
    Args:
        etiqueta: La etiqueta para el gráfico.
        valor: El valor estadístico a mostrar.
'''
    print(f"⚙️ [Tool] Creando Imagen: {etiqueta}")
    try:
        img = Image.new('RGB', (400, 200), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        
        # Dibujar texto
        d.text((20, 80), f"{etiqueta}: {valor}", fill=(0, 255, 0))
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        
        filename = f"grafico_{datetime.now().strftime('%H%M%S')}.png"
        artifact_part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
        version = await tool_context.save_artifact(filename, artifact_part)
        
        return {
            "status": "success",
            "filename": filename,
            "version": version,
            "message": f"Imagen '{filename}' generada con éxito."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def leer_y_analizar_archivo(tool_context: ToolContext, filename: str) -> dict:
    '''
    Lee el contenido textual de un artifact ya existente para analizarlo.
    '''
    print(f"   ⚙️ [Tool] Analizando artifact: {filename}")
    try:
        artifact = await tool_context.load_artifact(filename)
        if not artifact:
            return {"status": "error", "message": "No encontré ese archivo."}
        
        # Intentamos decodificar como texto para el análisis
        contenido = artifact.inline_data.data.decode('utf-8', errors='ignore')
        
        return {
            "status": "success",
            "snippet": contenido[:500],
            "total_length": len(contenido),
            "info": "Contenido extraído correctamente para tu análisis."
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# -------------------------
# Configuración del Agente
# -------------------------

root_agent = Agent(
    name="artifact_pro_assistant",
    model="gemini-3-flash-preview",
    description="Asistente experto en gestión de archivos y reportes binarios.",
    instruction=(
        "Eres un Agente experto en manejo de Artifacts. Tu especialidad es crear reportes PDF "
        "y generar visualizaciones gráficas simples.\n\n"
        "Cuando el usuario te pida un informe o gráfico:\n"
        "1. Usa la herramienta correspondiente.\n"
        "2. Dale al usuario el nombre exacto del archivo generado.\n"
        "3. Si el usuario te menciona un archivo que ya existe en la sesión, puedes usar "
        "'leer_y_analizar_artifact' para entender su contenido.\n\n"
        "Mantén un tono profesional y servicial."
    ),
    tools=[generar_pdf, generar_grafico_simple, leer_y_analizar_archivo, guardar_archivo]
)
