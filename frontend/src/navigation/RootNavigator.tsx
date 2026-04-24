import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useAuth } from "../context/AuthContext";
import ActivityScreen from "../screens/ActivityScreen";
import CreateEventScreen from "../screens/CreateEventScreen";
import EventDetailScreen from "../screens/EventDetailScreen";
import LoginScreen from "../screens/LoginScreen";
import RegisterScreen from "../screens/RegisterScreen";
import EventsScreen from "../screens/EventsScreen";
import FriendsScreen from "../screens/FriendsScreen";

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  const { accessToken } = useAuth();

  return (
    <NavigationContainer>
      {accessToken ? (
        <Stack.Navigator>
          <Stack.Screen name="Events" component={EventsScreen} />
          <Stack.Screen name="Friends" component={FriendsScreen} />
          <Stack.Screen name="Activity" component={ActivityScreen} />
          <Stack.Screen name="CreateEvent" component={CreateEventScreen} options={{ title: "Create Event" }} />
          <Stack.Screen name="EventDetail" component={EventDetailScreen} options={{ title: "Event Details" }} />
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
