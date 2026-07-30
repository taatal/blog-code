# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 2: Embedding generation and ChromaDB vector storage."""

import logging

import chromadb
from sentence_transformers import SentenceTransformer

from rag_pipeline.models import Chunk, ChunkMetadata, RetrievalResult

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
_BATCH_SIZE = 100


def create_embedder() -> SentenceTransformer:
    """Load the embedding model. Downloads on first use (~130MB)."""
    return SentenceTransformer(EMBEDDING_MODEL)


def create_vector_store(persist_dir: str) -> chromadb.ClientAPI:
    """Create or open a persistent ChromaDB instance.

    Args:
        persist_dir: Directory path for ChromaDB storage.
    """
    return chromadb.PersistentClient(path=persist_dir)


def build_chunk_id(metadata: ChunkMetadata) -> str:
    """Generate a deterministic ID from chunk metadata."""
    return f"{metadata.source}_p{metadata.page}_c{metadata.chunk_index}"


def index_chunks(
    chunks: list[Chunk],
    embedder: SentenceTransformer,
    client: chromadb.ClientAPI,
    collection_name: str = "documents",
) -> None:
    """Embed chunks and store them in ChromaDB.

    Args:
        chunks: List of Chunk objects to index.
        embedder: The sentence transformer model for encoding.
        client: ChromaDB client instance.
        collection_name: Name of the ChromaDB collection.
    """
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    ids = [build_chunk_id(chunk.metadata) for chunk in chunks]
    metadatas = [
        {
            "source": c.metadata.source,
            "page": c.metadata.page,
            "chunk_index": c.metadata.chunk_index,
        }
        for c in chunks
    ]

    for i in range(0, len(texts), _BATCH_SIZE):
        end = min(i + _BATCH_SIZE, len(texts))
        collection.add(
            ids=ids[i:end],
            documents=texts[i:end],
            embeddings=embeddings[i:end].tolist(),
            metadatas=metadatas[i:end],
        )

    logger.info("Indexed %d chunks into collection '%s'", len(chunks), collection_name)


def search_vectors(
    query: str,
    embedder: SentenceTransformer,
    client: chromadb.ClientAPI,
    collection_name: str = "documents",
    n_results: int = 20,
) -> list[RetrievalResult]:
    """Search the vector store and return ranked results.

    Args:
        query: The search query text.
        embedder: Model used to encode the query.
        client: ChromaDB client instance.
        collection_name: Name of the collection to search.
        n_results: Maximum number of results to return.

    Returns:
        List of RetrievalResult objects sorted by descending similarity.
    """
    collection = client.get_collection(name=collection_name)
    query_embedding = embedder.encode([query], normalize_embeddings=True)

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    ranked: list[RetrievalResult] = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        ranked.append(
            RetrievalResult(
                id=results["ids"][0][i],
                text=results["documents"][0][i],
                metadata=ChunkMetadata(
                    source=meta["source"],
                    page=meta["page"],
                    chunk_index=meta["chunk_index"],
                ),
                score=1.0 - results["distances"][0][i],
            )
        )

    return ranked
