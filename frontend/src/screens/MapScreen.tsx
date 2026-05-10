import { useFocusEffect } from "@react-navigation/native";
import React, { useCallback, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Button,
  ScrollView,
  Text,
  View,
} from "react-native";

import { listEventsForMap } from "../api/events";
import { listFriendLocations } from "../api/location";
import {
  buildLocationWebSocketUrl,
  parseFriendLocationPayload,
} from "../api/realtime";
import { listMyFriends } from "../api/users";
import { useAuth } from "../context/AuthContext";
import { EventItem, FriendLocation, User } from "../types";

type Bounds = {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
};

const DUBAI_CENTER = { lat: 25.2048, lng: 55.2708 };
const ABU_DHABI_CENTER = { lat: 24.4539, lng: 54.3773 };

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function computeBounds(centerLat: number, centerLng: number, latSpan: number, lngSpan: number): Bounds {
  return {
    minLat: clamp(centerLat - latSpan / 2, -90, 90),
    maxLat: clamp(centerLat + latSpan / 2, -90, 90),
    minLng: clamp(centerLng - lngSpan / 2, -180, 180),
    maxLng: clamp(centerLng + lngSpan / 2, -180, 180),
  };
}

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

function pointToPercentages(
  lat: number,
  lng: number,
  bounds: Bounds
): { xPct: number; yPct: number } | null {
  if (lat < bounds.minLat || lat > bounds.maxLat || lng < bounds.minLng || lng > bounds.maxLng) {
    return null;
  }

  const lngRange = bounds.maxLng - bounds.minLng;
  const latRange = bounds.maxLat - bounds.minLat;
  if (lngRange <= 0 || latRange <= 0) return null;

  const xPct = ((lng - bounds.minLng) / lngRange) * 100;
  const yPct = (1 - (lat - bounds.minLat) / latRange) * 100;
  return { xPct, yPct };
}

export default function MapScreen() {
  const { accessToken } = useAuth();

  const [centerLat, setCenterLat] = useState(DUBAI_CENTER.lat);
  const [centerLng, setCenterLng] = useState(DUBAI_CENTER.lng);
  const [latSpan, setLatSpan] = useState(0.4);
  const [lngSpan, setLngSpan] = useState(0.4);

  const [events, setEvents] = useState<EventItem[]>([]);
  const [friendLocations, setFriendLocations] = useState<FriendLocation[]>([]);
  const [friends, setFriends] = useState<User[]>([]);

  const [loading, setLoading] = useState(false);
  const [realtimeConnected, setRealtimeConnected] = useState(false);
  const websocketRef = useRef<WebSocket | null>(null);

  const bounds = useMemo(
    () => computeBounds(centerLat, centerLng, latSpan, lngSpan),
    [centerLat, centerLng, latSpan, lngSpan]
  );

  const friendNameById = useMemo(
    () =>
      friends.reduce<Record<string, string>>((acc, friend) => {
        acc[friend.id] = friend.full_name || friend.username;
        return acc;
      }, {}),
    [friends]
  );

  const upsertFriendLocation = useCallback((incoming: FriendLocation) => {
    setFriendLocations((previous) => {
      const deduped = previous.filter((item) => item.user_id !== incoming.user_id);
      return [incoming, ...deduped];
    });
  }, []);

  const loadData = useCallback(async () => {
    if (!accessToken) return;

    try {
      setLoading(true);
      const [eventsData, locationsData, friendsData] = await Promise.all([
        listEventsForMap(bounds, accessToken),
        listFriendLocations(accessToken),
        listMyFriends(accessToken),
      ]);
      setEvents(eventsData);
      setFriendLocations(locationsData);
      setFriends(friendsData);
    } catch (error: any) {
      Alert.alert("Failed to load map", formatApiError(error));
    } finally {
      setLoading(false);
    }
  }, [accessToken, bounds]);

  useFocusEffect(
    useCallback(() => {
      loadData();

      const refreshTimer = setInterval(() => {
        loadData();
      }, 30000);

      return () => {
        clearInterval(refreshTimer);
      };
    }, [loadData])
  );

  useFocusEffect(
    useCallback(() => {
      if (!accessToken) return undefined;

      let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
      let manuallyClosed = false;
      let socket: WebSocket | null = null;

      const connect = () => {
        if (manuallyClosed) return;

        const wsUrl = buildLocationWebSocketUrl(accessToken);
        socket = new WebSocket(wsUrl);
        websocketRef.current = socket;

        socket.onopen = () => {
          setRealtimeConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const parsed = typeof event.data === "string" ? JSON.parse(event.data) : event.data;
            const payload = parseFriendLocationPayload(parsed);
            if (payload) {
              upsertFriendLocation(payload);
            }
          } catch (error) {
            console.warn("Failed to parse realtime map payload", error);
          }
        };

        socket.onerror = () => {
          setRealtimeConnected(false);
        };

        socket.onclose = () => {
          setRealtimeConnected(false);
          if (websocketRef.current === socket) {
            websocketRef.current = null;
          }
          if (!manuallyClosed) {
            reconnectTimer = setTimeout(connect, 2000);
          }
        };
      };

      connect();

      return () => {
        manuallyClosed = true;
        setRealtimeConnected(false);
        if (reconnectTimer) clearTimeout(reconnectTimer);
        if (
          socket &&
          (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)
        ) {
          socket.close();
        }
        if (websocketRef.current === socket) {
          websocketRef.current = null;
        }
      };
    }, [accessToken, upsertFriendLocation])
  );

  const nudge = (latStep: number, lngStep: number) => {
    setCenterLat((current) => clamp(current + latStep, -90, 90));
    setCenterLng((current) => clamp(current + lngStep, -180, 180));
  };

  const zoom = (factor: number) => {
    setLatSpan((current) => clamp(current * factor, 0.05, 20));
    setLngSpan((current) => clamp(current * factor, 0.05, 20));
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 10 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Live Map</Text>
      <Text style={{ color: realtimeConnected ? "green" : "gray" }}>
        Realtime: {realtimeConnected ? "connected" : "disconnected"}
      </Text>
      <Text>
        Center: {centerLat.toFixed(4)}, {centerLng.toFixed(4)}
      </Text>
      <Text>
        Bounds: lat {bounds.minLat.toFixed(3)} to {bounds.maxLat.toFixed(3)} | lng {bounds.minLng.toFixed(3)} to {bounds.maxLng.toFixed(3)}
      </Text>

      <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
        <Button
          title="Dubai"
          onPress={() => {
            setCenterLat(DUBAI_CENTER.lat);
            setCenterLng(DUBAI_CENTER.lng);
            setLatSpan(0.4);
            setLngSpan(0.4);
          }}
        />
        <Button
          title="Abu Dhabi"
          onPress={() => {
            setCenterLat(ABU_DHABI_CENTER.lat);
            setCenterLng(ABU_DHABI_CENTER.lng);
            setLatSpan(0.4);
            setLngSpan(0.4);
          }}
        />
        <Button title={loading ? "Refreshing..." : "Refresh"} onPress={loadData} disabled={loading} />
      </View>

      <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
        <Button title="Zoom In" onPress={() => zoom(0.6)} />
        <Button title="Zoom Out" onPress={() => zoom(1.5)} />
        <Button title="North" onPress={() => nudge(latSpan * 0.25, 0)} />
        <Button title="South" onPress={() => nudge(-latSpan * 0.25, 0)} />
      </View>

      <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
        <Button title="West" onPress={() => nudge(0, -lngSpan * 0.25)} />
        <Button title="East" onPress={() => nudge(0, lngSpan * 0.25)} />
      </View>

      <View
        style={{
          height: 420,
          borderWidth: 1,
          borderColor: "#bbb",
          borderRadius: 12,
          backgroundColor: "#f5f8fa",
          overflow: "hidden",
          position: "relative",
        }}
      >
        {events.map((event) => {
          const point = pointToPercentages(event.latitude, event.longitude, bounds);
          if (!point) return null;
          return (
            <View
              key={`event:${event.id}`}
              style={{
                position: "absolute",
                left: `${point.xPct}%`,
                top: `${point.yPct}%`,
                transform: [{ translateX: -6 }, { translateY: -6 }],
                alignItems: "center",
              }}
            >
              <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#e53935" }} />
              <Text style={{ fontSize: 10, maxWidth: 120 }} numberOfLines={1}>
                {event.title}
              </Text>
            </View>
          );
        })}

        {friendLocations.map((location) => {
          const point = pointToPercentages(location.latitude, location.longitude, bounds);
          if (!point) return null;
          return (
            <View
              key={`friend:${location.user_id}`}
              style={{
                position: "absolute",
                left: `${point.xPct}%`,
                top: `${point.yPct}%`,
                transform: [{ translateX: -6 }, { translateY: -6 }],
                alignItems: "center",
              }}
            >
              <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#1e88e5" }} />
              <Text style={{ fontSize: 10, maxWidth: 120 }} numberOfLines={1}>
                {friendNameById[location.user_id] ?? location.user_id}
              </Text>
            </View>
          );
        })}

        {loading ? (
          <View style={{ position: "absolute", top: 0, right: 0, bottom: 0, left: 0, justifyContent: "center", alignItems: "center" }}>
            <ActivityIndicator />
          </View>
        ) : null}
      </View>

      <View style={{ gap: 4 }}>
        <Text>Legend:</Text>
        <Text>Red pins: events</Text>
        <Text>Blue pins: friend live locations</Text>
      </View>
    </ScrollView>
  );
}
