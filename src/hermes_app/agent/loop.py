"""Agentic loop — Gemini + tool calling until a final reply."""

from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from hermes_app.config import load_gemini_api_key
from hermes_app.memory.store import MemoryStore
from hermes_app.tools.registry import ToolRegistry
from hermes_app.tools import create_default_registry

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_MODEL = "gemini-2.5-flash"
MAX_TURNS = 8

SYSTEM_PROMPT = """You are the Hermes Agent App assistant in a local chat UI.

Rules:
1. Be friendly and concise.
2. After every user message, call update_report FIRST, then reply with a friendly message in the same turn.
3. Do NOT call send_telegram — Report.json updates are watched automatically and delivered to Telegram within ~1 minute.
4. For greetings like "hi", respond warmly and log the interaction in update_report.
5. You may use read_report to see current project status if helpful.
"""


class AgentLoop:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        memory: MemoryStore | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.registry = registry or create_default_registry()
        self.memory = memory or MemoryStore()
        self.model = model
        self.client = OpenAI(api_key=load_gemini_api_key(), base_url=GEMINI_BASE)

    def _messages(self, session_id: str) -> list[dict[str, Any]]:
        history = self.memory.get(f"history:{session_id}")
        if not isinstance(history, list):
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
        return history

    def _save_history(self, session_id: str, messages: list[dict[str, Any]]) -> None:
        self.memory.set(f"history:{session_id}", messages[-40:])

    def chat(self, user_message: str, session_id: str = "default") -> dict[str, Any]:
        messages = self._messages(session_id)
        messages.append({"role": "user", "content": user_message})

        report_updated = False
        tool_calls_made: list[str] = []

        for _ in range(MAX_TURNS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.registry.schemas(),
            )
            choice = response.choices[0]
            msg = choice.message

            assistant_entry: dict[str, Any] = {
                "role": "assistant",
                "content": msg.content or "",
            }
            if msg.tool_calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            messages.append(assistant_entry)

            if not msg.tool_calls:
                reply = (msg.content or "").strip()
                if not reply and report_updated:
                    reply = "Got it! I've updated Report.json — you should get a Telegram alert within about a minute."
                self._save_history(session_id, messages)
                return {
                    "reply": reply or "Hello! How can I help you today?",
                    "report_updated": report_updated,
                    "tools_used": tool_calls_made,
                }

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                result = self.registry.call(name, **args)
                tool_calls_made.append(name)
                if name == "update_report" and result.ok:
                    report_updated = True

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result.to_dict()),
                    }
                )

        self._save_history(session_id, messages)
        return {
            "reply": "I hit the turn limit — please try again.",
            "report_updated": report_updated,
            "tools_used": tool_calls_made,
        }
