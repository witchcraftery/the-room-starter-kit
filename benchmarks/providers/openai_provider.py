"""OpenAI API provider for benchmark testing."""
import os
import uuid
from typing import Optional

from openai import OpenAI

from .base import AgentProvider


class OpenAIProvider(AgentProvider):
    """Provider that uses the OpenAI Chat Completions API."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
    ):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self._sessions: dict[str, list[dict]] = {}

    def start_session(
        self,
        system_prompt: str,
        room_files: Optional[dict[str, str]] = None,
    ) -> str:
        session_id = str(uuid.uuid4())[:8]
        messages = [{"role": "system", "content": system_prompt}]

        # Inject room files as system context if provided
        if room_files:
            room_context = "# Room Files\n\n"
            for filename, content in room_files.items():
                room_context += f"## {filename}\n{content}\n\n"
            messages.append({"role": "system", "content": room_context})

        self._sessions[session_id] = messages
        return session_id

    def send_message(self, session_id: str, message: str) -> str:
        messages = self._sessions[session_id]
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply

    def end_session(self, session_id: str) -> None:
        # Session history is preserved in memory for analysis
        pass

    def get_session_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])
