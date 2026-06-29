"""Store API error body model."""

from quality_gate.models.common import ApiModel


class StoreApiError(ApiModel):
    """Unified contract for Store API error response bodies.

    Medusa varies the shape of error payloads across endpoints and status
    codes, so every field is optional. The model still parses a JSON error
    object without raising ``ValidationError``, which lets negative-path tests
    confirm the body is a contract-compatible JSON object.
    """

    message: str | None = None
    type: str | None = None
    code: str | None = None
