import {DurableObject} from 'cloudflare:workers';
import {RoomStore,RoomError,digest,token,DAY} from './store.mjs';
import {page,script,style} from './ui.mjs';
import {demoPage,scopedDemoPage} from './demo.mjs';
const json=(data,status=200,extra={})=>Response.json(data,{status,headers:{'cache-control':'no-store','x-content-type-options':'nosniff',...extra}});
const roomPrefix='/beta/boot-room';
const cookieName='__Host-bootroom';
export class BootRoom extends DurableObject {
 constructor(ctx,env){super(ctx,env);this.room=new RoomStore(ctx.storage);ctx.blockConcurrencyWhile(async()=>{if(await ctx.storage.getAlarm()===null)await ctx.storage.setAlarm(Date.now()+DAY);});}
 hash(request){return request.headers.get('x-room-session')||'';}
 async fetch(request){try{const path=new URL(request.url).pathname,hash=this.hash(request);
 if(path==='/api/socket'){
  if(request.headers.get('upgrade')?.toLowerCase()!=='websocket')return json({error:'WebSocket required'},426);
  const p=this.room.join(hash);if(this.ctx.getWebSockets().length>=20||this.ctx.getWebSockets(p.id).length>=2)return json({error:'Room connection limit reached'},429);
  const pair=new WebSocketPair(),client=pair[0],server=pair[1];this.ctx.acceptWebSocket(server,[p.id]);server.serializeAttachment({hash});server.send(JSON.stringify({type:'snapshot',...this.room.snapshot(hash)}));return new Response(null,{status:101,webSocket:client});
 }
 const a=request.method==='POST'?await request.json():{};let result;
 if(path==='/internal/invite')result=this.room.invite(a.name,a.hash,a.callSign,a.moderator);
 else if(path==='/api/walk-in')result=this.room.walkIn(a.campaign,a.session);
 else if(path==='/api/join')result=this.room.redeem(a.invite,a.session,a.campaign);
 else if(path==='/api/logout'){result=this.room.logout(hash);this.broadcast();}
 else if(path==='/api/state')result=this.room.snapshot(hash);
 else if(path==='/api/doors')result=this.room.doors();
 else if(path==='/api/read-closed')result=this.room.readClosed();
 else if(path==='/internal/admin'){result=this.room.admin(a);if(a.type==='doors')await this.ctx.storage.setAlarm(a.open?a.until:Date.now()+DAY);this.broadcast();}
 else return json({error:'not_found'},404);
 return json(result);
 }catch(e){return json({error:e instanceof RoomError?e.message:'Room temporarily unavailable'},e instanceof RoomError?e.status:503);}}
 async alarm(){this.room.admin({type:'status'});this.broadcast();await this.ctx.storage.setAlarm(Date.now()+DAY);}
 broadcast(){for(const ws of this.ctx.getWebSockets()){try{ws.send(JSON.stringify({type:'snapshot',...this.room.snapshot(ws.deserializeAttachment().hash)}));}catch{ws.close(1008,'Session ended');}}}
 webSocketMessage(ws,message){try{if(typeof message!=='string'||message.length>2048){ws.close(1009,'Message too large');return;}const a=JSON.parse(message);const result=this.room.action(ws.deserializeAttachment().hash,a);this.broadcast();ws.send(JSON.stringify({type:'ack',action:a.type,...result}));}catch(e){if(e instanceof RoomError&&[401,429].includes(e.status)){ws.close(1008,'Session ended');return;}ws.send(JSON.stringify({type:'error',error:e instanceof RoomError?e.message:'Room temporarily unavailable'}));}}
 webSocketClose(ws,code){ws.close([1000,1001,1008,1009,1011].includes(code)?code:1000,'');}
 webSocketError(ws){ws.close(1011,'Connection error');}
}
export default {async fetch(request,env){try{const u=new URL(request.url),scoped=u.pathname.startsWith(roomPrefix+'/'),path=scoped?u.pathname.slice(roomPrefix.length):u.pathname;
 if(scoped&&['/admin','/api/admin','/api/invite'].includes(path))return json({error:'not_found'},404);
 const framed=scoped&&['/','/chat'].includes(path)&&['shed','campaign'].includes(u.searchParams.get('frame'));
 const assets={'/demo':[scoped?scopedDemoPage:demoPage,'text/html; charset=utf-8'],'/':[page,'text/html; charset=utf-8'],'/chat':[page,'text/html; charset=utf-8'],'/admin':[page,'text/html; charset=utf-8'],'/room.js':[script,'text/javascript; charset=utf-8'],'/room.css':[style,'text/css; charset=utf-8']};
 if(assets[path]){if(!['GET','HEAD'].includes(request.method))return json({error:'method_not_allowed'},405);return new Response(request.method==='HEAD'?null:framed?page.replace('<html lang=', '<html data-frame="shed" lang='):assets[path][0],{headers:{'content-type':assets[path][1],'cache-control':'no-store','referrer-policy':'no-referrer','x-content-type-options':'nosniff','content-security-policy':"default-src 'none'; script-src 'self'; style-src 'self'; img-src https://tinfoilfacup.com; connect-src 'self'; frame-ancestors "+(framed?"'self'":"'none'")+"; base-uri 'none'; form-action 'none'"}});}
 if(path==='/health'&&request.method==='GET')return json({ok:true,service:'tffac-boot-room',stage:'invited-shed'});
 const post=['/api/walk-in','/api/join','/api/admin','/api/invite','/api/logout'].includes(path);if(!post&&!['/api/state','/api/socket','/api/doors','/api/read-closed'].includes(path))return json({error:'not_found'},404);
 if(request.method!==(post?'POST':'GET'))return json({error:'method_not_allowed'},405);
 if((post||path==='/api/socket')&&request.headers.get('origin')!==u.origin)return json({error:'origin_not_allowed'},403);
 let body={};if(post){if(!/^application\/json(?:;|$)/i.test(request.headers.get('content-type')||''))return json({error:'json_required'},415);const raw=await request.text();if(new TextEncoder().encode(raw).length>2048)return json({error:'body_too_large'},413);try{body=JSON.parse(raw);}catch{return json({error:'invalid_json'},400);}if(!body||typeof body!=='object'||Array.isArray(body))return json({error:'invalid_json'},400);}
 const stub=env.BOOT_ROOM.get(env.BOOT_ROOM.idFromName('invited-boot-room-v1'));
 if(path==='/api/read-closed')return scoped?stub.fetch('https://room.internal/api/read-closed'):json({error:'not_found'},404);
 if(path==='/api/doors'){
  const r=await stub.fetch('https://room.internal/api/doors');const headers=new Headers(r.headers);
  const origin=request.headers.get('origin');
  if(['https://tinfoilfacup.com','https://www.tinfoilfacup.com'].includes(origin)){headers.set('access-control-allow-origin',origin);headers.set('vary','Origin');}
  return new Response(r.body,{status:r.status,headers});
 }
 if(path==='/api/logout'){const old=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith(cookieName+'='))?.slice(cookieName.length+1)||'';if(/^[a-f0-9]{64}$/.test(old))await stub.fetch('https://room.internal/api/logout',{method:'POST',headers:{'x-room-session':await digest(old)},body:'{}'});return json({ok:true},200,{'set-cookie':cookieName+'=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'});}
 if(path==='/api/admin'||path==='/api/invite'){
  if(!env.ADMIN_TOKEN||request.headers.get('authorization')!==`Bearer ${env.ADMIN_TOKEN}`)return json({error:'unauthorized'},401);
  if(path==='/api/invite'){const invite=token();const r=await stub.fetch('https://room.internal/internal/invite',{method:'POST',body:JSON.stringify({name:body.name,callSign:body.callSign,moderator:body.moderator,hash:await digest(invite)})});if(!r.ok)return r;return json({...await r.json(),invite});}
  return stub.fetch('https://room.internal/internal/admin',{method:'POST',body:JSON.stringify(body)});
 }
 if(path==='/api/walk-in'){
  const session=token();
  const r=await stub.fetch('https://room.internal/api/walk-in',{method:'POST',body:JSON.stringify({campaign:body.campaign,session:await digest(session)})});
  if(!r.ok)return r;
  return json(await r.json(),200,{'set-cookie':`${cookieName}=${session}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=604800`});
 }
 if(path==='/api/join'){if(typeof body.invite!=='string'||!/^[a-f0-9]{64}$/.test(body.invite))return json({error:'invalid_invitation'},400);const session=token();const r=await stub.fetch('https://room.internal/api/join',{method:'POST',body:JSON.stringify({invite:await digest(body.invite),session:await digest(session),campaign:body.campaign})});if(!r.ok)return r;return json(await r.json(),200,{'set-cookie':`${cookieName}=${session}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=604800`});}
 const session=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith(cookieName+'='))?.slice(cookieName.length+1)||'';
 if(!/^[a-f0-9]{64}$/.test(session))return json({error:'Invitation required'},401);
 const h=new Headers(request.headers);h.delete('cookie');h.delete('authorization');h.set('x-room-session',await digest(session));return stub.fetch(new Request(new URL(path+u.search,u.origin),{method:request.method,headers:h}));
 }catch{return json({error:'Room temporarily unavailable'},503);}}};
