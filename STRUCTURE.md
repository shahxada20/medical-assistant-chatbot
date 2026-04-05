# Project Structure

```
medical-assistant-langchain-rag-flask/
├── .env                          # Environment variables (API keys, config)
├── .git/                         # Git version control
├── .gitignore                    # Git ignore patterns
├── .python-version               # Python version specification (3.14+)
├── .venv/                        # Virtual environment (uv-managed)
├── app.py                        # Flask application entry point (REST API routes)
├── main.py                       # CLI entry point for testing pipeline stages
├── setup.py                      # Project metadata and package configuration
├── pyproject.toml                # Project dependencies and metadata (uv)
├── requirements.txt              # Python dependencies (pip format)
├── uv.lock                       # uv lock file for reproducible installs
├── README.md                     # Project readme
├── commands.sh                   # Common commands reference (uv, git)
├── template.sh                   # Template/shell script utilities
│
├── Data/                         # Source medical data files
│   └── Medical_book.pdf          # Medical knowledge base PDF
│
├── src/                          # Core application logic
│   ├── __init__.py               # Package initializer
│   ├── helper.py                 # Helper/utility functions
│   └── prompt.py                 # Prompt templates for LLM
│
├── skills/                       # Skill/utility markdown files
│   └── review.md                 # Code review guidelines/skill
│
└── research/                     # Research notes and documentation
```

## Directory Descriptions

| Directory | Purpose |
|-----------|---------|
| `.venv/` | Virtual environment managed by uv |
| `Data/` | Raw medical PDF data for RAG ingestion |
| `src/` | Core application modules (prompts, helpers) |
| `skills/` | Markdown documentation for skills |
| `research/` | Research notes and exploration |

## File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Flask web server - handles HTTP requests and API endpoints |
| `main.py` | CLI script for testing and development |
| `setup.py` | Legacy package setup configuration |
| `pyproject.toml` | Modern Python project configuration (dependencies, metadata) |
| `requirements.txt` | Pip-compatible dependency list |
| `commands.sh` | Reference for common uv, git, flask, commands |
| `.env` | Environment variables (PINECONE_API_KEY, GROQ_API_KEY, etc.) |

## Tech Stack

- **Language**: Python 3.14+
- **LLM**: Groq Llama 4 / Ollama
- **Orchestration**: LangChain
- **Vector DB**: Pinecone
- **Backend**: Flask
- **Embeddings**: sentence-transformers
- **Environment**: uv

## Key Commands

```bash
# Environment
uv init                     # Initialize project
uv venv                     # Create virtual environment
source .venv/scripts/activate  # Activate venv (bash)
uv add <package>            # Add dependency
uv sync                     # Sync environment with lock file
uv pip list                 # List installed packages

# Git
git init
git add .
git commit -m "message"
git push -u origin main
```
