from langchain_openai import ChatOpenAI
from app.config import settings

def build_llm() -> ChatOpenAI:
    """Create a cheap-by-default LLM client.

    Notes on cost:
    - gpt-4o-mini is selected by default
    - max_tokens is capped (MAX_OUTPUT_TOKENS)
    """
    kwargs = dict(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        temperature=0,
        max_tokens=settings.max_output_tokens,
        timeout=settings.request_timeout_s,
        max_retries=settings.max_retries,
    )

    # base_url can be empty for OpenAI default
    if settings.openai_base_url.strip():
        kwargs["base_url"] = settings.openai_base_url.strip()

    return ChatOpenAI(**kwargs)
