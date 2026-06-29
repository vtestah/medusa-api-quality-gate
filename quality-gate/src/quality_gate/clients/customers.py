"""Client for Medusa Store customer registration flows."""

from collections.abc import Mapping
from typing import Any

from requests import Session

from quality_gate.clients.base import StoreApiClient
from quality_gate.config import Settings
from quality_gate.models.customers import StoreCustomerResponse


class StoreCustomersClient(StoreApiClient):
    """Store API client for customer profile creation and retrieval."""

    def __init__(self, session: Session, settings: Settings) -> None:
        super().__init__(session=session, settings=settings)

    def register_customer(
        self,
        *,
        token: str,
        email: str,
        first_name: str | None = None,
        last_name: str | None = None,
        locale: str | None = None,
        extra_payload: Mapping[str, Any] | None = None,
    ) -> StoreCustomerResponse:
        """Create a Store customer profile with a registration JWT."""

        payload: dict[str, Any] = {"email": email}
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        if extra_payload:
            payload.update(extra_payload)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if locale:
            headers["x-medusa-locale"] = locale

        response = self.post(
            "/store/customers",
            json=payload,
            headers=headers,
            expected_status_code=200,
        )
        return StoreCustomerResponse.model_validate(response.json())
