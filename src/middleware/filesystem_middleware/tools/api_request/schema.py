from typing import Literal
from pydantic import BaseModel, Field


class ApiRequestSchema(BaseModel):
    """Input schema for the `api_request` tool."""

    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = Field(
        description="HTTP method for the API request."
    )
    endpoint: str = Field(
        description="API endpoint path (e.g., '/users', '/transactions/123')."
    )
    payload: dict | None = Field(
        default=None,
        description="Request body for POST/PUT/PATCH requests."
    )
    params: dict | None = Field(
        default=None,
        description="Query parameters for filtering/pagination (e.g., {'limit': 10, 'offset': 0})."
    )
