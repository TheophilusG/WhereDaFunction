import React, { useState } from "react";
import { Alert, Button, Text, TextInput, View } from "react-native";
import { useAuth } from "../context/AuthContext";

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

export default function LoginScreen({ navigation }: any) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <View style={{ flex: 1, padding: 24, gap: 12, justifyContent: "center" }}>
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Login</Text>
      <TextInput
        placeholder="Email or Username"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        style={{ borderWidth: 1, padding: 10 }}
      />
      <TextInput placeholder="Password" value={password} secureTextEntry onChangeText={setPassword} style={{ borderWidth: 1, padding: 10 }} />
      <Button
        title="Login"
        onPress={async () => {
          try {
            const identifier = email.trim();
            if (!identifier) {
              Alert.alert("Missing input", "Enter your email or username.");
              return;
            }
            if (!password) {
              Alert.alert("Missing input", "Enter your password.");
              return;
            }
            await login(identifier.toLowerCase(), password);
          } catch (e: any) {
            Alert.alert("Login failed", formatApiError(e));
          }
        }}
      />
      <Button title="Go to Register" onPress={() => navigation.navigate("Register")} />
    </View>
  );
}
