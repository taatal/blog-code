# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""RAG pipeline orchestrator combining all retrieval and generation stages."""

import logging

import chromadb
from sentence_transformers import CrossEncoder, SentenceTransformer

from rag_pipeline.models import GenerationResult, RetrievalResult
from rag_pipeline.pipeline.bm25 import BM25Index
from rag_pipeline.pipeline.embed import search_vectors
from rag_pipeline.pipeline.fusion import reciprocal_rank_fusion
from rag_pipeline.pipeline.generate import generate_answer
from rag_pipeline.pipeline.rerank import rerank

logger = logging.getLogger(__name__)

_DEFAULT_RETRIEVE_K = 20
_DEFAULT_RERANK_K = 5


class RAGPipeline:
    """Full retrieval-augmented generation pipeline.

    Combines vector search, BM25 keyword search, reciprocal rank fusion,
    cross-encoder re-ranking, and LLM answer generation.
    """

    def __init__(
        self,
        embedder: SentenceTransformer,
        reranker: CrossEncoder,
        bm25_index: BM25Index,
        chroma_client: chromadb.ClientAPI,
        collection_name: str = "documents",
        top_k_retrieve: int = _DEFAULT_RETRIEVE_K,
        top_k_rerank: int = _DEFAULT_RERANK_K,
    ) -> None:
        """Initialize the RAG pipeline with all required components.

        Args:
            embedder: Sentence transformer for query/document encoding.
            reranker: Cross-encoder model for precision re-ranking.
            bm25_index: Pre-built BM25 keyword index.
            chroma_client: ChromaDB client with indexed vectors.
            collection_name: ChromaDB collection to query.
            top_k_retrieve: Candidates to retrieve from each method.
            top_k_rerank: Final passages to pass to the LLM.
        """
        self._embedder = embedder
        self._reranker = reranker
        self._bm25 = bm25_index
        self._chroma = chroma_client
        self._collection_name = collection_name
        self._top_k_retrieve = top_k_retrieve
        self._top_k_rerank = top_k_rerank

    def retrieve(self, query: str) -> list[RetrievalResult]:
        """Retrieve and re-rank relevant passages for a query.

        Runs vector search and BM25 in parallel, merges via RRF,
        then re-ranks the top candidates with the cross-encoder.

        Args:
            query: The user's question.

        Returns:
            Top-K re-ranked retrieval results.
        """
        vector_results = search_vectors(
            query,
            self._embedder,
            self._chroma,
            self._collection_name,
            self._top_k_retrieve,
        )

        bm25_results = self._bm25.search(query, self._top_k_retrieve)

        fused = reciprocal_rank_fusion([vector_results, bm25_results])

        reranked = rerank(
            query,
            fused[: self._top_k_retrieve],
            self._reranker,
            self._top_k_rerank,
        )

        logger.info(
            "Retrieved %d results (vector=%d, bm25=%d, fused=%d)",
            len(reranked),
            len(vector_results),
            len(bm25_results),
            len(fused),
        )
        return reranked

    def query(self, question: str) -> GenerationResult:
        """Full RAG pipeline: retrieve context then generate answer.

        Args:
            question: The user's question.

        Returns:
            GenerationResult with answer, sources, and token usage.
        """
        context = self.retrieve(question)

        if not context:
            return GenerationResult(
                answer="No relevant passages found for this question.",
                model="",
                sources=[],
                context=[],
            )

        return generate_answer(question, context)
