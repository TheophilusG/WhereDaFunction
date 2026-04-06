
import React, { useState } from "react";
import { Alert, Button, Text, TextInput, View } from "react-native";
import { useAuth } from "../context/AuthContext";

export default function RegisterScreen() {
  const { register } = useAuth();
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <View style={{ flex: 1, padding: 24, gap: 12, justifyContent: "center" }}>
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Register</Text>
      <TextInput placeholder="Username" value={username} onChangeText={setUsername} style={{ borderWidth: 1, padding: 10 }} />
      <TextInput placeholder="Full Name" value={fullName} onChangeText={setFullName} style={{ borderWidth: 1, padding: 10 }} />
      <TextInput placeholder="Email" value={email} onChangeText={setEmail} style={{ borderWidth: 1, padding: 10 }} />
      <TextInput placeholder="Password (min 8)" secureTextEntry value={password} onChangeText={setPassword} style={{ borderWidth: 1, padding: 10 }} />
      <Button
        title="Create Account"
        onPress={async () => {
          try {
            await register({
              username,
              full_name: fullName,
              email,
              password,
            });
          } catch (e: any) {
            Alert.alert("Register failed", e?.response?.data?.detail ?? "Unknown error");
          }
        }}
      />
    </View>
  );
}
