import {DurableObject} from 'cloudflare:workers';
import {LikeStore} from './store.mjs';
import {handleLikes} from './service.mjs';
export class TffacLikes extends DurableObject {
 constructor(ctx,env){super(ctx,env);this.store=new LikeStore(ctx.storage);}
 async fetch(request){const {op,hash,liked}=await request.json();return Response.json(op==='count'?this.store.count():op==='state'?this.store.state(hash):this.store.set(hash,liked));}
}
export default {
 fetch(request,env){return handleLikes(request,env,async(op,hash,liked)=>{
  const stub=env.TFFAC_LIKES.get(env.TFFAC_LIKES.idFromName('tffac-global-likes-v1'));
  const response=await stub.fetch('https://likes.internal/',{method:'POST',body:JSON.stringify({op,hash,liked})});
  if(!response.ok)throw Error('Like storage unavailable');return response.json();
 });}
};
