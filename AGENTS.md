# Repository Guidelines

## Project Structure & Module Organization
The course content is split between `sources/` (Spanish) and `sources_en/` (English), each class folder containing lesson-specific notebooks plus reusable `agent.py` examples. Deployment experiments live under `sources/Deploy/`, where `whatsapp_test/` holds a FastAPI bridge and `installation_scripts/` collects helper shell scripts. Place shared assets such as diagrams or sample data beside the module that consumes them, and mirror changes in both language variants when applicable.

## Build, Test, and Development Commands
Create a virtual environment before running notebooks or scripts: `python -m venv .venv && source .venv/bin/activate`. Install the baseline toolchain with `pip install google-adk==1.4.2 litellm==1.73.0 python-dotenv pydantic jupyter`, and add module-specific extras using `pip install -r sources/Deploy/whatsapp_test/requirements.txt` when working on the WhatsApp demo. Launch notebooks via `jupyter lab` or execute agents directly with `adk run path/to/agent.py`; use `adk web path/to/agent.py` while iterating on conversational flows. Start the WhatsApp sample locally using `uvicorn app:app --reload --port 8000`.

## Coding Style & Naming Conventions
Python modules follow PEP 8: 4-space indentation, `snake_case` for functions and tools, and descriptive docstrings that clarify agent capabilities. Keep instruction prompts in the language of the enclosing folder, and externalize secrets into environment variables loaded through `.env`. Notebook cells should mirror the structure of their matching `agent.py` so contributors can diff logic outside the notebook environment.

## Testing Guidelines
Automated coverage is light today, so add targeted unit tests whenever you introduce new helpers or tools. Prefer `pytest` for new suites (`pip install pytest`) and mirror tests across language variants when logic overlaps. For streaming or webhook flows, exercise the FastAPI endpoints with `pytest-asyncio` or `httpx.AsyncClient`, and document any manual test steps in the notebook markdown cells.

## Commit & Pull Request Guidelines
Use short, imperative commit messages (e.g., "Add MCP ecommerce server docs") and mention the class folder touched to aid navigation. Pull requests should include a concise summary, testing notes (`adk run`, `uvicorn`, etc.), and links to demo recordings or Colab runs when applicable. Never commit API keys; confirm `.env` updates are reflected in documentation instead.
