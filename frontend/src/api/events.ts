import { api } from "./client";
import { ApiEnvelope, EventItem } from "../types";

export async function listEvents(accessToken?: string) {
  const res = await api.get<ApiEnvelope<EventItem[]>>("/events", {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });

  return res.data.data;
}
