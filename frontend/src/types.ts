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
};

export type EventItem = {
  id: string;
  title: string;
  description: string;
  city: string;
  starts_at: string;
};
