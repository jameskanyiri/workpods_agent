from langchain.agents import create_agent

from src.tools.process_media_tool.tool import process_media
from src.tools.complete_onboarding_tool.tool import complete_onboarding

from src.state.state import CustomState

from src.context.context import AgentContext

from src.llm.llm_selector import dynamic_model_selector, default_llm

from src.prompt.prompt import context_aware_prompt
from src.middleware.gate_tools.gate_tools import gate_tools_for_onboarding
from src.middleware.todo.middleware import TodoListMiddleware


agent = create_agent(
    model=default_llm,
    tools=[
        process_media,
        complete_onboarding,
    ],
    state_schema=CustomState,
    context_schema=AgentContext,
    middleware=[
        TodoListMiddleware(),
        dynamic_model_selector,
        context_aware_prompt,
    ],
)
