# 后端说明

## 启动

```bash
python -m pip install -r requirements.txt
python start_server.py
```

或：

```bash
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

## 环境变量

```env
DEEPSEEK_API_KEY=your_api_key
# 或 OPENAI_API_KEY=your_api_key
# 或 API_KEY=your_api_key

API_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-reasoner
DEBUG_MODE=True
FRONTEND_URL=http://localhost:5173
```

## 测试

```bash
python -m pytest -q
```

## 核心接口

- `POST /api/divination/generate-line`
- `POST /api/divination/generate`
- `POST /api/divination/interpret`
- `GET /api/divination/karma-status`
- `POST /api/divination/recharge`
- `GET /api/divination/rate-limit-status`
