"""
Helper module for medical RAG chatbot.
ETL pipeline for medical knowledge: Load -> Transform -> Embed -> Store -> Query.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from prompt import llm_system_prompt

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pinecone import Pinecone, ServerlessSpec


# Path configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "Data"

# Default configurations
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_INDEX_NAME = "medical-assistant"
DEFAULT_INDEX_DIMENSION = 384


def _build_rag_pipeline(retriever, llm, prompt):
    """Private utility: Build RAG chain from components using LCEL."""
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def load_env_var():
    """Load and validate required environment variables."""
    load_dotenv()
    required_vars = ["PINECONE_API_KEY", "GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    return {var: os.getenv(var, "") for var in required_vars}


def load_pdf(data_path=None):
    """Load all PDF files from directory (defaults to DATA_DIR)."""
    data_dir = Path(data_path) if data_path else DATA_DIR

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    if not data_dir.is_dir():
        raise ValueError(f"Path is not a directory: {data_dir}")

    pdf_files = list(data_dir.glob("*.pdf"))
    if not pdf_files:
        raise ValueError(f"No PDF files found in: {data_dir}")

    loader = DirectoryLoader(
        str(data_dir),
        glob="*.pdf",
        show_progress=True,
        loader_cls=PyPDFLoader, #type:ignore
        use_multithreading=True
    )

    documents = loader.load()
    if not documents:
        raise RuntimeError("Document loader returned empty results.")

    return documents


def filter_documents(docs):
    """Filter documents to keep only page content and source metadata."""
    return [
        Document(page_content=doc.page_content, metadata={"source": doc.metadata.get("source", "unknown")})
        for doc in docs
    ]


def split_doc_into_chunks(minimal_docs, chunk_size=500, chunk_overlap=50):
    """Split documents into smaller chunks for embedding."""
    if not minimal_docs:
        raise ValueError("Cannot split empty document list.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        strip_whitespace=True
    )

    text_chunks = text_splitter.split_documents(minimal_docs)
    if not text_chunks:
        raise RuntimeError("Text splitting resulted in empty chunks.")

    return text_chunks


def load_embeddings_model(model_name=DEFAULT_EMBEDDING_MODEL):
    """Download and initialize HuggingFace embeddings model."""
    return HuggingFaceEmbeddings(model_name=model_name)


def initialize_pinecone_client(api_key=None):
    """Initialize Pinecone vector database client."""
    pinecone_api_key = api_key or os.getenv("PINECONE_API_KEY")

    if not pinecone_api_key:
        raise ValueError("Pinecone API key not provided. Set PINECONE_API_KEY in .env file.")

    return Pinecone(api_key=pinecone_api_key)


def pinecone_indexes(
    pc,
    index_name=DEFAULT_INDEX_NAME,
    dimension=DEFAULT_INDEX_DIMENSION,
    metric="cosine",
    cloud="aws",
    region="us-east-1"
):
    """Create Pinecone index if it doesn't exist."""
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud=cloud, region=region)
        )
    return index_name


def store_embeddings(documents, embedding, index_name):
    """Embed documents and store them in Pinecone vector store."""
    if not documents:
        raise ValueError("Cannot create vector store from empty document list.")

    return PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embedding,
        index_name=index_name
    )


def get_existing_vector_store(embedding, index_name):
    """Connect to existing Pinecone vector store."""
    return PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embedding
    )


def initialize_groq_llm(model_name=DEFAULT_LLM_MODEL, temperature=0, api_key=None):
    """Initialize Groq LLM client for text generation."""
    groq_api_key = api_key or os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError("Groq API key not provided. Set GROQ_API_KEY in .env file.")

    return ChatGroq(model=model_name, temperature=temperature)


def system_prompt():
    """Create medical-specific system prompt template."""
    system_prompt = llm_system_prompt
    return ChatPromptTemplate.from_template(system_prompt)


def build_rag_chain(vector_store, llm, prompt, k=3):
    """Build RAG chain using LangChain Expression Language (LCEL)."""
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return _build_rag_pipeline(retriever, llm, prompt)


def create_rag_chain_with_components(vector_store, llm, prompt, k=3):
    """Build RAG chain and return both retriever and chain."""
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    chain = _build_rag_pipeline(retriever, llm, prompt)
    return {"retriever": retriever, "chain": chain}


def initialize_rag_pipeline(data_path=None):
    """Initialize complete RAG pipeline from PDF ingestion to RAG chain."""
    env_vars = load_env_var()

    data_directory = Path(data_path) if data_path else DATA_DIR

    documents = load_pdf(str(data_directory))
    minimal_docs = filter_documents(documents)
    chunks = split_doc_into_chunks(minimal_docs)

    embedding = load_embeddings_model()

    pc = initialize_pinecone_client()
    index_name = pinecone_indexes(pc)
    vector_store = store_embeddings(chunks, embedding, index_name)

    llm = initialize_groq_llm()
    prompt = system_prompt()
    rag_chain = build_rag_chain(vector_store, llm, prompt)

    return {
        "env_vars": env_vars,
        "documents": documents,
        "minimal_docs": minimal_docs,
        "chunks": chunks,
        "embedding": embedding,
        "pc": pc,
        "index_name": index_name,
        "vector_store": vector_store,
        "llm": llm,
        "prompt": prompt,
        "rag_chain": rag_chain
    }
