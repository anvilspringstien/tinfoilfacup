/* One geometry authority. The two proofs use precisely the same code. */
(()=>{const stage=document.querySelector('.stage'),frame=document.querySelector('.frame'),content=frame.querySelector('.content');let pending=false;
function update(){pending=false;stage.style.setProperty('--shared-scale','1');frame.style.removeProperty('min-height');content.style.removeProperty('min-height');
const rect=frame.getBoundingClientRect();const bottom=Math.max(...[...content.children].map(el=>el.getBoundingClientRect().bottom));
const reserve=innerWidth>=1200?20:40;const required=Math.ceil(bottom-rect.top+reserve);
frame.style.minHeight=Math.max(rect.height,required)+'px';content.style.minHeight=required+'px';
const naturalBottom=Math.max(stage.getBoundingClientRect().bottom,frame.getBoundingClientRect().bottom,content.getBoundingClientRect().bottom);
const viewport=visualViewport?.height||innerHeight;const scale=innerWidth>=700?Math.min(1,Math.max(1,viewport-20)/Math.max(1,naturalBottom)):1;
stage.style.setProperty('--shared-scale',String(scale));
}
function schedule(){if(!pending){pending=true;requestAnimationFrame(update)}}
addEventListener('load',schedule);addEventListener('resize',schedule);visualViewport?.addEventListener('resize',schedule);document.fonts?.ready?.then(schedule);schedule();
})();