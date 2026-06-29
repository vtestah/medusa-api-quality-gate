"""Shared Pydantic base models."""

from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, StringConstraints

ItemT = TypeVar("ItemT")

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
"""Reusable non-empty string type: trims whitespace and requires at least one character."""


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
