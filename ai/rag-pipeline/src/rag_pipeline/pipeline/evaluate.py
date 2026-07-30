# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Retrieval quality evaluation with Recall@K and Mean Reciprocal Rank."""

from collections.abc import Callable

from rag_pipeline.models import EvaluationResult, RetrievalResult


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: list[str],
    k: int = 5,
) -> float:
    """Compute Recall@K: fraction of relevant documents found in top K results.

    Args:
        retrieved_ids: Ordered list of retrieved document IDs.
        relevant_ids: List of IDs that are known to be relevant.
        k: Number of top results to consider.

    Returns:
        Recall score between 0.0 and 1.0.
    """
    if not relevant_ids:
        return 0.0

    top_k = set(retrieved_ids[:k])
    relevant = set(relevant_ids)
    found = top_k.intersection(relevant)
    return len(found) / len(relevant)


def mean_reciprocal_rank(
    retrieved_ids: list[str],
    relevant_ids: list[str],
) -> float:
    """Compute MRR: reciprocal of the rank of the first relevant result.

    Args:
        retrieved_ids: Ordered list of retrieved document IDs.
        relevant_ids: List of IDs that are known to be relevant.

    Returns:
        MRR score between 0.0 and 1.0. Returns 0.0 if no relevant
        document is found in the retrieved list.
    """
    relevant = set(relevant_ids)

    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant:
            return 1.0 / rank

    return 0.0


def evaluate_retrieval(
    queries: list[dict],
    retrieval_fn: Callable[[str], list[RetrievalResult]],
    k: int = 5,
) -> EvaluationResult:
    """Run evaluation over a test set and compute aggregate metrics.

    Args:
        queries: Test set where each entry has 'query' (str) and
            'relevant_ids' (list of chunk IDs that contain the answer).
        retrieval_fn: Function that takes a query string and returns
            a list of RetrievalResult objects.
        k: Number of top results to evaluate against.

    Returns:
        EvaluationResult with aggregate recall@K and MRR.
    """
    recall_scores: list[float] = []
    mrr_scores: list[float] = []

    for test_case in queries:
        results = retrieval_fn(test_case["query"])
        retrieved_ids = [r.id for r in results]

        recall_scores.append(recall_at_k(retrieved_ids, test_case["relevant_ids"], k))
        mrr_scores.append(mean_reciprocal_rank(retrieved_ids, test_case["relevant_ids"]))

    num_queries = len(queries)
    return EvaluationResult(
        recall_at_k=sum(recall_scores) / num_queries if num_queries else 0.0,
        mrr=sum(mrr_scores) / num_queries if num_queries else 0.0,
        k=k,
        num_queries=num_queries,
    )
