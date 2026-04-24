import { useFocusEffect } from "@react-navigation/native";
import React, { useCallback, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Button,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";

import { listFriendsEvents } from "../api/friends";
import { listFriendLocations, updateMyLocation } from "../api/location";
import { listMyFriends } from "../api/users";
import { useAuth } from "../context/AuthContext";
import { FriendEventActivity, FriendLocation, User } from "../types";

function formatApiError(error: any): string {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg ?? JSON.stringify(item)).join("\n");
  }
  if (detail && typeof detail === "object") {
    return detail.message ?? JSON.stringify(detail);
  }
  return error?.message ?? "Unknown error";
}

function toLocalDateLabel(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function ActivityScreen() {
  const { accessToken } = useAuth();
  const [eventsFeed, setEventsFeed] = useState<FriendEventActivity[]>([]);
  const [friendLocations, setFriendLocations] = useState<FriendLocation[]>([]);
  const [friends, setFriends] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  const [latitude, setLatitude] = useState("25.2048");
  const [longitude, setLongitude] = useState("55.2708");
  const [accuracy, setAccuracy] = useState("5");

  const friendNameById = useMemo(
    () =>
      friends.reduce<Record<string, string>>((acc, friend) => {
        acc[friend.id] = friend.full_name || friend.username;
        return acc;
      }, {}),
    [friends]
  );

  const loadData = useCallback(async () => {
    if (!accessToken) return;

    try {
      setLoading(true);
      const [eventsData, locationsData, friendsData] = await Promise.all([
        listFriendsEvents(accessToken),
        listFriendLocations(accessToken),
        listMyFriends(accessToken),
      ]);
      setEventsFeed(eventsData);
      setFriendLocations(locationsData);
      setFriends(friendsData);
    } catch (error: any) {
      Alert.alert("Failed to load activity", formatApiError(error));
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const handleUpdateLocation = async () => {
    if (!accessToken) {
      Alert.alert("Not authenticated", "Please login again.");
      return;
    }

    const lat = Number(latitude);
    const lng = Number(longitude);
    const acc = Number(accuracy);

    if (Number.isNaN(lat) || lat < -90 || lat > 90) {
      Alert.alert("Invalid latitude", "Latitude must be between -90 and 90.");
      return;
    }
    if (Number.isNaN(lng) || lng < -180 || lng > 180) {
      Alert.alert("Invalid longitude", "Longitude must be between -180 and 180.");
      return;
    }
    if (Number.isNaN(acc) || acc < 0) {
      Alert.alert("Invalid accuracy", "Accuracy must be 0 or greater.");
      return;
    }

    try {
      setUpdating(true);
      await updateMyLocation({ latitude: lat, longitude: lng, accuracy: acc }, accessToken);
      Alert.alert("Location updated", "Your location was updated successfully.");
      await loadData();
    } catch (error: any) {
      Alert.alert("Update failed", formatApiError(error));
    } finally {
      setUpdating(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Activity</Text>
      <Button title={loading ? "Refreshing..." : "Refresh"} onPress={loadData} disabled={loading || updating} />

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Update My Location</Text>
        <TextInput
          placeholder="Latitude"
          value={latitude}
          onChangeText={setLatitude}
          keyboardType="numeric"
          style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 }}
        />
        <TextInput
          placeholder="Longitude"
          value={longitude}
          onChangeText={setLongitude}
          keyboardType="numeric"
          style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 }}
        />
        <TextInput
          placeholder="Accuracy"
          value={accuracy}
          onChangeText={setAccuracy}
          keyboardType="numeric"
          style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 }}
        />
        <Button title={updating ? "Updating..." : "Update Location"} onPress={handleUpdateLocation} disabled={updating} />
      </View>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Friends Attending Events</Text>
        {loading ? <ActivityIndicator /> : null}
        {eventsFeed.length === 0 ? <Text>No friend event activity yet.</Text> : null}
        {eventsFeed.map((item) => (
          <View key={`${item.friend_id}:${item.event.id}`} style={{ borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 10, gap: 4 }}>
            <Text style={{ fontWeight: "700" }}>{item.friend.full_name}</Text>
            <Text>@{item.friend.username}</Text>
            <Text>{item.event.title}</Text>
            <Text>{item.event.city}</Text>
            <Text>Starts: {toLocalDateLabel(item.event.starts_at)}</Text>
            <Text>Status: {item.status}</Text>
          </View>
        ))}
      </View>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Friend Locations</Text>
        {friendLocations.length === 0 ? <Text>No friend locations yet.</Text> : null}
        {friendLocations.map((location) => (
          <View key={location.user_id} style={{ borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 10, gap: 4 }}>
            <Text style={{ fontWeight: "700" }}>{friendNameById[location.user_id] ?? location.user_id}</Text>
            <Text>Lat: {location.latitude}</Text>
            <Text>Lng: {location.longitude}</Text>
            <Text>Accuracy: {location.accuracy ?? "n/a"}</Text>
            <Text>Updated: {toLocalDateLabel(location.updated_at)}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}
