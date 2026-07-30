# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 6: Grounded answer generation with source citations.

Supports Anthropic (default) and OpenAI providers via LLM_PROVIDER env var.
"""

import logging
import os

from rag_pipeline.models import GenerationResult, RetrievalResult

logger = logging.getLogger(__name__)

_DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6-20250514"
_DEFAULT_OPENAI_MODEL = "gpt-4o"
_MAX_TOKENS = 1024

SYSTEM_PROMPT = (
    "You are a precise research assistant. Answer the user's question "
    "using ONLY the provided context passages. For each claim you make, "
    "cite the source in brackets like [Source: filename, page N]. "
    "If the context does not contain enough information to answer "
    "the question, say so explicitly. Do not speculate or add information "
    "beyond what the passages contain."
)


def generate_answer(
    query: str,
    context_chunks: list[RetrievalResult],
    model: str | None = None,
) -> GenerationResult:
    """Generate a grounded answer using retrieved context.

    Routes to the appropriate LLM provider based on the LLM_PROVIDER
    environment variable. Defaults to Anthropic.

    Args:
        query: The user's question.
        context_chunks: Retrieved passages to use as context.
        model: Optional model override. Defaults per provider.

    Returns:
        GenerationResult with answer, sources, and token usage.
    """
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    context = _format_context(context_chunks)

    if provider == "openai":
        return _generate_openai(query, context, context_chunks, model)
    return _generate_anthropic(query, context, context_chunks, model)


def _generate_anthropic(
    query: str,
    context: str,
    context_chunks: list[RetrievalResult],
    model: str | None,
) -> GenerationResult:
    """Generate answer using Anthropic's Claude API."""
    import anthropic

    resolved_model = model or _DEFAULT_ANTHROPIC_MODEL
    client = anthropic.Anthropic(
        default_headers={"User-Agent": "taatal-rag-pipeline/0.1.0 (digital.taatal.com)"},
    )

    response = client.messages.create(
        model=resolved_model,
        max_tokens=_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Context passages:\n\n{context}\n\n---\n\nQuestion: {query}",
            }
        ],
    )

    logger.info("Generated answer via Anthropic (%s)", resolved_model)

    return GenerationResult(
        answer=response.content[0].text,
        model=resolved_model,
        sources=_extract_sources(context_chunks),
        context=context_chunks,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def _generate_openai(
    query: str,
    context: str,
    context_chunks: list[RetrievalResult],
    model: str | None,
) -> GenerationResult:
    """Generate answer using OpenAI's Chat Completions API."""
    from openai import OpenAI

    resolved_model = model or _DEFAULT_OPENAI_MODEL
    client = OpenAI(
        default_headers={"User-Agent": "taatal-rag-pipeline/0.1.0 (digital.taatal.com)"},
    )

    response = client.chat.completions.create(
        model=resolved_model,
        max_tokens=_MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context passages:\n\n{context}\n\n---\n\nQuestion: {query}",
            },
        ],
    )

    usage = response.usage
    logger.info("Generated answer via OpenAI (%s)", resolved_model)

    return GenerationResult(
        answer=response.choices[0].message.content or "",
        model=resolved_model,
        sources=_extract_sources(context_chunks),
        context=context_chunks,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
    )


def _extract_sources(chunks: list[RetrievalResult]) -> list[dict]:
    """Extract source references from retrieval results."""
    return [{"source": chunk.metadata.source, "page": chunk.metadata.page} for chunk in chunks]


def _format_context(chunks: list[RetrievalResult]) -> str:
    """Format retrieved chunks as numbered passages with source attribution."""
    passages = []
    for i, chunk in enumerate(chunks, start=1):
        header = f"[Passage {i} | Source: {chunk.metadata.source}, page {chunk.metadata.page}]"
        passages.append(f"{header}\n{chunk.text}")
    return "\n\n".join(passages)
