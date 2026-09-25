// Temporary branch-only 4.6 MB HTML patch helper; retire after application.
const fs=require('fs');
const path='beta/clubfinder-beta.html';
let html=fs.readFileSync(path,'utf8');
const edits=[
  [
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Tin Foil FA Cup Clubfinder v7.6</title>",
    "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><script>if(new URLSearchParams(location.search||'').get('stats')==='1')document.querySelector('meta[name=\"viewport\"]').setAttribute('content','width=980');</script><title>Tin Foil FA Cup Clubfinder v7.6</title>"
  ],
  [
    "const doc='<!doctype html><html><head><meta charset=\"utf-8\"><title>Tin Foil FA Cup Stats '+season+'</title>'+",
    "const doc='<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=980\"><title>Tin Foil FA Cup Stats '+season+'</title>'+"
  ]
];
for(const [oldText,newText] of edits){
  const count=html.split(oldText).length-1;
  if(count!==1)throw Error('Unsafe patch: expected one occurrence; found '+count+' of '+oldText.slice(0,70));
  html=html.replace(oldText,newText);
}
fs.writeFileSync(path,html);
console.log('Applied two exact viewport edits to BETA HTML only');
