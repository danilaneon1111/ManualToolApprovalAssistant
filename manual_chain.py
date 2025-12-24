from __future__ import annotations

from typing import List, Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.memory import ConversationBufferMemory
from rich.console import Console

from app.config import settings
from app.llm import build_llm
from app.prompts import agent_prompt
from app.tools import TOOLS

console = Console()

class ManualToolApprovalChain:
    """Chain with manual approval for tool calls.

    Flow:
    1) LLM answers with text OR proposes tool call(s)
    2) Operator approves/denies each tool call (y/n)
    3) Tool result (or denial) is returned to the LLM as ToolMessage
    4) LLM generates final answer
    """

    def __init__(self):
        self.llm = build_llm()
        self.tools = TOOLS
        self.tools_by_name = {t.name: t for t in self.tools}

        # Memory (LangChain requirement)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        # LLM configured for tool calling
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _load_history(self) -> List:
        return self.memory.load_memory_variables({}).get("chat_history", [])

    def _save_to_memory(self, user_input: str, ai_text: str) -> None:
        # ConversationBufferMemory expects {"input": ...}, {"output": ...}
        self.memory.save_context({"input": user_input}, {"output": ai_text})

    def _log_usage(self, msg: AIMessage, prefix: str = "usage") -> None:
        if not settings.log_usage:
            return
        meta = getattr(msg, "response_metadata", None) or {}
        usage = meta.get("token_usage") or meta.get("usage") or meta.get("usage_metadata")
        if usage:
            console.print(f"[dim]{prefix}: {usage}[/dim]")

    def invoke(self, user_input: str) -> str:
        if not user_input.strip():
            return "Пустой ввод. Напиши запрос."

        history = self._load_history()

        # 1) First model call
        prompt_value = agent_prompt.invoke({"chat_history": history, "input": user_input})
        ai: AIMessage = self.llm_with_tools.invoke(prompt_value)
        self._log_usage(ai, "llm#1")

        # Save the plain-text part to memory (for dialogue continuity)
        self._save_to_memory(user_input, ai.content or "")

        # Local per-turn history (we append tool messages here)
        turn_history = history + [HumanMessage(content=user_input), ai]

        # 2) Manual tool approval loop (bounded)
        loops = 0
        while getattr(ai, "tool_calls", None):
            loops += 1
            if loops > settings.max_tool_loops:
                return "Слишком много последовательных запросов к инструментам. Остановлено для экономии токенов."

            for call in ai.tool_calls:
                tool_name = call["name"]
                tool_args = call.get("args", {}) or {}
                call_id = call["id"]

                console.print(f"\n[bold yellow][TOOL PROPOSED][/bold yellow] {tool_name} args={tool_args}")
                decision = console.input("[cyan]Run tool? (y/n):[/cyan] ").strip().lower()

                if decision == "y":
                    try:
                        result = self.tools_by_name[tool_name].invoke(tool_args)
                        tool_msg = ToolMessage(content=str(result), tool_call_id=call_id)
                    except Exception as e:
                        tool_msg = ToolMessage(content=f"TOOL_ERROR: {type(e).__name__}: {e}", tool_call_id=call_id)
                else:
                    tool_msg = ToolMessage(content="TOOL_DENIED by operator", tool_call_id=call_id)

                turn_history.append(tool_msg)

            # 3) Ask the model for a final answer after tool results/denials
            prompt_value2 = agent_prompt.invoke(
                {"chat_history": turn_history, "input": "Сформируй итоговый ответ пользователю."}
            )
            ai = self.llm_with_tools.invoke(prompt_value2)
            self._log_usage(ai, f"llm#final(loop={loops})")
            turn_history.append(ai)

        return ai.content or "(empty model output)"
