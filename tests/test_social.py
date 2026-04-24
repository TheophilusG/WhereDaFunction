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
        "title": "Friends Meetup",
        "description": "Social meetup",
        "category": "networking",
        "location_name": "Marina",
        "latitude": 25.2048,
        "longitude": 55.2708,
        "address": "Dubai Marina",
        "city": "dubai",
        "starts_at": (now + timedelta(hours=1)).isoformat(),
        "ends_at": (now + timedelta(hours=2)).isoformat(),
        "is_public": True,
    }


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


def test_pending_requests_and_user_search(client: TestClient) -> None:
    user_a = register_user(client, "pending_a", "pending_a@example.com")
    user_b = register_user(client, "pending_b", "pending_b@example.com")
    user_c = register_user(client, "pending_c", "pending_c@example.com")

    send_response = client.post(
        f"{BASE}/friends/request",
        json={"addressee_id": user_b["user"]["id"]},
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert send_response.status_code == 201
    friendship_id = send_response.json()["data"]["id"]

    incoming_response = client.get(
        f"{BASE}/friends/requests/incoming",
        headers=auth_header(user_b["tokens"]["access_token"]),
    )
    assert incoming_response.status_code == 200
    incoming_data = incoming_response.json()["data"]
    assert len(incoming_data) == 1
    assert incoming_data[0]["friendship_id"] == friendship_id
    assert incoming_data[0]["user"]["id"] == user_a["user"]["id"]

    outgoing_response = client.get(
        f"{BASE}/friends/requests/outgoing",
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert outgoing_response.status_code == 200
    outgoing_data = outgoing_response.json()["data"]
    assert len(outgoing_data) == 1
    assert outgoing_data[0]["friendship_id"] == friendship_id
    assert outgoing_data[0]["user"]["id"] == user_b["user"]["id"]

    search_response = client.get(
        f"{BASE}/users/search",
        params={"query": "pending_c"},
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert search_response.status_code == 200
    results = search_response.json()["data"]
    assert any(user["id"] == user_c["user"]["id"] for user in results)


def test_friends_events_feed(client: TestClient) -> None:
    user_a = register_user(client, "feed_a", "feed_a@example.com")
    user_b = register_user(client, "feed_b", "feed_b@example.com")

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

    create_response = client.post(
        f"{BASE}/events",
        json=event_payload(),
        headers=auth_header(user_b["tokens"]["access_token"]),
    )
    event_id = create_response.json()["data"]["id"]

    rsvp_response = client.post(
        f"{BASE}/events/{event_id}/rsvp",
        params={"status_value": "going"},
        headers=auth_header(user_b["tokens"]["access_token"]),
    )
    assert rsvp_response.status_code == 200

    feed_response = client.get(
        f"{BASE}/friends/events",
        headers=auth_header(user_a["tokens"]["access_token"]),
    )
    assert feed_response.status_code == 200
    items = feed_response.json()["data"]
    assert len(items) == 1
    assert items[0]["friend"]["id"] == user_b["user"]["id"]
    assert items[0]["event"]["id"] == event_id
