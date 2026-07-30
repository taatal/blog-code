# Blog Code

Companion code for blog posts on [digital.taatal.com](https://digital.taatal.com). Production-ready implementations you can clone and run.

## Projects

| Project | Blog Post | Stack |
|---------|-----------|-------|
| [ai/rag-pipeline](ai/rag-pipeline/) | [Build a RAG Pipeline That Actually Works](https://digital.taatal.com/blogs/build-rag-pipeline-that-actually-works) | Python, ChromaDB, Sentence Transformers, Claude/OpenAI |
| [ai/doc-agent](ai/doc-agent/) | [Build an AI Document Processing Agent](https://digital.taatal.com/blogs/build-ai-document-processing-agent) | Python, Claude/OpenAI, PyMuPDF |
| [ai/db-mcp-server](ai/db-mcp-server/) | [Build an MCP Server for Database Analytics](https://digital.taatal.com/blogs/build-mcp-server-database-analytics) | Python, FastMCP, SQLite |
| [adobe/firefly-aem-pipeline](adobe/firefly-aem-pipeline/) | [Integrating Firefly Services into AEM](https://digital.taatal.com/blogs/integrating-firefly-services-aem-content-pipeline) | Python, httpx, Adobe Firefly API |
| [cloud/cicd-pipeline](cloud/cicd-pipeline/) | [Build a CI/CD Pipeline From Scratch](https://digital.taatal.com/blogs/build-cicd-pipeline-from-scratch) | Terraform, GitHub Actions, AWS ECS |

## Quick Start

Each project is a standalone package. Pick one:

```bash
git clone https://github.com/taatal/blog-code.git
cd blog-code/ai/rag-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Every Python project installs with `pip install -e .` and runs from the command line.

## Author

Built by [Taatal Digital](https://digital.taatal.com) Engineering.

## License

MIT
