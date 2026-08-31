export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');
export type Place = { id:number; name:string; address?:string; city?:string; category?:string; description?:string; image_url?:string; average_rating?:number; ratings_count?:number };
export type Dish = { id:number; place_id:number; name:string; description?:string; price?:number; image_url?:string };
export type Rating = { id:number; place_id:number; score:number; comment?:string };
export async function api<T>(path:string, options:RequestInit={}) : Promise<T> {
 const token=localStorage.getItem('twogether_token'); const headers=new Headers(options.headers); const isLogin=path==='/auth/login'; if(!isLogin) headers.set('Content-Type','application/json'); if(token) headers.set('Authorization',`Bearer ${token}`); const request={...options,headers,body:isLogin&&typeof options.body==='string'?new URLSearchParams(Object.entries(JSON.parse(options.body)) as [string,string][]):options.body};
 const response=await fetch(`${API_URL}${path}`, request); if(!response.ok){const body=await response.json().catch(()=>({})); throw new Error(body.detail || `No se pudo completar la solicitud (${response.status})`)} return response.status===204? undefined as T: response.json();
}
export const endpoints={places:'/places', place:(id:number)=>`/places/${id}`, dishes:(id:number)=>`/places/${id}/dishes`, ratings:(id:number)=>`/places/${id}/ratings`};
