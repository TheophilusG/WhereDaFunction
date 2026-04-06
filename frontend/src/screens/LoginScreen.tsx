import React, { useState } from "react";
import { Alert, Button, Text, TextInput, View } from "react-native";
import { useAuth } from "../context/AuthContext";

export default function LoginScreen({ navigation }: any) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <View style={{ flex: 1, padding: 24, gap: 12, justifyContent: "center" }}>
      <Text style={{ fontSize: 24, fontWeight: "600" }}>Login</Text>
      <TextInput placeholder="Email" value={email} onChangeText={setEmail} style={{ borderWidth: 1, padding: 10 }} />
      <TextInput placeholder="Password" value={password} secureTextEntry onChangeText={setPassword} style={{ borderWidth: 1, padding: 10 }} />
      <Button
        title="Login"
        onPress={async () => {
          try {
            await login(email, password);
          } catch (e: any) {
            Alert.alert("Login failed", e?.response?.data?.detail ?? "Unknown error");
          }
        }}
      />
      <Button title="Go to Register" onPress={() => navigation.navigate("Register")} />
    </View>
  );
}
