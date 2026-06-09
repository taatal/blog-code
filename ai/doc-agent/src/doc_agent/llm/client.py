import os
import json

PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower()

_anthropic_client = None
_openai_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        from anthropic import Anthropic
        _anthropic_client = Anthropic()
    return _anthropic_client


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI()
    return _openai_client


_OPENAI_MODEL_MAP = {
    "sonnet": "gpt-4o-mini",
    "haiku": "gpt-4o-mini",
    "opus": "gpt-4o",
}


def _map_model(model_hint: str) -> str:
    if PROVIDER != "openai":
        return model_hint
    for key, mapped in _OPENAI_MODEL_MAP.items():
        if key in model_hint:
            return mapped
    return "gpt-4o"


def _tool_to_openai_format(tool: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool["input_schema"],
        },
    }


def create_message(model: str, max_tokens: int, messages: list, tools=None, tool_choice=None):
    model = _map_model(model)

    if PROVIDER == "openai":
        return _call_openai(model, max_tokens, messages, tools, tool_choice)
    return _call_anthropic(model, max_tokens, messages, tools, tool_choice)


def _call_anthropic(model, max_tokens, messages, tools, tool_choice):
    client = _get_anthropic_client()
    kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = tool_choice

    response = client.messages.create(**kwargs)
    return _parse_anthropic_response(response)


def _call_openai(model, max_tokens, messages, tools, tool_choice):
    client = _get_openai_client()
    oai_messages = _convert_messages_to_openai(messages)

    kwargs = {"model": model, "max_tokens": max_tokens, "messages": oai_messages}
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
                                    "arguments": json.dumps(block["input"]),
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
            oai_messages.append({"role": role, "content": str(content)})

    return oai_messages


class LLMResponse:
    def __init__(self, text=None, tool_name=None, tool_input=None):
        self.text = text
        self.tool_name = tool_name
        self.tool_input = tool_input


def _parse_anthropic_response(response) -> LLMResponse:
    for block in response.content:
        if block.type == "tool_use":
            return LLMResponse(tool_name=block.name, tool_input=block.input)
    return LLMResponse(text=response.content[0].text)


def _parse_openai_response(response) -> LLMResponse:
    choice = response.choices[0]
    if choice.message.tool_calls:
        tc = choice.message.tool_calls[0]
        return LLMResponse(
            tool_name=tc.function.name,
            tool_input=json.loads(tc.function.arguments),
        )
    return LLMResponse(text=choice.message.content)
