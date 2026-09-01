import React, { useState } from 'react';
import { Alert, ScrollView, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../src/api';
import { useAuth } from '../src/auth';
import { Button, Field, styles } from '../src/ui';
export default function Profile() { const { user, signOut } = useAuth(); const router = useRouter(); const [name] = useState(user?.name ?? ''); const [email] = useState(user?.email ?? ''); const [show, setShow] = useState(false); return <ScrollView style={styles.screen} contentContainerStyle={styles.content}><Text style={styles.title}>Account</Text><Text style={styles.subtitle}>Your TwoGether session</Text><Field label="Name" value={name} onChangeText={() => {}} /><Field label="Email" value={email} onChangeText={() => {}} /><Button title="Change password" onPress={() => router.push('/(auth)/change-password')} secondary />{user?.is_admin ? <Button title="Manage users" onPress={() => router.push('/admin')} secondary /> : null}<Button title="Sign out" onPress={() => Alert.alert('Sign out?', undefined, [{ text: 'Cancel', style: 'cancel' }, { text: 'Sign out', style: 'destructive', onPress: signOut }])} /></ScrollView>; }
