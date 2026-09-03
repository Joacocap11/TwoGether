import React, { useState } from 'react';
import { Image, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, imageUrl } from '../../src/api';
import { Button, ConfirmDelete, DateText, ErrorState, Loading, Photo, styles, orderByTone, personTone, personColor } from '../../src/ui';
import { TestForm } from '../(tabs)/tests';

export default function TestDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const isNew = id === 'new';
  const numeric = Number(id);
  const query = useQuery({
    queryKey: ['tests'],
    queryFn: api.tests,
    enabled: !isNew,
    select: items => items.find(test => test.id === numeric),
  });
  const qc = useQueryClient();
  const router = useRouter();
  const [editing, setEditing] = useState(isNew);
  const [modalImage, setModalImage] = useState<string>();

  if (!isNew && query.isPending) return <Loading />;
  if (!isNew && query.isError) return <ErrorState message="No se pudo cargar el test." retry={() => query.refetch()} />;
  if (!isNew && !query.data) return <ErrorState message="No se encontró el test." retry={() => query.refetch()} />;

  if (editing) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Text style={styles.title}>{isNew ? 'Nuevo test' : 'Editar test'}</Text>
        <TestForm item={query.data} onDone={() => setEditing(false)} />
        {!isNew ? <Button title="Cancelar" onPress={() => setEditing(false)} secondary /> : null}
      </ScrollView>
    );
  }

  const item = query.data!;
  const outcomes = orderByTone(item.outcomes, o => o.user.name);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>{item.title}</Text>
          <DateText value={item.test_date} />
        </View>
        <ConfirmDelete
          label="test"
          onConfirm={async () => {
            await api.deleteTest(numeric);
            qc.invalidateQueries({ queryKey: ['tests'] });
            router.back();
          }}
        />
      </View>
      {item.notes ? <Text style={[styles.muted, { marginVertical: 12 }]}>{item.notes}</Text> : null}
      <Button title="Editar test" onPress={() => setEditing(true)} secondary />
      {outcomes.map(outcome => {
        const tone = personTone(outcome.user.name);
        const accent = personColor(tone);
        return (
          <View key={outcome.id} style={[styles.card, { borderColor: accent, borderWidth: 1.5, marginTop: 14 }]}>
            <Text style={{ color: accent, fontWeight: '800', fontSize: 18, marginBottom: 10 }}>{outcome.user.name}</Text>
            {outcome.image_path ? (
              <Pressable onPress={() => setModalImage(outcome.image_path!)}>
                <Photo path={outcome.image_path} size={180} />
              </Pressable>
            ) : (
              <Text style={styles.muted}>Todavía no hay captura.</Text>
            )}
          </View>
        );
      })}
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
