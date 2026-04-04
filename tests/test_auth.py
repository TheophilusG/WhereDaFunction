from fastapi.testclient import TestClient


BASE = "/api/v1"


def register_user(client: TestClient, username: str, email: str, password: str = "password123") -> dict:
    response = client.post(
        f"{BASE}/auth/register",
        json={
            "username": username,
            "full_name": f"{username} full",
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_register_and_login(client: TestClient) -> None:
    register_data = register_user(client, "user_one", "one@example.com")
    assert register_data["user"]["email"] == "one@example.com"
    assert register_data["tokens"]["access_token"]
    assert register_data["tokens"]["refresh_token"]

    login_response = client.post(
        f"{BASE}/auth/login",
        json={"email": "one@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200


def test_refresh_rotates_and_revokes_old_token(client: TestClient) -> None:
    register_data = register_user(client, "user_two", "two@example.com")
    old_refresh = register_data["tokens"]["refresh_token"]

    refresh_response = client.post(
        f"{BASE}/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert refresh_response.status_code == 200
    new_refresh = refresh_response.json()["data"]["refresh_token"]
    assert new_refresh != old_refresh

    stale_refresh_response = client.post(
        f"{BASE}/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert stale_refresh_response.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    register_data = register_user(client, "user_three", "three@example.com")
    refresh_token = register_data["tokens"]["refresh_token"]

    logout_response = client.post(
        f"{BASE}/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["data"]["revoked"] is True

    refresh_response = client.post(
        f"{BASE}/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401
