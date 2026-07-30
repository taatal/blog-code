# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Unit tests for the retrieval pipeline logic.

Tests verify pure-logic modules (fusion, evaluation, BM25, chunking)
without requiring model downloads or API keys.
"""

from rag_pipeline.models import Chunk, ChunkMetadata, RetrievalResult
from rag_pipeline.pipeline.bm25 import BM25Index
from rag_pipeline.pipeline.evaluate import mean_reciprocal_rank, recall_at_k
from rag_pipeline.pipeline.fusion import reciprocal_rank_fusion
from rag_pipeline.pipeline.ingest import chunk_text


def _make_result(doc_id: str, text: str = "", score: float = 0.0) -> RetrievalResult:
    """Helper to create a RetrievalResult for testing."""
    return RetrievalResult(
        id=doc_id,
        text=text,
        metadata=ChunkMetadata(source="test.pdf", page=1, chunk_index=0),
        score=score,
    )


def _make_chunk(text: str, page: int, chunk_index: int = 0) -> Chunk:
    """Helper to create a Chunk for testing."""
    return Chunk(
        text=text,
        word_count=len(text.split()),
        metadata=ChunkMetadata(source="t.pdf", page=page, chunk_index=chunk_index),
    )


class TestReciprocalRankFusion:
    """Tests for the RRF merge algorithm."""

    def test_ranks_by_combined_score(self) -> None:
        list1 = [_make_result("a"), _make_result("b"), _make_result("c")]
        list2 = [_make_result("b"), _make_result("d"), _make_result("a")]

        fused = reciprocal_rank_fusion([list1, list2], k=60)

        assert fused[0].id == "b"
        assert fused[1].id == "a"
        assert fused[0].rrf_score > fused[1].rrf_score

    def test_single_list_preserves_order(self) -> None:
        docs = [_make_result("x"), _make_result("y")]
        fused = reciprocal_rank_fusion([docs], k=60)

        assert fused[0].id == "x"
        assert fused[1].id == "y"

    def test_empty_lists_returns_empty(self) -> None:
        fused = reciprocal_rank_fusion([[], []])
        assert fused == []


class TestRecallAtK:
    """Tests for the Recall@K evaluation metric."""

    def test_all_relevant_found(self) -> None:
        retrieved = ["a", "b", "c", "d", "e"]
        relevant = ["b", "d"]
        assert recall_at_k(retrieved, relevant, k=5) == 1.0

    def test_partial_recall(self) -> None:
        retrieved = ["a", "b", "c", "d", "e"]
        relevant = ["b", "f"]
        assert recall_at_k(retrieved, relevant, k=5) == 0.5

    def test_no_relevant_found(self) -> None:
        retrieved = ["a", "b", "c"]
        relevant = ["x", "y"]
        assert recall_at_k(retrieved, relevant, k=3) == 0.0

    def test_empty_relevant_returns_zero(self) -> None:
        assert recall_at_k(["a", "b"], [], k=5) == 0.0


class TestMeanReciprocalRank:
    """Tests for the MRR evaluation metric."""

    def test_first_position(self) -> None:
        assert mean_reciprocal_rank(["a", "b", "c"], ["a"]) == 1.0

    def test_second_position(self) -> None:
        assert mean_reciprocal_rank(["a", "b", "c"], ["b"]) == 0.5

    def test_third_position(self) -> None:
        result = mean_reciprocal_rank(["a", "b", "c"], ["c"])
        assert abs(result - 1.0 / 3) < 1e-9

    def test_not_found(self) -> None:
        assert mean_reciprocal_rank(["a", "b", "c"], ["d"]) == 0.0


class TestBM25Index:
    """Tests for the BM25 keyword search index."""

    def test_exact_term_match_ranks_first(self) -> None:
        chunks = [
            _make_chunk(
                "AEM Cloud Service uses immutable deployments",
                page=1,
            ),
            _make_chunk(
                "The Firefly API has a default rate limit RPM",
                page=2,
            ),
            _make_chunk(
                "OAuth authentication requires no user interaction",
                page=3,
            ),
            _make_chunk(
                "Vector databases store embeddings for search",
                page=4,
            ),
        ]
        index = BM25Index(chunks)
        results = index.search("RPM rate limit Firefly")

        assert len(results) > 0
        assert results[0].metadata.page == 2

    def test_empty_query_returns_empty(self) -> None:
        chunks = [_make_chunk("Some content here", page=1)]
        index = BM25Index(chunks)
        results = index.search("")
        assert results == []


class TestChunking:
    """Tests for recursive text chunking."""

    def test_respects_paragraph_boundaries(self) -> None:
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunk_text(text, chunk_size=5, overlap=1)
        assert len(chunks) >= 2

    def test_single_small_text_not_split(self) -> None:
        text = "Short text here."
        chunks = chunk_text(text, chunk_size=512, overlap=64)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "Short text here."

    def test_empty_text_returns_empty(self) -> None:
        chunks = chunk_text("", chunk_size=512, overlap=64)
        assert chunks == []

    def test_whitespace_only_returns_empty(self) -> None:
        chunks = chunk_text("   \n\n   ", chunk_size=512, overlap=64)
        assert chunks == []
