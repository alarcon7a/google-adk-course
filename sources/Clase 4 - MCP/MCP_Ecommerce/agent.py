# ecommerce_mcp_client/agent.py
"""
Agente ADK que consume el servidor MCP de e-commerce.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# IMPORTANTE: Reemplaza esto con la ruta absoluta a tu servidor MCP
# Por ejemplo: "/home/usuario/proyectos/ecommerce_mcp_server.py"
PATH_TO_MCP_SERVER = os.path.abspath("MCP_Ecommerce/ecommerce_mcp_server.py")

# Verifica que el archivo existe
if not os.path.exists(PATH_TO_MCP_SERVER):
    print(f"⚠️ ADVERTENCIA: No se encuentra el servidor MCP en: {PATH_TO_MCP_SERVER}")
    print("Por favor, actualiza PATH_TO_MCP_SERVER con la ruta correcta.")

# Crear el agente con las herramientas del servidor MCP
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='ecommerce_mcp_assistant',
    instruction=(
        "Eres un asistente de compras profesional que ayuda a los usuarios con:\n"
        "1. 🔍 Buscar productos en nuestro catálogo\n"
        "2. 🛒 Agregar productos al carrito\n"
        "3. 💰 Aplicar códigos de descuento (WELCOME10, SAVE20, VIP30)\n"
        "4. 📊 Ver el carrito y calcular totales\n"
        "5. 🎯 Recomendar productos populares\n\n"
        "Características especiales:\n"
        "- Búsqueda inteligente de productos\n"
        "- Cálculo automático de impuestos (8%)\n"
        "- Envío gratis en compras superiores a $100\n"
        "- Recomendaciones personalizadas\n\n"
        "Sé amigable y proactivo. Si un usuario busca algo que no existe exacto, "
        "sugiere alternativas. Menciona cuando están cerca del envío gratis."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='python3',  # o 'python' dependiendo de tu sistema
                args=[PATH_TO_MCP_SERVER],
                # Opcional: pasar variables de entorno si son necesarias
                env={
                    "PYTHONUNBUFFERED": "1"  # Para ver los logs en tiempo real
                }
            ),
            # Opcional: filtrar qué herramientas exponer del servidor MCP
            # tool_filter=['buscar_producto', 'agregar_al_carrito', 'ver_carrito']
        )
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=800,
        top_p=0.9
    )
)