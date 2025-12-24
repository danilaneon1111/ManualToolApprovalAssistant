import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")  # optional (custom endpoint)
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Cost control (defaults are intentionally small/cheap)
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "256"))
    request_timeout_s: int = int(os.getenv("REQUEST_TIMEOUT_S", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "2"))
    max_tool_loops: int = int(os.getenv("MAX_TOOL_LOOPS", "3"))

    # Interface
    interface: str = os.getenv("INTERFACE", "cli")

    # Logging
    log_usage: bool = os.getenv("LOG_USAGE", "1").strip() not in {"0", "false", "False"}

settings = Settings()
