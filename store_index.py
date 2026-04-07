"""
Store index module - Handles Pinecone vector store creation and management.
Imports relevant functions from helper.py for embedding and vector DB operations.
"""

from pathlib import Path

from src.helper import (
    load_env_var,
    load_pdf,
    filter_documents,
    split_doc_into_chunks,
    load_embeddings_model,
    initialize_pinecone_client,
    pinecone_indexes,
    store_embeddings,
    get_existing_vector_store,
    DATA_DIR,
)


def build_index(data_path=None, index_name="medical-assistant"):
    """
    Build the complete Pinecone index from PDF documents.

    This is the main entry point for populating the vector index.

    Args:
        data_path: Optional path to PDF directory (defaults to DATA_DIR)
        index_name: Name of the Pinecone index

    Returns:
        Dictionary with index info and vector store:
        - index_name: Name of the created/existing index
        - vector_store: PineconeVectorStore instance
        - document_count: Number of documents processed
        - chunk_count: Number of chunks created
    """
    # Load environment
    load_env_var()

    # Determine data directory
    data_directory = Path(data_path) if data_path else DATA_DIR

    # ETL Pipeline
    documents = load_pdf(str(data_directory))
    minimal_docs = filter_documents(documents)
    chunks = split_doc_into_chunks(minimal_docs)

    # Load embeddings
    embedding = load_embeddings_model()

    # Initialize Pinecone
    pc = initialize_pinecone_client()

    # Create or get index
    created_index_name = pinecone_indexes(pc, index_name=index_name)

    # Store embeddings
    vector_store = store_embeddings(chunks, embedding, created_index_name)

    return {
        "index_name": created_index_name,
        "vector_store": vector_store,
        "document_count": len(documents),
        "chunk_count": len(chunks)
    }


def get_vector_store(index_name="medical-assistant"):
    """
    Get existing vector store for querying.

    Args:
        index_name: Name of the Pinecone index

    Returns:
        PineconeVectorStore instance
    """
    embedding = load_embeddings_model()
    return get_existing_vector_store(embedding, index_name)


if __name__ == "__main__":
    # CLI entry point for building the index
    print("Building Pinecone index...")
    result = build_index()
    print(f"Index '{result['index_name']}' created/updated.")
    print(f"Processed {result['document_count']} documents into {result['chunk_count']} chunks.")
