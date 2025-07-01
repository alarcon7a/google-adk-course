# 🚀 Curso Práctico de Google Agent Development Kit (ADK) 🤖
![Copia de Copia de Copia de Copia de Copia de Creacion de agentes AI](https://github.com/user-attachments/assets/4fd4c71f-c6ec-4f78-a49f-0c0e6a61f1e4)

¡Bienvenido al curso práctico y avanzado sobre el Google Agent Development Kit (ADK)! Este repositorio contiene una serie de notebooks de Jupyter diseñados para llevarte desde los fundamentos hasta técnicas avanzadas en el desarrollo de agentes de IA con ADK.

## 🎯 ¿Qué es Google ADK?

El Agent Development Kit (ADK) de Google es un framework de código abierto diseñado para simplificar el desarrollo de agentes y sistemas multiagente inteligentes. Permite construir sistemas donde múltiples agentes colaboran, utilizando cualquier modelo de IA (Gemini, Claude, GPT, Llama, etc.) y ofreciendo herramientas integradas para tareas comunes.

## 📚 Contenido del Curso

Este curso está estructurado en varios módulos, cada uno enfocado en un aspecto clave de ADK:

1.  **Módulo 1: Introducción al ADK**
    *   Conceptos fundamentales del ADK.
    *   Ventajas clave y por qué usarlo.
    *   Instalación y configuración del entorno.
    *   Componentes principales: Agentes, Herramientas (Tools), Ejecutores (Runners) y Sesiones (Sessions).
    *   Creación de tu primer agente funcional con búsqueda en Google.
    *   Uso de `adk web` y `adk run` para interactuar con agentes.
- [Ver Video Tutorial](https://youtu.be/zgc8l1c83x8)   

2.  **Módulo 2: Manejo Avanzado de LLMs**
    *   Flexibilidad de modelos con **LiteLLM**: Integración de Claude, GPT, Llama y otros.
    *   Ajuste fino del comportamiento del LLM con parámetros (`temperature`, `top_p`, `max_output_tokens`).
    *   Generación de **output estructurado** utilizando Pydantic para respuestas JSON predecibles y validadas.
    *   Ejemplos prácticos comparando diferentes modelos y configuraciones.
- [Ver Video Tutorial](https://youtu.be/WF1NwVd-nbU)   

3.  **Módulo 3: Dominando las Herramientas (Tools)**
    *   Concepto y importancia de las Herramientas en ADK.
    *   Uso de **herramientas preconstruidas**:
        *   `google_search`: Para búsqueda de información actualizada.
        *   `BuiltInCodeExecutor`: Para ejecución segura de código Python generado por el LLM.
    *   Creación de **herramientas personalizadas**:
        *   Definición de funciones con type hints y docstrings descriptivos.
        *   Ejemplos: Calculadora, Búsqueda de Productos, Cálculo de Porcentajes.
    *   **Buenas prácticas** para el diseño de herramientas efectivas.
    *   Casos de uso avanzados:
        *   Herramientas con estado y contexto (ej. carrito de compras).
        *   Combinación de múltiples herramientas en un agente especializado (ej. agente de e-commerce).
- [Ver Video Tutorial](https://youtu.be/RaW3U5Sb9ks)   

4.  **Módulo 4: Integración con MCP (Model Context Protocol)**
    *   Introducción al **Model Context Protocol (MCP)**: Protocolo estándar para conectar sistemas de IA con fuentes de datos externas.
    *   Configuración y uso de **servidores MCP** con ADK.
    *   Implementación práctica de diferentes tipos de MCP:
        *   **MCP Folder**: Acceso y manipulación de archivos y directorios.
        *   **MCP Twitter**: Integración con redes sociales para análisis y contenido.
        *   **MCP Maps**: Servicios de geolocalización y mapas.
        *   **MCP E-commerce**: Gestión de productos, inventario y transacciones.
    *   Creación de **servidores MCP personalizados** para casos de uso específicos.
    *   Ejemplos prácticos de agentes que consumen datos de múltiples fuentes MCP.
- [Ver Video Tutorial](https://youtu.be/qrN-l9U7nrs)   

5.  **Módulo 5: Workflows Avanzados con ADK**
    *   Diseño e implementación de **workflows complejos** usando múltiples agentes.
    *   Patrones de ejecución:
        *   **Sequential Agent**: Ejecución secuencial de tareas con dependencias.
        *   **Parallel Agent**: Procesamiento paralelo para optimizar rendimiento.
        *   **Loop Agent**: Iteración y refinamiento automático de resultados.
    *   **Orquestación de agentes**: Coordinación y comunicación entre múltiples agentes especializados.
    *   Manejo de **estados compartidos** y **contexto persistente** entre agentes.
    *   Casos de uso avanzados: Pipelines de procesamiento de datos, sistemas de toma de decisiones, y automatización compleja.
- [Ver Video Tutorial](https://youtu.be/ui16aeZrQTc)   

     
## 🛠️ Prerrequisitos

*   Conocimientos básicos de Python.
*   Comprensión fundamental de los Modelos de Lenguaje Grandes (LLMs).
*   Cuenta de Google (para ejecutar en Google Colab).
*   **API Keys** para los modelos que desees utilizar (Google AI Studio, OpenAI, Anthropic, etc.).

## 🚀 Cómo Empezar

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/alarcon7a/google-adk-course
    cd google-adk-course
    ```
2.  **Opción A: Ejecutar en Google Colab (Recomendado para empezar):**
    *   Haz clic en el botón "Abrir en Colab" en la parte superior de este README.
    *   Abre cada notebook (`.ipynb`) individualmente en Colab.
    *   Sigue las instrucciones dentro de cada notebook para instalar dependencias y configurar API Keys.

3.  **Opción B: Ejecutar Localmente:**
    *   **Crea un entorno virtual (recomendado):**
        ```bash
        python -m venv adk-env
        source adk-env/bin/activate  # En Windows: adk-env\Scripts\activate
        ```
    *   **Instala las dependencias base:**
        ```bash
        pip install google-adk==1.4.2 litellm==1.73.0 python-dotenv pydantic jupyter
        ```
        *Nota: Cada notebook puede requerir la instalación de paquetes adicionales.*
    *   **Configura tus API Keys:**
        *   Crea un archivo `.env` en la raíz del proyecto (puedes copiar de `.env.example` si se proporciona).
        *   Añade tus API Keys al archivo `.env`:
            ```env
            GOOGLE_API_KEY="tu_google_api_key"
            OPENAI_API_KEY="tu_openai_api_key"
            ANTHROPIC_API_KEY="tu_anthropic_api_key"
            # Para Azure OpenAI
            # AZURE_API_KEY="tu_azure_api_key"
            # AZURE_API_BASE="tu_azure_endpoint"
            # AZURE_API_VERSION="tu_api_version"
            ```
    *   **Inicia Jupyter Notebook o JupyterLab:**
        ```bash
        jupyter lab
        # o
        jupyter notebook
        # o
        Cualquier IDE  de confianza
        ```
    *   Abre los notebooks (`.ipynb`) y sigue las instrucciones.
    *   Recuerda seguir tambien los archivos .py con adk web o adk run

## 🔑 Conceptos Clave Cubiertos

*   `LlmAgent`: El componente central para crear agentes basados en LLM.
*   `LiteLlm`: Para usar una amplia variedad de modelos de lenguaje.
*   `google_search`: Herramienta preconstruida para búsquedas en Google.
*   `BuiltInCodeExecutor`: Para ejecutar código Python de forma segura.
*   **Herramientas Personalizadas**: Funciones Python decoradas o simplemente pasadas como lista al agente.
*   `generate_content_config`: Para especificar parámetros como `temperature`, `max_output_tokens`, `top_p`.
*   `output_schema`: Para definir la estructura de salida deseada usando modelos Pydantic.
*   `Runner`: Para gestionar la ejecución e interacción con los agentes.
*   `InMemorySessionService`: Para gestionar el historial de conversación en memoria.
*   Type Hints y Docstrings: Esenciales para que ADK entienda la funcionalidad y los parámetros de las herramientas.

## 🙌 Contribuciones

Las contribuciones son bienvenidas. Si encuentras errores, tienes sugerencias o quieres añadir nuevos ejemplos, por favor abre un _issue_ o envía un _pull request_.

## 📄 Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

*   Al equipo de Google por desarrollar y mantener el Agent Development Kit.
*   A las comunidades de AI por sacar tantas herramientas de integración increible
*   A mis seguidores en redes sociales y mi canal de YouTube

---

¡Espero que este curso te sea de gran utilidad para dominar el Google ADK!
