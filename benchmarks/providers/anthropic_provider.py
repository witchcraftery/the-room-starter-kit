"""Anthropic API provider for benchmark testing."""
import os
import uuid
from typing import Optional

import anthropic

from providers.base import AgentProvider


class AnthropicProvider(AgentProvider):
    """Provider that uses the Anthropic Messages API."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None,
    ):
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self._sessions: dict[str, list[dict]] = {}

    def start_session(
        self,
        system_prompt: str,
        room_files: Optional[dict[str, str]] = None,
    ) -> str:
        session_id = str(uuid.uuid4())[:8]

        # Build the system message — Anthropic uses a separate system param
        system_content = system_prompt
        if room_files:
            system_content += "\n\n# Room Files\n\n"
            for filename, content in room_files.items():
                system_content += f"## {filename}\n{content}\n\n"

        # Store system separately (Anthropic API convention)
        self._sessions[session_id] = {
            "system": system_content,
            "messages": [],
        }
        return session_id

    def send_message(self, session_id: str, message: str) -> str:
        session = self._sessions[session_id]
        session["messages"].append({"role": "user", "content": message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=session["system"],
            messages=session["messages"],
        )

        reply = response.content[0].text
        session["messages"].append({"role": "assistant", "content": reply})
        return reply

    def end_session(self, session_id: str) -> None:
        pass

    def get_session_history(self, session_id: str) -> list[dict]:
        session = self._sessions.get(session_id, {})
        return session.get("messages", [])
