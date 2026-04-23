import { useFocusEffect } from "@react-navigation/native";
import React, { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Button,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";

import {
  acceptFriendRequest,
  listIncomingFriendRequests,
  listOutgoingFriendRequests,
  sendFriendRequest,
} from "../api/friends";
import { listMyFriends, searchUsers } from "../api/users";
import { useAuth } from "../context/AuthContext";
import { FriendRequestItem, User } from "../types";

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

function FriendRow({ user }: { user: User }) {
  return (
    <View style={{ borderWidth: 1, borderColor: "#ddd", padding: 10, borderRadius: 8 }}>
      <Text style={{ fontWeight: "700" }}>{user.full_name}</Text>
      <Text>@{user.username}</Text>
      <Text>{user.email}</Text>
    </View>
  );
}

function PendingRow({
  request,
  onAccept,
  accepting,
}: {
  request: FriendRequestItem;
  onAccept: (friendshipId: string) => Promise<void>;
  accepting: boolean;
}) {
  return (
    <View style={{ borderWidth: 1, borderColor: "#ddd", padding: 10, borderRadius: 8, gap: 6 }}>
      <Text style={{ fontWeight: "700" }}>{request.user.full_name}</Text>
      <Text>@{request.user.username}</Text>
      <Text>{request.user.email}</Text>
      <Button title={accepting ? "Accepting..." : "Accept Request"} onPress={() => onAccept(request.friendship_id)} disabled={accepting} />
    </View>
  );
}

export default function FriendsScreen() {
  const { accessToken } = useAuth();
  const [friends, setFriends] = useState<User[]>([]);
  const [incoming, setIncoming] = useState<FriendRequestItem[]>([]);
  const [outgoing, setOutgoing] = useState<FriendRequestItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const loadData = useCallback(async () => {
    if (!accessToken) return;

    try {
      setLoading(true);
      const [friendsData, incomingData, outgoingData] = await Promise.all([
        listMyFriends(accessToken),
        listIncomingFriendRequests(accessToken),
        listOutgoingFriendRequests(accessToken),
      ]);
      setFriends(friendsData);
      setIncoming(incomingData);
      setOutgoing(outgoingData);
    } catch (error: any) {
      Alert.alert("Failed to load friends", formatApiError(error));
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useFocusEffect(
    useCallback(() => {
      loadData();
    }, [loadData])
  );

  const runSearch = async () => {
    if (!accessToken) {
      Alert.alert("Not authenticated", "Please login again.");
      return;
    }

    const normalized = searchQuery.trim();
    if (!normalized) {
      Alert.alert("Search required", "Enter a username, name, or email.");
      return;
    }

    try {
      setActionLoading(true);
      const results = await searchUsers(normalized, accessToken);
      setSearchResults(results);
    } catch (error: any) {
      Alert.alert("Search failed", formatApiError(error));
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendRequest = async (addresseeId: string) => {
    if (!accessToken) {
      Alert.alert("Not authenticated", "Please login again.");
      return;
    }

    try {
      setActionLoading(true);
      await sendFriendRequest(addresseeId, accessToken);
      Alert.alert("Request sent", "Friend request sent successfully.");
      await loadData();
    } catch (error: any) {
      Alert.alert("Request failed", formatApiError(error));
    } finally {
      setActionLoading(false);
    }
  };

  const handleAcceptRequest = async (friendshipId: string) => {
    if (!accessToken) {
      Alert.alert("Not authenticated", "Please login again.");
      return;
    }

    try {
      setActionLoading(true);
      await acceptFriendRequest(friendshipId, accessToken);
      Alert.alert("Friend added", "Friend request accepted.");
      await loadData();
    } catch (error: any) {
      Alert.alert("Accept failed", formatApiError(error));
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>Friends</Text>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Find People</Text>
        <TextInput
          placeholder="Search by username, full name, or email"
          value={searchQuery}
          onChangeText={setSearchQuery}
          autoCapitalize="none"
          style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 10 }}
        />
        <Button title={actionLoading ? "Searching..." : "Search"} onPress={runSearch} disabled={actionLoading} />
        {searchResults.length === 0 ? <Text>No search results yet.</Text> : null}
        {searchResults.map((user) => (
          <View key={user.id} style={{ borderWidth: 1, borderColor: "#ddd", padding: 10, borderRadius: 8, gap: 6 }}>
            <Text style={{ fontWeight: "700" }}>{user.full_name}</Text>
            <Text>@{user.username}</Text>
            <Text>{user.email}</Text>
            <Button
              title={actionLoading ? "Sending..." : "Send Friend Request"}
              onPress={() => handleSendRequest(user.id)}
              disabled={actionLoading}
            />
          </View>
        ))}
      </View>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Incoming Requests</Text>
        {incoming.length === 0 ? <Text>No incoming requests.</Text> : null}
        {incoming.map((request) => (
          <PendingRow
            key={request.friendship_id}
            request={request}
            onAccept={handleAcceptRequest}
            accepting={actionLoading}
          />
        ))}
      </View>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>Outgoing Requests</Text>
        {outgoing.length === 0 ? <Text>No outgoing requests.</Text> : null}
        {outgoing.map((request) => (
          <FriendRow key={request.friendship_id} user={request.user} />
        ))}
      </View>

      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 18, fontWeight: "600" }}>My Friends</Text>
        {loading ? <ActivityIndicator /> : null}
        {friends.length === 0 ? <Text>No friends yet.</Text> : null}
        {friends.map((friend) => (
          <FriendRow key={friend.id} user={friend} />
        ))}
      </View>
    </ScrollView>
  );
}
