# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Unified LLM client with provider abstraction for Anthropic and OpenAI."""

from __future__ import annotations

import os
import json

PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()

_anthropic_client = None
_openai_client = None


_USER_AGENT = "taatal-doc-agent/0.1.0 (digital.taatal.com)"


def _get_anthropic_client():
    """Return a cached Anthropic client instance."""
    global _anthropic_client
    if _anthropic_client is None:
        from anthropic import Anthropic
        _anthropic_client = Anthropic(
            default_headers={"User-Agent": _USER_AGENT},
        )
    return _anthropic_client


def _get_openai_client():
    """Return a cached OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(
            default_headers={"User-Agent": _USER_AGENT},
        )
    return _openai_client


_OPENAI_MODEL_MAP = {
    "sonnet": "gpt-4o-mini",
    "haiku": "gpt-4o-mini",
    "opus": "gpt-4o",
}


def _map_model(model_hint: str) -> str:
    """Map an Anthropic model hint to the equivalent OpenAI model."""
    if PROVIDER != "openai":
        return model_hint
    for key, mapped in _OPENAI_MODEL_MAP.items():
        if key in model_hint:
            return mapped
    return "gpt-4o"


def _tool_to_openai_format(tool: dict) -> dict:
    """Convert an Anthropic-style tool definition to OpenAI format."""
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool["input_schema"],
        },
    }


def create_message(
    model: str,
    max_tokens: int,
    messages: list,
    tools: list[dict] | None = None,
    tool_choice: dict | None = None,
) -> LLMResponse:
    """Send a message to the configured LLM provider and return the response.

    Args:
        model: Model identifier or hint (e.g. 'claude-sonnet-4-6-20250514').
        max_tokens: Maximum tokens in the response.
        messages: Conversation messages in Anthropic format.
        tools: Optional list of tool definitions.
        tool_choice: Optional tool choice constraint.

    Returns:
        An LLMResponse containing either text or tool-use output.
    """
    model = _map_model(model)

    if PROVIDER == "openai":
        return _call_openai(
            model, max_tokens, messages, tools, tool_choice
        )
    return _call_anthropic(
        model, max_tokens, messages, tools, tool_choice
    )


def _call_anthropic(
    model: str,
    max_tokens: int,
    messages: list,
    tools: list[dict] | None,
    tool_choice: dict | None,
) -> LLMResponse:
    """Execute a request against the Anthropic API."""
    client = _get_anthropic_client()
    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = tool_choice

    response = client.messages.create(**kwargs)
    return _parse_anthropic_response(response)


def _call_openai(
    model: str,
    max_tokens: int,
    messages: list,
    tools: list[dict] | None,
    tool_choice: dict | None,
) -> LLMResponse:
    """Execute a request against the OpenAI API."""
    client = _get_openai_client()
    oai_messages = _convert_messages_to_openai(messages)

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": oai_messages,
    }
    if tools:
        kwargs["tools"] = [_tool_to_openai_format(t) for t in tools]
    if tool_choice:
        kwargs["tool_choice"] = {
            "type": "function",
            "function": {"name": tool_choice["name"]},
        }

    response = client.chat.completions.create(**kwargs)
    return _parse_openai_response(response)


def _convert_messages_to_openai(messages: list) -> list:
    """Convert Anthropic-format messages to OpenAI chat format."""
    oai_messages = []

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if isinstance(content, str):
            oai_messages.append({"role": role, "content": content})
        elif isinstance(content, list):
            if role == "assistant":
                for block in content:
                    if block.get("type") == "tool_use":
                        oai_messages.append({
                            "role": "assistant",
                            "tool_calls": [{
                                "id": block["id"],
                                "type": "function",
                                "function": {
                                    "name": block["name"],
                                    "arguments": json.dumps(
                                        block["input"]
                                    ),
                                },
                            }],
                        })
            elif role == "user":
                for block in content:
                    if block.get("type") == "tool_result":
                        oai_messages.append({
                            "role": "tool",
                            "tool_call_id": block["tool_use_id"],
                            "content": block["content"],
                        })
        else:
            oai_messages.append(
                {"role": role, "content": str(content)}
            )

    return oai_messages


class LLMResponse:
    """Normalized response from an LLM provider."""

    def __init__(
        self,
        text: str | None = None,
        tool_name: str | None = None,
        tool_input: dict | None = None,
    ) -> None:
        self.text = text
        self.tool_name = tool_name
        self.tool_input = tool_input


def _parse_anthropic_response(response) -> LLMResponse:
    """Parse an Anthropic API response into an LLMResponse."""
    for block in response.content:
        if block.type == "tool_use":
            return LLMResponse(
                tool_name=block.name, tool_input=block.input
            )
    return LLMResponse(text=response.content[0].text)


def _parse_openai_response(response) -> LLMResponse:
    """Parse an OpenAI API response into an LLMResponse."""
    choice = response.choices[0]
    if choice.message.tool_calls:
        tc = choice.message.tool_calls[0]
        return LLMResponse(
            tool_name=tc.function.name,
            tool_input=json.loads(tc.function.arguments),
        )
    return LLMResponse(text=choice.message.content)
