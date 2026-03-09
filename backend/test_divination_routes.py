import hashlib
from types import SimpleNamespace

import pytest
from fastapi import Response
from fastapi.testclient import TestClient

import api_main
from app.routers import divination


class StableAgent:
    def consult(self, hexagram_data, user_input, stream_mode=False):
        return "【技师在思考】稳住\n\n【正式解读】一切正常"

    def get_hexagram_info(self, hexagram_name, hexagram_nature):
        return {
            "composition": hexagram_nature.replace("\n", "上"),
            "meaning": f"{hexagram_name}说明",
            "quote": "测试卦辞",
        }


class ConfigErrorAgent:
    def __init__(self):
        raise ValueError("缺少 API Key")


class EmptyInterpretationAgent(StableAgent):
    def consult(self, hexagram_data, user_input, stream_mode=False):
        return ""


class PreviewBlockedKarmaSystem:
    def __init__(self):
        self.max_vitality = 100.0
        self.current_vitality = 2.0
        self.total_uses = 0
        self.last_active_time = 0

    def update_vitality(self):
        return {"current_vitality": self.current_vitality}

    def calculate_cost_preview(self):
        return {
            "can_afford": False,
            "estimated_cost": 15.0,
            "current_vitality": self.current_vitality,
            "delta_t": 1.0,
            "is_glitch": True,
            "warning_level": "DANGER",
        }

    def get_status(self):
        return {
            "current_vitality": self.current_vitality,
            "max_vitality": self.max_vitality,
            "percentage": 2.0,
            "total_uses": self.total_uses,
            "can_use": True,
        }


class CommitFailKarmaSystem:
    def __init__(self):
        self.max_vitality = 100.0
        self.current_vitality = 50.0
        self.total_uses = 0
        self.last_active_time = 0

    def update_vitality(self):
        return {"current_vitality": self.current_vitality}

    def calculate_cost_preview(self):
        return {
            "can_afford": True,
            "estimated_cost": 5.0,
            "current_vitality": self.current_vitality,
            "delta_t": 10.0,
            "is_glitch": False,
            "warning_level": "NORMAL",
        }

    def commit_transaction(self, cost):
        return False

    def record_use(self):
        raise AssertionError("结算失败时不应记录使用")


@pytest.fixture(autouse=True)
def reset_divination_state():
    divination.user_karma_systems.clear()
    divination.request_records.clear()
    divination.user_locks.clear()
    yield
    divination.user_karma_systems.clear()
    divination.request_records.clear()
    divination.user_locks.clear()


def make_request(headers=None, cookies=None, host="127.0.0.1"):
    return SimpleNamespace(
        headers=headers or {},
        cookies=cookies or {},
        client=SimpleNamespace(host=host) if host is not None else None,
    )


def sample_hexagram_data():
    return {
        "original_name": "乾为天",
        "changed_name": "坤为地",
        "original_binary": [1, 1, 1, 1, 1, 1],
        "changed_binary": [0, 0, 0, 0, 0, 0],
        "original_symbol": "☰\n☰",
        "changed_symbol": "☷\n☷",
        "original_nature": "天\n天",
        "changed_nature": "地\n地",
        "original_hexagram": [7, 7, 7, 7, 7, 7],
        "changed_hexagram": [8, 8, 8, 8, 8, 8],
    }


def test_get_client_ip_prefers_forwarded_headers():
    forwarded_req = make_request(headers={"X-Forwarded-For": "1.1.1.1, 2.2.2.2"}, host="9.9.9.9")
    cf_req = make_request(headers={"CF-Connecting-IP": "3.3.3.3"}, host="9.9.9.9")
    direct_req = make_request(headers={}, host="4.4.4.4")
    unknown_req = make_request(headers={}, host=None)

    assert divination.get_client_ip(forwarded_req) == "1.1.1.1"
    assert divination.get_client_ip(cf_req) == "3.3.3.3"
    assert divination.get_client_ip(direct_req) == "4.4.4.4"
    assert divination.get_client_ip(unknown_req) == "unknown"


def test_get_user_id_prefers_header_then_cookie_then_hash():
    header_response = Response()
    header_req = make_request(
        headers={"X-Device-ID": "device_12345"},
        cookies={"user_id": "cookie_12345"},
    )
    assert divination.get_user_id(header_req, header_response) == "device_12345"
    assert "user_id=device_12345" in header_response.headers["set-cookie"]

    cookie_response = Response()
    cookie_req = make_request(
        headers={"X-Device-ID": "bad"},
        cookies={"user_id": "cookie_12345"},
    )
    assert divination.get_user_id(cookie_req, cookie_response) == "cookie_12345"
    assert "user_id=cookie_12345" in cookie_response.headers["set-cookie"]

    fallback_response = Response()
    fallback_req = make_request(
        headers={"User-Agent": "pytest-agent"},
        cookies={"user_id": "short"},
        host="8.8.8.8",
    )
    expected = hashlib.md5("8.8.8.8:pytest-agent".encode()).hexdigest()
    assert divination.get_user_id(fallback_req, fallback_response) == expected
    assert "user_id=" in fallback_response.headers["set-cookie"]
    assert divination.is_valid_user_id("short") is False


def test_rate_limit_helpers_cleanup_and_block(monkeypatch):
    now = 10_000.0
    user_id = "device_12345"
    divination.request_records[user_id]["interpret"] = [now - 4_000, now - 100, now - 10]
    monkeypatch.setattr(divination.time, "time", lambda: now)

    info = divination.get_rate_limit_info(user_id, "interpret", max_requests=2, window_seconds=3_600)
    allowed, checked = divination.check_rate_limit(user_id, "interpret", max_requests=2, window_seconds=3_600)
    divination.record_rate_limit_request(user_id, "interpret")

    assert divination.request_records[user_id]["interpret"] == [now - 100, now - 10, now]
    assert info["current_requests"] == 2
    assert info["is_limited"] is True
    assert info["retry_after"] == 3501
    assert allowed is False
    assert checked["remaining_requests"] == 0


def test_cleanup_inactive_users_removes_stale_state(monkeypatch):
    now = 100_000.0
    stale_system = divination.KarmaSystem()
    stale_system.last_active_time = now - (25 * 3600)
    fresh_system = divination.KarmaSystem()
    fresh_system.last_active_time = now - 60

    divination.user_karma_systems["stale_user"] = stale_system
    divination.user_karma_systems["fresh_user"] = fresh_system
    divination.request_records["stale_user"]["interpret"] = [now - 4_000]
    divination.request_records["fresh_user"]["interpret"] = [now - 120]
    divination.request_records["empty_user"]

    monkeypatch.setattr(divination.time, "time", lambda: now)
    divination.cleanup_inactive_users()

    assert "stale_user" not in divination.user_karma_systems
    assert "fresh_user" in divination.user_karma_systems
    assert "stale_user" not in divination.request_records
    assert "empty_user" not in divination.request_records
    assert "fresh_user" in divination.request_records


def test_generate_endpoint_returns_500_when_processor_fails(monkeypatch):
    def broken_output():
        raise RuntimeError("generator boom")

    monkeypatch.setattr(divination, "output_hexagram_results", broken_output)

    with TestClient(api_main.app) as client:
        response = client.post("/api/divination/generate")

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["error"] == "生成卦象失败"
    assert detail["message"] == "generator boom"


def test_interpret_invalid_hex_lines_falls_back_to_backend_generation(monkeypatch):
    calls = []

    def fake_output_hexagram_results(original_hexagram_values=None):
        calls.append(original_hexagram_values)
        return sample_hexagram_data()

    monkeypatch.setattr(divination, "output_hexagram_results", fake_output_hexagram_results)
    monkeypatch.setattr(divination, "YiMasterAgent", StableAgent)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/interpret",
            json={"question": "测试问题", "hex_lines": [1, 2, 3, 4, 5, 6]},
            headers={"X-Device-ID": "device_12345"},
        )

    assert response.status_code == 200
    assert calls == [None]


def test_interpret_returns_500_when_ai_config_invalid(monkeypatch):
    monkeypatch.setattr(divination, "output_hexagram_results", lambda **kwargs: sample_hexagram_data())
    monkeypatch.setattr(divination, "YiMasterAgent", ConfigErrorAgent)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/interpret",
            json={"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]},
            headers={"X-Device-ID": "device_12345"},
        )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail["error"] == "AI服务配置错误"
    assert "API Key" in detail["message"]


def test_interpret_returns_502_when_ai_returns_empty_content(monkeypatch):
    monkeypatch.setattr(divination, "output_hexagram_results", lambda **kwargs: sample_hexagram_data())
    monkeypatch.setattr(divination, "YiMasterAgent", EmptyInterpretationAgent)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/interpret",
            json={"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]},
            headers={"X-Device-ID": "device_12345"},
        )
        rate_limit_status = client.get(
            "/api/divination/rate-limit-status",
            headers={"X-Device-ID": "device_12345"},
        ).json()

    assert response.status_code == 502
    assert response.json()["detail"]["error"] == "AI解读失败"
    assert rate_limit_status["status"]["interpret"]["current_requests"] == 0


def test_interpret_returns_429_when_preview_is_glitched(monkeypatch):
    user_id = "device_12345"
    divination.user_karma_systems[user_id] = PreviewBlockedKarmaSystem()
    monkeypatch.setattr(divination, "output_hexagram_results", lambda **kwargs: sample_hexagram_data())
    monkeypatch.setattr(divination, "YiMasterAgent", StableAgent)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/interpret",
            json={"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]},
            headers={"X-Device-ID": user_id},
        )

    assert response.status_code == 429
    detail = response.json()["detail"]
    assert detail["error"] == "元气不足"
    assert "操作过于频繁" in detail["message"]


def test_interpret_returns_500_when_commit_fails(monkeypatch):
    user_id = "device_12345"
    divination.user_karma_systems[user_id] = CommitFailKarmaSystem()
    monkeypatch.setattr(divination, "output_hexagram_results", lambda **kwargs: sample_hexagram_data())
    monkeypatch.setattr(divination, "YiMasterAgent", StableAgent)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/interpret",
            json={"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]},
            headers={"X-Device-ID": user_id},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "结算失败，请重试"


def test_recharge_returns_429_when_rate_limited(monkeypatch):
    now = 20_000.0
    user_id = "device_12345"
    divination.request_records[user_id]["recharge"] = [now - 10] * 5
    monkeypatch.setattr(divination.time, "time", lambda: now)

    with TestClient(api_main.app) as client:
        response = client.post(
            "/api/divination/recharge",
            headers={"X-Device-ID": user_id},
        )

    assert response.status_code == 429
    detail = response.json()["detail"]
    assert detail["error"] == "请求过于频繁"
    assert detail["limit_info"]["current_requests"] == 5
