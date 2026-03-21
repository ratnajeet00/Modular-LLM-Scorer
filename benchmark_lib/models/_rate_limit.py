"""Shared rate-limit utilities for API provider models.

Parses the retry wait time from 429 responses (Retry-After header and
message body) and applies it with random jitter to prevent thundering
herd when multiple benchmark workers all hit the limit simultaneously.
"""
from __future__ import annotations

import logging
import random
import re
import time

import requests

logger = logging.getLogger(__name__)

# Minimum seconds to wait on any 429, regardless of what the API says.
# This prevents hammering if the server's suggested wait is tiny.
_MIN_RATE_LIMIT_WAIT = 5.0

# Extra random jitter fraction applied on top of the suggested wait.
# e.g. 0.5 means the actual wait is between 1x and 1.5x the suggested time.
# This staggers concurrent workers so they don't all retry at the same instant.
_JITTER_FRACTION = 0.5


def parse_retry_after(response: requests.Response) -> float | None:
    """Return the number of seconds to wait as instructed by the server.

    Checks (in order):
    1. ``Retry-After`` HTTP header (standard)
    2. ``x-ratelimit-reset-requests`` header (Groq-specific, seconds)
    3. ``"try again in Xs"`` / ``"retry after Xs"`` in the response body
    """
    # --- 1. Standard Retry-After header ---
    retry_after = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass

    # --- 2. Groq-specific reset header ---
    groq_reset = (
        response.headers.get("x-ratelimit-reset-requests")
        or response.headers.get("x-ratelimit-reset-tokens")
    )
    if groq_reset:
        # Value is like "2s", "1m30s", or plain seconds
        parsed = _parse_duration_string(groq_reset)
        if parsed is not None:
            return parsed

    # --- 3. Parse wait time from error message body ---
    try:
        body_text = response.text
    except Exception:
        return None

    # Matches: "try again in 2s", "retry after 1.5s", "please wait 30 seconds"
    pattern = re.compile(
        r"(?:try again|retry after|please wait)\s+in\s+([\d.]+)\s*(s|second|seconds|ms|milliseconds?|m|min|minute|minutes?)?",
        re.IGNORECASE,
    )
    m = pattern.search(body_text)
    if m:
        value = float(m.group(1))
        unit = (m.group(2) or "s").lower()
        if unit.startswith("m") and not unit.startswith("ms"):
            value *= 60
        elif unit.startswith("ms"):
            value /= 1000
        return value

    return None


def _parse_duration_string(s: str) -> float | None:
    """Parse strings like '2s', '1m30s', '500ms' into seconds."""
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        pass
    total = 0.0
    for value, unit in re.findall(r"([\d.]+)\s*(h|m|s|ms)", s, re.IGNORECASE):
        v = float(value)
        u = unit.lower()
        if u == "h":
            total += v * 3600
        elif u == "m":
            total += v * 60
        elif u == "s":
            total += v
        elif u == "ms":
            total += v / 1000
    return total if total > 0 else None


def wait_for_rate_limit(
    response: requests.Response,
    provider: str,
    attempt: int,
    fallback_base: float = 10.0,
) -> float:
    """Sleep the appropriate amount for a 429 response and return seconds waited.

    Args:
        response:      The 429 HTTP response object.
        provider:      Label used in log messages (e.g. "Groq", "Together").
        attempt:       Current retry attempt number (0-indexed), used for
                       exponential fallback when no server hint is available.
        fallback_base: Base seconds for exponential fallback when the server
                       gives no wait hint.

    Returns:
        Number of seconds actually slept.
    """
    suggested = parse_retry_after(response)

    if suggested is not None:
        base_wait = max(suggested, _MIN_RATE_LIMIT_WAIT)
        source = f"server hint={suggested:.1f}s"
    else:
        # Fall back to exponential backoff
        base_wait = max(fallback_base * (2 ** attempt), _MIN_RATE_LIMIT_WAIT)
        source = "exponential fallback"

    # Add jitter: uniformly distributed in [base_wait, base_wait * (1 + jitter)]
    jitter = random.uniform(0, base_wait * _JITTER_FRACTION)
    total_wait = base_wait + jitter

    logger.warning(
        "[%s] Rate limited (429). Waiting %.1fs (%s + %.1fs jitter).",
        provider,
        total_wait,
        source,
        jitter,
    )
    time.sleep(total_wait)
    return total_wait
