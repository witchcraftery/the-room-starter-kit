"""Abstract base class for agent providers."""
from abc import ABC, abstractmethod
from typing import Optional


class AgentProvider(ABC):
    """Interface for communicating with an LLM agent."""

    @abstractmethod
    def start_session(
        self,
        system_prompt: str,
        room_files: Optional[dict[str, str]] = None,
    ) -> str:
        """Start a new agent session.

        Args:
            system_prompt: The system prompt for the session.
            room_files: Optional dict of {filename: content} for room files.
                        If None, this is a control (no-room) session.

        Returns:
            session_id: A unique identifier for this session.
        """
        ...

    @abstractmethod
    def send_message(self, session_id: str, message: str) -> str:
        """Send a user message and return the agent's response.

        Args:
            session_id: The session to send to.
            message: The user message.

        Returns:
            The agent's response text.
        """
        ...

    @abstractmethod
    def end_session(self, session_id: str) -> None:
        """End a session. Simulates a gap / context reset.

        Args:
            session_id: The session to end.
        """
        ...

    @abstractmethod
    def get_session_history(self, session_id: str) -> list[dict]:
        """Return the full message history for a session.

        Returns:
            List of {"role": "user"|"assistant", "content": "..."} dicts.
        """
        ...
