from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

from src.tools.think_tool.tool import think_tool
from src.tools.todo_tool.tool import write_todos
from src.tools.ask_user_input_tool.tool import ask_user_input
from src.tools.activate_skill_tool.tool import activate_skill
from src.tools.write_file_tool.tool import write_file
from src.tools.read_file_tool.tool import read_file
from src.tools.edit_file_tool.tool import edit_file
from src.tools.ls_tool.tool import ls_tool
from src.tools.glob_tool.tool import glob_tool
from src.tools.grep_tool.tool import grep_tool
from src.tools.execute_script_tool.tool import execute_script
from src.tools.delete_file_tool.tool import delete_file
from src.tools.task_tool.tool import task
from src.tools.merge_sections_tool.tool import merge_sections
from src.tools.process_media_tool.tool import process_media
from src.tools.complete_onboarding_tool.tool import complete_onboarding

from src.state.state import CustomState

from src.context.context import AgentContext

from src.llm.llm_selector import dynamic_model_selector, default_llm

from src.prompt.prompt import context_aware_prompt
from src.middleware.gate_tools import gate_tools_for_onboarding


agent = create_agent(
    model=default_llm,
    tools=[
        write_todos,
        think_tool,
        ask_user_input,
        activate_skill,
        write_file,
        read_file,
        edit_file,
        ls_tool,
        glob_tool,
        grep_tool,
        execute_script,
        delete_file,
        task,
        merge_sections,
        process_media,
        complete_onboarding,
    ],
    state_schema=CustomState,
    context_schema=AgentContext,
    middleware=[
        dynamic_model_selector,
        context_aware_prompt,
        gate_tools_for_onboarding,
    ],
)
