import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, Text, TextInput, View } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { api, Place } from '../../src/api';
import { Button, DateText, ErrorState, Loading, PhotoGallery, Stars, styles, colors } from '../../src/ui';

const categoryLabels: Record<string, string> = { all: 'Todos', dinner: 'Cena', lunch: 'Almuerzo', snack: 'Merienda' };

export default function Restaurants() {
  const router = useRouter();
  const query = useQuery({ queryKey: ['places'], queryFn: api.places });
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const categories = useMemo(() => ['all', ...new Set((query.data ?? []).map(item => item.category).filter(Boolean) as string[])], [query.data]);
  const items = (query.data ?? []).filter(item => (!search || `${item.name} ${item.location ?? ''}`.toLowerCase().includes(search.toLowerCase())) && (category === 'all' || category === item.category));
  if (query.isPending) return <Loading />;
  if (query.isError) return <ErrorState message="No se pudieron cargar los restaurantes." retry={() => query.refetch()} />;
  return <View style={styles.screen}><FlatList data={items} keyExtractor={item => String(item.id)} contentContainerStyle={styles.content} refreshing={query.isRefetching} onRefresh={() => query.refetch()} ListHeaderComponent={<><Text style={styles.title}>Restaurantes</Text><Text style={styles.subtitle}>Nuestros restaurantes y momentos compartidos.</Text><TextInput value={search} onChangeText={setSearch} placeholder="Buscar por nombre o ubicación" placeholderTextColor="#61717B" style={styles.input} /><View style={{ flexDirection: 'row', marginBottom: 16, flexWrap: 'wrap', gap: 7 }}>{categories.map(value => <Pressable key={value} onPress={() => setCategory(value)} style={[styles.chip, category === value && styles.chipActive]}><Text style={[styles.chipText, category === value && styles.chipTextActive]}>{categoryLabels[value] ?? value}</Text></Pressable>)}</View><Button title="＋ Nuevo restaurante" onPress={() => router.push('/place/new')} /></>} renderItem={({ item }) => <RestaurantCard item={item} onPress={() => router.push(`/place/${item.id}`)} />} ListEmptyComponent={<View style={styles.empty}><Text style={styles.muted}>Aún no hay restaurantes.</Text></View>} /></View>;
}

function RestaurantCard({ item, onPress }: { item: Place; onPress: () => void }) {
  return <Pressable onPress={onPress} style={styles.card}><View style={{ flexDirection: 'row', gap: 13 }}><PhotoGallery paths={[item.image_path, ...(item.photos ?? [])]} /><View style={{ flex: 1 }}><View style={{ flexDirection: 'row', justifyContent: 'space-between', gap: 8 }}><Text style={{ color: colors.ink, fontSize: 18, fontWeight: '800', flex: 1 }}>{item.name}</Text>{item.category ? <Text style={[styles.chipTextActive, { backgroundColor: colors.blue, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 10, overflow: 'hidden' }]}>{categoryLabels[item.category] ?? item.category}</Text> : null}</View>{item.location ? <Text style={styles.muted}>{item.location}</Text> : null}<DateText value={item.visit_date} /><View style={[styles.row, { marginTop: 6 }]}><Stars score={item.place_average_rating ?? item.average_rating ?? 0} /><Text style={styles.muted}>Lugar {item.place_average_rating?.toFixed(1) ?? item.average_rating?.toFixed(1) ?? '—'}</Text></View><Text style={[styles.muted, { marginTop: 3 }]}>Plato {item.dish_average_rating?.toFixed(1) ?? '—'}</Text></View></View></Pressable>;
}
