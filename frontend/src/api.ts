export const API_URL=(import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export const API_ORIGIN=API_URL.replace(/\/api\/v1\/?$/,'');
export type Place={id:number;name:string;visit_date:string;location?:string|null;notes?:string|null;image_path?:string|null;average_rating?:number|null};
export type Dish={id:number;name:string;description?:string|null;visit_id:number;user_id?:number|null;score:number;notes?:string|null;image_path?:string|null};
export type Rating={id:number;score:number;comment?:string|null;user_id:number;visit_id:number};
export type TestRecord={id:number;title:string;result:string;test_date:string;notes?:string|null;image_path?:string|null};
export type User={id:number;name:string;email:string};
export function imageUrl(path?:string|null){return path?path.startsWith('http')?path:`${API_ORIGIN}/uploads/${path}`:undefined}
export async function api<T>(path:string, options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('twogether_token'); const headers=new Headers(options.headers); const isLogin=path==='/auth/login';
 if(options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type','application/json');
 if(token) headers.set('Authorization',`Bearer ${token}`);
 const request={...options,headers,body:isLogin&&typeof options.body==='string'?new URLSearchParams(Object.entries(JSON.parse(options.body)) as [string,string][]):options.body};
 const response=await fetch(`${API_URL}${path}`,request); if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.detail||`No se pudo completar la solicitud (${response.status})`)}
 return response.status===204?undefined as T:response.json();
}
export const endpoints={places:'/places',place:(id:number)=>`/places/${id}`,placeUpload:(id:number)=>`/places/${id}/upload`,ratings:(id:number)=>`/places/${id}/ratings`,dishes:'/dishes',dish:(id:number)=>`/dishes/${id}`,dishUpload:(id:number)=>`/dishes/${id}/upload`,tests:'/tests',test:(id:number)=>`/tests/${id}`,testUpload:(id:number)=>`/tests/${id}/upload`};
