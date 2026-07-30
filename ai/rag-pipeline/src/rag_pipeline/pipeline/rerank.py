# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 5: Cross-encoder re-ranking for precision scoring."""

from sentence_transformers import CrossEncoder

from rag_pipeline.models import RetrievalResult

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


def create_reranker() -> CrossEncoder:
    """Load the cross-encoder re-ranking model. Downloads on first use (~90MB)."""
    return CrossEncoder(RERANKER_MODEL)


def rerank(
    query: str,
    candidates: list[RetrievalResult],
    reranker: CrossEncoder,
    top_k: int = 5,
) -> list[RetrievalResult]:
    """Re-rank candidates using a cross-encoder model.

    Cross-encoders process query and document together, producing
    more accurate relevance scores than bi-encoder similarity.
    Only applied to the top candidates from fusion for efficiency.

    Args:
        query: The search query text.
        candidates: Pre-filtered candidate results to re-score.
        reranker: The cross-encoder model instance.
        top_k: Number of top results to return after re-ranking.

    Returns:
        Top-K results sorted by descending cross-encoder score.
    """
    if not candidates:
        return []

    pairs = [(query, result.text) for result in candidates]
    scores = reranker.predict(pairs)

    reranked = [
        RetrievalResult(
            id=candidates[i].id,
            text=candidates[i].text,
            metadata=candidates[i].metadata,
            score=candidates[i].score,
            rrf_score=candidates[i].rrf_score,
            rerank_score=float(scores[i]),
        )
        for i in range(len(candidates))
    ]

    reranked.sort(key=_by_rerank_score, reverse=True)
    return reranked[:top_k]


def _by_rerank_score(result: RetrievalResult) -> float:
    """Sort key for results by re-rank score."""
    return result.rerank_score
