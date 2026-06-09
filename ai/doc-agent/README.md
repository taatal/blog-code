# Doc Agent

A document processing pipeline that classifies PDFs, extracts structured data, validates it with arithmetic checks, and retries when something looks wrong.

Drop invoices, contracts, purchase orders, or receipts into a folder. Get clean JSON out the other side.

For the full architecture walkthrough and every design decision explained, read the blog post:
[Build an AI Document Processing Agent](https://digital.taatal.com/blogs/build-ai-document-processing-agent)

## Get started

Requires Python 3.11+ and an API key (Anthropic or OpenAI).

```bash
git clone https://github.com/taatal/blog-code.git
cd blog-code/ai/doc-agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set your API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or use OpenAI instead:

```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY="sk-..."
```

## Run it

Process a single file:

```bash
doc-agent --file ./documents/sample-invoice.pdf
```

Process a folder of PDFs:

```bash
doc-agent --input ./documents --output ./results
```

Each PDF produces a JSON file in the output directory, named after the source file.

## What happens inside

```
PDF in --> Text extraction --> Classification --> Field extraction --> Validation --> JSON out
                                                        ^                  |
                                                        |                  |
                                                        +-- retry with ----+
                                                            error context
```

1. Text and tables are extracted from the PDF using PyMuPDF
2. The LLM classifies the document type (invoice, contract, purchase order, receipt)
3. Structured fields are extracted using tool calling with a schema per document type
4. Arithmetic validation checks the numbers (line items sum correctly, tax adds up)
5. If validation fails, the LLM re-extracts with the specific errors as feedback

## Sample output

```json
{
  "filename": "sample-invoice.pdf",
  "document_type": "invoice",
  "data": {
    "vendor_name": "Nexus Cloud Solutions Pvt Ltd",
    "invoice_number": "NCS/2026/0847",
    "invoice_date": "2026-04-18",
    "line_items": [
      {"description": "Cloud Infrastructure Consulting", "quantity": 40, "unit_price": 4500, "total": 180000},
      {"description": "AWS Architecture Review", "quantity": 1, "unit_price": 75000, "total": 75000},
      {"description": "Terraform Module Development", "quantity": 16, "unit_price": 5000, "total": 80000}
    ],
    "subtotal": 335000,
    "tax_amount": 60300,
    "total_amount": 395300
  },
  "confidence": 0.94,
  "processing_time_ms": 3847,
  "needs_review": false,
  "review_reasons": []
}
```

## Project layout

```
src/doc_agent/
  cli.py              Entry point
  process.py          Orchestrator (single + batch)
  schemas.py          Extraction schemas per document type
  llm/client.py       Provider abstraction (Anthropic / OpenAI)
  pipeline/
    intake.py         PDF text and table extraction
    classify.py       Document type classification
    extract.py        Field extraction with retry loop
    validate.py       Arithmetic and business rule checks
    retry.py          Exponential backoff for API errors
```

## Numbers

- ~$0.03 per document (Anthropic pricing)
- 60-100 documents per minute at 5 concurrent workers
- Validation catches ~70% of extraction errors without human intervention

## License

MIT
