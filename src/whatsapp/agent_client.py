import os
import uuid

from langgraph_sdk import get_client

LANGGRAPH_API_URL = os.environ.get("LANGGRAPH_API_URL", "http://localhost:2024")
THREAD_NAMESPACE = os.environ.get(
    "THREAD_NAMESPACE", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
)
GRAPH_NAME = "workpods_agent"


def get_thread_id(phone_number: str) -> str:
    """Generate a deterministic thread ID from a phone number."""
    return str(uuid.uuid5(uuid.UUID(THREAD_NAMESPACE), phone_number))


async def get_agent_response(
    phone_number: str,
    user_message: str | list[dict],
    sender_name: str = "",
) -> str:
    """Send a message to the LangGraph agent and return the AI response.

    `user_message` may be a plain string (for text messages) or a list of
    LangChain-standard content blocks (for images, PDFs, and other files).
    """
    client = get_client(url=LANGGRAPH_API_URL)
    thread_id = get_thread_id(phone_number)

    # Create thread or reuse existing one
    await client.threads.create(thread_id=thread_id, if_exists="do_nothing")

    # Run the agent and wait for the final result
    result = await client.runs.wait(
        thread_id,
        GRAPH_NAME,
        input={"messages": [{"role": "human", "content": user_message}]},
        config={"configurable": {"context": {"user_name": sender_name or "No user name"}}},
    )

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if msg.get("type") != "ai":
            continue
        content = msg.get("content")
        if isinstance(content, str):
            return content
        # Handle multimodal responses: extract text from content blocks
        if isinstance(content, list):
            text_parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            if text_parts:
                return "\n".join(text_parts)

    return ""
