import { api } from "./client";
import { ApiEnvelope, User } from "../types";

export async function getMe(accessToken: string) {
  const res = await api.get<ApiEnvelope<User>>("/users/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}

export async function searchUsers(query: string, accessToken: string, limit = 20) {
  const res = await api.get<ApiEnvelope<User[]>>("/users/search", {
    params: { query, limit },
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}

export async function listMyFriends(accessToken: string) {
  const res = await api.get<ApiEnvelope<User[]>>("/users/me/friends", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}
