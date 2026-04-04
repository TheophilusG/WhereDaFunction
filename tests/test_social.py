from fastapi.testclient import TestClient


BASE = "/api/v1"


def register_user(client: TestClient, username: str, email: str) -> dict:
    response = client.post(
        f"{BASE}/auth/register",
        json={
            "username": username,
            "full_name": f"{username} full",
            "email": email,
            "password": "password123",
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


def auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_friend_request_accept_and_list(client: TestClient) -> None:
    user_a = register_user(client, "friend_a", "friend_a@example.com")
    user_b = register_user(client, "friend_b", "friend_b@example.com")

    send_response = client.post(
        f"{BASE}/friends/request",
        json={"addressee_id": user_b["user"]["id"]},
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert send_response.status_code == 201
    friendship_id = send_response.json()["data"]["id"]

    accept_response = client.patch(
        f"{BASE}/friends/{friendship_id}/accept",
        headers=auth_header(user_b["tokens"]["access_token"]),
    )
    assert accept_response.status_code == 200

    list_response = client.get(
        f"{BASE}/users/me/friends",
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["count"] == 1


def test_location_update_and_friend_lookup(client: TestClient) -> None:
    user_a = register_user(client, "loc_a", "loc_a@example.com")
    user_b = register_user(client, "loc_b", "loc_b@example.com")

    send_response = client.post(
        f"{BASE}/friends/request",
        json={"addressee_id": user_b["user"]["id"]},
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    friendship_id = send_response.json()["data"]["id"]

    client.patch(
        f"{BASE}/friends/{friendship_id}/accept",
        headers=auth_header(user_b["tokens"]["access_token"]),
    )

    update_response = client.post(
        f"{BASE}/location/update",
        json={"latitude": 24.4539, "longitude": 54.3773, "accuracy": 5.0},
        headers=auth_header(user_b["tokens"]["access_token"]),
    )
    assert update_response.status_code == 200

    list_response = client.get(
        f"{BASE}/location/friends",
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["count"] == 1
