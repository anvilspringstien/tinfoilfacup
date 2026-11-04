// Public, read-only fiction. No room state, credentials or client script.
export const samplePeople = {
 sid:['Sid','DEMO 01612','Harrogate Town'],
 checky:['Checky','DEMO 01755','AFC Fylde'],
 dot:['Dot','DEMO 01428','York City'],
 mo:['Mo','DEMO 01904','Salisbury FC'],
 jean:['Jean','DEMO 01107','Chester FC'],
 bert:['Bert','DEMO 01862','Dartford FC'],
 barry:['Boot Room Barry','DEMO · MODERATOR','Keeping the kettle on']
};
export const sampleMessages = [
 ['barry','12:00','Doors unlocked. Kettle on. Who’s heading out for a bit of Cup football?',3],
 ['sid','12:02','Train booked, scarf found. Still deciding whether lunch counts as my first pie.',2],
 ['dot','12:04','It counts as preparation. A matchday pie is a separate department.',4],
 ['checky','12:06','Anyone else checking the weather every ten minutes, as if that’ll improve it?',2],
 ['mo','12:08','Packed a waterproof. The forecast can do what it likes now.',1],
 ['jean','12:11','My Campaign has taken me somewhere I’d never have thought to visit. That’s the best bit of this.',4],
 ['bert','12:14','Same. Came for the Cup, stayed for the little ground with the very big welcome.',3],
 ['sid','12:17','Important travel question: how early is too early to arrive?',1],
 ['dot','12:19','If the person opening the gate asks you for help, possibly then.',5,7],
 ['barry','12:23','Help with the gate is fine. Volunteering me to mark the pitch is another matter.',3],
 ['checky','12:27','Right. Sandwich for the journey or save the space?',1],
 ['mo','12:29','Save the space. You don’t travel all that way to review a sandwich from home.',4,10],
 ['jean','12:34','I’m bringing a friend who doesn’t follow football. They’ve already asked about the food twice.',3],
 ['bert','12:36','A natural. They’ll be explaining the draw to you by Monday.',2,12],
 ['sid','13:02','Arrived. Proper little buzz around the place. You can hear the warm-up from the road.',3],
 ['dot','13:08','That moment when you turn the corner and see the floodlights. Every time.',5],
 ['checky','13:15','Pie secured. Temperature somewhere between enthusiastic and volcanic.',4],
 ['barry','13:17','Give it a minute, pigeon. We’ve only just opened.',3,16],
 ['mo','13:29','Lovely chatting to a home supporter about where everyone’s journey started. We’re all taking different routes to the same afternoon.',4],
 ['jean','13:43','That’s it, isn’t it. Different scarves, same Cup.',5,18],
 ['bert','14:02','Programmes in the bag. Tea in hand. Phone going away for a bit. Enjoy your afternoons, all.',3],
 ['sid','16:56','Back on the train. Tired feet, happy head. Exactly what I needed.',4],
 ['checky','17:03','My friend now wants to know when we’re doing it again. I think the pie helped.',4],
 ['dot','17:08','See you for the draw. I’ve got an entirely unreasonable wish-list ready.',3],
 ['barry','17:12','That’ll do nicely. Get home safely. Same Cup. Different journeys. Good company.',6]
];
const escape = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const rows=sampleMessages.map(([person,time,text,hearts,reply],i)=>{
 const [name,call,custodian]=samplePeople[person];
 const parent=reply===undefined?null:sampleMessages[reply];
 const quote=parent?'<div class="quote"><strong>'+escape(samplePeople[parent[0]][0])+'</strong><span>'+escape(parent[2])+'</span></div>':'';
 return '<article class="message-row'+(person==='checky'?' own':'')+'"><span class="avatar'+(person==='checky'?' blue':'')+'" aria-hidden="true">'+escape(name[0])+'</span><div class="bubble"><div class="sender"><strong>'+escape(name)+'</strong><span class="sample-call">'+escape(call)+'</span></div><div class="sample-custodian">'+escape(custodian)+'</div>'+quote+'<p>'+escape(text)+'</p><div class="message-meta"><span class="sample-heart" aria-label="'+hearts+' sample hearts">♡ '+hearts+'</span><time>'+time+'</time></div></div></article>';
}).join('');
export const demoPage='<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#171612"><title>Sample conversation · The Boot Room</title><link rel="stylesheet" href="/room.css"></head><body><main class="workbench"><section class="phone-shell demo-room" aria-label="Sample Boot Room conversation"><div class="room"><div class="room-scroll"><header class="room-header"><div class="room-top"><span>TIN FOIL FA CUP</span><a class="entrance-back" href="/">Entrance ↗</a></div><div class="room-title"><div><p class="eyebrow">PULL UP A CHAIR</p><h2>The Boot Room</h2><p>Get in. Get talking.</p></div><img src="https://tinfoilfacup.com/beta/tffc-splash-logo-q80.webp" alt="Tin Foil FA Cup crest"></div></header><div class="door-line"><span class="room-sign closed">SAMPLE CONVERSATION</span><a class="entrance-back" href="/">Back to the door ↗</a></div><p class="sample-notice">A fictional qualifying-round afternoon. These pigeons, call signs and messages are made up to give you a feel for the room. This is a read-only demo, separate from the live chat.</p><div class="messages" aria-label="25 fictional sample messages"><p class="sample-date">A qualifying-round Saturday · 25 sample posts</p>'+rows+'</div><footer class="room-footer"><a href="/">← Back to the entrance</a><span>ONE CUP. PLENTY TO TALK ABOUT.</span></footer></div></div><p class="frame-caption">THE BOOT ROOM · A TIN FOIL FA CUP ADVENTURE</p></section></main></body></html>';
