import time
import logging

logger = logging.getLogger(__name__)


def call_with_retry(fn, max_attempts=3, base_delay=2):
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            err_str = str(e).lower()
            is_retryable = any(k in err_str for k in ["rate", "timeout", "500", "502", "503"])
            if is_retryable and attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retryable error: {e}. Waiting {delay}s.")
                time.sleep(delay)
            else:
                raise

    raise RuntimeError(f"API call failed after {max_attempts} attempts")
