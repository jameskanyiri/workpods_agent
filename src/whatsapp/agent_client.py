import os
import uuid

from langgraph_sdk import get_client

LANGGRAPH_API_URL = os.environ.get("LANGGRAPH_API_URL", "http://localhost:2024")
THREAD_NAMESPACE = os.environ.get(
    "THREAD_NAMESPACE", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
)
GRAPH_NAME = "ada_project"


def get_thread_id(phone_number: str) -> str:
    """Generate a deterministic thread ID from a phone number."""
    return str(uuid.uuid5(uuid.UUID(THREAD_NAMESPACE), phone_number))


async def get_agent_response(phone_number: str, user_message: str) -> str:
    """Send a message to the LangGraph agent and return the AI response."""
    client = get_client(url=LANGGRAPH_API_URL)
    thread_id = get_thread_id(phone_number)

    # Create thread or reuse existing one
    await client.threads.create(thread_id=thread_id, if_exists="do_nothing")

    # Run the agent and wait for the final result
    result = await client.runs.wait(
        thread_id,
        GRAPH_NAME,
        input={"messages": [{"role": "human", "content": user_message}]},
    )

    messages = result.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if last_msg.get("type") == "ai" and isinstance(last_msg.get("content"), str):
            return last_msg["content"]

    return ""
