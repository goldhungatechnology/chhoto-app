import json

from src.shared.infrastructure.background_task_manager.adapter.dramatiq.dramatiq_background_task_manager import (
    DLQMiddleware,
)


class _FakeRedis:
    def __init__(self):
        self.kv: dict[str, str] = {}
        self.list_data: list[str] = []

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self.kv[key] = value

    def lpush(self, _key: str, value: str) -> None:
        self.list_data.insert(0, value)

    def ltrim(self, _key: str, _start: int, _end: int) -> None:
        return None

    def expire(self, _key: str, _ttl: int) -> None:
        return None


class _FakeBrokerWithCallableClient:
    def __init__(self, redis_client: _FakeRedis):
        self.client = redis_client


class _FakeMessage:
    def __init__(self, retries: int, max_retries: int):
        self.actor_name = "sample-task"
        self.message_id = "msg-1"
        self.options = {"retries": retries, "max_retries": max_retries}
        self.args = (1, 2)
        self.kwargs = {"foo": "bar"}


def test_dlq_not_stored_before_retries_exhausted(monkeypatch):
    middleware = DLQMiddleware()
    stored = {"called": False}

    def _fake_store(_broker, _message):
        stored["called"] = True

    monkeypatch.setattr(middleware, "_store_to_dlq", _fake_store)

    middleware.after_nack(
        broker=object(),
        message=_FakeMessage(retries=0, max_retries=3),
    )

    assert stored["called"] is False


def test_dlq_stored_when_retries_exhausted():
    middleware = DLQMiddleware()
    redis_client = _FakeRedis()
    broker = _FakeBrokerWithCallableClient(redis_client)

    middleware.after_nack(
        broker=broker,
        message=_FakeMessage(retries=3, max_retries=3),
    )

    assert "dlq_message:msg-1" in redis_client.kv
    assert redis_client.list_data

    payload = json.loads(redis_client.list_data[0])
    assert payload["message_id"] == "msg-1"
    assert payload["options"]["max_retries"] == 3
