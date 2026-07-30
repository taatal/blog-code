# RAG Pipeline

Production RAG pipeline with hybrid search, re-ranking, and retrieval evaluation.

**Blog post:** [Build a RAG Pipeline That Actually Works](https://digital.taatal.com/blogs/build-rag-pipeline-that-actually-works)

## What It Does

- Ingests PDF documents and splits them into semantically coherent chunks
- Retrieves using both vector search (ChromaDB) and BM25 keyword matching
- Merges results with Reciprocal Rank Fusion (Cormack et al., SIGIR 2009)
- Re-ranks candidates with a cross-encoder model for precision
- Generates grounded answers with source citations (Claude or OpenAI)
- Includes retrieval evaluation with Recall@K and MRR metrics

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

export ANTHROPIC_API_KEY="sk-ant-..."
# Or: export LLM_PROVIDER=openai && export OPENAI_API_KEY="sk-..."

rag-pipeline ingest --input ./documents
rag-pipeline query "Your question here"
```

## Performance

| Stage | Latency |
|-------|---------|
| Vector search | ~15ms |
| BM25 search | ~3ms |
| Reciprocal Rank Fusion | <1ms |
| Cross-encoder re-rank | ~11ms |
| Answer generation (LLM) | ~2-4s |

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Author

Built by [Taatal Digital](https://digital.taatal.com) Engineering.

## License

MIT
