import pytest

from tests.dummy.auth.fake_user import FakeUser


@pytest.mark.asyncio
async def test_signup(async_client):
    fake_user = FakeUser.build()

    response = await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "User signed up successfully"
    assert "session_uuid" in response.cookies


@pytest.mark.asyncio
async def test_signup_duplicate_email(async_client):
    fake_user = FakeUser.build()

    await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    response = await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_login(async_client):
    fake_user = FakeUser.build()

    await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "User logged in successfully"
    assert "session_uuid" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_password(async_client):
    fake_user = FakeUser.build()

    await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": fake_user.email,
            "password": "WrongPassword1!",
            "captcha_token": "dummy_token",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    fake_user = FakeUser.build()

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": fake_user.email,
            "password": fake_user.password,
            "captcha_token": "dummy_token",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"] == "Invalid credentials"
