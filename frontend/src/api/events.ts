import { api } from "./client";
import { ApiEnvelope, EventCreatePayload, EventItem } from "../types";

export async function listEvents(accessToken?: string) {
  const res = await api.get<ApiEnvelope<EventItem[]>>("/events", {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });

  return res.data.data;
}

export async function createEvent(payload: EventCreatePayload, accessToken: string) {
  const res = await api.post<ApiEnvelope<EventItem>>("/events", payload, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  return res.data.data;
}
