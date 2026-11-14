const fs=require('fs');
const vm=require('node:vm');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');
function assert(cond,msg){if(!cond)throw new Error(msg);}

assert(html.includes('<meta name="viewport" content="width=980">'),
  'Stats report must retain its existing 980px printable/pinchable viewport');

assert(html.includes('.stats-actions{position:fixed;'),
  'Stats actions must stay fixed while the report scrolls');
assert(html.includes('frame.getBoundingClientRect().width/frame.offsetWidth'),
  'The fixed bar must account for the report frame scale');
assert(html.includes("viewport?.addEventListener('scroll',scheduleFit)"),
  'The bar must follow the visual viewport when panning');
assert(html.includes('padding-bottom:var(--stats-bottom-space,84px)'),
  'The final report content must be able to scroll above the bar');

// Report markup can execute while the parent frame is still being fitted.
const start=html.indexOf('  function statsActions(){');
const end=html.indexOf("    const status=bar.querySelector('.stats-share-status');",start);
assert(start>=0&&end>start,'Locate Stats toolbar placement code');
let frameWidth=980;
let notifyShellResize;
const frames=[];
const bar={offsetHeight:60,style:{setProperty(){}}};
const shell={};
const frame={parentElement:shell,offsetWidth:980,getBoundingClientRect:()=>({width:frameWidth})};
const viewport={width:980,height:1600,scale:1};
const window=Object.assign(new EventTarget(),{
  frameElement:frame,innerHeight:1600,
  visualViewport:Object.assign(new EventTarget(),viewport),
  parent:Object.assign(new EventTarget(),{
    ResizeObserver:class {
      constructor(callback){notifyShellResize=callback;}
      observe(element){assert(element===shell,'Observe the containing shell');}
      disconnect(){}
    }
  })
});
const document={querySelector:()=>bar,body:{style:{setProperty(){}}}};
vm.runInNewContext(html.slice(start,end)+'}statsActions();',{
  window,document,AbortController,requestAnimationFrame:callback=>frames.push(callback)
});
assert(bar.style.width==='520px','Fit immediately using the initial geometry');
frames.shift()?.();
frameWidth=390;
notifyShellResize();
assert(frames.length===1,'Refit after the shell settles without rotating');
frames.shift()();
assert(bar.style.width==='390px','The bar must fit the portrait frame');
console.log('BETA STATS TOUCH RETURN VISIBILITY: PASS');
