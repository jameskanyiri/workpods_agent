from langchain.agents import create_agent

from src.state.state import CustomState

from src.context.context import AgentContext

from src.llm.llm_selector import dynamic_model_selector, default_llm

from src.middleware.todo_middleware.middleware import TodoListMiddleware

from src.prompt.prompt import context_aware_prompt
from src.middleware.auth_middleware.middleware import AuthMiddleware
from src.middleware.filesystem_middleware.middleware import FilesystemMiddleware
from src.middleware.skills_middleware.middleware import SkillsMiddleware
from src.middleware.loop_detection.middleware import LoopDetectionMiddleware
from src.middleware.pre_completion_check.middleware import PreCompletionCheckMiddleware
from src.middleware.summarization.middleware import SummarizationMiddleware


agent = create_agent(
    model=default_llm,
    tools=[],
    state_schema=CustomState,
    context_schema=AgentContext,
    middleware=[
        AuthMiddleware(),
        FilesystemMiddleware(),
        SkillsMiddleware(),
        TodoListMiddleware(),
        LoopDetectionMiddleware(),
        PreCompletionCheckMiddleware(),
        dynamic_model_selector,
        context_aware_prompt,
    ],
)
