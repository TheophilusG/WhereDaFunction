import { api } from "./client";
import {
  ApiEnvelope,
  EventAttendee,
  EventCreatePayload,
  EventItem,
  RSVPRecord,
  RSVPStatus,
} from "../types";

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

export async function getEvent(eventId: string, accessToken?: string) {
  const res = await api.get<ApiEnvelope<EventItem>>(`/events/${eventId}`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });
  return res.data.data;
}

export async function getEventAttendees(eventId: string, accessToken?: string) {
  const res = await api.get<ApiEnvelope<EventAttendee[]>>(`/events/${eventId}/attendees`, {
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });
  return res.data.data;
}

export async function upsertEventRsvp(eventId: string, status: RSVPStatus, accessToken: string) {
  const res = await api.post<ApiEnvelope<RSVPRecord>>(
    `/events/${eventId}/rsvp`,
    null,
    {
      params: { status_value: status },
      headers: { Authorization: `Bearer ${accessToken}` },
    }
  );
  return res.data.data;
}

export async function removeEventRsvp(eventId: string, accessToken: string) {
  const res = await api.delete<ApiEnvelope<{ deleted: boolean }>>(`/events/${eventId}/rsvp`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data.data;
}
