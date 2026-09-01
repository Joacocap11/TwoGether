import React, { useState } from 'react';
import { Image, KeyboardAvoidingView, Platform, Text, View } from 'react-native';
import { useAuth } from '../../src/auth';
import { Button, Field, styles } from '../../src/ui';
export default function Login() {
  const { signIn } = useAuth(); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  async function submit() { setError(''); setBusy(true); try { await signIn(email, password); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to sign in'); } finally { setBusy(false); } }
  return <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined}><View style={[styles.content, { flex: 1, justifyContent: 'center' }]}><Image source={require('../../assets/twogether-login.png')} style={{ width: '100%', height: 180, resizeMode: 'contain', marginBottom: 16 }} /><Text style={[styles.title, { textAlign: 'center' }]}>Welcome back</Text><Text style={[styles.subtitle, { textAlign: 'center' }]}>Your shared memories, together.</Text><Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" placeholder="you@example.com" /><Field label="Password" value={password} onChangeText={setPassword} secureTextEntry placeholder="Your password" />{error ? <Text style={styles.error}>{error}</Text> : null}<Button title={busy ? 'Signing in…' : 'Sign in'} onPress={submit} disabled={busy} /></View></KeyboardAvoidingView>;
}
