import React, { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { api } from '../../src/api';
import { useAuth } from '../../src/auth';
import { Button, Field, styles, colors } from '../../src/ui';

export default function ChangePassword() {
  const { mustChangePassword, refreshUser } = useAuth();
  const router = useRouter();
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit() {
    setError('');
    if (!mustChangePassword && !current) return setError('Ingresa tu contraseña actual.');
    if (next.length < 8) return setError('La nueva contraseña debe tener al menos 8 caracteres.');
    if (next !== confirm) return setError('Las contraseñas no coinciden.');
    setBusy(true);
    try {
      await api.changePassword({ current_password: current || undefined, new_password: next, confirm_password: confirm });
      await refreshUser();
      if (mustChangePassword) {
        router.replace('/(tabs)');
      } else {
        Alert.alert('Contraseña actualizada', 'Tu contraseña se cambió correctamente.', [{ text: 'Aceptar', onPress: () => router.back() }]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo cambiar la contraseña.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.cream }} edges={['top', 'bottom']}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <View style={[styles.content, { flex: 1, justifyContent: 'center' }]}>
          <Text style={styles.title}>{mustChangePassword ? 'Define una nueva contraseña' : 'Cambiar contraseña'}</Text>
          <Text style={styles.subtitle}>
            {mustChangePassword ? 'Un administrador solicitó actualizar tu contraseña antes de continuar.' : 'Mantén segura tu cuenta.'}
          </Text>
          {!mustChangePassword && (
            <Field label="Contraseña actual" value={current} onChangeText={setCurrent} secureTextEntry autoCapitalize="none" autoCorrect={false} />
          )}
          <Field label="Nueva contraseña" value={next} onChangeText={setNext} secureTextEntry autoCapitalize="none" autoCorrect={false} />
          <Field
            label="Confirmar contraseña"
            value={confirm}
            onChangeText={setConfirm}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            onSubmitEditing={submit}
          />
          {error ? <Text style={styles.error}>{error}</Text> : null}
          <Button title={busy ? 'Guardando…' : 'Guardar contraseña'} onPress={submit} disabled={busy} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
