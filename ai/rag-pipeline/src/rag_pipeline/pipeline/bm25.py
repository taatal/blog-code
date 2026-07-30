# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 3: BM25 keyword search index."""

from rank_bm25 import BM25Okapi

from rag_pipeline.models import Chunk, RetrievalResult
from rag_pipeline.pipeline.embed import build_chunk_id


class BM25Index:
    """BM25 keyword index over a chunk corpus.

    BM25Okapi requires the full tokenized corpus at construction time.
    There is no incremental add. To update the index, reconstruct it
    with the complete chunk list.
    """

    def __init__(self, chunks: list[Chunk]) -> None:
        """Initialize the BM25 index from a list of chunks.

        Args:
            chunks: The full document chunk corpus.
        """
        self._chunks = chunks
        tokenized = [self._tokenize(chunk.text) for chunk in chunks]
        self._index = BM25Okapi(tokenized)

    def search(self, query: str, n_results: int = 20) -> list[RetrievalResult]:
        """Search the BM25 index and return ranked results.

        Args:
            query: The search query text.
            n_results: Maximum number of results to return.

        Returns:
            List of RetrievalResult objects sorted by descending BM25 score.
        """
        tokenized_query = self._tokenize(query)
        scores = self._index.get_scores(tokenized_query)

        scored: list[RetrievalResult] = []
        for i, score in enumerate(scores):
            if score > 0:
                chunk = self._chunks[i]
                scored.append(
                    RetrievalResult(
                        id=build_chunk_id(chunk.metadata),
                        text=chunk.text,
                        metadata=chunk.metadata,
                        score=float(score),
                    )
                )

        scored.sort(key=_by_score, reverse=True)
        return scored[:n_results]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Whitespace tokenization with lowercasing."""
        return text.lower().split()


def _by_score(result: RetrievalResult) -> float:
    """Sort key for retrieval results by score."""
    return result.score
