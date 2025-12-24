import datetime
from langchain_core.tools import tool

@tool
def get_time_utc() -> str:
    """Вернуть текущее время UTC в ISO-формате."""
    return datetime.datetime.utcnow().isoformat() + "Z"

@tool
def calc(expression: str) -> str:
    """Безопасный калькулятор: поддерживает + - * / скобки. Запрещает буквы и подозрительные символы."""
    allowed = set("0123456789+-*/(). ")
    if any(ch not in allowed for ch in expression):
        return "ERROR: invalid characters in expression"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"

TOOLS = [get_time_utc, calc]
