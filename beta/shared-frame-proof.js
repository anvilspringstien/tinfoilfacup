/* Opt-in proof of concept: ?viewportFit=1; no persistent settings. */
(function(){
 if(new URLSearchParams(location.search).get('viewportFit')==='0'||window.innerWidth<700)return;
 document.documentElement.classList.add('tffc-viewport-fit');
 const stage=document.querySelector('.stage');
 const field=stage.querySelector('.field');
 let scheduled=false;
 const update=()=>{
  scheduled=false;
  stage.style.setProperty('--tffc-fit-scale','1');
  field.style.removeProperty('overflow');
  // Clear previous orientation's measurements before measuring at natural size.
  field.style.removeProperty('min-height');
  const content=field.querySelector('.content');
  content.style.removeProperty('min-height');
  const children=[...content.children];
  const fieldRect=field.getBoundingClientRect();
  const lastBottom=Math.max(...children.map(el=>el.getBoundingClientRect().bottom));
  // Reserve visible breathing room beneath the footer inside the border.
  // Tall iPad portrait needs 40px; wide desktop has a shorter, flex-start
  // layout and needs less reserve. Keep iPad landscape and phone unchanged.
  const footerReserve=window.innerWidth>=1200?20:40;
  const required=Math.ceil(lastBottom-fieldRect.top+footerReserve);
  field.style.minHeight=Math.max(fieldRect.height,required)+'px';
  content.style.minHeight=required+'px';
  // In tall portrait layouts the flex child may extend beyond the stage's
  // fixed 100svh box. Fit the lowest actual border/content edge instead.
  const stageBottom=stage.getBoundingClientRect().bottom;
  const fieldBottom=field.getBoundingClientRect().bottom;
  const contentBottom=content.getBoundingClientRect().bottom;
  const naturalBottom=Math.max(stageBottom,fieldBottom,contentBottom);
  const viewport=window.visualViewport?.height||window.innerHeight;
  const heightFit=Math.min(1,Math.max(1,viewport-20)/Math.max(1,naturalBottom));
  const scale=heightFit;
  stage.style.setProperty('--tffc-fit-scale',String(scale));
 };
 const schedule=()=>{
  if(scheduled)return;
  scheduled=true;
  requestAnimationFrame(update);
 };
 window.addEventListener('load',schedule);
 window.addEventListener('resize',schedule);
 window.addEventListener('orientationchange',schedule);
 window.visualViewport?.addEventListener('resize',schedule);
 document.fonts?.ready?.then(schedule);
 schedule();
})();
