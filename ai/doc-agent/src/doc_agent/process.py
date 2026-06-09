import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from doc_agent.pipeline.intake import extract_text
from doc_agent.pipeline.classify import classify_document
from doc_agent.pipeline.extract import extract_with_retry

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    filename: str
    document_type: str
    data: dict
    confidence: float
    processing_time_ms: int
    needs_review: bool
    review_reasons: list[str]


def elapsed_ms(start: datetime) -> int:
    return int((datetime.now(timezone.utc) - start).total_seconds() * 1000)


def process_document(pdf_path: Path) -> ProcessingResult:
    start = datetime.now(timezone.utc)

    doc = extract_text(pdf_path)

    classification = classify_document(doc)
    doc_type = classification["category"]

    if doc_type == "unknown":
        return ProcessingResult(
            filename=pdf_path.name,
            document_type="unknown",
            data={},
            confidence=classification["confidence"],
            processing_time_ms=elapsed_ms(start),
            needs_review=True,
            review_reasons=["Document could not be classified"],
        )

    extraction = extract_with_retry(doc, doc_type)

    review_reasons = []
    if extraction.get("needs_review"):
        review_reasons.append("Validation failed after max retries")
    if extraction["validation"].warnings:
        review_reasons.extend(extraction["validation"].warnings)
    if classification["confidence"] < 0.85:
        review_reasons.append(f"Low classification confidence: {classification['confidence']}")

    return ProcessingResult(
        filename=pdf_path.name,
        document_type=doc_type,
        data=extraction["data"],
        confidence=classification["confidence"],
        processing_time_ms=elapsed_ms(start),
        needs_review=bool(review_reasons),
        review_reasons=review_reasons,
    )


def process_batch(pdf_dir: Path, output_dir: Path, max_workers: int = 5):
    output_dir.mkdir(parents=True, exist_ok=True)
    pdfs = list(pdf_dir.glob("*.pdf"))

    if not pdfs:
        logger.warning(f"No PDF files found in {pdf_dir}")
        return {"processed": [], "needs_review": [], "failed": []}

    results = {"processed": [], "needs_review": [], "failed": []}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_document, pdf): pdf
            for pdf in pdfs
        }

        for future in as_completed(futures):
            pdf = futures[future]
            try:
                result = future.result()

                output_file = output_dir / f"{pdf.stem}.json"
                output_file.write_text(json.dumps({
                    "filename": result.filename,
                    "document_type": result.document_type,
                    "data": result.data,
                    "confidence": result.confidence,
                    "processing_time_ms": result.processing_time_ms,
                    "needs_review": result.needs_review,
                    "review_reasons": result.review_reasons,
                }, indent=2))

                if result.needs_review:
                    results["needs_review"].append(result.filename)
                else:
                    results["processed"].append(result.filename)

                logger.info(
                    f"{result.filename}: {result.document_type} "
                    f"({result.processing_time_ms}ms) "
                    f"{'[REVIEW]' if result.needs_review else '[OK]'}"
                )

            except Exception as e:
                results["failed"].append({"file": pdf.name, "error": str(e)})
                logger.error(f"{pdf.name}: FAILED - {e}")

    logger.info(
        f"\nDone. Processed: {len(results['processed'])}, "
        f"Review: {len(results['needs_review'])}, "
        f"Failed: {len(results['failed'])}"
    )

    return results
