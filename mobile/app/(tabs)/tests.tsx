import React, { useEffect, useRef, useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View } from 'react-native';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { api, TestRecord, UploadFile } from '../../src/api';
import { pickImage } from '../../src/picker';
import {
  Button,
  DateText,
  ErrorState,
  Field,
  Loading,
  PhotoGallery,
  PhotoPicker,
  styles,
  colors,
  orderByTone,
  personTone,
  personColor,
} from '../../src/ui';

export default function Tests() {
  const query = useQuery({ queryKey: ['tests'], queryFn: api.tests });
  const router = useRouter();
  const [search, setSearch] = useState('');
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar los tests." retry={() => query.refetch()} />;
  const items = (query.data ?? []).filter(
    item => !search || `${item.title} ${item.notes ?? ''}`.toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <View style={styles.screen}>
      <FlatList
        data={items}
        keyExtractor={x => String(x.id)}
        contentContainerStyle={styles.content}
        refreshing={query.isRefetching}
        onRefresh={() => query.refetch()}
        ListHeaderComponent={
          <>
            <Text style={styles.title}>Tests</Text>
            <Text style={styles.subtitle}>Tus resultados y recuerdos compartidos.</Text>
            <TextInput
              value={search}
              onChangeText={setSearch}
              placeholder="Buscar por título o notas"
              placeholderTextColor="#61717B"
              style={styles.input}
            />
            <Button title="＋ Nuevo test" onPress={() => router.push('/test/new')} />
          </>
        }
        renderItem={({ item }) => <TestCard item={item} onPress={() => router.push(`/test/${item.id}`)} />}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.muted}>Aún no hay tests.</Text>
          </View>
        }
      />
    </View>
  );
}

function TestCard({ item, onPress }: { item: TestRecord; onPress: () => void }) {
  const photos = (item.outcomes ?? []).map(o => o.image_path).filter((path): path is string => Boolean(path));
  return (
    <Pressable onPress={onPress} style={[styles.card, { flexDirection: 'row', gap: 13 }]}>
      <PhotoGallery paths={photos} />
      <View style={{ flex: 1 }}>
        <Text style={{ color: colors.ink, fontSize: 18, fontWeight: '800' }}>{item.title}</Text>
        <DateText value={item.test_date} />
        {item.notes ? (
          <Text style={[styles.muted, { marginTop: 4 }]} numberOfLines={2}>
            {item.notes}
          </Text>
        ) : null}
      </View>
    </Pressable>
  );
}

type OutcomeDraft = {
  user_id: number;
  name: string;
  outcomeId?: number;
  photo: UploadFile | null;
  existingPhoto: string | null;
};

export function TestForm({ item, onDone }: { item?: TestRecord; onDone: (value: TestRecord) => void }) {
  const router = useRouter();
  const qc = useQueryClient();
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const createdIdRef = useRef<number | null>(null);
  const [title, setTitle] = useState(item?.title ?? '');
  const [date, setDate] = useState(item?.test_date ?? '');
  const [notes, setNotes] = useState(item?.notes ?? '');
  const [entries, setEntries] = useState<OutcomeDraft[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!users.data?.length || entries.length) return;
    if (item) {
      const ordered = orderByTone(item.outcomes, o => o.user.name);
      setEntries(ordered.map(o => ({ user_id: o.user_id, name: o.user.name, outcomeId: o.id, photo: null, existingPhoto: o.image_path ?? null })));
    } else {
      const ordered = orderByTone(users.data, u => u.name).slice(0, 2);
      setEntries(ordered.map(u => ({ user_id: u.id, name: u.name, outcomeId: undefined, photo: null, existingPhoto: null })));
    }
  }, [users.data, item, entries.length]);

  const updateEntry = (index: number, patch: Partial<OutcomeDraft>) =>
    setEntries(current => current.map((entry, i) => (i === index ? { ...entry, ...patch } : entry)));

  const mutation = useMutation({
    mutationFn: async () => {
      if (!title || !/^\d{4}-\d{2}-\d{2}$/.test(date) || entries.length !== 2) {
        throw new Error('Agrega un título, una fecha ISO (AAAA-MM-DD) y dos usuarios activos.');
      }
      const payload = { title, test_date: date, notes: notes || null, outcomes: entries.map(entry => ({ user_id: entry.user_id })) };
      // Once the test exists (this save or an earlier failed attempt), every retry updates
      // the same record instead of creating a new one.
      const existingId = createdIdRef.current ?? item?.id ?? null;
      const result = existingId ? await api.updateTest(existingId, payload) : await api.createTest(payload);
      createdIdRef.current = result.id;

      for (const entry of entries) {
        if (!entry.photo) continue;
        const outcome = result.outcomes.find(o => o.user_id === entry.user_id);
        if (outcome?.id) await api.uploadOutcome(outcome.id, entry.photo);
      }
      return result;
    },
    onSuccess: async value => {
      setEntries(current => current.map(entry => ({ ...entry, photo: null })));
      await qc.invalidateQueries({ queryKey: ['tests'] });
      onDone(value);
      router.replace(`/test/${value.id}`);
    },
    onError: e => setError(e instanceof Error ? e.message : 'No se pudo guardar el test.'),
  });

  async function pickEntryPhoto(index: number) {
    const file = await pickImage();
    if (file) updateEntry(index, { photo: file });
  }

  return (
    <View>
      <Field label="Título" value={title} onChangeText={setTitle} placeholder="Nombre del test" />
      <Field label="Fecha del test (AAAA-MM-DD)" value={date} onChangeText={setDate} placeholder="2026-01-31" />
      <Field label="Notas" value={notes} onChangeText={setNotes} multiline />
      {entries.map((entry, index) => {
        const tone = personTone(entry.name);
        const accent = personColor(tone);
        return (
          <View key={entry.user_id} style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 14 }]}>
            <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{entry.name}</Text>
            <PhotoPicker
              label={`Captura de ${entry.name}`}
              uri={entry.photo?.uri}
              existing={entry.existingPhoto}
              tone={tone}
              onPick={() => pickEntryPhoto(index)}
            />
          </View>
        );
      })}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Button title={mutation.isPending ? 'Guardando…' : 'Guardar test'} onPress={() => mutation.mutate()} disabled={mutation.isPending} />
    </View>
  );
}
