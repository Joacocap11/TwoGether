import * as SecureStore from 'expo-secure-store';

const configuredApiUrl = (process.env.EXPO_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '');
export const API_BASE_URL = configuredApiUrl.replace(/\/api\/v1$/, '');
const API_ROOT = configuredApiUrl.endsWith('/api/v1') ? configuredApiUrl : `${configuredApiUrl}/api/v1`;
const TOKEN_KEY = 'twogether.access_token';

export type User = { id: number; name: string; email: string; is_active: boolean; is_admin: boolean; must_change_password: boolean; created_at?: string };
export type Rating = { id?: number; user_id: number; visit_id?: number; score: number; comment?: string | null; opinion?: string | null; user?: { id: number; name: string } };
export type Dish = { id?: number; name: string; visit_id: number; user_id?: number | null; score: number; dish_price?: number | null; drink_price?: number | null; dessert_price?: number | null; image_path?: string | null; user?: { id: number; name: string } };
export type PlaceCategory = 'lunch' | 'snack' | 'dinner';
export const placeCategoryLabels: Record<PlaceCategory, string> = { lunch: 'Almuerzo', snack: 'Merienda', dinner: 'Cena' };
export type Place = { id: number; name: string; visit_date: string; location?: string | null; notes?: string | null; category?: PlaceCategory | null; currency?: 'UYU' | 'USD' | null; image_path?: string | null; photos?: string[]; average_rating?: number | null; place_average_rating?: number | null; dish_average_rating?: number | null; ratings?: Rating[]; dishes?: Dish[] };
export type TestOutcome = { id: number; test_record_id: number; user_id: number; result?: string | null; image_path?: string | null; user: { id: number; name: string } };
export type TestRecord = { id: number; title: string; result?: string | null; test_date: string; notes?: string | null; image_path?: string | null; outcomes: TestOutcome[] };
export type Media = { id: number; title: string; media_type: 'series' | 'movie'; watched_date: string; category?: string | null; image_path?: string | null; average_rating?: number | null; ratings: MediaRating[] };
export type MediaRating = { id?: number; user_id: number; score: number; opinion?: string | null };
export type Hotel = { id: number; name: string; visit_date: string; location?: string | null; total_price?: number | null; currency?: 'UYU' | 'USD' | null; image_path?: string | null; average_rating?: number | null; ratings: HotelRating[] };
export type HotelRating = { id?: number; user_id: number; score: number; opinion?: string | null };

export class ApiError extends Error { constructor(public status: number, message: string) { super(message); this.name = 'ApiError'; } }
const apiMessageTranslations: Record<string, string> = {
  'Incorrect email or password': 'Correo o contraseña incorrectos.',
  'Field required': 'Este campo es obligatorio.',
  'Passwords do not match': 'Las contraseñas no coinciden.',
  'Current password is incorrect': 'La contraseña actual es incorrecta.',
  'Email already registered': 'El correo ya está registrado.',
};
function translateApiMessage(message: string) { return apiMessageTranslations[message] ?? message; }
export function formatApiError(detail: unknown, status: number) {
  if (typeof detail === 'string' && detail.trim()) return translateApiMessage(detail.trim());
  if (Array.isArray(detail)) {
    const messages = detail.map(item => {
      if (typeof item === 'string') return translateApiMessage(item);
      if (item && typeof item === 'object' && 'msg' in item && typeof item.msg === 'string') return translateApiMessage(item.msg);
      return '';
    }).filter(Boolean);
    if (messages.length) return messages.join(' · ');
  }
  if (detail && typeof detail === 'object' && 'msg' in detail && typeof detail.msg === 'string') return translateApiMessage(detail.msg);
  return status ? `No se pudo completar la solicitud (${status})` : 'No se pudo conectar con TwoGether.';
}
export const imageUrl = (path?: string | null) => {
  if (!path) return undefined;
  if (path.startsWith('http')) return path;
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/uploads/${path}`}`;
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!API_BASE_URL) throw new ApiError(0, 'No se pudo conectar con TwoGether.');
  const token = await SecureStore.getItemAsync(TOKEN_KEY);
  const headers = new Headers(init.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(init.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  let response: Response;
  try { response = await fetch(`${API_ROOT}${path}`, { ...init, headers }); }
  catch { throw new ApiError(0, 'No se pudo conectar con TwoGether.'); }
  if (response.status === 401) { await SecureStore.deleteItemAsync(TOKEN_KEY); throw new ApiError(401, 'La sesión expiró.'); }
  if (!response.ok) {
    let detail: unknown;
    try { detail = (await response.json()).detail; } catch { /* non-JSON response */ }
    throw new ApiError(response.status, formatApiError(detail, response.status));
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export async function login(email: string, password: string) {
  if (!API_BASE_URL) throw new ApiError(0, 'No se pudo conectar con TwoGether.');
  const body = `username=${encodeURIComponent(email.trim())}&password=${encodeURIComponent(password)}`;
  let response: Response;
  try {
    response = await fetch(`${API_ROOT}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
  } catch { throw new ApiError(0, 'No se pudo conectar con TwoGether.'); }
  if (!response.ok) {
    let detail: unknown;
    try { detail = (await response.json()).detail; } catch { /* non-JSON response */ }
    throw new ApiError(response.status, formatApiError(detail, response.status));
  }
  const token: { access_token: string; must_change_password: boolean } = await response.json();
  await SecureStore.setItemAsync(TOKEN_KEY, token.access_token);
  return token;
}
export async function logout() { await SecureStore.deleteItemAsync(TOKEN_KEY); }
export async function storedToken() { return SecureStore.getItemAsync(TOKEN_KEY); }
export const api = {
  me: () => request<User>('/auth/me'),
  changePassword: (data: { current_password?: string; new_password: string; confirm_password: string }) => request<User>('/auth/change-password', { method: 'POST', body: JSON.stringify(data) }),
  places: () => request<Place[]>('/places'),
  place: (id: number) => request<Place>(`/places/${id}`),
  createPlace: (data: unknown) => request<Place>('/places/complete', { method: 'POST', body: JSON.stringify(data) }),
  updatePlace: (id: number, data: unknown) => request<Place>(`/places/${id}/complete`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePlace: (id: number) => request<void>(`/places/${id}`, { method: 'DELETE' }),
  uploadPlace: (id: number, file: UploadFile) => upload<Place>(`/places/${id}/upload`, file),
  uploadDish: (id: number, file: UploadFile) => upload<Dish>(`/dishes/${id}/upload`, file),
  tests: () => request<TestRecord[]>('/tests'),
  createTest: (data: unknown) => request<TestRecord>('/tests/complete', { method: 'POST', body: JSON.stringify(data) }),
  updateTest: (id: number, data: unknown) => request<TestRecord>(`/tests/${id}/complete`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTest: (id: number) => request<void>(`/tests/${id}`, { method: 'DELETE' }),
  uploadTest: (id: number, file: UploadFile) => upload<TestRecord>(`/tests/${id}/upload`, file),
  uploadOutcome: (id: number, file: UploadFile) => upload<TestRecord>(`/tests/outcomes/${id}/upload`, file),
  media: () => request<Media[]>('/media'), mediaOne: (id: number) => request<Media>(`/media/${id}`),
  createMedia: (data: unknown) => request<Media>('/media', { method: 'POST', body: JSON.stringify(data) }), updateMedia: (id: number, data: unknown) => request<Media>(`/media/${id}`, { method: 'PUT', body: JSON.stringify(data) }), deleteMedia: (id: number) => request<void>(`/media/${id}`, { method: 'DELETE' }), uploadMedia: (id: number, file: UploadFile) => upload<Media>(`/media/${id}/upload`, file),
  hotels: () => request<Hotel[]>('/hotels'), hotel: (id: number) => request<Hotel>(`/hotels/${id}`), createHotel: (data: unknown) => request<Hotel>('/hotels', { method: 'POST', body: JSON.stringify(data) }), updateHotel: (id: number, data: unknown) => request<Hotel>(`/hotels/${id}`, { method: 'PUT', body: JSON.stringify(data) }), deleteHotel: (id: number) => request<void>(`/hotels/${id}`, { method: 'DELETE' }), uploadHotel: (id: number, file: UploadFile) => upload<Hotel>(`/hotels/${id}/upload`, file),
  users: () => request<User[]>('/users'), createUser: (data: unknown) => request<User>('/users', { method: 'POST', body: JSON.stringify(data) }), setUserActive: (id: number, active: boolean) => request<User>(`/users/${id}/active?active=${active}`, { method: 'PATCH' }), forcePassword: (id: number) => request<User>(`/users/${id}/force-password-change`, { method: 'POST' }),
};
export type UploadFile = { uri: string; name: string; type: string };
async function upload<T>(path: string, file: UploadFile) { const data = new FormData(); data.append('image', file as unknown as Blob); return request<T>(path, { method: 'POST', body: data }); }
