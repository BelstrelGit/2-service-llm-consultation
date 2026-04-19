"""Integration tests for Auth Service endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.main import app
from app.api.deps import get_db

engine_test = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_full_flow(client: AsyncClient):
    # Register
    resp = await client.post(
        "/auth/register",
        json={"email": "gorelikov@email.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Login
    resp = await client.post(
        "/auth/login",
        data={"username": "gorelikov@email.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # Me
    resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    user = resp.json()
    assert user["email"] == "gorelikov@email.com"
    assert user["role"] == "user"
    assert "id" in user
    assert "created_at" in user


async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "dup@email.com", "password": "pass1"},
    )
    resp = await client.post(
        "/auth/register",
        json={"email": "dup@email.com", "password": "pass2"},
    )
    assert resp.status_code == 409


async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "user@email.com", "password": "correct"},
    )
    resp = await client.post(
        "/auth/login",
        data={"username": "user@email.com", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_me_without_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_invalid_token(client: AsyncClient):
    resp = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert resp.status_code == 401
