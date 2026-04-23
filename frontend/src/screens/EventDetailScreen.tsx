import React, { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Alert, Button, ScrollView, Text, View } from "react-native";

import {
  getEvent,
  getEventAttendees,
  removeEventRsvp,
  upsertEventRsvp,
} from "../api/events";
import { useAuth } from "../context/AuthContext";
import { EventAttendee, EventItem, RSVPStatus } from "../types";

function formatApiError(error: any): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg ?? JSON.stringify(item))
      .join("\n");
  }
  if (detail && typeof detail === "object") {
    return detail.message ?? JSON.stringify(detail);
  }
  return error?.message ?? "Unknown error";
}

function toLocalDateLabel(value: string): string {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

export default function EventDetailScreen({ route }: any) {
  const { accessToken } = useAuth();
  const eventId: string = route?.params?.eventId;

  const [event, setEvent] = useState<EventItem | null>(null);
  const [attendees, setAttendees] = useState<EventAttendee[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [myStatus, setMyStatus] = useState<RSVPStatus | null>(null);

  const loadData = useCallback(async () => {
    if (!eventId) return;
    try {
      setLoading(true);
      const [eventData, attendeeData] = await Promise.all([
        getEvent(eventId, accessToken ?? undefined),
        getEventAttendees(eventId, accessToken ?? undefined),
      ]);
      setEvent(eventData);
      setAttendees(attendeeData);
    } catch (error: any) {
      Alert.alert("Failed to load event", formatApiError(error));
    } finally {
      setLoading(false);
    }
  }, [eventId, accessToken]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const setRsvp = async (status: RSVPStatus) => {
    if (!accessToken) {
      Alert.alert("Not authenticated", "Please login again.");
      return;
    }
    if (!eventId) {
      Alert.alert("Missing event", "Event ID was not provided.");
      return;
    }

    try {
      setSubmitting(true);
      const record = await upsertEventRsvp(eventId, status, accessToken);
      setMyStatus(record.status);
      await loadData();
      Alert.alert("RSVP updated", `Your RSVP is now '${record.status}'.`);
    } catch (error: any) {
      Alert.alert("Failed to RSVP", formatApiError(error));
    } finally {
      setSubmitting(false);
    }
  };

  const clearRsvp = async () => {
    if (!accessToken || !eventId) {
      Alert.alert("Not ready", "Please login again.");
      return;
    }

    try {
      setSubmitting(true);
      await removeEventRsvp(eventId, accessToken);
      setMyStatus(null);
      await loadData();
      Alert.alert("RSVP removed", "Your RSVP has been removed.");
    } catch (error: any) {
      Alert.alert("Failed to remove RSVP", formatApiError(error));
    } finally {
      setSubmitting(false);
    }
  };

  if (!eventId) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16 }}>
        <Text>Missing event ID.</Text>
      </View>
    );
  }

  if (loading && !event) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }

  if (!event) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16 }}>
        <Text>Event not found.</Text>
        <Button title="Retry" onPress={loadData} />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 8 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>{event.title}</Text>
      <Text>{event.description}</Text>
      <Text>Category: {event.category}</Text>
      <Text>City: {event.city}</Text>
      <Text>Location: {event.location_name}</Text>
      <Text>Address: {event.address}</Text>
      <Text>Starts: {toLocalDateLabel(event.starts_at)}</Text>
      <Text>Ends: {toLocalDateLabel(event.ends_at)}</Text>
      <Text>Attendees (going): {attendees.length}</Text>
      <Text>{myStatus ? `Your RSVP: ${myStatus}` : "You have not RSVPed yet."}</Text>

      <View style={{ gap: 8 }}>
        <Button title="RSVP: Going" onPress={() => setRsvp("going")} disabled={submitting} />
        <Button title="RSVP: Interested" onPress={() => setRsvp("interested")} disabled={submitting} />
        <Button title="RSVP: Not Going" onPress={() => setRsvp("not_going")} disabled={submitting} />
        <Button title="Remove RSVP" onPress={clearRsvp} disabled={submitting} />
      </View>
    </ScrollView>
  );
}
