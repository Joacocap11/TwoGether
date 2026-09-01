import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../src/auth';
import { colors } from '../src/ui';
const queryClient = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 15_000 } } });
function Guard() {
  const { user, loading, mustChangePassword } = useAuth(); const segments = useSegments() as string[]; const router = useRouter();
  useEffect(() => { if (loading) return; const inAuth = segments[0] === '(auth)'; const changing = segments[1] === 'change-password'; if (!user && !inAuth) router.replace('/(auth)/login'); else if (user && inAuth && mustChangePassword && !changing) router.replace('/(auth)/change-password'); else if (user && inAuth && !mustChangePassword && !changing) router.replace('/(tabs)'); }, [loading, user, mustChangePassword, segments, router]);
  return <Stack screenOptions={{ headerTintColor: colors.ink, headerBackTitle: 'Atrás', headerStyle: { backgroundColor: colors.cream }, headerShadowVisible: false, contentStyle: { backgroundColor: colors.cream } }}><Stack.Screen name="(auth)" options={{ headerShown: false }} /><Stack.Screen name="(tabs)" options={{ headerShown: false }} /><Stack.Screen name="place/[id]" options={{ title: 'Restaurante' }} /><Stack.Screen name="test/[id]" options={{ title: 'Test' }} /><Stack.Screen name="media/[id]" options={{ title: 'Serie o película' }} /><Stack.Screen name="hotel/[id]" options={{ title: 'Hotel' }} /><Stack.Screen name="profile" options={{ title: 'Mi cuenta' }} /><Stack.Screen name="admin" options={{ title: 'Gestionar usuarios' }} /></Stack>;
}
export default function RootLayout() { return <QueryClientProvider client={queryClient}><AuthProvider><Guard /></AuthProvider></QueryClientProvider>; }
