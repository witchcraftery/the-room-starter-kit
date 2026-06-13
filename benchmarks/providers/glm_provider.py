"""Z.AI / GLM provider for benchmark testing.

OpenAI-compatible API that handles GLM reasoning models (reasoning_content field).
"""
import os
import uuid
from typing import Optional

from openai import OpenAI

from .base import AgentProvider


class GLMProvider(AgentProvider):
    """Provider that uses the Z.AI GLM API (OpenAI-compatible)."""

    def __init__(
        self,
        model: str = "glm-5.2",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.client = OpenAI(
            api_key=api_key or os.getenv("GLM_API_KEY"),
            base_url=base_url or os.getenv("GLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
        )
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
            max_tokens=4096,
        )

        choice = response.choices[0].message
        reply = choice.content or ""

        # GLM reasoning models may put everything in reasoning_content
        # if max_tokens is too low. Log it for debugging but use content.
        if not reply and hasattr(choice, "reasoning_content") and choice.reasoning_content:
            reply = f"[Reasoning only — no content produced. Reasoning: {choice.reasoning_content[:200]}...]"

        messages.append({"role": "assistant", "content": reply})
        return reply

    def end_session(self, session_id: str) -> None:
        pass

    def get_session_history(self, session_id: str) -> list[dict]:
        return self._sessions.get(session_id, [])
