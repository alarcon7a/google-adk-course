# Parte de agent.py --> Sigue la guía en https://google.github.io/adk-docs/get-started/quickstart/ para la configuración inicial.
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.tools import google_search
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Usar un modelo de Gemini eficiente. Puedes cambiarlo si lo necesitas.
GEMINI_MODELO = "gemini-2.5-flash"

# --- 1. Definir Sub-Agentes "Especialistas" (que se ejecutarán en paralelo) ---

# Especialista 1: Investigador de Vuelos
investigador_vuelos = LlmAgent(
    name="InvestigadorVuelos",
    model=GEMINI_MODELO,
    instruction="""Eres un Asistente de IA especializado en viajes.
Investiga y resume las opciones de vuelos para un viaje segun indique el usuario.
Usa la herramienta de Búsqueda de Google proporcionada.
Resume tus hallazgos clave de forma concisa, mencionando aerolíneas y rangos de precios aproximados.
Tu salida debe ser *únicamente* el resumen.
""",
    description="Investiga y resume opciones de vuelos.",
    tools=[google_search],
    # Almacena el resultado en el 'estado' para que el agente sintetizador lo use
    output_key="resultado_vuelos"
)

# Especialista 2: Investigador de Hoteles
investigador_hoteles = LlmAgent(
    name="InvestigadorHoteles",
    model=GEMINI_MODELO,
    instruction="""Eres un Asistente de IA especializado en alojamiento.
Investiga y resume opciones de hoteles el destino proporcionado por el usuario.
Usa la herramienta de Búsqueda de Google proporcionada.
Resume tus hallazgos clave de forma concisa, mencionando tipos de hoteles (ej. de lujo, boutique, económicos) y zonas populares.
Tu salida debe ser *únicamente* el resumen.
""",
    description="Investiga y resume opciones de hoteles.",
    tools=[google_search],
    # Almacena el resultado en el 'estado'
    output_key="resultado_hoteles"
)

# Especialista 3: Investigador de Actividades
investigador_actividades = LlmAgent(
    name="InvestigadorActividades",
    model=GEMINI_MODELO,
    instruction="""Eres un Asistente de IA especializado en turismo local.
Investiga y resume las principales actividades y atracciones turísticas para hacer en el destino indicado por el usuario.
Usa la herramienta de Búsqueda de Google proporcionada.
Resume tus hallazgos clave de forma concisa, mencionando al menos 3 actividades populares.
Tu salida debe ser *únicamente* el resumen.
""",
    description="Investiga y resume actividades turísticas.",
    tools=[google_search],
    # Almacena el resultado en el 'estado'
    output_key="resultado_actividades"
)

# --- 2. Crear el ParallelAgent (Ejecuta los investigadores de forma concurrente) ---
# Este agente orquesta la ejecución simultánea de los especialistas.
# Finaliza una vez que todos los especialistas han completado su tarea y
# guardado sus resultados en el 'estado' de la sesión.
agente_investigacion_paralela = ParallelAgent(
    name="AgenteInvestigacionParalelaViaje",
    sub_agents=[investigador_vuelos, investigador_hoteles, investigador_actividades],
    description="Ejecuta múltiples agentes de investigación de viajes en paralelo."
)

# --- 3. Definir el Agente Sintetizador (Se ejecuta *después* de los agentes en paralelo) ---
# Este agente toma los resultados almacenados en el 'estado' por los agentes paralelos
# y los consolida en una única propuesta de viaje estructurada.
agente_sintetizador = LlmAgent(
    name="AgenteSintesisItinerario",
    model=GEMINI_MODELO,
    instruction="""Eres un Asistente de IA experto en crear itinerarios de viaje.

Tu tarea principal es combinar los siguientes resúmenes de investigación en una propuesta de viaje clara y estructurada.

**Fundamental: Tu respuesta completa DEBE basarse *exclusivamente* en la información proporcionada en los 'Resúmenes de Entrada' a continuación. NO añadas ningún conocimiento externo, hechos o detalles que no estén presentes en estos resúmenes específicos.**

**Resúmenes de Entrada:**

* **Vuelos:**
    {resultado_vuelos}

* **Alojamiento:**
    {resultado_hoteles}

* **Actividades:**
    {resultado_actividades}

**Formato de Salida:**

## Propuesta de Itinerario de Viaje

### Opciones de Vuelos
(Basado en los hallazgos del InvestigadorVuelos)
[Sintetiza y detalla *únicamente* la información del resumen de vuelos proporcionado.]

### Opciones de Alojamiento
(Basado en los hallazgos del InvestigadorHoteles)
[Sintetiza y detalla *únicamente* la información del resumen de hoteles proporcionado.]

### Actividades Recomendadas
(Basado en los hallazgos del InvestigadorActividades)
[Sintetiza y detalla *únicamente* la información del resumen de actividades proporcionado.]

### Conclusión del Plan
[Ofrece una breve declaración final que conecte *únicamente* los hallazgos presentados anteriormente.]

Tu salida debe ser *únicamente* el reporte estructurado siguiendo este formato. No incluyas frases introductorias o finales fuera de esta estructura.
""",
    description="Combina los hallazgos de los agentes de investigación en una propuesta de viaje estructurada.",
    # No necesita herramientas, ya que solo procesa texto de entrada.
    # No necesita output_key, ya que su respuesta directa es el resultado final del pipeline.
)


# --- 4. Crear el SequentialAgent (Orquesta el flujo completo) ---
# Este es el agente principal que se ejecutará. Primero ejecuta el ParallelAgent
# para poblar el 'estado', y luego ejecuta el AgenteSintetizador para producir el resultado final.
pipeline_planificacion_viaje = SequentialAgent(
    name="PipelinePlanificacionViajeCompleto",
    # Primero la investigación en paralelo, luego la síntesis.
    sub_agents=[agente_investigacion_paralela, agente_sintetizador],
    description="Coordina la investigación paralela de un viaje y sintetiza los resultados."
)

# El `root_agent` es el punto de entrada para ejecutar todo el flujo de trabajo.
root_agent = pipeline_planificacion_viaje