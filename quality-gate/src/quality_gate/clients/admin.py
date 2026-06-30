"""Client for Medusa Admin API authentication and read checks."""

from requests import Response, Session

from quality_gate.clients.base import BaseApiClient
from quality_gate.config import Settings
from quality_gate.models.admin import AdminProductsResponse
from quality_gate.models.auth import AuthTokenResponse


class AdminApiClient(BaseApiClient):
    """Admin API client: email/password login plus bearer-authenticated reads.

    Unlike the Store API clients, the admin client does not send the publishable
    key. It authenticates with an admin user's credentials and then carries the
    returned JWT as an ``Authorization: Bearer`` token.
    """

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def request_login(
        self,
        *,
        email: str,
        password: str,
        expected_status_code: int | None = None,
    ) -> Response:
        """POST admin credentials to the emailpass provider; return raw response."""

        return self.post(
            "/auth/user/emailpass",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            expected_status_code=expected_status_code,
        )

    def login(self, *, email: str, password: str) -> str:
        """Authenticate as an admin user and return the bearer token."""

        response = self.request_login(
            email=email,
            password=password,
            expected_status_code=200,
        )
        return AuthTokenResponse.model_validate(response.json()).token

    def request_products(
        self,
        *,
        token: str | None = None,
        expected_status_code: int | None = None,
    ) -> Response:
        """GET /admin/products, bearer-authenticated when a token is provided."""

        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self.get(
            "/admin/products",
            headers=headers,
            expected_status_code=expected_status_code,
        )

    def list_products(self, *, token: str) -> AdminProductsResponse:
        """Fetch and validate the Admin API products listing."""

        response = self.request_products(token=token, expected_status_code=200)
        return AdminProductsResponse.model_validate(response.json())
