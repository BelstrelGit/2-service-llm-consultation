"""Test configuration: mock Redis with fakeredis, centralized patches."""

import pytest
import fakeredis.aioredis


@pytest.fixture
def fake_redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def patch_redis(fake_redis, mocker):
    mocker.patch("app.bot.handlers.get_redis", return_value=fake_redis)
