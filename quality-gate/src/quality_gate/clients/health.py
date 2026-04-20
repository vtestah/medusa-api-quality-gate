"""Client for Medusa health checks."""

from requests import Session

from quality_gate.clients.base import BaseApiClient
from quality_gate.config import Settings
from quality_gate.models.health import HealthResponse


class HealthClient(BaseApiClient):
    """Read-only client for infrastructure smoke checks."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def retrieve(self) -> HealthResponse:
        response = self.get("/health")
        response.raise_for_status()
        return HealthResponse.model_validate(response.json())
