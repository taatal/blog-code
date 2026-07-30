# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Data models for the RAG pipeline."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChunkMetadata:
    """Metadata attached to each document chunk for provenance tracking."""

    source: str
    page: int
    chunk_index: int


@dataclass(frozen=True)
class Chunk:
    """A single text chunk extracted from a document."""

    text: str
    word_count: int
    metadata: ChunkMetadata


@dataclass(frozen=True)
class RetrievalResult:
    """A single result from a retrieval stage."""

    id: str
    text: str
    metadata: ChunkMetadata
    score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0


@dataclass(frozen=True)
class GenerationResult:
    """The output of the full RAG pipeline."""

    answer: str
    model: str
    sources: list[dict] = field(default_factory=list)
    context: list[RetrievalResult] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class EvaluationResult:
    """Aggregate retrieval quality metrics."""

    recall_at_k: float
    mrr: float
    k: int
    num_queries: int
