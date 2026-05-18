"""Client for Medusa storefront authentication flows."""

from requests import Response, Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings


class StoreAuthClient(StoreApiClient):
    """Storefront auth client for customer registration preflight checks."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def request_customer_registration_token(
        self,
        *,
        email: str,
        password: str | None = None,
    ) -> Response:
        """Request a customer registration token without hiding HTTP errors."""

        payload = {"email": email}
        if password is not None:
            payload["password"] = password

        return self.post(
            "/auth/customer/emailpass/register",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
