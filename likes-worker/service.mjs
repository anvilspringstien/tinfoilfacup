import {adminPage} from './admin-ui.mjs';
const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const json=(body,status=200,headers={})=>Response.json(body,{status,headers:{'cache-control':'no-store',...headers}});
export async function handleLikes(request,env,call) {
 const url=new URL(request.url),path=url.pathname;
 const page=adminPage(path,request.method);if(page)return page;
 if(path==='/health'&&request.method==='GET')return json({ok:true,service:'tffac-likes',contract_version:1});
 if(path==='/admin/count'&&request.method==='GET'){
  if(!env.ADMIN_TOKEN||request.headers.get('authorization')!==`Bearer ${env.ADMIN_TOKEN}`)return json({error:'unauthorized'},401);
  try{return json(await call('count'));}catch{return json({error:'temporarily_unavailable'},503);}
 }
 if(!['/state','/reaction'].includes(path))return json({error:'not_found'},404);
 const origin=request.headers.get('origin');
 const allowed=String(env.ALLOWED_ORIGINS||'').split(',').map(x=>x.trim()).filter(Boolean);
 if(!origin||!allowed.includes(origin))return json({error:'origin_not_allowed'},403);
 const cors={'access-control-allow-origin':origin,'vary':'Origin','access-control-allow-methods':'POST, OPTIONS','access-control-allow-headers':'content-type','access-control-max-age':'86400'};
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:cors});
 if(request.method!=='POST')return json({error:'method_not_allowed'},405,{...cors,allow:'POST, OPTIONS'});
 if(!/^application\/json(?:;|$)/i.test(request.headers.get('content-type')||''))return json({error:'json_required'},415,cors);
 if(Number(request.headers.get('content-length')||0)>512)return json({error:'request_too_large'},413,cors);
 let body;
 try{const text=await request.text();if(new TextEncoder().encode(text).length>512)return json({error:'request_too_large'},413,cors);body=JSON.parse(text);}catch{return json({error:'invalid_json'},400,cors);}
 if(!body||!UUID.test(body.token||'')||(path==='/reaction'&&typeof body.liked!=='boolean'))return json({error:'invalid_reaction'},400,cors);
 if(Object.keys(body).some(k=>!['token',...(path==='/reaction'?['liked']:[])].includes(k)))return json({error:'unexpected_fields'},400,cors);
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(body.token.toLowerCase()));
 const hash=Array.from(new Uint8Array(digest),n=>n.toString(16).padStart(2,'0')).join('');
 try{return json(await call(path==='/state'?'state':'set',hash,body.liked),200,cors);}
 catch{return json({error:'temporarily_unavailable'},503,cors);}
}
