from abc import ABC, abstractmethod
from typing import AsyncIterator

from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.models import MiMoModels, DeepSeekModels, OpenAIModels


class LLMProvider(ABC):
    """LLM 统一抽象接口"""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """同步对话"""
        ...

    @abstractmethod
    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """流式对话"""
        ...


class MiMoProvider(LLMProvider):
    """MiMo API（OpenAI 兼容接口）"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.mimo_api_key,
            base_url=settings.mimo_base_url,
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", MiMoModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", MiMoModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class DeepSeekProvider(LLMProvider):
    """DeepSeek API（OpenAI 兼容接口）"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", DeepSeekModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", DeepSeekModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIProvider(LLMProvider):
    """OpenAI 兼容接口"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", OpenAIModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        return response.choices[0].message.content or ""

    async def chat_stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", OpenAIModels.DEFAULT),
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def get_llm_provider() -> LLMProvider:
    """根据配置返回对应的 LLM Provider 实例"""
    settings = get_settings()
    providers = {
        "mimo": MiMoProvider,
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
    }
    provider_cls = providers.get(settings.llm_provider)
    if not provider_cls:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    return provider_cls()
