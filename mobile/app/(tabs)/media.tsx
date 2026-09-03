import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { api, Media, User } from '../../src/api';
import { Button, DateText, ErrorState, Loading, Photo, styles, colors, orderByTone, personTone, personColor } from '../../src/ui';

const typeLabels: Record<string, string> = { all: 'Todas', movie: 'Películas', series: 'Series' };

export default function MediaList() {
  const query = useQuery({ queryKey: ['media'], queryFn: api.media });
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [type, setType] = useState<'all' | 'movie' | 'series'>('all');
  const items = useMemo(
    () =>
      (query.data ?? []).filter(
        x => (!search || `${x.title} ${x.category ?? ''}`.toLowerCase().includes(search.toLowerCase())) && (type === 'all' || x.media_type === type),
      ),
    [query.data, search, type],
  );
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar las series y películas." retry={() => query.refetch()} />;
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
          <Text style={styles.title}>Series / Películas</Text>
          <Text style={styles.subtitle}>Lo que miran y disfrutan juntos.</Text>
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar por título o categoría"
            placeholderTextColor="#61717B"
            style={styles.input}
          />
          <View style={{ flexDirection: 'row', marginBottom: 12 }}>
            {(['all', 'movie', 'series'] as const).map(value => (
              <Pressable key={value} onPress={() => setType(value)} style={[styles.chip, type === value && styles.chipActive]}>
                <Text style={[styles.chipText, type === value && styles.chipTextActive]}>{typeLabels[value]}</Text>
              </Pressable>
            ))}
          </View>
          <Button title="＋ Nueva serie o película" onPress={() => router.push('/media/new')} />
        </>
      }
      renderItem={({ item }) => <MediaCard item={item} users={users.data ?? []} onPress={() => router.push(`/media/${item.id}`)} />}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text style={styles.muted}>Aún no hay series o películas.</Text>
        </View>
      }
    />
  );
}

function MediaCard({ item, users, onPress }: { item: Media; users: User[]; onPress: () => void }) {
  const ordered = orderByTone(item.ratings, r => users.find(u => u.id === r.user_id)?.name);
  return (
    <Pressable style={[styles.card, { flexDirection: 'row', gap: 13 }]} onPress={onPress}>
      <Photo path={item.image_path} />
      <View style={{ flex: 1 }}>
        <Text style={{ color: colors.ink, fontSize: 18, fontWeight: '800' }}>{item.title}</Text>
        <Text style={styles.muted}>
          {typeLabels[item.media_type]} · {item.category ?? 'Sin categoría'}
        </Text>
        <DateText value={item.watched_date} />
        <View style={[styles.row, { marginTop: 6, flexWrap: 'wrap', gap: 10 }]}>
          {ordered.map(rating => {
            const name = users.find(u => u.id === rating.user_id)?.name ?? 'Usuario';
            const accent = personColor(personTone(name));
            return (
              <Text key={rating.user_id} style={{ color: accent, fontWeight: '700' }}>
                {name} {rating.score}/10
              </Text>
            );
          })}
          <Text style={{ color: colors.ink, fontWeight: '700' }}>Promedio {item.average_rating != null ? `${item.average_rating.toFixed(1)}/10` : '—'}</Text>
        </View>
      </View>
    </Pressable>
  );
}
