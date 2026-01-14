from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="eres un asistente que analiza audios y responde preguntas sobre ellos, tambien puedes responder preguntas generales sin necesidad del audio.",
    instruction="Analiza el audio proporcionado y responde a las preguntas basadas en su contenido, si no hay audio, responde preguntas generales.",
)