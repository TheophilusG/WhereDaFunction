import { api } from "./client";
import { ApiEnvelope, TokenPair, User } from "../types";

export async function login(email: string, password: string) {
  const res = await api.post<ApiEnvelope<{ user: User; tokens: TokenPair }>>(
    "/auth/login",
    { email, password }
  );
  return res.data.data;
}

export async function register(payload: {
  username: string;
  full_name: string;
  email: string;
  password: string;
}) {
  const res = await api.post<ApiEnvelope<{ user: User; tokens: TokenPair }>>(
    "/auth/register",
    payload
  );
  return res.data.data;
}
