# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 4: Reciprocal Rank Fusion for merging ranked lists.

Reference:
    Cormack, G.V., Clarke, C.L.A., and Buettcher, S. (2009).
    "Reciprocal Rank Fusion outperforms Condorcet and individual
    Rank Learning Methods." SIGIR '09, pp. 758-759. ACM.
"""

from rag_pipeline.models import RetrievalResult

# Default constant from the original SIGIR 2009 paper.
# Also the hardcoded default in Elasticsearch (v8.8+), Weaviate (v1.20+),
# and LangChain's EnsembleRetriever.
RRF_K = 60


def reciprocal_rank_fusion(
    ranked_lists: list[list[RetrievalResult]],
    k: int = RRF_K,
) -> list[RetrievalResult]:
    """Merge multiple ranked lists using Reciprocal Rank Fusion.

    Formula: RRF(d) = sum(1 / (k + rank_i(d))) for each list i

    Args:
        ranked_lists: Two or more ranked result lists to merge.
        k: Smoothing constant (default 60 per the original paper).

    Returns:
        Single merged list sorted by descending RRF score.
    """
    scores: dict[str, float] = {}
    docs: dict[str, RetrievalResult] = {}

    for ranked_list in ranked_lists:
        for rank, result in enumerate(ranked_list, start=1):
            scores[result.id] = scores.get(result.id, 0.0) + 1.0 / (k + rank)
            if result.id not in docs:
                docs[result.id] = result

    fused = [
        RetrievalResult(
            id=doc_id,
            text=docs[doc_id].text,
            metadata=docs[doc_id].metadata,
            score=docs[doc_id].score,
            rrf_score=rrf_score,
        )
        for doc_id, rrf_score in scores.items()
    ]

    fused.sort(key=_by_rrf_score, reverse=True)
    return fused


def _by_rrf_score(result: RetrievalResult) -> float:
    """Sort key for results by RRF score."""
    return result.rrf_score
