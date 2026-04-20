"""Health endpoint models."""

from quality_gate.models.common import ApiModel


class HealthResponse(ApiModel):
    """Minimal Medusa health contract."""

    status: str
