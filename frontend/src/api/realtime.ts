import { FriendLocation } from "../types";

const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL;

function normalizedBaseUrlForWebSocket(): string {
  if (!apiBaseUrl) {
    throw new Error("Missing EXPO_PUBLIC_API_BASE_URL");
  }

  const trimmed = apiBaseUrl.trim().replace(/\/+$/, "");
  if (trimmed.startsWith("https://")) {
    return `wss://${trimmed.slice("https://".length)}`;
  }
  if (trimmed.startsWith("http://")) {
    return `ws://${trimmed.slice("http://".length)}`;
  }

  throw new Error("EXPO_PUBLIC_API_BASE_URL must start with http:// or https://");
}

export function buildLocationWebSocketUrl(accessToken: string): string {
  const wsBaseUrl = normalizedBaseUrlForWebSocket();
  return `${wsBaseUrl}/ws/location?token=${encodeURIComponent(accessToken)}`;
}

export function parseFriendLocationPayload(raw: unknown): FriendLocation | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const candidate = raw as Record<string, unknown>;

  if (typeof candidate.user_id !== "string") return null;
  if (typeof candidate.latitude !== "number") return null;
  if (typeof candidate.longitude !== "number") return null;
  if (typeof candidate.updated_at !== "string") return null;

  const accuracy =
    typeof candidate.accuracy === "number" ? candidate.accuracy : null;

  return {
    user_id: candidate.user_id,
    latitude: candidate.latitude,
    longitude: candidate.longitude,
    accuracy,
    updated_at: candidate.updated_at,
  };
}
