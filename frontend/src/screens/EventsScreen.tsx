import React, { useEffect, useState } from "react";
import { Button, FlatList, Text, View } from "react-native";
import { listEvents } from "../api/events";
import { useAuth } from "../context/AuthContext";
import { EventItem } from "../types";

export default function EventsScreen() {
  const { accessToken, logout } = useAuth();
  const [events, setEvents] = useState<EventItem[]>([]);

  useEffect(() => {
    listEvents(accessToken ?? undefined).then(setEvents).catch(console.error);
  }, [accessToken]);

  return (
    <View style={{ flex: 1, padding: 16, gap: 8 }}>
      <Button title="Logout" onPress={logout} />
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Events</Text>
      <FlatList
        data={events}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={{ borderWidth: 1, padding: 12, marginBottom: 8 }}>
            <Text style={{ fontWeight: "700" }}>{item.title}</Text>
            <Text>{item.description}</Text>
            <Text>{item.city}</Text>
          </View>
        )}
        ListEmptyComponent={<Text>No events yet.</Text>}
      />
    </View>
  );
}
