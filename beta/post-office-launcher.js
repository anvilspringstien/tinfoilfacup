/* Add to the two BETA pages only after live mailbox verification. */
(function(){
 'use strict';
 var source=document.currentScript,base=new URL('.',source.src),loading=null;
 function load(){
  if(window.tffcOpenPostOffice)return Promise.resolve();
  if(loading)return loading;
  loading=new Promise(function(resolve,reject){
   var css=document.createElement('link');css.rel='stylesheet';css.href=new URL('post-office.css',base).href;
   var js=document.createElement('script');js.src=new URL('post-office.js',base).href;js.async=true;
   var cssReady=new Promise(function(ok,bad){css.onload=ok;css.onerror=bad});
   js.onload=function(){cssReady.then(resolve,reject)};js.onerror=reject;
   document.head.appendChild(css);document.head.appendChild(js);
  }).catch(function(error){loading=null;throw error});return loading;
 }
 document.addEventListener('click',function(event){
  if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  var link=event.target.closest('a[href]');if(!link)return;
  var config=window.TFFC_POST_OFFICE||{endpoint:"https://tffc-barry-post-office.anvilspringstien.workers.dev/messages",sitekey:"0x4AAAAAAFm9afKRjLbSGnx5"};
  if(!config||!config.endpoint||!config.sitekey)return;
  var url;try{url=new URL(link.href)}catch(_){return}
  if(url.origin!=='https://mail.google.com'||url.searchParams.get('to')!=='tinfoilfacup@gmail.com')return;
  var subject=url.searchParams.get('su')||'',kind;
  if(/Issue Report/i.test(subject))kind='issue';else if(/Feedback/i.test(subject))kind='feedback';else return;
  event.preventDefault();
  load().then(function(){window.tffcOpenPostOffice(kind,config)}).catch(function(){window.location.href=link.href});
 });
})();
