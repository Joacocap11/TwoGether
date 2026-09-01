export const API_URL=(import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export const API_ORIGIN=API_URL.replace(/\/api\/v1\/?$/,'');
export type User={id:number;name:string;email?:string};
export type PlaceCategory='lunch'|'snack'|'dinner';
export type Place={id:number;name:string;category?:PlaceCategory|null;visit_date:string;location?:string|null;notes?:string|null;image_path?:string|null;photos?:string[];average_rating?:number|null;place_average_rating?:number|null;dish_average_rating?:number|null;ratings?:Rating[];dishes?:Dish[]};
export type Dish={id:number;name:string;description?:string|null;visit_id:number;user_id:number;score:number;notes?:string|null;image_path?:string|null};
export type Rating={id:number;score:number;comment?:string|null;user_id:number;visit_id:number};
export type TestOutcome={id:number;user_id:number;result?:string|null;image_path?:string|null};
export type TestRecord={id:number;title:string;test_date:string;notes?:string|null;outcomes?:TestOutcome[];result?:string|null;image_path?:string|null};
export type MediaType='series'|'movie';
export type MediaRating={id:number;user_id:number;score:number};
export type MediaEntry={id:number;title:string;media_type:MediaType;watched_date:string;category?:string|null;image_path?:string|null;ratings:MediaRating[];average_rating?:number|null};
export type HotelRating={id:number;user_id:number;score:number;opinion?:string|null};
export type HotelVisit={id:number;name:string;visit_date:string;location?:string|null;image_path?:string|null;ratings:HotelRating[];average_rating?:number|null};
function formatApiError(detail:unknown,status:number){if(Array.isArray(detail))return detail.map(x=>typeof x==='object'&&x&&'msg' in x?String(x.msg):String(x)).join(' · ');if(detail&&typeof detail==='object'&&'msg' in detail)return String(detail.msg);return typeof detail==='string'?detail:`No se pudo completar la solicitud (${status})`}
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{const token=localStorage.getItem('twogether_token');const headers=new Headers(options.headers);const login=path==='/auth/login';if(options.body&&!(options.body instanceof FormData)&&!headers.has('Content-Type')&&!login)headers.set('Content-Type','application/json');if(token)headers.set('Authorization',`Bearer ${token}`);const body=login&&typeof options.body==='string'?new URLSearchParams(Object.entries(JSON.parse(options.body)) as [string,string][]):options.body;const r=await fetch(`${API_URL}${path}`,{...options,headers,body});if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(formatApiError(d.detail,r.status))}return r.status===204?undefined as T:r.json()}
export function imageUrl(path?:string|null){return path?(path.startsWith('http')?path:`${API_ORIGIN}/uploads/${path}`):undefined}
export const endpoints={places:'/places',place:(id:number)=>`/places/${id}`,placeUpload:(id:number)=>`/places/${id}/upload`,ratings:(id:number)=>`/places/${id}/ratings`,dishes:'/dishes',dish:(id:number)=>`/dishes/${id}`,dishUpload:(id:number)=>`/dishes/${id}/upload`,tests:'/tests',test:(id:number)=>`/tests/${id}`,testUpload:(id:number)=>`/tests/${id}/upload`,testOutcomeUpload:(testId:number,outcomeId:number)=>`/tests/${testId}/outcomes/${outcomeId}/upload`,completePlaces:'/places/complete',completeTests:'/tests/complete',media:'/media',mediaItem:(id:number)=>`/media/${id}`,mediaUpload:(id:number)=>`/media/${id}/upload`,hotels:'/hotels',hotel:(id:number)=>`/hotels/${id}`,hotelUpload:(id:number)=>`/hotels/${id}/upload`};
export const updatePlaceComplete=(id:number,data:unknown)=>api<Place>(`/places/${id}/complete`,{method:'PUT',body:JSON.stringify(data)});
export const uploadPlaceImage=(id:number,file:File)=>{const body=new FormData();body.append('image',file);return api<Place>(endpoints.placeUpload(id),{method:'POST',body})};
export const uploadDishImage=(id:number,file:File)=>{const body=new FormData();body.append('image',file);return api<Dish>(endpoints.dishUpload(id),{method:'POST',body})};
export const createTest=(data:unknown)=>api<TestRecord>(endpoints.completeTests,{method:'POST',body:JSON.stringify(data)});
export const updateTest=(id:number,data:unknown)=>api<TestRecord>(`/tests/${id}/complete`,{method:'PUT',body:JSON.stringify(data)});
export const uploadTestOutcomeImage=(testId:number,outcomeId:number,file:File)=>{const body=new FormData();body.append('image',file);return api<TestRecord>(endpoints.testOutcomeUpload(testId,outcomeId),{method:'POST',body})};

export const createPlaceComplete=(data:unknown)=>api<Place>(endpoints.completePlaces,{method:'POST',body:JSON.stringify(data)});
