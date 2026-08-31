"""Text-only Stage 1 companion chat; no hardware actions are exposed here."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, Sequence


SYSTEM_PROMPT = """You are BertRobo, a warm, concise AI companion in Stage 1.
You currently exist as a text chat program running on a Raspberry Pi. You do not
have access to motors, sensors, a camera, a microphone, files, a web browser, or
the physical world. Never claim that you performed a physical action. Be helpful,
honest about uncertainty, and keep most replies short enough for future speech."""


class ConfigurationError(ValueError):
    """Raised when required local configuration is absent or invalid."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class LLMClient(Protocol):
    def respond(self, messages: Sequence[ChatMessage]) -> str: ...


class OpenAIResponsesClient:
    """Thin adapter around OpenAI's Responses API."""

    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY is not set")
        if not model:
            raise ConfigurationError("BERTROBO_MODEL must not be empty")

        try:
            from openai import OpenAI
        except ImportError as error:
            raise ConfigurationError(
                "OpenAI SDK is missing; run '.venv/bin/python -m pip install -e .[dev]'"
            ) from error

        self._client = OpenAI(api_key=api_key)
        self._model = model

    @classmethod
    def from_environment(cls) -> "OpenAIResponsesClient":
        return cls(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model=os.environ.get("BERTROBO_MODEL", "gpt-5-mini"),
        )

    def respond(self, messages: Sequence[ChatMessage]) -> str:
        try:
            response = self._client.responses.create(
                model=self._model,
                instructions=SYSTEM_PROMPT,
                input=[{"role": message.role, "content": message.content} for message in messages],
            )
        except Exception as error:  # SDK exposes several transport/API error types.
            raise RuntimeError(str(error)) from error

        text = response.output_text.strip()
        if not text:
            raise RuntimeError("language service returned no text")
        return text


class ChatSession:
    """A bounded, in-memory conversation. Durable memory arrives in Stage 4."""

    def __init__(self, client: LLMClient, max_messages: int = 16) -> None:
        if max_messages < 2:
            raise ValueError("max_messages must be at least 2")
        self._client = client
        self._max_messages = max_messages
        self.messages: list[ChatMessage] = []

    def reply(self, user_text: str) -> str:
        clean_text = user_text.strip()
        if not clean_text:
            raise ValueError("user message must not be empty")

        self.messages.append(ChatMessage("user", clean_text))
        self.messages = self.messages[-self._max_messages :]
        reply = self._client.respond(self.messages)
        self.messages.append(ChatMessage("assistant", reply))
        self.messages = self.messages[-self._max_messages :]
        return reply
