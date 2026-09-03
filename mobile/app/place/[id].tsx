import React, { useEffect, useRef, useState } from 'react';
import { Image, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, imageUrl, Place, PlaceCategory, UploadFile, placeCategoryLabels } from '../../src/api';
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
  formatISO,
  personTone,
  personColor,
} from '../../src/ui';

const CATEGORIES: PlaceCategory[] = ['lunch', 'snack', 'dinner'];

type EntryDraft = {
  user_id: number;
  name: string;
  dish: { name: string; score: number; dish_price: string; drink_price: string; dessert_price: string };
  rating: { score: number; comment: string };
  photo: UploadFile | null;
  existingPhoto: string | null;
};

const blankEntry = (userId: number, name: string): EntryDraft => ({
  user_id: userId,
  name,
  dish: { name: '', score: 8, dish_price: '', drink_price: '', dessert_price: '' },
  rating: { score: 8, comment: '' },
  photo: null,
  existingPhoto: null,
});

// Joaco always first, Selena second — resolved by name, never assumed from array order.
function orderByTone<T>(items: T[], nameOf: (item: T) => string | undefined) {
  return [...items].sort((a, b) => {
    const toneA = personTone(nameOf(a));
    const toneB = personTone(nameOf(b));
    if (toneA === toneB) return 0;
    return toneA === 'joaco' ? -1 : 1;
  });
}

export default function PlaceScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const isNew = id === 'new';
  const numericId = Number(id);
  const router = useRouter();
  const qc = useQueryClient();
  const createdIdRef = useRef<number | null>(null);

  const detail = useQuery({ queryKey: ['place', numericId], queryFn: () => api.place(numericId), enabled: !isNew });
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });

  const [editing, setEditing] = useState(isNew);
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [location, setLocation] = useState('');
  const [notes, setNotes] = useState('');
  const [category, setCategory] = useState<PlaceCategory>('dinner');
  const [currency, setCurrency] = useState<'UYU' | 'USD'>('UYU');
  const [generalPhoto, setGeneralPhoto] = useState<UploadFile | null>(null);
  const [entries, setEntries] = useState<EntryDraft[]>([]);
  const [error, setError] = useState('');
  const [modalImage, setModalImage] = useState<string>();

  useEffect(() => {
    const item = detail.data;
    if (!item || !users.data?.length) return;
    setName(item.name);
    setDate(item.visit_date);
    setLocation(item.location ?? '');
    setNotes(item.notes ?? '');
    setCategory(item.category ?? 'dinner');
    setCurrency(item.currency ?? 'UYU');
    const knownIds = item.dishes?.map(d => d.user_id).filter((v): v is number => v != null) ?? [];
    const people = knownIds.length === 2 ? knownIds.map(uid => users.data!.find(u => u.id === uid)).filter(Boolean) : users.data!.slice(0, 2);
    const ordered = orderByTone(people as { id: number; name: string }[], p => p.name);
    setEntries(ordered.map(person => {
      const dish = item.dishes?.find(d => d.user_id === person.id);
      const rating = item.ratings?.find(r => r.user_id === person.id);
      return {
        user_id: person.id,
        name: person.name,
        dish: {
          name: dish?.name ?? '',
          score: dish?.score ?? 8,
          dish_price: dish?.dish_price != null ? String(dish.dish_price) : '',
          drink_price: dish?.drink_price != null ? String(dish.drink_price) : '',
          dessert_price: dish?.dessert_price != null ? String(dish.dessert_price) : '',
        },
        rating: { score: rating?.score ?? 8, comment: rating?.comment ?? '' },
        photo: null,
        existingPhoto: dish?.image_path ?? null,
      };
    }));
  }, [detail.data, users.data]);

  useEffect(() => {
    if (!isNew || entries.length || !users.data?.length) return;
    const ordered = orderByTone(users.data, u => u.name).slice(0, 2);
    setEntries(ordered.map(u => blankEntry(u.id, u.name)));
  }, [isNew, users.data, entries.length]);

  const updateEntry = (index: number, patch: Partial<EntryDraft>) =>
    setEntries(current => current.map((entry, i) => (i === index ? { ...entry, ...patch } : entry)));

  const save = useMutation({
    mutationFn: async () => {
      if (!name || !/^\d{4}-\d{2}-\d{2}$/.test(formatISO(date)) || entries.length !== 2) {
        throw new Error('Agrega un nombre, una fecha y dos usuarios.');
      }
      const payload = {
        place: { name, visit_date: formatISO(date), location: location || null, notes: notes || null, category, currency },
        entries: entries.map(entry => ({
          user_id: entry.user_id,
          dish: {
            name: entry.dish.name,
            score: entry.dish.score,
            dish_price: entry.dish.dish_price === '' ? null : Number(entry.dish.dish_price),
            drink_price: entry.dish.drink_price === '' ? null : Number(entry.dish.drink_price),
            dessert_price: entry.dish.dessert_price === '' ? null : Number(entry.dish.dessert_price),
          },
          rating: { score: entry.rating.score, comment: entry.rating.comment || null },
        })),
      };
      // Once the place exists (this save or an earlier failed attempt), every retry updates
      // the same record instead of creating a new one.
      const existingId = createdIdRef.current ?? (isNew ? null : numericId);
      const result = existingId ? await api.updatePlace(existingId, payload) : await api.createPlace(payload);
      createdIdRef.current = result.id;

      if (generalPhoto) await api.uploadPlace(result.id, generalPhoto);
      for (const entry of entries) {
        if (!entry.photo) continue;
        const dish = result.dishes?.find(d => d.user_id === entry.user_id);
        if (dish?.id) await api.uploadDish(dish.id, entry.photo);
      }
      return result.id;
    },
    onSuccess: async savedId => {
      setGeneralPhoto(null);
      setEntries(current => current.map(entry => ({ ...entry, photo: null })));
      setEditing(false);
      await qc.invalidateQueries({ queryKey: ['places'] });
      await qc.invalidateQueries({ queryKey: ['place', savedId] });
      router.replace(`/place/${savedId}`);
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar el restaurante.'),
  });

  if (!isNew && detail.isPending) return <Loading />;
  if (!isNew && detail.isError) return <ErrorState message={(detail.error as Error).message} retry={() => detail.refetch()} />;
  if (!isNew && detail.data && (!entries.length || !name)) return <Loading />;

  const item: Place | undefined = detail.data;

  async function pickGeneralPhoto() {
    const file = await pickImage();
    if (file) setGeneralPhoto(file);
  }
  async function pickEntryPhoto(index: number) {
    const file = await pickImage();
    if (file) updateEntry(index, { photo: file });
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
            label="restaurante"
            onConfirm={async () => {
              await api.deletePlace(numericId);
              qc.invalidateQueries({ queryKey: ['places'] });
              router.back();
            }}
          />
        </View>
        {item.category ? (
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
            {placeCategoryLabels[item.category]}
          </Text>
        ) : null}
        <View style={{ flexDirection: 'row', gap: 9, marginTop: 15, flexWrap: 'wrap' }}>
          {(item.photos ?? []).map((path, index) => (
            <Pressable key={`${path}-${index}`} onPress={() => setModalImage(path)}>
              <Photo path={path} size={102} />
            </Pressable>
          ))}
        </View>
        {entries.map(entry => {
          const tone = personTone(entry.name);
          const accent = personColor(tone);
          return (
            <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5 }]}>
              <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 8 }}>{entry.name}</Text>
              {entry.existingPhoto ? (
                <Pressable onPress={() => setModalImage(entry.existingPhoto!)} style={{ marginBottom: 10 }}>
                  <Photo path={entry.existingPhoto} size={96} />
                </Pressable>
              ) : null}
              <Text style={styles.label}>Plato: {entry.dish.name || 'Sin especificar'}</Text>
              <Text style={[styles.muted, { marginBottom: 4 }]}>Puntuación del plato: {entry.dish.score}/10</Text>
              <Text style={[styles.muted, { marginBottom: 4 }]}>Puntuación del lugar: {entry.rating.score}/10</Text>
              {entry.rating.comment ? <Text style={styles.muted}>“{entry.rating.comment}”</Text> : null}
            </View>
          );
        })}
        <Button title="Editar restaurante" onPress={() => setEditing(true)} secondary />
        <Modal visible={Boolean(modalImage)} transparent onRequestClose={() => setModalImage(undefined)}>
          <Pressable style={{ flex: 1, backgroundColor: '#000c', justifyContent: 'center', alignItems: 'center' }} onPress={() => setModalImage(undefined)}>
            <Image source={{ uri: imageUrl(modalImage) }} style={{ width: '94%', height: '70%', resizeMode: 'contain' }} />
          </Pressable>
        </Modal>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{isNew ? 'Nuevo restaurante' : 'Editar restaurante'}</Text>
      <Field label="Nombre" value={name} onChangeText={setName} placeholder="Nombre del restaurante" />
      <Field label="Fecha de visita" value={date} onChangeText={setDate} placeholder="DD/MM/AAAA" />
      <Field label="Ubicación" value={location} onChangeText={setLocation} />
      <Field label="Notas" value={notes} onChangeText={setNotes} multiline />
      <Text style={styles.label}>Categoría</Text>
      <View style={{ flexDirection: 'row', gap: 7 }}>
        {CATEGORIES.map(value => (
          <Pressable key={value} onPress={() => setCategory(value)} style={[styles.chip, category === value && styles.chipActive]}>
            <Text style={[styles.chipText, category === value && styles.chipTextActive]}>{placeCategoryLabels[value]}</Text>
          </Pressable>
        ))}
      </View>

      <Text style={[styles.label, { marginTop: 16 }]}>Foto general</Text>
      <PhotoPicker label="Foto del restaurante" uri={generalPhoto?.uri} existing={item?.image_path} onPick={pickGeneralPhoto} />

      {entries.map((entry, index) => {
        const tone = personTone(entry.name);
        const accent = personColor(tone);
        return (
          <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 16 }]}>
            <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{entry.name}</Text>
            <PhotoPicker
              label={`Foto del plato de ${entry.name}`}
              uri={entry.photo?.uri}
              existing={entry.existingPhoto}
              tone={tone}
              onPick={() => pickEntryPhoto(index)}
            />
            <View style={{ marginTop: 12 }}>
              <Field label="Plato" value={entry.dish.name} onChangeText={value => updateEntry(index, { dish: { ...entry.dish, name: value } })} />
              <Field
                label="Precio del plato"
                value={entry.dish.dish_price}
                onChangeText={value => updateEntry(index, { dish: { ...entry.dish, dish_price: value } })}
                keyboardType="numeric"
              />
              <Field
                label="Precio de bebida"
                value={entry.dish.drink_price}
                onChangeText={value => updateEntry(index, { dish: { ...entry.dish, drink_price: value } })}
                keyboardType="numeric"
              />
              <Field
                label="Precio de postre"
                value={entry.dish.dessert_price}
                onChangeText={value => updateEntry(index, { dish: { ...entry.dish, dessert_price: value } })}
                keyboardType="numeric"
              />
              <Text style={styles.label}>Puntuación del plato</Text>
              <ScoreSelector value={entry.dish.score} tone={tone} onChange={score => updateEntry(index, { dish: { ...entry.dish, score } })} />
              <Text style={[styles.label, { marginTop: 14 }]}>Puntuación del lugar</Text>
              <ScoreSelector value={entry.rating.score} tone={tone} onChange={score => updateEntry(index, { rating: { ...entry.rating, score } })} />
              <Field
                label="Opinión del lugar (opcional)"
                value={entry.rating.comment}
                onChangeText={value => updateEntry(index, { rating: { ...entry.rating, comment: value } })}
                multiline
              />
            </View>
          </View>
        );
      })}

      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={save.isPending ? 'Guardando…' : 'Guardar restaurante'} onPress={() => save.mutate()} disabled={save.isPending} />
      {!isNew ? <Button title="Cancelar" onPress={() => setEditing(false)} secondary /> : null}
    </ScrollView>
  );
}
