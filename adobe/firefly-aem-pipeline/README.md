# Firefly-to-AEM Asset Pipeline

Companion code for [Integrating Adobe Firefly Services into Your AEM Content Pipeline](https://digital.taatal.com/blogs/integrating-firefly-services-aem-content-pipeline).

This project demonstrates how to connect Adobe Firefly Services (generative AI) with AEM Assets as a Cloud Service. It covers OAuth authentication, rate-limited generation, the Direct Binary Upload protocol, and pipeline orchestration.

Read the blog post for the full architectural context and design decisions behind each module.

## Project structure

```
src/firefly_aem/
    auth.py       OAuth Server-to-Server token management with caching
    generate.py   Firefly API client with async support and rate limiting
    upload.py     AEM Direct Binary Upload (3-step protocol)
    pipeline.py   Orchestrator connecting generation to upload
    cli.py        CLI entry point for running the full pipeline
```

## Running it yourself

If you have Firefly Services entitlement and an AEM as a Cloud Service instance:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp config.example.json config.json
# Fill in your credentials from Adobe Developer Console
firefly-aem --config config.json
```

## Key concepts demonstrated

- **OAuth Server-to-Server**: Machine-to-machine authentication via Adobe IMS with 24-hour token caching
- **Rate limiting**: Sliding window enforcing Adobe's published 4 RPM default, with re-check after sleep for concurrent safety
- **Direct Binary Upload**: The 3-step protocol AEM Cloud Service requires (initiate, PUT to CDN, complete)
- **Error isolation**: Individual variant failures do not break the entire batch
- **Separation of concerns**: Generation logic runs outside AEM. AEM handles governance, processing, and distribution.

## Requirements

- Python 3.11+
- Adobe Developer Console project with Firefly Services API
- AEM as a Cloud Service with Service Credentials configured

## Notes

- `config.json` contains secrets. Never commit it.
- Firefly output URLs are presigned and temporary. The pipeline downloads immediately after generation.
- The Photoshop API (background removal) is a separate entitlement from core Firefly Services.
