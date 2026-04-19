"""Test configuration: mock Redis with fakeredis."""

import pytest
import fakeredis.aioredis


@pytest.fixture
def fake_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)
