"""Shared Pydantic base models."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

ItemT = TypeVar("ItemT")


class ApiModel(BaseModel):
    """Common base model with relaxed parsing for Medusa payloads."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class DataEnvelope(ApiModel, Generic[ItemT]):
    """Generic wrapper for endpoints that return a top-level data key."""

    data: ItemT


class PaginatedEnvelope(ApiModel, Generic[ItemT]):
    """Generic wrapper for paginated Medusa list endpoints."""

    count: int | None = None
    limit: int | None = None
    offset: int | None = None
