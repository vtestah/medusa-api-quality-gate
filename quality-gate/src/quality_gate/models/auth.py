"""Auth response models."""

from quality_gate.models.common import ApiModel


class AuthErrorResponse(ApiModel):
    """Error contract returned by Medusa auth endpoints."""

    type: str | None = None
    message: str
