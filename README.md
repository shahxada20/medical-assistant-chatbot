# MediAssist: Medical RAG Chatbot

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![Pinecone](https://img.shields.io/badge/Pinecone-272727?style=for-the-badge&logo=pinecone&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-f55036?style=for-the-badge&logo=groq&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

# Project Overview:
This project is an AI chatbot designed to answer clinical queries. It features a RAG system with a Flask-based web interface to interact with the Retrieval pipeline, which pulls context from a vector database.

# Objective: 🚀
I built MediAssist to tackle the "hallucination" problem in medical AI. Instead of letting an LLM guess, this system forces the model to look at verified medical literature (Gale Encyclopedia of Medicine) before speaking. 

Its design showcases an end-to-end AI Engineering pipeline: **from raw PDF ingestion** to **embedding context into vector database** and serving clinical queries via a **live and responsive web-based chat interface**.


# Tech Stack: 🛠

| Component | Technology | Configuration | Description |
|-----------|------------|------------------------|---------------|
| **Embeddings** | HuggingFace | sentence-transformers/all-MiniLM-L6-v2 | a lightweight model that runs efficiently on local hardware during development |
| **LLM Provider** | Groq API | Llama 4 Scout (17B) | providing a real-time chat experience |
| **Vector Database** | Pinecone | Serverless, 384 dimensions, cosine similarity | chosen for its ease of scaling without managing local infrastructure |
| **Orchestration** | LangChain | LCEL | using LCEL (LangChain Expression Language) for modular, readable chains |
| **Backend Framework** | Flask 3.1 | REST API | A lightweight framework for RESTful API server & template rendering |
| **Containerization** | Docker | Planned for production deployment | - |

# How it Works: 📖

1. **Data Ingestion (The ETL Pipeline)** ─ We don't just dump text. The process is systematic:
   - **Extract**: Raw PDFs are parsed using PyPDF.
   - **Chunking**: I used a 500-character chunk size and 50-character overlap. This balance ensures we don't lose the medical context between snippets.
   - **Vectorizing**: Text is converted into 384-dimensional vector embeddings.
   - **Upserting**: These embeddings are stored in a Pinecone index named medical-assistant.
     
2. **The Retrieval Loop** ─ When you ask a question:
   - The system creates a vector for your query ─ clinical entities (symptoms, conditions, medications).
   - It semantically searches Pinecone for the Top 3 most relevant matches (k=3).
   - It injects those matches into a specialized Clinical System Prompt.
   - The LLM generates a response or admits it doesn't know if the context is missing.
    

# Local Setup: 💻
If you're running this on a machine with limited storage, I recommend using ``uv`` to keep your environment clean.

#### Prerequisites
- Python 3.12+
- uv
#### Setup Keys
Create a .env file in the project root and add:
- [Pinecone](https://www.pinecone.io/) API Key
- [Groq](https://groq.com/) API KEY
- [HuggingFace](https://huggingface.co/) API Key


# Quick Start: ⚡
#### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/medical-assistant-chatbot.git
```
#### 2. Set up a virtual environment with uv
```bash
uv venv
.venv\Scripts\activate
uv sync
```
#### 3. Running the Project
Place your PDFs in the Data/ folder and run:
```bash
python store_index.py
```
This will take a few minutes, depending on the document size.
This will:
- Load PDFs from the `Data/` directory
- Split documents into chunks
- Generate embeddings
- Store vectors in Pinecone

#### 4. Launch the Chatbot
```bash
python app.py
```
Navigate to http://localhost:5000 to start chatting.


# Future Improvements: ⚙
- **AWS Deployment**: Moving the Flask app to an EC2 instance via docker image with an S3 bucket for document storage.
  
- **Frontend**: I’m working on a frontend redesign that supports real-time token streaming. This will eliminate the wait time for the user, providing a much smoother, modern chat experience.


#### **Deployment**
- [ ] **AWS Deployment**: Containerized deployment on ECS with ALB routing
- [ ] **CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- [ ] **Dockerfile**: Multi-stage build for production image

#### **Enhancement**
- [ ] **UI**: Enhance Frontend UI
- [ ] **Expanded Medical Datasets**:
  - PubMed Central Open Access subset
  - MIMIC-III clinical notes (de-identified)
  - DrugBank pharmacological data
- [ ] **Health Check Endpoint**: Add `/api/health` for monitoring
- [ ] **Ingestion Endpoint**: Add `/api/ingest` for dynamic PDF upload

#### **Infrastructure Upgradation**
- [ ] **Multi-Model Support**: Ollama integration for local LLM fallback
- [ ] **Caching Layer**: Redis for query result caching
- [ ] **Evaluation Framework**: RAGAS metrics for retrieval/generation quality
- [ ] **Observability**: LangSmith tracing for pipeline debugging
- [ ] **Authorization**: JWT-based API authentication


# Project Structure 📁
```
medical-assistant-chatbot/
├── .env                          # Environment variables (API keys)
├── .gitignore                    # Git ignore patterns
├── .python-version               # Python version specification (3.12+)
├── app.py                        # Flask application entry point
├── main.py                       # CLI placeholder
├── pyproject.toml                # Project dependencies (uv)
├── requirements.txt              # Python dependencies (pip format)
├── uv.lock                       # Dependency lock file
├── README.md                     # Project documentation
├── store_index.py                # ETL pipeline CLI - builds Pinecone index
├── Data/                         # Source medical PDFs
│   └── Medical_book.pdf
├── templates/                    # Flask templates
│   └── chat.html                 # Chat interface
├── static/                       # Static assets
│   └── style.css                 # CSS styling
├── src/                          # Core application logic
│   ├── __init__.py
│   ├── helper.py                 # modular code for ETL pipeline + RAG utilities
│   └── prompt.py                 # Clinical system prompts
└── notebooks/                    # Jupyter notebooks for experimentation
    └── trials.ipynb
```

**MediAssist** - Clinical AI Infrastructure for Evidence-Based Medical Information Retrieval

