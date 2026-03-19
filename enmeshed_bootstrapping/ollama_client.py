# pyright: reportUnknownMemberType = false, reportAny = false, reportExplicitAny = false

from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import Any

import ollama
from ollama import ChatResponse, Message, Tool


class OllamaClient:
    """Ollama wrapper with fixed model and think settings."""

    _model: str
    _client: ollama.Client

    def __init__(
        self,
        model: str,
        ollama_host: str | None = None,
    ) -> None:
        self._model = model
        self._client = ollama.Client(host=ollama_host)

    @lru_cache(maxsize=1)
    def _is_thinking_model(self) -> bool:
        capabilities = self._client.show(self._model).capabilities
        if capabilities is None:
            return False
        return "thinking" in capabilities

    def chat(
        self,
        messages: Sequence[Mapping[str, Any] | Message] | None = None,
        *,
        tools: Sequence[Mapping[str, Any] | Tool | Callable[..., Any]] | None = None,
    ) -> ChatResponse:
        return self._client.chat(
            model=self._model,
            messages=messages,
            tools=tools,
            think=self._is_thinking_model(),
        )
