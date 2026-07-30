# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Retry logic for transient LLM API failures."""

from __future__ import annotations

import time
import logging

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3
_BASE_DELAY = 2


def call_with_retry(
    fn,
    max_attempts: int = _MAX_ATTEMPTS,
    base_delay: int = _BASE_DELAY,
):
    """Call a function with exponential backoff on transient errors.

    Args:
        fn: Zero-argument callable to invoke.
        max_attempts: Maximum number of attempts before raising.
        base_delay: Base delay in seconds (doubled each retry).

    Returns:
        The return value of fn() on success.

    Raises:
        Exception: The last exception if all retries are exhausted or
            the error is not retryable.
    """
    _retryable_keywords = ("rate", "timeout", "500", "502", "503")

    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            err_str = str(e).lower()
            is_retryable = any(
                k in err_str for k in _retryable_keywords
            )
            if is_retryable and attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "Retryable error: %s. Waiting %ds.", e, delay
                )
                time.sleep(delay)
            else:
                raise
