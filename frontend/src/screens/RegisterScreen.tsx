
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

export default function RegisterScreen() {
  const { register } = useAuth();
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <View style={{ flex: 1, padding: 24, gap: 12, justifyContent: "center" }}>
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Register</Text>
      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
        style={{ borderWidth: 1, padding: 10 }}
      />
      <TextInput
        placeholder="Full Name"
        value={fullName}
        onChangeText={setFullName}
        style={{ borderWidth: 1, padding: 10 }}
      />
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        style={{ borderWidth: 1, padding: 10 }}
      />
      <TextInput placeholder="Password (min 8)" secureTextEntry value={password} onChangeText={setPassword} style={{ borderWidth: 1, padding: 10 }} />
      <Button
        title="Create Account"
        onPress={async () => {
          try {
            const normalizedUsername = username.trim();
            const normalizedFullName = fullName.trim();
            const normalizedEmail = email.trim().toLowerCase();

            if (normalizedUsername.length < 3) {
              Alert.alert("Invalid username", "Username must be at least 3 characters.");
              return;
            }
            if (!normalizedFullName) {
              Alert.alert("Invalid full name", "Please enter your full name.");
              return;
            }
            if (!normalizedEmail.includes("@")) {
              Alert.alert("Invalid email", "Please enter a valid email address.");
              return;
            }
            if (password.length < 8) {
              Alert.alert("Invalid password", "Password must be at least 8 characters.");
              return;
            }

            await register({
              username: normalizedUsername,
              full_name: normalizedFullName,
              email: normalizedEmail,
              password,
            });
          } catch (e: any) {
            Alert.alert("Register failed", formatApiError(e));
          }
        }}
      />
    </View>
  );
}
