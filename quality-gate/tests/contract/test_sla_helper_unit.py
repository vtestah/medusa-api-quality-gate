"""Unit tests for the response-time (soft SLA) assertion helper.

These run without a live runtime: each builds a :class:`requests.Response` with a
synthetic ``elapsed`` so the pass, boundary, over-SLA, and bad-argument branches
are all exercised deterministically.
"""

from datetime import timedelta

import pytest
from requests import Response

from quality_gate.timing import DEFAULT_MAX_SECONDS, assert_response_within_sla

pytestmark = pytest.mark.contract


def _response_with_elapsed(seconds: float) -> Response:
    """Build a response whose ``elapsed`` round-trip time is ``seconds``."""
    response = Response()
    response.elapsed = timedelta(seconds=seconds)
    response.url = "http://localhost:9000/health"
    return response


def test_returns_elapsed_seconds_when_under_threshold() -> None:
    """A fast response returns its measured elapsed time and does not raise."""
    response = _response_with_elapsed(0.25)

    elapsed = assert_response_within_sla(response, max_seconds=5.0)

    assert elapsed == pytest.approx(0.25)


def test_uses_generous_default_threshold() -> None:
    """Called without an explicit bound, the generous default applies."""
    response = _response_with_elapsed(DEFAULT_MAX_SECONDS / 2)

    elapsed = assert_response_within_sla(response)

    assert elapsed == pytest.approx(DEFAULT_MAX_SECONDS / 2)


def test_raises_when_elapsed_equals_threshold() -> None:
    """The bound is exclusive: an elapsed time equal to it is a violation."""
    response = _response_with_elapsed(5.0)

    with pytest.raises(AssertionError) as excinfo:
        assert_response_within_sla(response, max_seconds=5.0)

    assert "soft SLA" in str(excinfo.value)
    assert "/health" in str(excinfo.value)


def test_raises_when_elapsed_exceeds_threshold() -> None:
    """A response slower than the bound raises with both durations reported."""
    response = _response_with_elapsed(7.5)

    with pytest.raises(AssertionError) as excinfo:
        assert_response_within_sla(response, max_seconds=5.0)

    message = str(excinfo.value)
    assert "7.500s" in message
    assert "5.000s" in message


@pytest.mark.parametrize("bad_max", [0.0, -1.0])
def test_rejects_non_positive_threshold(bad_max: float) -> None:
    """A non-positive ``max_seconds`` is a programming error, not a slow response."""
    response = _response_with_elapsed(0.1)

    with pytest.raises(ValueError, match="max_seconds must be positive"):
        assert_response_within_sla(response, max_seconds=bad_max)
