import os
from typing import Any, Dict, List, Optional
from yukta.core.Clients import VLLMClient

_VLLM_BASE = os.getenv("VLLM_BASE_URL", "http://192.168.200.46:11449")
_VLLM_MODEL = os.getenv("VLLM_MODEL", "qwen3-6-27b")


class _Qwen3VLLMClient(VLLMClient):
    """VLLMClient that injects enable_thinking=false for Qwen3 models."""

    def generate(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs,
    ):
        # Qwen3 thinking off — pass as chat_template_kwargs at API level
        kwargs.setdefault("chat_template_kwargs", {"enable_thinking": False})
        return super().generate(messages=messages, tools=tools, stream=stream, **kwargs)


def make_llm_client(temperature: float = 0.4) -> _Qwen3VLLMClient:
    return _Qwen3VLLMClient(
        model_name=_VLLM_MODEL,
        base_url=_VLLM_BASE,
        temperature=temperature,
    )
