# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Command-line interface for the RAG pipeline."""

import argparse
import json
import logging
import sys
from pathlib import Path

from rag_pipeline.models import Chunk, ChunkMetadata
from rag_pipeline.pipeline.bm25 import BM25Index
from rag_pipeline.pipeline.embed import create_embedder, create_vector_store, index_chunks
from rag_pipeline.pipeline.ingest import ingest_pdf
from rag_pipeline.pipeline.rerank import create_reranker
from rag_pipeline.query import RAGPipeline

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 512
_DEFAULT_OVERLAP = 64
_DEFAULT_TOP_K = 5
_DEFAULT_DB_PATH = ".rag_store"
_DEFAULT_CHUNKS_FILE = ".rag_chunks.json"


def _print_banner() -> None:
    """Print the startup banner."""
    from rag_pipeline import __version__

    print(f"\n  Taatal Digital | RAG Pipeline v{__version__}")
    print("  https://digital.taatal.com\n")


def main() -> None:
    """Entry point for the rag-pipeline CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    _print_banner()

    parser = argparse.ArgumentParser(
        prog="rag-pipeline",
        description="Production RAG pipeline with hybrid search and re-ranking",
    )
    subparsers = parser.add_subparsers(dest="command")

    _add_ingest_parser(subparsers)
    _add_query_parser(subparsers)

    args = parser.parse_args()

    if args.command == "ingest":
        _run_ingest(args)
    elif args.command == "query":
        _run_query(args)
    else:
        parser.print_help()
        sys.exit(1)


def _add_ingest_parser(subparsers) -> None:
    """Configure the 'ingest' subcommand."""
    ingest_parser = subparsers.add_parser("ingest", help="Ingest PDF documents")
    ingest_parser.add_argument("--input", type=Path, required=True, help="PDF file or directory")
    ingest_parser.add_argument(
        "--db", type=Path, default=Path(_DEFAULT_DB_PATH), help="Vector store path"
    )
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=_DEFAULT_CHUNK_SIZE,
        help="Maximum words per chunk",
    )
    ingest_parser.add_argument(
        "--overlap",
        type=int,
        default=_DEFAULT_OVERLAP,
        help="Word overlap between chunks",
    )


def _add_query_parser(subparsers) -> None:
    """Configure the 'query' subcommand."""
    query_parser = subparsers.add_parser("query", help="Query the knowledge base")
    query_parser.add_argument("question", type=str, help="Your question")
    query_parser.add_argument(
        "--db", type=Path, default=Path(_DEFAULT_DB_PATH), help="Vector store path"
    )
    query_parser.add_argument(
        "--chunks-file",
        type=Path,
        default=Path(_DEFAULT_CHUNKS_FILE),
        help="Path to the persisted chunks JSON",
    )
    query_parser.add_argument(
        "--top-k",
        type=int,
        default=_DEFAULT_TOP_K,
        help="Number of passages to retrieve",
    )


def _run_ingest(args: argparse.Namespace) -> None:
    """Execute the ingestion pipeline."""
    logger.info("Loading embedding model...")
    embedder = create_embedder()

    pdf_paths = _resolve_pdf_paths(args.input)
    if not pdf_paths:
        logger.error("No PDF files found at %s", args.input)
        sys.exit(1)

    logger.info("Found %d PDF file(s)", len(pdf_paths))

    all_chunks: list[Chunk] = []
    for pdf_path in pdf_paths:
        chunks = ingest_pdf(pdf_path, args.chunk_size, args.overlap)
        all_chunks.extend(chunks)
        logger.info("  %s: %d chunks", pdf_path.name, len(chunks))

    logger.info("Total chunks: %d. Embedding and indexing...", len(all_chunks))

    client = create_vector_store(str(args.db))
    index_chunks(all_chunks, embedder, client)

    _persist_chunks(all_chunks, Path(_DEFAULT_CHUNKS_FILE))

    logger.info("Done. Vector store: %s | Chunks: %s", args.db, _DEFAULT_CHUNKS_FILE)


def _run_query(args: argparse.Namespace) -> None:
    """Execute the query pipeline."""
    if not args.db.exists():
        logger.error("No vector store found. Run 'rag-pipeline ingest' first.")
        sys.exit(1)

    if not args.chunks_file.exists():
        logger.error("Chunks file not found at %s", args.chunks_file)
        sys.exit(1)

    logger.info("Loading models...")
    embedder = create_embedder()
    reranker = create_reranker()

    chunks = _load_chunks(args.chunks_file)
    bm25_index = BM25Index(chunks)
    client = create_vector_store(str(args.db))

    pipeline = RAGPipeline(
        embedder=embedder,
        reranker=reranker,
        bm25_index=bm25_index,
        chroma_client=client,
        top_k_rerank=args.top_k,
    )

    result = pipeline.query(args.question)

    print(f"\nQuestion: {args.question}\n")
    print(f"Answer:\n{result.answer}")
    print("\nSources:")
    for source in result.sources:
        print(f"  - {source['source']}, page {source['page']}")
    print(f"\nTokens: {result.input_tokens} input, {result.output_tokens} output")


def _resolve_pdf_paths(input_path: Path) -> list[Path]:
    """Resolve input to a list of PDF file paths."""
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        return [input_path]
    if input_path.is_dir():
        return sorted(input_path.glob("*.pdf"))
    return []


def _persist_chunks(chunks: list[Chunk], output_path: Path) -> None:
    """Serialize chunks to JSON for BM25 reconstruction at query time."""
    serializable = [
        {
            "text": chunk.text,
            "word_count": chunk.word_count,
            "metadata": {
                "source": chunk.metadata.source,
                "page": chunk.metadata.page,
                "chunk_index": chunk.metadata.chunk_index,
            },
        }
        for chunk in chunks
    ]
    output_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def _load_chunks(chunks_path: Path) -> list[Chunk]:
    """Deserialize chunks from the persisted JSON file."""
    raw = json.loads(chunks_path.read_text(encoding="utf-8"))
    return [
        Chunk(
            text=item["text"],
            word_count=item["word_count"],
            metadata=ChunkMetadata(
                source=item["metadata"]["source"],
                page=item["metadata"]["page"],
                chunk_index=item["metadata"]["chunk_index"],
            ),
        )
        for item in raw
    ]


if __name__ == "__main__":
    main()
