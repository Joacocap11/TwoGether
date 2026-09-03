import React from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/auth';
import { Button, styles, colors } from '../src/ui';

export default function Profile() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.subtitle}>Tu sesión de TwoGether</Text>
      <View style={styles.card}>
        <Text style={styles.label}>Nombre</Text>
        <Text style={{ color: colors.ink, fontSize: 17, fontWeight: '700', marginBottom: 14 }}>{user?.name}</Text>
        <Text style={styles.label}>Correo</Text>
        <Text style={{ color: colors.ink, fontSize: 17, fontWeight: '700', marginBottom: 14 }}>{user?.email}</Text>
        <Text style={styles.label}>Rol</Text>
        <Text
          style={{
            alignSelf: 'flex-start',
            color: '#fff',
            backgroundColor: user?.is_admin ? colors.blue : colors.muted,
            paddingHorizontal: 10,
            paddingVertical: 4,
            borderRadius: 10,
            fontWeight: '700',
            overflow: 'hidden',
          }}
        >
          {user?.is_admin ? 'Administrador' : 'Usuario'}
        </Text>
      </View>
      <Button title="Cambiar contraseña" onPress={() => router.push('/(auth)/change-password')} secondary />
      {user?.is_admin ? <Button title="Gestionar usuarios" onPress={() => router.push('/admin')} secondary /> : null}
      <Button
        title="Cerrar sesión"
        onPress={() =>
          Alert.alert('¿Cerrar sesión?', undefined, [
            { text: 'Cancelar', style: 'cancel' },
            { text: 'Cerrar sesión', style: 'destructive', onPress: signOut },
          ])
        }
      />
    </ScrollView>
  );
}
