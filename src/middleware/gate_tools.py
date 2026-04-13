from typing import Callable, Awaitable

from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse


ONBOARDING_TOOL_NAMES = {
    "think",
    "write_file",
    "read_file",
    "edit_file",
    "execute_script",
    "complete_onboarding",
    "process_media",
}


@wrap_model_call
async def gate_tools_for_onboarding(
    request: ModelRequest,
    handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
) -> ModelResponse:
    """Filter tools based on onboarding state.

    When is_user_onboarded is False, only onboarding-relevant tools are available.
    """
    is_onboarded = request.state.get("is_user_onboarded", False)
    if not is_onboarded:
        filtered = [t for t in request.tools if t.name in ONBOARDING_TOOL_NAMES]
        request = request.override(tools=filtered)
    return await handler(request)
