import pytest, asyncio
from packages.common.config import settings
from packages.common.logger import get_logger, set_correlation_id, get_correlation_id
from packages.common.exceptions import NotFoundException
from packages.common.resilience import CircuitBreaker, CircuitState
from packages.common.pagination import CursorPagination
from packages.security.crypto import hash_password, verify_password, generate_otp, encrypt_payload, decrypt_payload
from packages.security.jwt import create_access_token, decode_token
from packages.events.schemas import MessageSentEvent
from packages.events.bus import InMemoryEventBus

def test_settings():
    assert settings.PROJECT_NAME is not None

def test_correlation():
    set_correlation_id("c-123")
    assert get_correlation_id() == "c-123"

def test_exceptions():
    exc = NotFoundException("Missing item")
    assert exc.status_code == 404

def test_crypto():
    h = hash_password("pass12345")
    assert verify_password("pass12345", h)
    assert not verify_password("wrong", h)
    assert len(generate_otp(6)) == 6
    enc = encrypt_payload("Hello", "secret")
    assert decrypt_payload(enc, "secret") == "Hello"

def test_jwt():
    t = create_access_token("usr-1", "dev-1", "alex")
    c = decode_token(t)
    assert c.sub == "usr-1"
    assert c.device_id == "dev-1"

def test_pagination():
    cur = CursorPagination.encode_cursor({"seq": 100})
    dec = CursorPagination.decode_cursor(cur)
    assert dec["seq"] == 100

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker("test-cb", failure_threshold=2)
    async def bad(): raise ValueError("err")
    with pytest.raises(ValueError): await cb.call(bad)
    with pytest.raises(ValueError): await cb.call(bad)
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_events():
    bus = InMemoryEventBus()
    res = []
    async def handler(e): res.append(e)
    await bus.subscribe("msg", handler)
    await bus.publish("msg", MessageSentEvent(partition_key="c-1", message_id="m-1", conversation_id="c-1", sender_id="u-1", sequence_number=1, content="hi"))
    await asyncio.sleep(0.05)
    assert len(res) == 1
