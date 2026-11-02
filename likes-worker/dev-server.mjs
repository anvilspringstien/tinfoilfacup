// Local-only, persistent shared Shed server. Never deploy this Node adapter.
import http from 'node:http';
import {readFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import os from 'node:os';
import {randomBytes} from 'node:crypto';
import {LikeStore} from './store.mjs';
import {handleLikes} from './service.mjs';
import {openStorage} from './sqlite-node.mjs';
const root=path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const data=path.join(os.tmpdir(),'tffac-likes-shed');await mkdir(data,{recursive:true,mode:0o700});
const store=new LikeStore(openStorage(path.join(data,'likes.sqlite')));
const postcode=JSON.parse(await readFile(path.join(root,'tests/fixtures/likes-postcode.json'),'utf8'));
const admin=randomBytes(24).toString('hex');
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.jpg':'image/jpeg'};
const server=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://'+req.headers.host);
  if(url.pathname.startsWith('/__likes/')){
   const origin=req.headers.origin||'';
   const known=/^http:\/\/(?:terminal\.local|localhost|127\.0\.0\.1)(?::\d+)?$/.test(origin);
   const body=[];let size=0;for await(const part of req){size+=part.length;if(size>512){res.writeHead(413);res.end();return;}body.push(part);}
   const request=new Request('http://likes.local/'+url.pathname.slice('/__likes/'.length),{method:req.method,headers:req.headers,...(body.length?{body:Buffer.concat(body)}:{})});
   const response=await handleLikes(request,{ALLOWED_ORIGINS:known?origin:'http://localhost',ADMIN_TOKEN:admin},(op,hash,liked)=>store[op](hash,liked));
   res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));return;
  }
  if(url.pathname==='/beta/like-config.json'){
   res.writeHead(200,{'content-type':'application/json','cache-control':'no-store'});res.end(JSON.stringify({enabled:false,endpoint:'/__likes'}));return;
  }
  if(url.pathname==='/__shed/postcode'){
   res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify(postcode));return;
  }
  if(url.pathname==='/__shed/count'){
   // Available solely on this private development preview, never Worker/public route.
   res.writeHead(200,{'content-type':'application/json','cache-control':'no-store'});res.end(JSON.stringify(store.count()));return;
  }
  const pathname=decodeURIComponent(url.pathname==='/'?'/beta/likes-shed.html':url.pathname.endsWith('/')?url.pathname+'index.html':url.pathname);
  const file=path.resolve(root,'.'+pathname);if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
  let bytes=await readFile(file);const ext=path.extname(file);
  if(ext==='.html'){
   // Isolated preview searches use local fixtures; no production counter calls.
   const guard='<script>(()=>{const f=window.fetch.bind(window);window.fetch=(u,o)=>/tffac-clubfinder-counter/.test(String(u))?Promise.reject(Error("Shed: identity counter disabled")):/api.postcodes.io\\/postcodes\\/CV12(?:%20| )?8NN/i.test(String(u))?f("/__shed/postcode"):f(u,o)})();</script>';
   bytes=Buffer.from(bytes.toString().replace('<head>','<head>'+guard));
  }
  res.writeHead(200,{'content-type':mime[ext]||'application/octet-stream','cache-control':'no-store'});res.end(bytes);
 }catch{res.writeHead(404);res.end('Not found');}
});
server.listen(Number(process.env.PORT||4173),'0.0.0.0',()=>console.log('TFFAC Like Shed ready'));
