import os
from typing import Any, Dict, List, Optional
from yukta.core.Clients import VLLMClient

def _normalize_base(url: str) -> str:
    # VLLMClient appends the "/v1/" prefix to every endpoint itself, so the base
    # must NOT already end in /v1 (the .env value does → would yield /v1/v1/...).
    url = (url or "").rstrip("/")
    if url.endswith("/v1"):
        url = url[: -len("/v1")]
    return url


_VLLM_BASE = _normalize_base(os.getenv("VLLM_BASE_URL", "http://192.168.200.23:11642"))
_VLLM_MODEL = os.getenv("VLLM_MODEL", "qwen36-35b")


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
