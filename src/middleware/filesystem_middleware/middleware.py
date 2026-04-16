from langchain.agents.middleware.types import (
    AgentMiddleware,
    ContextT,
    ModelRequest,
)
from langchain_core.messages import SystemMessage

from src.middleware.filesystem_middleware.state import FilesystemState
from src.middleware.filesystem_middleware.prompt import FILESYSTEM_SYSTEM_PROMPT

from src.middleware.filesystem_middleware.tools.ls.ls_tool import ls
from src.middleware.filesystem_middleware.tools.read_file.read_file_tool import read_file
from src.middleware.filesystem_middleware.tools.write_file.write_file_tool import write_file
from src.middleware.filesystem_middleware.tools.edit_file.edit_file_tool import edit_file
from src.middleware.filesystem_middleware.tools.glob.glob_tool import glob
from src.middleware.filesystem_middleware.tools.grep.grep_tool import grep
from src.middleware.filesystem_middleware.tools.api_request.api_request_tool import api_request


class FilesystemMiddleware(
    AgentMiddleware[FilesystemState, ContextT]
):
    """Middleware for providing filesystem tools and API request capabilities to an agent.

    This middleware bundles filesystem tools (ls, read_file, write_file, edit_file,
    glob, grep) and an api_request tool into a single middleware. It injects a system
    prompt guiding the agent on how to use the tools and manages the filesystem state.
    """

    state_schema = FilesystemState

    def __init__(self) -> None:
        super().__init__()
        self.tools = [
            ls,
            read_file,
            write_file,
            edit_file,
            glob,
            grep,
            api_request,
        ]

    def _inject_system_prompt(self, request: ModelRequest) -> ModelRequest:
        extra = {"type": "text", "text": FILESYSTEM_SYSTEM_PROMPT}

        if request.system_message is not None:
            new_content = [*request.system_message.content_blocks, extra]
        else:
            new_content = [extra]

        return request.override(system_message=SystemMessage(content=new_content))

    async def awrap_model_call(self, request, handler):
        return await handler(self._inject_system_prompt(request))
