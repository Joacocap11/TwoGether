import React, { useState } from 'react';
import { Alert, Pressable, ScrollView, Text, View } from 'react-native';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, User } from '../src/api';
import { useAuth } from '../src/auth';
import { Button, ErrorState, Field, Loading, styles, colors } from '../src/ui';

const emailPattern = /^\S+@\S+\.\S+$/;

export default function Admin() {
  const { user } = useAuth();
  if (!user?.is_admin) return <AccessDenied />;
  return <AdminScreen />;
}

function AccessDenied() {
  return (
    <View style={[styles.screen, styles.empty]}>
      <Text style={[styles.title, { fontSize: 20, textAlign: 'center' }]}>Acceso denegado</Text>
      <Text style={[styles.muted, { textAlign: 'center', marginTop: 6 }]}>Esta sección es solo para administradores.</Text>
    </View>
  );
}

function AdminScreen() {
  const query = useQuery({ queryKey: ['users'], queryFn: api.users });
  const qc = useQueryClient();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const create = useMutation({
    mutationFn: () => {
      if (!name || !emailPattern.test(email) || password.length < 8) {
        throw new Error('Agrega un nombre, un correo válido y una contraseña temporal de al menos 8 caracteres.');
      }
      return api.createUser({ name, email, password });
    },
    onSuccess: () => {
      setName('');
      setEmail('');
      setPassword('');
      setError('');
      qc.invalidateQueries({ queryKey: ['users'] });
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo crear el usuario.'),
  });
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar los usuarios." retry={() => query.refetch()} />;
  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.subtitle}>Crea cuentas y controla el acceso.</Text>
      {query.data?.map(item => <UserRow key={item.id} user={item} onRefresh={() => qc.invalidateQueries({ queryKey: ['users'] })} />)}
      <Text style={[styles.title, { fontSize: 21, marginTop: 16 }]}>Crear usuario</Text>
      <Field label="Nombre" value={name} onChangeText={setName} />
      <Field label="Correo" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" autoCorrect={false} />
      <Field label="Contraseña temporal" value={password} onChangeText={setPassword} secureTextEntry autoCapitalize="none" autoCorrect={false} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={create.isPending ? 'Creando…' : 'Crear usuario'} onPress={() => create.mutate()} disabled={create.isPending} />
    </ScrollView>
  );
}

function UserRow({ user, onRefresh }: { user: User; onRefresh: () => void }) {
  const active = useMutation({ mutationFn: () => api.setUserActive(user.id, !user.is_active), onSuccess: onRefresh });
  const force = useMutation({ mutationFn: () => api.forcePassword(user.id), onSuccess: onRefresh });
  function toggleActive() {
    if (!user.is_active) {
      active.mutate();
      return;
    }
    Alert.alert(`¿Desactivar a ${user.name}?`, 'No va a poder iniciar sesión hasta que lo reactives.', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Desactivar', style: 'destructive', onPress: () => active.mutate() },
    ]);
  }
  return (
    <View style={styles.card}>
      <Text style={{ color: colors.ink, fontWeight: '800', fontSize: 17 }}>{user.name}</Text>
      <Text style={styles.muted}>{user.email}</Text>
      <Text style={{ color: user.is_active ? colors.green : colors.error, marginTop: 5 }}>
        {user.is_active ? 'Activo' : 'Inactivo'}
        {user.is_admin ? ' · Administrador' : ''}
      </Text>
      {user.must_change_password ? <Text style={{ color: colors.yellow, fontWeight: '700', marginTop: 3 }}>Cambio de contraseña pendiente</Text> : null}
      <View style={{ flexDirection: 'row', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
        <Pressable
          style={[styles.chip, user.is_active && { borderColor: colors.yellow }, active.isPending && { opacity: 0.5 }]}
          onPress={toggleActive}
          disabled={active.isPending}
        >
          <Text style={[styles.chipText, user.is_active && { color: colors.yellow }]}>{user.is_active ? 'Desactivar' : 'Activar'}</Text>
        </Pressable>
        <Pressable
          style={[styles.chip, force.isPending && { opacity: 0.5 }]}
          disabled={force.isPending}
          onPress={() =>
            Alert.alert(`¿Forzar cambio de contraseña de ${user.name}?`, 'Va a tener que definir una nueva contraseña en su próximo ingreso.', [
              { text: 'Cancelar', style: 'cancel' },
              { text: 'Confirmar', onPress: () => force.mutate() },
            ])
          }
        >
          <Text style={styles.chipText}>Forzar cambio de contraseña</Text>
        </Pressable>
      </View>
    </View>
  );
}
