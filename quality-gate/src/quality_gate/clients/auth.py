"""Client for Medusa storefront authentication flows."""

from requests import Response, Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.models.auth import AuthTokenResponse


class StoreAuthClient(StoreApiClient):
    """Storefront auth client for customer registration preflight checks."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def request_customer_registration_token(
        self,
        *,
        email: str,
        password: str | None = None,
        expected_status_code: int | None = None,
    ) -> Response:
        """Request a customer registration token without hiding HTTP errors."""

        payload = {"email": email}
        if password is not None:
            payload["password"] = password

        return self.post(
            "/auth/customer/emailpass/register",
            json=payload,
            headers={"Content-Type": "application/json"},
            expected_status_code=expected_status_code,
        )

    def create_customer_registration_token(
        self,
        *,
        email: str,
        password: str,
    ) -> AuthTokenResponse:
        """Request and validate a JWT used to create the customer profile."""

        response = self.request_customer_registration_token(
            email=email,
            password=password,
            expected_status_code=200,
        )
        return AuthTokenResponse.model_validate(response.json())
