from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command, interrupt

from .description import ASK_USER_INPUT_TOOL_DESCRIPTION
from .schema import Question


@tool(description=ASK_USER_INPUT_TOOL_DESCRIPTION)
def ask_user_input(
    display_name: str = "Waiting for your input",
    questions: list[Question] = None,
    runtime: ToolRuntime = None,
) -> Command:
    """Ask the user structured questions with predefined options."""
    tool_call_id = runtime.tool_call_id

    # Validate question count
    if len(questions) < 1 or len(questions) > 3:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: Must provide 1 to 3 questions.",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # Validate each question's options
    for q in questions:
        if len(q.options) < 2 or len(q.options) > 4:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=f"Error: Each question must have 2 to 4 options. "
                            f"Question \"{q.question}\" has {len(q.options)}.",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

    questions_dump = [q.model_dump() for q in questions]

    # Pause execution and surface questions to the frontend
    # The frontend renders the questions as interactive UI
    # User responses come back as the interrupt's resume value
    response = interrupt({
        "questions": questions_dump,
        "display_name": display_name,
    })

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=response,
                    tool_call_id=tool_call_id,
                    name=display_name,
                )
            ],
        }
    )
