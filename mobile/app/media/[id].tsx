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

const typeLabels: Record<'movie' | 'series', string> = { movie: 'Película', series: 'Serie' };

type EntryDraft = { user_id: number; name: string; score: number; opinion: string };

export default function MediaDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const isNew = id === 'new';
  const numeric = Number(id);
  const router = useRouter();
  const qc = useQueryClient();
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const detail = useQuery({ queryKey: ['mediaOne', numeric], queryFn: () => api.mediaOne(numeric), enabled: !isNew });
  const createdIdRef = useRef<number | null>(null);

  const [editing, setEditing] = useState(isNew);
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [category, setCategory] = useState('');
  const [type, setType] = useState<'movie' | 'series'>('movie');
  const [poster, setPoster] = useState<UploadFile | null>(null);
  const [entries, setEntries] = useState<EntryDraft[]>([]);
  const [error, setError] = useState('');
  const [modalImage, setModalImage] = useState<string>();

  useEffect(() => {
    const item = detail.data;
    if (!item || !users.data?.length) return;
    setTitle(item.title);
    setDate(item.watched_date);
    setCategory(item.category ?? '');
    setType(item.media_type);
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
      if (!title || !/^\d{4}-\d{2}-\d{2}$/.test(date) || entries.length !== 2) {
        throw new Error('Agrega un título, una fecha ISO (AAAA-MM-DD) y dos valoraciones.');
      }
      const payload = {
        title,
        media_type: type,
        watched_date: date,
        category: category || null,
        ratings: entries.map(entry => ({ user_id: entry.user_id, score: entry.score, opinion: entry.opinion || null })),
      };
      // Once the entry exists (this save or an earlier failed attempt), every retry updates
      // the same record instead of creating a new one.
      const existingId = createdIdRef.current ?? (isNew ? null : numeric);
      const result = existingId ? await api.updateMedia(existingId, payload) : await api.createMedia(payload);
      createdIdRef.current = result.id;
      if (poster) await api.uploadMedia(result.id, poster);
      return result.id;
    },
    onSuccess: async savedId => {
      setPoster(null);
      setEditing(false);
      await qc.invalidateQueries({ queryKey: ['media'] });
      await qc.invalidateQueries({ queryKey: ['mediaOne', savedId] });
      router.replace(`/media/${savedId}`);
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar.'),
  });

  if (!isNew && detail.isPending) return <Loading />;
  if (!isNew && detail.isError) return <ErrorState message={(detail.error as Error).message} retry={() => detail.refetch()} />;
  if (!isNew && detail.data && (!entries.length || !title)) return <Loading />;

  const item = detail.data;

  async function pickPoster() {
    const file = await pickImage();
    if (file) setPoster(file);
  }

  if (!isNew && item && !editing) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>{item.title}</Text>
            <DateText value={item.watched_date} />
          </View>
          <ConfirmDelete
            label="serie o película"
            onConfirm={async () => {
              await api.deleteMedia(numeric);
              qc.invalidateQueries({ queryKey: ['media'] });
              router.back();
            }}
          />
        </View>
        <Text
          style={{
            alignSelf: 'flex-start',
            color: '#fff',
            backgroundColor: colors.blue,
            paddingHorizontal: 10,
            paddingVertical: 4,
            borderRadius: 10,
            marginTop: 8,
            fontWeight: '700',
            overflow: 'hidden',
          }}
        >
          {typeLabels[item.media_type]}
        </Text>
        <Text style={[styles.muted, { marginTop: 6 }]}>{item.category ?? 'Sin categoría'}</Text>
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
        <Button title="Editar" onPress={() => setEditing(true)} secondary />
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
      <Text style={styles.title}>{isNew ? 'Nueva serie o película' : 'Editar serie o película'}</Text>
      <Field label="Título" value={title} onChangeText={setTitle} placeholder="Título" />
      <Field label="Fecha (AAAA-MM-DD)" value={date} onChangeText={setDate} placeholder="2026-01-31" />
      <Field label="Categoría" value={category} onChangeText={setCategory} placeholder="Opcional" />
      <View style={{ flexDirection: 'row', marginBottom: 13 }}>
        {(['movie', 'series'] as const).map(value => (
          <Pressable key={value} style={[styles.chip, type === value && styles.chipActive]} onPress={() => setType(value)}>
            <Text style={[styles.chipText, type === value && styles.chipTextActive]}>{typeLabels[value]}</Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.label}>Póster</Text>
      <PhotoPicker label="Foto del póster" uri={poster?.uri} existing={item?.image_path} onPick={pickPoster} />
      {entries.map((entry, index) => {
        const tone = personTone(entry.name);
        const accent = personColor(tone);
        return (
          <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 16 }]}>
            <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{entry.name}</Text>
            <Text style={styles.label}>Puntuación</Text>
            <ScoreSelector value={entry.score} tone={tone} onChange={score => updateEntry(index, { score })} />
            <Field
              label="Opinión (opcional)"
              value={entry.opinion}
              onChangeText={opinion => updateEntry(index, { opinion })}
              multiline
            />
          </View>
        );
      })}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={save.isPending ? 'Guardando…' : 'Guardar'} onPress={() => save.mutate()} disabled={save.isPending} />
      {!isNew ? <Button title="Cancelar" onPress={() => setEditing(false)} secondary /> : null}
    </ScrollView>
  );
}
