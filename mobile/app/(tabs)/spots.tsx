import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { api, Spot, SpotStatus } from '../../src/api';
import { Button, DateText, ErrorState, Loading, Photo, styles, colors } from '../../src/ui';

export default function Spots() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<SpotStatus | null>(null);
  const query = useQuery({ queryKey: ['spots', filter], queryFn: () => api.spots(filter ?? undefined) });
  const router = useRouter();
  const items = useMemo(
    () => (query.data ?? []).filter(x => `${x.name} ${x.location ?? ''}`.toLowerCase().includes(search.toLowerCase())),
    [query.data, search],
  );
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar los lugares." retry={() => query.refetch()} />;
  return (
    <FlatList
      data={items}
      keyExtractor={x => String(x.id)}
      style={styles.screen}
      contentContainerStyle={styles.content}
      refreshing={query.isRefetching}
      onRefresh={() => query.refetch()}
      ListHeaderComponent={
        <>
          <Text style={styles.title}>Lugares</Text>
          <Text style={styles.subtitle}>Para descubrir juntos.</Text>
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar lugares..."
            placeholderTextColor="#61717B"
            style={styles.input}
          />
          <View style={[styles.row, { marginBottom: 14 }]}>
            {([null, 'wishlist', 'visited'] as (SpotStatus | null)[]).map(value => (
              <Pressable key={value ?? 'all'} onPress={() => setFilter(value)} style={[styles.chip, filter === value && styles.chipActive]}>
                <Text style={[styles.chipText, filter === value && styles.chipTextActive]}>{value ? (value === 'visited' ? 'Visitado' : 'Por visitar') : 'Todos'}</Text>
              </Pressable>
            ))}
          </View>
          <Button title="＋ Nuevo lugar" onPress={() => router.push('/spot/new')} />
        </>
      }
      renderItem={({ item }) => <SpotCard item={item} onPress={() => router.push(`/spot/${item.id}`)} />}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text style={styles.muted}>Aún no hay lugares.</Text>
        </View>
      }
    />
  );
}

function SpotCard({ item, onPress }: { item: Spot; onPress: () => void }) {
  return (
    <Pressable style={[styles.card, { flexDirection: 'row', gap: 13 }]} onPress={onPress}>
      <Photo path={item.image_path} />
      <View style={{ flex: 1 }}>
        <View style={[styles.row, { justifyContent: 'space-between' }]}>
          <Text style={{ color: colors.ink, fontSize: 18, fontWeight: '800' }}>{item.name}</Text>
          <Text style={{ color: item.status === 'visited' ? colors.green : colors.muted, fontWeight: '700' }}>{item.status === 'visited' ? 'Visitado' : 'Por visitar'}</Text>
        </View>
        {item.location ? <Text style={styles.muted}>{item.location}</Text> : null}
        {item.status === 'visited' && item.visit_date ? <DateText value={item.visit_date} /> : null}
        {item.status === 'visited' ? (
          <Text style={{ color: colors.ink, fontWeight: '700', marginTop: 6 }}>
            Promedio {item.average_rating != null ? `${item.average_rating.toFixed(1)}/10` : '—'}
          </Text>
        ) : null}
      </View>
    </Pressable>
  );
}
