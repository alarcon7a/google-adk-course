# Guion de YouTube · Clase 7: Sesiones y Memoria en Google ADK

## Objetivo del video
- Motivar a developers y PMs a entender por qué el estado y la memoria son claves para agentes confiables.
- Presentar la Clase 7 como un taller práctico lleno de demos accionables.
- Invitar a descargar el notebook y seguir el curso completo.

## Estructura narrativa

### 0:00 – Hook (20 segundos)
**Presentador/a en cámara:**
"¿Tu agente recuerda lo que prometió hace cinco minutos? Hoy te muestro cómo darle memoria real y personalizar cada turno como si fuera un concierge humano."  
**Visual:** Plano medio, subtítulos dinámicos con palabras clave "Sesiones", "Estado", "Memoria".  
**B-roll sugerido:** Animación rápida de un chatbot olvidando información y luego actualizándose.

### 0:20 – Introducción y credenciales (30 segundos)
**Presentador/a:**
"Bienvenidos a la Clase 7 del curso de Google ADK. Soy [TU NOMBRE], y en los próximos minutos aprenderás a usar `session.state` y Memory Services para construir experiencias memorables."  
"Si estás construyendo asistentes para soporte, e-commerce o productividad, este episodio te va a ahorrar semanas de prueba y error."  
**CTA suave:** "Suscríbete y activa la campanita para no perderte el resto de la serie."  
**Visual:** Lower third con nombre, cargo y logo del curso.

### 0:50 – Contexto del problema (45 segundos)
**Presentador/a:**
"Cuando un agente no usa estado, responde como si fuera la primera vez. Sin memoria, no hay follow-up, no hay personalización."  
"Google ADK nos da dos superpoderes: sesiones ricas en eventos y memorias persistentes."  
**Visual:** Gráfico dividido en tres: `events`, `state`, `memory`.  
**Tip de ritmo:** Incluye un corte con zoom o cambio de cámara para mantener la atención.

### 1:35 – Capítulo 1: Dominando `session.state` (2 minutos)
**Demo guiada:**
1. "Abrimos el notebook de la Clase 7 y cargamos el helper `call_agent_async`."
2. "En el primer ejemplo, el concierge de viajes combina preferencias con el tono correcto gracias a `user:` y estado local."  
3. "Luego pasamos al nuevo caso práctico de mesa de ayuda: usamos `registrar_avance` para documentar acciones, calcular el tiempo consumido y mantener visible el SLA."  
"Cada interacción modifica el estado y el agente responde con contexto fresco."  
**Visual:** Capturas de pantalla del notebook resaltando las claves `user:`, `temp:` y los prints de depuración.  
**B-roll sugerido:** Sobreimpresión de snippets de código con animaciones de check.

### 3:35 – Capítulo 2: Memoria a largo plazo (2 minutos)
**Presentador/a:**
"El estado vive dentro de la sesión, pero la memoria nos permite aprender de conversaciones pasadas."  
"Primero usamos `InMemoryMemoryService` para prototipar, y después conectamos Vertex AI Memory Bank para producción."  
**Demo guiada:**
- Mostrar cómo `memory_service.add_session_to_memory()` guarda datos relevantes.
- Resaltar la nueva celda que comprueba variables `VERTEX_PROJECT_ID`, `VERTEX_LOCATION` y `VERTEX_AGENT_ENGINE_ID` antes de llamar a Vertex.
- Explicar el segundo runner que consulta memorias desde Vertex con la herramienta `load_memory`.
**Visual:** Diagrama de flujo con "Captura" → "Memoria" → "Consulta".

### 5:35 – Mejores prácticas y checklist (1 minuto)
**Presentador/a:**
"Antes de cerrar, toma nota de estas reglas de oro:"  
- "Documenta qué claves usas en `state` y limpia `temp:` en cada turno."  
- "Envía a memoria solo lo valioso; menos ruido, mejores resultados."  
- "Configura tu Agent Engine en Vertex y prueba primero en staging."  
**Visual:** Lista animada con íconos y ticks.

### 6:35 – CTA final (25 segundos)
**Presentador/a:**
"Descarga el notebook, ejecuta `adk run` y cuéntame en los comentarios qué caso de uso vas a potenciar con sesiones y memoria."  
"En la descripción te dejo los repos y el checklist completo. Nos vemos en la próxima clase."  
**Visual:** Outro con branding del curso y recordatorio de suscribirse.

## Buenas prácticas aplicadas
- Hook potente en <20s con promesa clara.
- Ritmo dinámico con cortes cada 30-45 segundos y B-roll contextualizado.
- CTA intermedio y final para fomentar suscripción y engagement.
- Script en segunda persona para conectar con quienes construyen agentes.
- Secciones cortas con objetivos específicos para facilitar la edición.

## Preparación antes de grabar
1. Actualizar el `.env` con las variables de Vertex y probar las celdas en vivo.
2. Preparar capturas del notebook con resaltados de estado y memoria.
3. Configurar teleprompter o tarjetas con los bullets clave.
4. Verificar iluminación frontal suave y fondo con branding del curso.
5. Cargar assets (animaciones, lower thirds) en el editor antes de la sesión de grabación.

