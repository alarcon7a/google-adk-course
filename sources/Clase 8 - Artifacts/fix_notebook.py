import json

notebook_path = '/Users/alarcon7a/GIT/google-adk-course/sources/Clase 8 - Artifacts/artifacts.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'gcs_bucket_name_py ="alarcon_agent_bucket"' in source:
            # Fix indentation and app_name
            new_source = [
                "from google.adk.artifacts import GcsArtifactService\n",
                "\n",
                "# Specify the GCS bucket name\n",
                "gcs_bucket_name_py =\"TU_BUCKET_AQUI\" # <--- CAMBIA ESTO por un bucket que te pertenezca\n",
                "APP_NAME_PERSISTENT = \"tutorial_artifacts_persistent\"\n",
                "USER_ID_PERSISTENT = \"student_2\"\n",
                "SESSION_ID_PERSISTENT = \"session_demo_02\"\n",
                "\n",
                "session_persistent = await session_service.create_session(\n",
                "    app_name=APP_NAME_PERSISTENT,\n",
                "    user_id=USER_ID_PERSISTENT,\n",
                "    session_id=SESSION_ID_PERSISTENT,\n",
                ")\n",
                "\n",
                "try:\n",
                "    gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)\n",
                "    print(f\"Python GcsArtifactService initialized for bucket: {gcs_bucket_name_py}\")\n",
                "    \n",
                "    agente_creador = LlmAgent(\n",
                "        name=\"AgenteCreador\",\n",
                "        model=\"gemini-3-flash-preview\",\n",
                "        instruction=(\n",
                "            \"Eres un asistente administrativo experto. \"\n",
                "            \"Tu trabajo es generar reportes y visualizaciones cuando el usuario lo pida. \"\n",
                "            \"Usa las herramientas disponibles. Cuando generes un archivo, informa al usuario el nombre exacto del archivo generado.\"\n",
                "        ),\n",
                "        tools=[generar_reporte_pdf, generar_imagen_estadistica]\n",
                "    )\n",
                "\n",
                "    # Importante: Pasamos el 'artifact_service' al Runner\n",
                "    runner_persistent = Runner(\n",
                "        agent=agente_creador,\n",
                "        app_name=APP_NAME_PERSISTENT,\n",
                "        session_service=session_service,\n",
                "        artifact_service=gcs_service_py\n",
                "    )\n",
                "\n",
                "    print(f\"🤖 Agente '{agente_creador.name}' listo con {len(agente_creador.tools)} herramientas.\")\n",
                "\n",
                "except Exception as e:\n",
                "    print(f\"Error initializing Python GcsArtifactService: {e}\")\n"
            ]
            cell['source'] = new_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook updated successfully.")
