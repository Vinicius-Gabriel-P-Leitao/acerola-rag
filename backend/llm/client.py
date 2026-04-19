from typing import Any

from llama_index.core.bridge.pydantic import Field
from llama_index.core.llms import (
    CompletionResponse,
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from openai import OpenAI

# URLs base para cada provider OpenAI-compatível
_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

PROVIDER_MODELS: dict[str, list[str]] = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o3-mini"],
    "ollama": ["llama3.2", "mistral", "codellama", "qwen2.5"],
    "gemini": [
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
    "claude": ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-7"],
}


# ── OpenAI-compatible (OpenAI, Ollama, Gemini) ────────────────────────────────


class OpenAISDKLLM(CustomLLM):
    model: str = Field(default="gpt-4o-mini")
    api_key: str = Field(default="")
    base_url: str = Field(default="")
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=1024)
    system_prompt: str | None = Field(default=None)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=self.model,
            context_window=128_000,
            num_output=self.max_tokens,
        )

    def _client(self) -> OpenAI:
        kwargs: dict[str, Any] = {"api_key": self.api_key or "sk-no-key"}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAI(**kwargs)

    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self._client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return CompletionResponse(text=response.choices[0].message.content or "")

    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self._client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        accumulated = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            accumulated += delta

            yield CompletionResponse(text=accumulated, delta=delta)


# ── Anthropic (Claude) ────────────────────────────────────────────────────────


class AnthropicLLM(CustomLLM):
    model: str = Field(default="claude-sonnet-4-6")
    api_key: str = Field(default="")
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=1024)
    system_prompt: str | None = Field(default=None)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=self.model,
            context_window=200_000,
            num_output=self.max_tokens,
        )

    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        from anthropic import Anthropic

        req_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.system_prompt:
            req_kwargs["system"] = self.system_prompt

        message = Anthropic(api_key=self.api_key).messages.create(**req_kwargs)
        text = "".join(getattr(block, "text", "") for block in message.content)
        return CompletionResponse(text=text)

    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        from anthropic import Anthropic

        req_kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.system_prompt:
            req_kwargs["system"] = self.system_prompt

        accumulated = ""
        with Anthropic(api_key=self.api_key).messages.stream(**req_kwargs) as stream:
            for text in stream.text_stream:
                accumulated += text
                yield CompletionResponse(text=accumulated, delta=text)


# ── Factory ───────────────────────────────────────────────────────────────────


def create_llm(
    provider: str,
    model: str,
    api_key: str,
    ollama_base_url: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str | None = None,
) -> CustomLLM:
    if provider == "openai":
        return OpenAISDKLLM(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    if provider == "ollama":
        return OpenAISDKLLM(
            model=model,
            api_key="ollama",
            base_url=ollama_base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    if provider == "gemini":
        return OpenAISDKLLM(
            model=model,
            api_key=api_key,
            base_url=_GEMINI_BASE_URL,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    if provider == "claude":
        return AnthropicLLM(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )
    raise ValueError(
        f"Provider desconhecido: '{provider}'. Use: openai | ollama | gemini | claude"
    )
