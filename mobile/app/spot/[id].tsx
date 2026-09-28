import React, { useEffect, useState } from 'react';
import { Image, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, imageUrl, SpotStatus, UploadFile } from '../../src/api';
import { useAuth } from '../../src/auth';
import { pickImage } from '../../src/picker';
import {
  Button,
  ConfirmDelete,
  DateText,
  ErrorState,
  Field,
  KeyboardAwareScreen,
  Loading,
  Photo,
  PhotoPicker,
  ScoreSelector,
  styles,
  colors,
  orderByTone,
  personTone,
  personColor,
} from '../../src/ui';

export default function SpotDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const isNew = id === 'new';
  const numeric = Number(id);
  const router = useRouter();
  const qc = useQueryClient();
  const { user } = useAuth();
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const detail = useQuery({ queryKey: ['spot', numeric], queryFn: () => api.spot(numeric), enabled: !isNew });

  const [editing, setEditing] = useState(isNew);
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [visitDate, setVisitDate] = useState('');
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState<SpotStatus>('wishlist');
  const [photo, setPhoto] = useState<UploadFile | null>(null);
  const [error, setError] = useState('');
  const [modalImage, setModalImage] = useState<string>();

  useEffect(() => {
    const item = detail.data;
    if (!item) return;
    setName(item.name);
    setLocation(item.location ?? '');
    setVisitDate(item.visit_date ?? '');
    setNotes(item.notes ?? '');
    setStatus(item.status);
  }, [detail.data]);

  const save = useMutation({
    mutationFn: async () => {
      if (!name) throw new Error('Agregá un nombre para el lugar.');
      const payload = { name, location: location || null, visit_date: status === 'visited' ? (visitDate || null) : null, notes: notes || null, status };
      const result = isNew ? await api.createSpot(payload) : await api.updateSpot(numeric, payload);
      if (photo) await api.uploadSpot(result.id, photo);
      return result.id;
    },
    onSuccess: async savedId => {
      setPhoto(null);
      setEditing(false);
      await qc.invalidateQueries({ queryKey: ['spots'] });
      await qc.invalidateQueries({ queryKey: ['spot', savedId] });
      router.replace(`/spot/${savedId}`);
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar el lugar.'),
  });

  const toggleStatus = useMutation({
    mutationFn: async () => {
      const item = detail.data!;
      return api.updateSpot(numeric, { name: item.name, location: item.location ?? null, visit_date: item.visit_date ?? null, notes: item.notes ?? null, status: item.status === 'visited' ? 'wishlist' : 'visited' });
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ['spots'] });
      await qc.invalidateQueries({ queryKey: ['spot', numeric] });
    },
  });

  if (!isNew && detail.isPending) return <Loading />;
  if (!isNew && detail.isError) return <ErrorState message={(detail.error as Error).message} retry={() => detail.refetch()} />;

  const item = detail.data;

  async function pickPhoto() {
    const file = await pickImage();
    if (file) setPhoto(file);
  }

  if (!isNew && item && !editing) {
    const people = orderByTone(users.data ?? [], u => u.name).slice(0, 2);
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>{item.name}</Text>
            {item.location ? <Text style={styles.muted}>{item.location}</Text> : null}
            <Text style={{ color: item.status === 'visited' ? colors.green : colors.muted, fontWeight: '700', marginTop: 4 }}>
              {item.status === 'visited' ? 'Visitado' : 'Por visitar'}
            </Text>
            {item.status === 'visited' && item.visit_date ? <DateText value={item.visit_date} /> : null}
          </View>
          <ConfirmDelete
            label="lugar"
            onConfirm={async () => {
              await api.deleteSpot(numeric);
              qc.invalidateQueries({ queryKey: ['spots'] });
              router.back();
            }}
          />
        </View>
        {item.notes ? <Text style={[styles.muted, { marginTop: 10 }]}>{item.notes}</Text> : null}
        {item.image_path ? (
          <Pressable onPress={() => setModalImage(item.image_path!)} style={{ alignSelf: 'center', marginTop: 16 }}>
            <Photo path={item.image_path} size={180} />
          </Pressable>
        ) : null}
        <Button
          title={item.status === 'visited' ? 'Volver a la lista de deseos' : 'Marcar como visitado'}
          onPress={() => toggleStatus.mutate()}
          secondary
        />
        {item.status !== 'visited' ? (
          <Text style={[styles.muted, { textAlign: 'center', marginTop: 20 }]}>Marcá este lugar como visitado para poder puntuarlo.</Text>
        ) : (
          <>
            <Text style={[styles.title, { fontSize: 20, marginTop: 20 }]}>
              Promedio {item.average_rating != null ? `${item.average_rating.toFixed(1)}/10` : 'Sin puntuaciones todavía'}
            </Text>
            {people.map(person => {
              const rating = item.ratings?.find(r => r.user_id === person.id);
              const tone = personTone(person.name);
              const accent = personColor(tone);
              const mine = user?.id === person.id;
              return mine ? (
                <SpotRatingEditor
                  key={person.id}
                  name={person.name}
                  tone={tone}
                  spotId={numeric}
                  existing={rating}
                  onSaved={() => qc.invalidateQueries({ queryKey: ['spot', numeric] })}
                />
              ) : (
                <View key={person.id} style={[styles.card, { borderColor: accent, borderWidth: 1.5 }]}>
                  <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 8 }}>{person.name}</Text>
                  {rating ? (
                    <>
                      <Text style={{ color: accent, fontWeight: '800', marginBottom: 6 }}>{rating.score}/10</Text>
                      {rating.comment ? <Text style={styles.muted}>“{rating.comment}”</Text> : null}
                    </>
                  ) : (
                    <Text style={styles.muted}>Sin puntuación todavía</Text>
                  )}
                </View>
              );
            })}
          </>
        )}
        <Button title="Editar lugar" onPress={() => setEditing(true)} secondary />
        <Modal visible={Boolean(modalImage)} transparent onRequestClose={() => setModalImage(undefined)}>
          <Pressable style={{ flex: 1, backgroundColor: '#000c', justifyContent: 'center', alignItems: 'center' }} onPress={() => setModalImage(undefined)}>
            <Pressable
              onPress={() => setModalImage(undefined)}
              style={{ position: 'absolute', top: 50, right: 24, zIndex: 1, backgroundColor: '#0006', borderRadius: 20, padding: 8 }}
            >
              <Text style={{ color: '#fff', fontSize: 20, fontWeight: '800' }}>✕</Text>
            </Pressable>
            <Image source={{ uri: imageUrl(modalImage) }} style={{ width: '94%', height: '70%', resizeMode: 'contain' }} />
          </Pressable>
        </Modal>
      </ScrollView>
    );
  }

  return (
    <KeyboardAwareScreen style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{isNew ? 'Nuevo lugar' : 'Editar lugar'}</Text>
      <Field label="Nombre" value={name} onChangeText={setName} placeholder="Nombre del lugar" />
      <Field label="Ubicación" value={location} onChangeText={setLocation} />
      <Field label="Notas" value={notes} onChangeText={setNotes} multiline />
      <Text style={styles.label}>Estado</Text>
      <View style={{ flexDirection: 'row', marginBottom: 12 }}>
        {(['wishlist', 'visited'] as const).map(value => (
          <Pressable key={value} onPress={() => setStatus(value)} style={[styles.chip, status === value && styles.chipActive]}>
            <Text style={[styles.chipText, status === value && styles.chipTextActive]}>{value === 'visited' ? 'Visitado' : 'Por visitar'}</Text>
          </Pressable>
        ))}
      </View>
      {status === 'visited' ? <Field label="Fecha de visita (AAAA-MM-DD)" value={visitDate} onChangeText={setVisitDate} placeholder="2026-01-31" /> : null}
      <Text style={styles.label}>Foto</Text>
      <PhotoPicker label="Foto del lugar" uri={photo?.uri} existing={item?.image_path} onPick={pickPhoto} />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={save.isPending ? 'Guardando…' : 'Guardar lugar'} onPress={() => save.mutate()} disabled={save.isPending} />
      {!isNew ? <Button title="Cancelar" onPress={() => setEditing(false)} secondary /> : null}
    </KeyboardAwareScreen>
  );
}

function SpotRatingEditor({
  name,
  tone,
  spotId,
  existing,
  onSaved,
}: {
  name: string;
  tone: 'joaco' | 'selena';
  spotId: number;
  existing?: { score: number; comment?: string | null };
  onSaved: () => void;
}) {
  const accent = personColor(tone);
  const [score, setScore] = useState(existing?.score ?? 8);
  const [comment, setComment] = useState(existing?.comment ?? '');
  const [error, setError] = useState('');
  const save = useMutation({
    mutationFn: () => (existing ? api.updateMySpotRating(spotId, { score, comment: comment || null }) : api.rateSpot(spotId, { score, comment: comment || null })),
    onSuccess: onSaved,
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar la puntuación.'),
  });
  return (
    <View style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 16 }]}>
      <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{name}</Text>
      <Text style={styles.label}>Tu puntuación</Text>
      <ScoreSelector value={score} tone={tone} onChange={setScore} />
      <Field label="Comentario (opcional)" value={comment} onChangeText={setComment} multiline />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={save.isPending ? 'Guardando…' : existing ? 'Actualizar puntuación' : 'Guardar puntuación'} onPress={() => save.mutate()} disabled={save.isPending} />
    </View>
  );
}
