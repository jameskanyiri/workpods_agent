from langchain.agents.middleware.types import AgentState
from typing import Annotated, NotRequired
from src.middleware.filesystem_middleware.schema import FileData
from src.middleware.filesystem_middleware.utils import file_data_reducer


class FilesystemState(AgentState):
    """State for the filesystem middleware."""

    files: Annotated[NotRequired[dict[str, FileData]], file_data_reducer]
    """Files in the filesystem."""

    access_token: NotRequired[str]
    """JWT access token for the Workpods backend API."""

    refresh_token: NotRequired[str]
    """JWT refresh token for obtaining new access tokens."""

    workspace_id: NotRequired[str]
    """Current workspace UUID for API calls."""