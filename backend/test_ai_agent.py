from types import SimpleNamespace

import pytest

from app.services import ai_agent


def build_non_stream_response(reasoning=None, content=None):
    message = SimpleNamespace(reasoning_content=reasoning, content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def build_stream_chunk(reasoning=None, content=None):
    delta = SimpleNamespace(reasoning_content=reasoning, content=content)
    choice = SimpleNamespace(delta=delta)
    return SimpleNamespace(choices=[choice])


class FakeCompletions:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeOpenAIClient:
    def __init__(self, response=None, error=None):
        self.chat = SimpleNamespace(completions=FakeCompletions(response=response, error=error))


class OpenAIFactory:
    def __init__(self, client):
        self.client = client
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return self.client


def create_agent(
    monkeypatch,
    response=None,
    error=None,
    base_url="https://example.com/v1",
    model="test-model",
):
    fake_client = FakeOpenAIClient(response=response, error=error)
    factory = OpenAIFactory(fake_client)
    monkeypatch.setattr(ai_agent.settings, "API_KEY", "test-key", raising=False)
    monkeypatch.setattr(ai_agent.settings, "API_BASE_URL", base_url, raising=False)
    monkeypatch.setattr(ai_agent.settings, "AI_MODEL", model, raising=False)
    monkeypatch.setattr(ai_agent, "OpenAI", factory)
    return ai_agent.YiMasterAgent(), fake_client, factory


def sample_hexagram_data(original_hexagram=None, original_name="乾为天"):
    return {
        "original_hexagram": original_hexagram or [9, 9, 9, 9, 9, 9],
        "original_name": original_name,
        "original_nature": "天\n天",
        "changed_name": "坤为地",
        "changed_nature": "地\n地",
    }


def test_remove_markdown_removes_images_before_links():
    text = """# 标题
![配图](https://example.com/image.png)
[链接](https://example.com)
- **条目**
> `引用`
"""

    cleaned = ai_agent.remove_markdown(text)

    assert "标题" in cleaned
    assert "链接" in cleaned
    assert "条目" in cleaned
    assert "image.png" not in cleaned
    assert "!配图" not in cleaned
    assert "[" not in cleaned
    assert "`" not in cleaned


def test_agent_init_requires_api_key(monkeypatch):
    monkeypatch.setattr(ai_agent.settings, "API_KEY", None, raising=False)

    with pytest.raises(ValueError, match="API_KEY"):
        ai_agent.YiMasterAgent()


def test_consult_non_stream_uses_yongjiu_and_fallbacks(monkeypatch):
    agent, fake_client, factory = create_agent(
        monkeypatch,
        response=build_non_stream_response(reasoning=None, content=None),
    )

    result = agent.consult(sample_hexagram_data(), "测试问题", stream_mode=False)

    assert factory.calls[0]["api_key"] == "test-key"
    assert factory.calls[0]["base_url"] == "https://example.com/v1"
    call = fake_client.chat.completions.calls[0]
    user_prompt = call["messages"][1]["content"]

    assert call["stream"] is False
    assert call["model"] == "test-model"
    assert "动爻：用九" in user_prompt
    assert "【技师在思考】" in result
    assert "无需多言" in result
    assert "请稍候" in result


def test_consult_stream_strips_markdown_output(monkeypatch):
    stream_response = [
        build_stream_chunk(reasoning="**推理**", content=None),
        build_stream_chunk(reasoning=None, content="# 建议\n[继续](https://example.com)"),
    ]
    agent, fake_client, _ = create_agent(monkeypatch, response=stream_response)

    result = agent.consult(
        sample_hexagram_data(original_hexagram=[7, 8, 9, 8, 6, 7], original_name="火天大有"),
        "测试问题",
        stream_mode=True,
    )

    assert fake_client.chat.completions.calls[0]["stream"] is True
    assert "**" not in result
    assert "#" not in result
    assert "https://example.com" not in result
    assert "推理" in result
    assert "建议" in result
    assert "继续" in result


def test_consult_wraps_upstream_errors(monkeypatch):
    agent, _, _ = create_agent(monkeypatch, error=RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="技师连接断开：boom"):
        agent.consult(sample_hexagram_data(), "测试问题", stream_mode=False)


def test_get_hexagram_info_parses_fenced_json_and_fills_defaults(monkeypatch):
    response = build_non_stream_response(
        content='```json\n{"meaning":"**吉**"}\n```'
    )
    agent, _, _ = create_agent(monkeypatch, response=response)

    result = agent.get_hexagram_info("火天大有", "离\n乾")

    assert result["composition"] == "离上乾"
    assert result["meaning"] == "吉"
    assert "卦象如人生" in result["quote"]


def test_get_hexagram_info_raises_on_invalid_json(monkeypatch):
    response = build_non_stream_response(content="not json")
    agent, _, _ = create_agent(monkeypatch, response=response)

    with pytest.raises(ValueError):
        agent.get_hexagram_info("火天大有", "离\n乾")


def test_get_hexagram_info_returns_fallback_on_generic_error(monkeypatch):
    agent, _, _ = create_agent(monkeypatch, error=RuntimeError("network down"))

    result = agent.get_hexagram_info("火天大有", "离\n乾")

    assert result["composition"] == "离上乾"
    assert "火天大有卦" in result["meaning"]
    assert "卦象如人生" in result["quote"]
