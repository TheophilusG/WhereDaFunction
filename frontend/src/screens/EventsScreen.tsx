import { useFocusEffect } from "@react-navigation/native";
import React, { useCallback, useState } from "react";
import { ActivityIndicator, Button, FlatList, Text, View } from "react-native";
import { listEvents } from "../api/events";
import { useAuth } from "../context/AuthContext";
import { EventItem } from "../types";

export default function EventsScreen({ navigation }: any) {
  const { accessToken, logout } = useAuth();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(false);

  const loadEvents = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listEvents(accessToken ?? undefined);
      setEvents(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useFocusEffect(
    useCallback(() => {
      loadEvents();
    }, [loadEvents])
  );

  return (
    <View style={{ flex: 1, padding: 16, gap: 8 }}>
      <Button title="Create Event" onPress={() => navigation.navigate("CreateEvent")} />
      <Button title="Logout" onPress={logout} />
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Events</Text>
      {loading ? <ActivityIndicator /> : null}
      <FlatList
        data={events}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={{ borderWidth: 1, padding: 12, marginBottom: 8 }}>
            <Text style={{ fontWeight: "700" }}>{item.title}</Text>
            <Text>{item.description}</Text>
            <Text>{item.location_name}</Text>
            <Text>{item.city}</Text>
          </View>
        )}
        onRefresh={loadEvents}
        refreshing={loading}
        ListEmptyComponent={<Text>No events yet.</Text>}
      />
    </View>
  );
}
