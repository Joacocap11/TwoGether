import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Text, View } from 'react-native';
import { useRouter } from 'expo-router';
import { api } from '../../src/api';
import { useAuth } from '../../src/auth';
import { Button, Field, styles } from '../../src/ui';
export default function ChangePassword() {
  const { mustChangePassword, refreshUser } = useAuth(); const router = useRouter(); const [current, setCurrent] = useState(''); const [next, setNext] = useState(''); const [confirm, setConfirm] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  async function submit() { setError(''); if (next.length < 8) return setError('New password must be at least 8 characters.'); if (next !== confirm) return setError('Passwords do not match.'); setBusy(true); try { await api.changePassword({ current_password: current || undefined, new_password: next, confirm_password: confirm }); await refreshUser(); router.replace('/(tabs)'); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to change password'); } finally { setBusy(false); } }
  return <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined}><View style={[styles.content, { flex: 1, justifyContent: 'center' }]}><Text style={styles.title}>{mustChangePassword ? 'Set a new password' : 'Change password'}</Text><Text style={styles.subtitle}>{mustChangePassword ? 'An administrator asked you to update your password before continuing.' : 'Keep your account secure.'}</Text>{!mustChangePassword && <Field label="Current password" value={current} onChangeText={setCurrent} secureTextEntry /> }<Field label="New password" value={next} onChangeText={setNext} secureTextEntry /><Field label="Confirm new password" value={confirm} onChangeText={setConfirm} secureTextEntry />{error ? <Text style={styles.error}>{error}</Text> : null}<Button title={busy ? 'Saving…' : 'Save password'} onPress={submit} disabled={busy} /></View></KeyboardAvoidingView>;
}
