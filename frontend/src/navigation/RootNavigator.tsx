import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useAuth } from "../context/AuthContext";
import CreateEventScreen from "../screens/CreateEventScreen";
import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";
import EventsScreen from "../screens/EventsScreen";

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const { accessToken } = useAuth();

  return (
    <NavigationContainer>
      {accessToken ? (
        <Stack.Navigator>
          <Stack.Screen name="Events" component={EventsScreen} />
          <Stack.Screen name="CreateEvent" component={CreateEventScreen} options={{ title: "Create Event" }} />
        </Stack.Navigator>
      ) : (
        <Stack.Navigator>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Register" component={RegisterScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}
