import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { api, Hotel, User } from '../../src/api';
import { Button, DateText, ErrorState, Loading, Photo, styles, colors, orderByTone, personTone, personColor } from '../../src/ui';

export function formatPrice(total: number | null | undefined, currency: 'UYU' | 'USD' | null | undefined) {
  if (total == null || !currency) return 'Precio no registrado';
  return `${currency} ${total.toLocaleString('es-UY', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function Hotels() {
  const query = useQuery({ queryKey: ['hotels'], queryFn: api.hotels });
  const users = useQuery({ queryKey: ['users'], queryFn: api.users });
  const router = useRouter();
  const [search, setSearch] = useState('');
  const items = useMemo(
    () => (query.data ?? []).filter(x => `${x.name} ${x.location ?? ''}`.toLowerCase().includes(search.toLowerCase())),
    [query.data, search],
  );
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar los hoteles." retry={() => query.refetch()} />;
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
          <Text style={styles.title}>Hoteles</Text>
          <Text style={styles.subtitle}>Estadías y recuerdos compartidos.</Text>
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Buscar hoteles..."
            placeholderTextColor="#61717B"
            style={styles.input}
          />
          <Button title="＋ Nuevo hotel" onPress={() => router.push('/hotel/new')} />
        </>
      }
      renderItem={({ item }) => <HotelCard item={item} users={users.data ?? []} onPress={() => router.push(`/hotel/${item.id}`)} />}
      ListEmptyComponent={
        <View style={styles.empty}>
          <Text style={styles.muted}>Aún no hay hoteles.</Text>
        </View>
      }
    />
  );
}

function HotelCard({ item, users, onPress }: { item: Hotel; users: User[]; onPress: () => void }) {
  const ordered = orderByTone(item.ratings, r => users.find(u => u.id === r.user_id)?.name);
  return (
    <Pressable style={[styles.card, { flexDirection: 'row', gap: 13 }]} onPress={onPress}>
      <Photo path={item.image_path} />
      <View style={{ flex: 1 }}>
        <Text style={{ color: colors.ink, fontSize: 18, fontWeight: '800' }}>{item.name}</Text>
        {item.location ? <Text style={styles.muted}>{item.location}</Text> : null}
        <DateText value={item.visit_date} />
        <Text style={{ color: colors.blue, fontWeight: '800', marginTop: 4 }}>{formatPrice(item.total_price, item.currency)}</Text>
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
