from datetime import datetime, timedelta, timezone

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


def event_payload() -> dict:
    now = datetime.now(tz=timezone.utc)
    return {
        "title": "Sunset Social",
        "description": "Rooftop meetup",
        "category": "networking",
        "location_name": "Marina Rooftop",
        "latitude": 25.2048,
        "longitude": 55.2708,
        "address": "Dubai Marina",
        "city": "dubai",
        "starts_at": (now + timedelta(hours=1)).isoformat(),
        "ends_at": (now + timedelta(hours=3)).isoformat(),
        "is_public": True,
    }


def test_create_and_list_events(client: TestClient) -> None:
    user_data = register_user(client, "event_host", "event_host@example.com")
    headers = auth_header(user_data["tokens"]["access_token"])

    create_response = client.post(f"{BASE}/events", json=event_payload(), headers=headers)
    assert create_response.status_code == 201
    created_event = create_response.json()["data"]
    assert created_event["title"] == "Sunset Social"

    list_response = client.get(f"{BASE}/events")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["count"] >= 1


def test_event_update_is_host_only(client: TestClient) -> None:
    host = register_user(client, "host_user", "host@example.com")
    other = register_user(client, "other_user", "other@example.com")

    create_response = client.post(
        f"{BASE}/events",
        json=event_payload(),
        headers=auth_header(host["tokens"]["access_token"]),
    )
    event_id = create_response.json()["data"]["id"]

    forbidden_update = client.patch(
        f"{BASE}/events/{event_id}",
        json={"title": "Hijacked"},
        headers=auth_header(other["tokens"]["access_token"]),
    )
    assert forbidden_update.status_code == 403
