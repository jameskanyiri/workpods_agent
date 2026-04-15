from langchain.agents import AgentState
from typing import Annotated, NotRequired

from src.state.schema import VFile
from src.state.utils import merge_vfs


class CustomState(AgentState):
    active_skill: NotRequired[str]
    vfs: Annotated[NotRequired[dict[str, VFile]], merge_vfs]
    is_user_onboarded: NotRequired[bool] = False



