import { api } from "./client";
import { ApiEnvelope, FriendLocation } from "../types";

export async function listFriendLocations(accessToken: string) {
  const res = await api.get<ApiEnvelope<FriendLocation[]>>("/location/friends", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}

export async function updateMyLocation(
  payload: { latitude: number; longitude: number; accuracy?: number },
  accessToken: string
) {
  const res = await api.post<ApiEnvelope<FriendLocation>>("/location/update", payload, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}
