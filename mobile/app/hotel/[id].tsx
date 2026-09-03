import React, { useEffect, useRef, useState } from 'react';
import { Image, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, imageUrl, UploadFile } from '../../src/api';
import { pickImage } from '../../src/picker';
import {
  Button,
  ConfirmDelete,
  DateText,
  ErrorState,
  Field,
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
import { formatPrice } from '../(tabs)/hotels';

type EntryDraft = { user_id: number; name: string; score: number; opinion: string };

export default function HotelDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const isNew = id === 'new';
  const numeric = Number(id);
  const router = useRouter();
  const qc = useQueryClient();
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const detail = useQuery({ queryKey: ['hotel', numeric], queryFn: () => api.hotel(numeric), enabled: !isNew });
  const createdIdRef = useRef<number | null>(null);

  const [editing, setEditing] = useState(isNew);
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [location, setLocation] = useState('');
  const [price, setPrice] = useState('');
  const [currency, setCurrency] = useState<'UYU' | 'USD'>('UYU');
  const [photo, setPhoto] = useState<UploadFile | null>(null);
  const [entries, setEntries] = useState<EntryDraft[]>([]);
  const [error, setError] = useState('');
  const [modalImage, setModalImage] = useState<string>();

  useEffect(() => {
    const item = detail.data;
    if (!item || !users.data?.length) return;
    setName(item.name);
    setDate(item.visit_date);
    setLocation(item.location ?? '');
    setPrice(item.total_price == null ? '' : String(item.total_price));
    setCurrency(item.currency ?? 'UYU');
    const ordered = orderByTone(item.ratings, r => users.data!.find(u => u.id === r.user_id)?.name);
    setEntries(
      ordered.map(rating => ({
        user_id: rating.user_id,
        name: users.data!.find(u => u.id === rating.user_id)?.name ?? `Usuario ${rating.user_id}`,
        score: rating.score,
        opinion: rating.opinion ?? '',
      })),
    );
  }, [detail.data, users.data]);

  useEffect(() => {
    if (!isNew || entries.length || !users.data?.length) return;
    const ordered = orderByTone(users.data, u => u.name).slice(0, 2);
    setEntries(ordered.map(u => ({ user_id: u.id, name: u.name, score: 8, opinion: '' })));
  }, [isNew, users.data, entries.length]);

  const updateEntry = (index: number, patch: Partial<EntryDraft>) =>
    setEntries(current => current.map((entry, i) => (i === index ? { ...entry, ...patch } : entry)));

  const save = useMutation({
    mutationFn: async () => {
      if (!name || !/^\d{4}-\d{2}-\d{2}$/.test(date) || entries.length !== 2) {
        throw new Error('Agrega un nombre, una fecha ISO (AAAA-MM-DD) y dos valoraciones.');
      }
      const payload = {
        name,
        visit_date: date,
        location: location || null,
        total_price: price === '' ? null : Number(price),
        currency: price === '' ? null : currency,
        ratings: entries.map(entry => ({ user_id: entry.user_id, score: entry.score, opinion: entry.opinion || null })),
      };
      // Once the hotel exists (this save or an earlier failed attempt), every retry updates
      // the same record instead of creating a new one.
      const existingId = createdIdRef.current ?? (isNew ? null : numeric);
      const result = existingId ? await api.updateHotel(existingId, payload) : await api.createHotel(payload);
      createdIdRef.current = result.id;
      if (photo) await api.uploadHotel(result.id, photo);
      return result.id;
    },
    onSuccess: async savedId => {
      setPhoto(null);
      setEditing(false);
      await qc.invalidateQueries({ queryKey: ['hotels'] });
      await qc.invalidateQueries({ queryKey: ['hotel', savedId] });
      router.replace(`/hotel/${savedId}`);
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar el hotel.'),
  });

  if (!isNew && detail.isPending) return <Loading />;
  if (!isNew && detail.isError) return <ErrorState message={(detail.error as Error).message} retry={() => detail.refetch()} />;
  if (!isNew && detail.data && (!entries.length || !name)) return <Loading />;

  const item = detail.data;

  async function pickPhoto() {
    const file = await pickImage();
    if (file) setPhoto(file);
  }

  if (!isNew && item && !editing) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>{item.name}</Text>
            <DateText value={item.visit_date} />
            {item.location ? <Text style={styles.muted}>{item.location}</Text> : null}
          </View>
          <ConfirmDelete
            label="hotel"
            onConfirm={async () => {
              await api.deleteHotel(numeric);
              qc.invalidateQueries({ queryKey: ['hotels'] });
              router.back();
            }}
          />
        </View>
        <Text style={{ color: colors.blue, fontWeight: '800', fontSize: 17, marginTop: 8 }}>{formatPrice(item.total_price, item.currency)}</Text>
        {item.image_path ? (
          <Pressable onPress={() => setModalImage(item.image_path!)} style={{ alignSelf: 'center', marginTop: 16 }}>
            <Photo path={item.image_path} size={180} />
          </Pressable>
        ) : null}
        <Text style={[styles.title, { fontSize: 20, marginTop: 20 }]}>
          Promedio {item.average_rating != null ? `${item.average_rating.toFixed(1)}/10` : '—'}
        </Text>
        {entries.map(entry => {
          const tone = personTone(entry.name);
          const accent = personColor(tone);
          return (
            <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5 }]}>
              <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 8 }}>{entry.name}</Text>
              <Text style={{ color: accent, fontWeight: '800', marginBottom: 6 }}>{entry.score}/10</Text>
              {entry.opinion ? <Text style={styles.muted}>“{entry.opinion}”</Text> : null}
            </View>
          );
        })}
        <Button title="Editar hotel" onPress={() => setEditing(true)} secondary />
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
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{isNew ? 'Nuevo hotel' : 'Editar hotel'}</Text>
      <Field label="Nombre" value={name} onChangeText={setName} placeholder="Nombre del hotel" />
      <Field label="Fecha de visita (AAAA-MM-DD)" value={date} onChangeText={setDate} placeholder="2026-01-31" />
      <Field label="Ubicación" value={location} onChangeText={setLocation} />
      <Field label="Precio total" value={price} onChangeText={setPrice} keyboardType="numeric" placeholder="0.00" />
      <Text style={styles.label}>Moneda</Text>
      <View style={{ flexDirection: 'row', marginBottom: 12 }}>
        {(['UYU', 'USD'] as const).map(value => (
          <Pressable key={value} onPress={() => setCurrency(value)} style={[styles.chip, currency === value && styles.chipActive]}>
            <Text style={[styles.chipText, currency === value && styles.chipTextActive]}>{value}</Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.label}>Foto</Text>
      <PhotoPicker label="Foto del hotel" uri={photo?.uri} existing={item?.image_path} onPick={pickPhoto} />
      {entries.map((entry, index) => {
        const tone = personTone(entry.name);
        const accent = personColor(tone);
        return (
          <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 16 }]}>
            <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{entry.name}</Text>
            <Text style={styles.label}>Puntuación</Text>
            <ScoreSelector value={entry.score} tone={tone} onChange={score => updateEntry(index, { score })} />
            <Field label="Opinión (opcional)" value={entry.opinion} onChangeText={opinion => updateEntry(index, { opinion })} multiline />
          </View>
        );
      })}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={save.isPending ? 'Guardando…' : 'Guardar hotel'} onPress={() => save.mutate()} disabled={save.isPending} />
      {!isNew ? <Button title="Cancelar" onPress={() => setEditing(false)} secondary /> : null}
    </ScrollView>
  );
}
