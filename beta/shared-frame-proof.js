/* Shed geometry proof: shared viewport-only scale, never content height. */
(function(){
 const stage=document.querySelector('.stage');
 if(!stage)return;
 const update=()=>{
  const height=window.visualViewport?.height||window.innerHeight;
  const scale=window.innerWidth>=700?Math.min(1,(height-20)/1015):1;
  stage.style.setProperty('--tffc-fit-scale',String(scale));
 };
 document.documentElement.classList.add('tffc-viewport-fit');
 window.addEventListener('resize',update);
 window.addEventListener('orientationchange',update);
 window.visualViewport?.addEventListener('resize',update);
 update();
})();