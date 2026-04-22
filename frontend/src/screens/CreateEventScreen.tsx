import React, { useMemo, useState } from "react";
import { Alert, Button, ScrollView, Text, TextInput, View } from "react-native";

import { createEvent } from "../api/events";
import { useAuth } from "../context/AuthContext";
import { EventCategory, EventCity } from "../types";

function formatApiError(error: any): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const path = Array.isArray(item?.loc) ? item.loc.join(".") : "field";
        const msg = item?.msg ?? JSON.stringify(item);
        return `${path}: ${msg}`;
      })
      .join("\n");
  }
  if (detail && typeof detail === "object") {
    return detail.message ?? JSON.stringify(detail);
  }
  return error?.message ?? "Unknown error";
}

export default function CreateEventScreen({ navigation }: any) {
  const { accessToken } = useAuth();

  const now = useMemo(() => new Date(), []);
  const defaultStart = useMemo(() => new Date(now.getTime() + 60 * 60 * 1000).toISOString(), [now]);
  const defaultEnd = useMemo(() => new Date(now.getTime() + 2 * 60 * 60 * 1000).toISOString(), [now]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<EventCategory>("networking");
  const [locationName, setLocationName] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState<EventCity>("dubai");
  const [latitude, setLatitude] = useState("25.2048");
  const [longitude, setLongitude] = useState("55.2708");
  const [startsAt, setStartsAt] = useState(defaultStart);
  const [endsAt, setEndsAt] = useState(defaultEnd);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async () => {
    try {
      if (!accessToken) {
        Alert.alert("Not authenticated", "Please login again.");
        return;
      }

      const normalizedTitle = title.trim();
      const normalizedDescription = description.trim();
      const normalizedLocation = locationName.trim();
      const normalizedAddress = address.trim();

      if (!normalizedTitle) {
        Alert.alert("Invalid title", "Please enter an event title.");
        return;
      }
      if (!normalizedDescription) {
        Alert.alert("Invalid description", "Please enter an event description.");
        return;
      }
      if (!normalizedLocation) {
        Alert.alert("Invalid location", "Please enter a location name.");
        return;
      }
      if (!normalizedAddress) {
        Alert.alert("Invalid address", "Please enter an address.");
        return;
      }

      const lat = Number(latitude);
      const lng = Number(longitude);
      if (Number.isNaN(lat) || lat < -90 || lat > 90) {
        Alert.alert("Invalid latitude", "Latitude must be a number between -90 and 90.");
        return;
      }
      if (Number.isNaN(lng) || lng < -180 || lng > 180) {
        Alert.alert("Invalid longitude", "Longitude must be a number between -180 and 180.");
        return;
      }

      const startDate = new Date(startsAt);
      const endDate = new Date(endsAt);
      if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
        Alert.alert("Invalid datetime", "Use ISO datetime format, e.g. 2026-04-21T18:00:00.000Z");
        return;
      }
      if (endDate <= startDate) {
        Alert.alert("Invalid datetime", "End time must be after start time.");
        return;
      }

      setSubmitting(true);

      await createEvent(
        {
          title: normalizedTitle,
          description: normalizedDescription,
          category,
          location_name: normalizedLocation,
          latitude: lat,
          longitude: lng,
          address: normalizedAddress,
          city,
          starts_at: startDate.toISOString(),
          ends_at: endDate.toISOString(),
          is_public: true,
        },
        accessToken
      );

      Alert.alert("Success", "Event created.");
      navigation.goBack();
    } catch (error: any) {
      Alert.alert("Create event failed", formatApiError(error));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 10 }}>
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Create Event</Text>

      <TextInput
        placeholder="Title"
        value={title}
        onChangeText={setTitle}
        style={{ borderWidth: 1, padding: 10 }}
      />

      <TextInput
        placeholder="Description"
        value={description}
        onChangeText={setDescription}
        multiline
        style={{ borderWidth: 1, padding: 10, minHeight: 80, textAlignVertical: "top" }}
      />

      <Text>Category</Text>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
        {(["networking", "party", "concert", "brunch", "sports", "other"] as EventCategory[]).map((item) => (
          <Button key={item} title={item} onPress={() => setCategory(item)} color={category === item ? "#0a7" : undefined} />
        ))}
      </View>

      <TextInput
        placeholder="Location Name"
        value={locationName}
        onChangeText={setLocationName}
        style={{ borderWidth: 1, padding: 10 }}
      />

      <TextInput
        placeholder="Address"
        value={address}
        onChangeText={setAddress}
        style={{ borderWidth: 1, padding: 10 }}
      />

      <Text>City</Text>
      <View style={{ flexDirection: "row", gap: 8 }}>
        <Button title="dubai" onPress={() => setCity("dubai")} color={city === "dubai" ? "#0a7" : undefined} />
        <Button title="abu_dhabi" onPress={() => setCity("abu_dhabi")} color={city === "abu_dhabi" ? "#0a7" : undefined} />
      </View>

      <TextInput
        placeholder="Latitude"
        keyboardType="numeric"
        value={latitude}
        onChangeText={setLatitude}
        style={{ borderWidth: 1, padding: 10 }}
      />

      <TextInput
        placeholder="Longitude"
        keyboardType="numeric"
        value={longitude}
        onChangeText={setLongitude}
        style={{ borderWidth: 1, padding: 10 }}
      />

      <TextInput
        placeholder="Starts At (ISO)"
        value={startsAt}
        onChangeText={setStartsAt}
        autoCapitalize="none"
        style={{ borderWidth: 1, padding: 10 }}
      />

      <TextInput
        placeholder="Ends At (ISO)"
        value={endsAt}
        onChangeText={setEndsAt}
        autoCapitalize="none"
        style={{ borderWidth: 1, padding: 10 }}
      />

      <Button title={submitting ? "Creating..." : "Create Event"} onPress={onSubmit} disabled={submitting} />
    </ScrollView>
  );
}
