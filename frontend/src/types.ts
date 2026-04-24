export type ApiEnvelope<T> = {
  data: T;
  error: string | null;
  meta: unknown;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type User = {
  id: string;
  username: string;
  full_name: string;
  email: string;
  phone?: string | null;
  avatar_url?: string | null;
  bio?: string | null;
  is_vendor?: boolean;
  location_sharing?: boolean;
  created_at?: string;
};

export type EventItem = {
  id: string;
  title: string;
  description: string;
  category: EventCategory;
  location_name: string;
  latitude: number;
  longitude: number;
  address: string;
  city: string;
  starts_at: string;
  ends_at: string;
  is_public: boolean;
  is_live: boolean;
  max_capacity: number | null;
  cover_image_url: string | null;
  ticket_url: string | null;
  created_at: string;
};

export type EventCategory =
  | "party"
  | "brunch"
  | "concert"
  | "sports"
  | "networking"
  | "other";

export type EventCity = "dubai" | "abu_dhabi";

export type EventCreatePayload = {
  title: string;
  description: string;
  category: EventCategory;
  location_name: string;
  latitude: number;
  longitude: number;
  address: string;
  city: EventCity;
  starts_at: string;
  ends_at: string;
  is_public?: boolean;
  max_capacity?: number;
  cover_image_url?: string;
  ticket_url?: string;
};

export type RSVPStatus = "going" | "interested" | "not_going";

export type EventAttendee = {
  user_id: string;
  status: RSVPStatus;
  created_at: string;
};

export type RSVPRecord = {
  id: string;
  event_id: string;
  user_id: string;
  status: RSVPStatus;
  created_at: string;
};

export type FriendRequestItem = {
  friendship_id: string;
  user: User;
  created_at: string;
};

export type FriendPreview = {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string | null;
};

export type FriendEventActivity = {
  friend_id: string;
  friend: FriendPreview;
  event: EventItem;
  status: RSVPStatus;
};

export type FriendLocation = {
  user_id: string;
  latitude: number;
  longitude: number;
  accuracy: number | null;
  updated_at: string;
};
