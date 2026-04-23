import { api } from "./client";
import { ApiEnvelope, FriendRequestItem } from "../types";

export async function sendFriendRequest(addresseeId: string, accessToken: string) {
  const res = await api.post<ApiEnvelope<{ id: string }>>(
    "/friends/request",
    { addressee_id: addresseeId },
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  return res.data.data;
}

export async function listIncomingFriendRequests(accessToken: string) {
  const res = await api.get<ApiEnvelope<FriendRequestItem[]>>("/friends/requests/incoming", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}

export async function listOutgoingFriendRequests(accessToken: string) {
  const res = await api.get<ApiEnvelope<FriendRequestItem[]>>("/friends/requests/outgoing", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}

export async function acceptFriendRequest(friendshipId: string, accessToken: string) {
  const res = await api.patch<ApiEnvelope<{ id: string }>>(
    `/friends/${friendshipId}/accept`,
    null,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  return res.data.data;
}

export async function listFriendsEvents(accessToken: string) {
  const res = await api.get<ApiEnvelope<any[]>>("/friends/events", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}
