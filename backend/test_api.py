from fastapi.testclient import TestClient

import api_main
from app.routers import divination


class SuccessfulAgent:
    def consult(self, hexagram_data, user_input, stream_mode=False):
        return "【技师在思考】一切正常\n\n【正式解读】测试解读成功"

    def get_hexagram_info(self, hexagram_name, hexagram_nature):
        return {
            "composition": hexagram_nature.replace("\n", "上"),
            "meaning": f"{hexagram_name} 测试说明",
            "quote": "测试卦辞",
        }


class FailingAgent:
    def consult(self, hexagram_data, user_input, stream_mode=False):
        raise RuntimeError("上游 AI 超时")

    def get_hexagram_info(self, hexagram_name, hexagram_nature):
        return None


def test_root_endpoint():
    with TestClient(api_main.app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_line_endpoint():
    with TestClient(api_main.app) as client:
        response = client.post("/api/divination/generate-line")

    assert response.status_code == 200
    data = response.json()
    assert data["value"] in {6, 7, 8, 9}
    assert data["binary"] in {0, 1}
    assert data["name"] in {"老阴", "少阳", "少阴", "老阳"}
    assert "karma_status" in data


def test_rate_limit_status_endpoint():
    with TestClient(api_main.app) as client:
        response = client.get("/api/divination/rate-limit-status")

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "status" in data
    assert "interpret" in data["status"]
    assert "recharge" in data["status"]
    assert response.cookies.get("user_id")


def test_rate_limit_status_reuses_cookie_based_user_id():
    device_id = "123e4567-e89b-12d3-a456-426614174000"

    with TestClient(api_main.app) as client:
        first_response = client.get(
            "/api/divination/rate-limit-status",
            headers={"X-Device-ID": device_id},
        )

        assert first_response.status_code == 200
        assert first_response.cookies.get("user_id") == device_id
        assert first_response.json()["user_id"] == f"{device_id[:8]}..."

        cookie_response = client.get("/api/divination/rate-limit-status")

        assert cookie_response.status_code == 200
        assert cookie_response.json()["user_id"] == f"{device_id[:8]}..."


def test_interpret_failure_does_not_consume_vitality_or_rate_limit(monkeypatch):
    device_id = "123e4567-e89b-12d3-a456-426614174101"
    payload = {"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]}

    monkeypatch.setattr(divination, "YiMasterAgent", FailingAgent)

    with TestClient(api_main.app) as client:
        before_status = client.get(
            "/api/divination/karma-status",
            headers={"X-Device-ID": device_id},
        ).json()

        response = client.post(
            "/api/divination/interpret",
            json=payload,
            headers={"X-Device-ID": device_id},
        )

        after_status = client.get(
            "/api/divination/karma-status",
            headers={"X-Device-ID": device_id},
        ).json()

        rate_limit_status = client.get(
            "/api/divination/rate-limit-status",
            headers={"X-Device-ID": device_id},
        ).json()

    assert response.status_code == 502
    assert before_status["current_vitality"] == after_status["current_vitality"] == 100.0
    assert rate_limit_status["status"]["interpret"]["current_requests"] == 0


def test_interpret_and_recharge_use_separate_rate_limit_buckets(monkeypatch):
    device_id = "123e4567-e89b-12d3-a456-426614174202"
    payload = {"question": "测试问题", "hex_lines": [7, 7, 7, 7, 7, 7]}

    monkeypatch.setattr(divination, "YiMasterAgent", SuccessfulAgent)

    with TestClient(api_main.app) as client:
        interpret_response = client.post(
            "/api/divination/interpret",
            json=payload,
            headers={"X-Device-ID": device_id},
        )
        recharge_response = client.post(
            "/api/divination/recharge",
            headers={"X-Device-ID": device_id},
        )
        status = client.get(
            "/api/divination/rate-limit-status",
            headers={"X-Device-ID": device_id},
        ).json()

    assert interpret_response.status_code == 200
    assert recharge_response.status_code == 200
    assert status["status"]["interpret"]["current_requests"] == 1
    assert status["status"]["recharge"]["current_requests"] == 1
