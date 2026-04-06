import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { login as apiLogin, register as apiRegister } from "../api/auth";

type AuthContextType = {
  accessToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    username: string;
    full_name: string;
    email: string;
    password: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

const ACCESS_TOKEN_KEY = "access_token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    AsyncStorage.getItem(ACCESS_TOKEN_KEY).then((token) => {
      if (token) setAccessToken(token);
    });
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      accessToken,
      login: async (email, password) => {
        const data = await apiLogin(email, password);
        setAccessToken(data.tokens.access_token);
        await AsyncStorage.setItem(ACCESS_TOKEN_KEY, data.tokens.access_token);
      },
      register: async (payload) => {
        const data = await apiRegister(payload);
        setAccessToken(data.tokens.access_token);
        await AsyncStorage.setItem(ACCESS_TOKEN_KEY, data.tokens.access_token);
      },
      logout: async () => {
        setAccessToken(null);
        await AsyncStorage.removeItem(ACCESS_TOKEN_KEY);
      },
    }),
    [accessToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
