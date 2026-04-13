import base64

from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from langgraph.types import Command

from src.whatsapp.whatsapp_client import get_media_url, download_media

from .description import PROCESS_MEDIA_TOOL_DESCRIPTION
from .prompt import MEDIA_PROCESSING_PROMPT


def _content_block_type(mime_type: str) -> str:
    """Map a MIME type to a LangChain content block type."""
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("audio/"):
        return "audio"
    return "file"


@tool(description=PROCESS_MEDIA_TOOL_DESCRIPTION)
async def process_media(
    media_id: str,
    mime_type: str,
    instruction: str,
    runtime: ToolRuntime,
    filename: str = "document",
) -> Command:
    """Download a WhatsApp media file, process it with an LLM, and return the analysis."""
    try:
        url, resolved_mime = await get_media_url(media_id)
        media_bytes = await download_media(url)
    except Exception as exc:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Failed to download media {media_id}: {exc}",
                        tool_call_id=runtime.tool_call_id,
                    )
                ]
            }
        )

    b64_data = base64.b64encode(media_bytes).decode("utf-8")
    final_mime = resolved_mime or mime_type
    block_type = _content_block_type(final_mime)

    # Build the content block for the LLM
    if block_type == "file":
        # OpenAI requires the nested file format with a data URI for documents
        media_block = {
            "type": "file",
            "file": {
                "file_data": f"data:{final_mime};base64,{b64_data}",
                "filename": filename,
            },
        }
    else:
        media_block = {
            "type": block_type,
            "base64": b64_data,
            "mime_type": final_mime,
        }

    # Invoke a vision-capable LLM to process the media
    llm = init_chat_model("openai:gpt-5.4", streaming=False)
    response = await llm.ainvoke([
        SystemMessage(content=MEDIA_PROCESSING_PROMPT),
        HumanMessage(content=[
            media_block,
            {"type": "text", "text": instruction},
        ]),
    ])

    response = f"Media {media_id} processed successfully. {response.text}"

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=response,
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )
