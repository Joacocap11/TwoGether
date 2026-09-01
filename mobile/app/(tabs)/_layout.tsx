import React from 'react';
import { Pressable } from 'react-native';
import { Tabs, Link } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../../src/ui';

export default function TabsLayout() {
  return <Tabs screenOptions={{ tabBarActiveTintColor: colors.blue, tabBarInactiveTintColor: colors.muted, tabBarStyle: { backgroundColor: colors.paper, borderTopColor: colors.border }, headerStyle: { backgroundColor: colors.cream }, headerShadowVisible: false, headerTintColor: colors.ink, headerTitle: () => null, headerRight: () => <Link href="/profile" asChild><Pressable style={{ marginRight: 15 }}><Ionicons name="person-circle-outline" size={28} color={colors.blue} /></Pressable></Link> }}>
    <Tabs.Screen name="index" options={{ title: 'Restaurantes', tabBarIcon: ({ color, size }) => <Ionicons name="restaurant-outline" color={color} size={size} /> }} />
    <Tabs.Screen name="tests" options={{ title: 'Tests', tabBarIcon: ({ color, size }) => <Ionicons name="clipboard-outline" color={color} size={size} /> }} />
    <Tabs.Screen name="media" options={{ title: 'Series', tabBarIcon: ({ color, size }) => <Ionicons name="film-outline" color={color} size={size} /> }} />
    <Tabs.Screen name="hotels" options={{ title: 'Hoteles', tabBarIcon: ({ color, size }) => <Ionicons name="bed-outline" color={color} size={size} /> }} />
  </Tabs>;
}
