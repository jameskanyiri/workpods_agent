from langchain.agents.middleware.types import ModelRequest
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import wrap_model_call, ModelResponse

default_llm = init_chat_model(
    "openai:gpt-5.4",
)


@wrap_model_call
async def dynamic_model_selector(request: ModelRequest, handler) -> ModelResponse:
    """
    Dynamic model selector based on the request.
    Converts the preferred_llm string from context into an actual model object.
    """
    context = request.runtime.context

    # Get the preferred LLM and temperature from the context
    preferred_llm = context.preferred_llm

    # Initialize the model with the preferred LLM and temperature
    request.model = init_chat_model(preferred_llm)
    return await handler(request)