export const API_URL=(import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export const API_ORIGIN=API_URL.replace(/\/api\/v1\/?$/,'');
export type Place={id:number;name:string;visit_date:string;location?:string|null;notes?:string|null;image_path?:string|null;average_rating?:number|null};
export type Dish={id:number;name:string;description?:string|null;visit_id:number;user_id?:number|null;score:number;notes?:string|null;image_path?:string|null};
export type Rating={id:number;score:number;comment?:string|null;user_id:number;visit_id:number};
export type TestRecord={id:number;title:string;result:string;test_date:string;notes?:string|null;image_path?:string|null};
export type User={id:number;name:string;email:string};
export function imageUrl(path?:string|null){return path?path.startsWith('http')?path:`${API_ORIGIN}/uploads/${path}`:undefined}
function formatApiError(detail: unknown, status: number): string {
 if (Array.isArray(detail)) {
  return detail.map(item => {
   if (item && typeof item === 'object' && 'msg' in item) {
    const field = 'loc' in item && Array.isArray(item.loc) ? String(item.loc[item.loc.length - 1]) : 'campo';
    return `${field}: ${String(item.msg)}`;
   }
   return String(item);
  }).join(' · ');
 }
 if (detail && typeof detail === 'object' && 'msg' in detail) return String(detail.msg);
 return typeof detail === 'string' ? detail : `No se pudo completar la solicitud (${status})`;
}
export async function api<T>(path:string, options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('twogether_token'); const headers=new Headers(options.headers); const isLogin=path==='/auth/login';
 if(options.body && !(options.body instanceof FormData) && !headers.has('Content-Type') && !isLogin) headers.set('Content-Type','application/json');
 if(token) headers.set('Authorization',`Bearer ${token}`);
 const request={...options,headers,body:isLogin&&typeof options.body==='string'?new URLSearchParams(Object.entries(JSON.parse(options.body)) as [string,string][]):options.body};
 const response=await fetch(`${API_URL}${path}`,request); if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(formatApiError(body.detail,response.status))}
 return response.status===204?undefined as T:response.json();
}
export const endpoints={places:'/places',place:(id:number)=>`/places/${id}`,placeUpload:(id:number)=>`/places/${id}/upload`,ratings:(id:number)=>`/places/${id}/ratings`,dishes:'/dishes',dish:(id:number)=>`/dishes/${id}`,dishUpload:(id:number)=>`/dishes/${id}/upload`,tests:'/tests',test:(id:number)=>`/tests/${id}`,testUpload:(id:number)=>`/tests/${id}/upload`};
