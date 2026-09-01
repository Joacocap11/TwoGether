import React, { useState } from 'react';
import { Image, KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ApiError } from '../../src/api';
import { useAuth } from '../../src/auth';
import { Button, Field } from '../../src/ui';

const loginColors = {
  background: '#F7F3EA',
  blue: '#284B63',
  text: '#284B63',
  muted: '#61717B',
  errorBackground: '#FFF4E5',
  errorText: '#8A4B08',
};
function loginErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 401) return 'Correo o contraseña incorrectos.';
  if (error instanceof ApiError && error.status === 0) return 'No se pudo conectar con TwoGether.';
  if (error instanceof ApiError) return error.message;
  return 'No se pudo conectar con TwoGether.';
}

export default function Login() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (busy) return;
    setError('');
    setBusy(true);
    try {
      await signIn(email, password);
    } catch (cause) {
      setError(loginErrorMessage(cause));
    } finally {
      setBusy(false);
    }
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: loginColors.background }} edges={['top', 'bottom']}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', padding: 24, paddingBottom: 40 }}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode={Platform.OS === 'ios' ? 'interactive' : 'on-drag'}
        >
          <View style={{ width: '100%', maxWidth: 430, alignSelf: 'center' }}>
            <Image
              source={require('../../assets/twogether-login.png')}
              style={{ width: '100%', height: 145, resizeMode: 'contain', marginBottom: 18 }}
            />
            <Text style={{ color: loginColors.text, fontSize: 28, fontWeight: '800', textAlign: 'center', marginBottom: 7 }}>
              Bienvenidos a TwoGether
            </Text>
            <Text style={{ color: loginColors.muted, fontSize: 16, textAlign: 'center', marginBottom: 28 }}>
              Nuestros momentos, en un solo lugar.
            </Text>
            <Field
              label="Correo"
              value={email}
              onChangeText={setEmail}
              placeholder="tu@correo.com"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
            <Field
              label="Contraseña"
              value={password}
              onChangeText={setPassword}
              placeholder="Tu contraseña"
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
              onSubmitEditing={submit}
            />
            {error ? (
              <View style={{ backgroundColor: loginColors.errorBackground, borderColor: '#F0D5A5', borderWidth: 1, borderRadius: 10, padding: 12, marginBottom: 12 }}>
                <Text style={{ color: loginColors.errorText, lineHeight: 20 }}>{error}</Text>
              </View>
            ) : null}
            <Button title={busy ? 'Entrando...' : 'Entrar'} onPress={submit} disabled={busy} color={loginColors.blue} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
