"""Lenient response-time (soft SLA) assertion helper.

A small, dependency-free check used by the live smoke tests to flag pathological
latency without flaking on normal variance. ``requests`` records the round-trip
duration on every response as :attr:`requests.Response.elapsed` (a ``timedelta``);
this helper reads that value, so it measures server plus transport time and never
starts its own timer.
"""

from requests import Response

DEFAULT_MAX_SECONDS = 5.0
"""Generous default ceiling: a soft SLA meant to catch pathological latency only."""


def assert_response_within_sla(
    response: Response,
    *,
    max_seconds: float = DEFAULT_MAX_SECONDS,
) -> float:
    """Assert ``response`` finished within ``max_seconds`` and return the elapsed seconds.

    Reads :attr:`requests.Response.elapsed` (populated by ``requests`` for every
    sent request), so the measurement reflects the request round-trip rather than
    any client-side timer. The threshold is intentionally lenient — this is a soft
    SLA to surface pathological latency, not a strict performance benchmark.

    Args:
        response: A :class:`requests.Response` returned by a completed request.
        max_seconds: Exclusive upper bound in seconds; must be positive.

    Returns:
        The measured elapsed time in seconds.

    Raises:
        ValueError: If ``max_seconds`` is not positive.
        AssertionError: If the response took ``max_seconds`` seconds or longer.
    """
    if max_seconds <= 0:
        raise ValueError("max_seconds must be positive")

    elapsed_seconds = response.elapsed.total_seconds()
    if elapsed_seconds >= max_seconds:
        raise AssertionError(
            f"Response exceeded the soft SLA: {elapsed_seconds:.3f}s "
            f">= {max_seconds:.3f}s for {response.url or '<unknown url>'}"
        )
    return elapsed_seconds
