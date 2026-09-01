import React, { useState } from 'react';
import { Alert, ScrollView, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../src/auth';
import { Button, Field, styles } from '../src/ui';
export default function Profile() { const { user, signOut } = useAuth(); const router = useRouter(); const [name] = useState(user?.name ?? ''); const [email] = useState(user?.email ?? ''); return <ScrollView style={styles.screen} contentContainerStyle={styles.content}><Text style={styles.title}>Mi cuenta</Text><Text style={styles.subtitle}>Tu sesión de TwoGether</Text><Field label="Nombre" value={name} onChangeText={() => {}} /><Field label="Correo" value={email} onChangeText={() => {}} /><Button title="Cambiar contraseña" onPress={() => router.push('/(auth)/change-password')} secondary />{user?.is_admin ? <Button title="Gestionar usuarios" onPress={() => router.push('/admin')} secondary /> : null}<Button title="Cerrar sesión" onPress={() => Alert.alert('¿Cerrar sesión?', undefined, [{ text: 'Cancelar', style: 'cancel' }, { text: 'Cerrar sesión', style: 'destructive', onPress: signOut }])} /></ScrollView>; }
