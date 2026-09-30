#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('beta/clubfinder-beta.html','utf8');

function array(name){
  const re=new RegExp('\\b(?:const|let|var)\\s+'+name+'\\s*=\\s*\\[');
  const m=html.match(re);
  assert(m,name+' array missing from BETA Clubfinder');
  const start=html.indexOf('[',m.index);
  let depth=0,inString=false,escape=false,quote='';
  for(let i=start;i<html.length;i++){
    const ch=html[i];
    if(inString){
      if(escape)escape=false;
      else if(ch==='\\\\')escape=true;
      else if(ch===quote)inString=false;
    }else{
      if(ch==='"'||ch==="'"){inString=true;quote=ch;}
      else if(ch==='[')depth++;
      else if(ch===']'){
        depth--;
        if(depth===0)return JSON.parse(html.slice(start,i+1));
      }
    }
  }
  throw Error('Unbalanced '+name+' array');
}

const norm=s=>String(s||'').toLowerCase().replace(/&/g,' and ')
  .replace(/\b(fc|afc|cfc|football club)\b/g,' ')
  .replace(/[^a-z0-9]+/g,' ').trim();

const eligible=array('ELIGIBLE');
const grounds=array('GROUNDS');
const law2=array('LAW2_ORIGIN_LOCATIONS');

const gloucester=eligible.filter(c=>norm(c.name)==='gloucester city');
assert.equal(gloucester.length,1,'Gloucester City eligible identity is missing or ambiguous');
assert.equal(gloucester[0].name,'Gloucester City AFC','BETA public identity regressed from Gloucester City AFC');
assert.equal(eligible.some(c=>c.name==='Gloucester FC'),false,'Retired Gloucester FC label returned');

function groundByName(name){
  const key=norm(name);
  return grounds.find(g=>norm(g.name||g.club)===key) ||
         law2.find(g=>norm(g.name||g.club)===key) || {};
}

const current=groundByName('Gloucester City AFC');
assert.equal(current.ground,'The KMM Energy Stadium','Gloucester current ground drifted');
assert.equal(current.postcode,'GL2 5HD','Gloucester current postcode drifted');
assert.equal(String(current.verification||'').toLowerCase(),'verified','Gloucester current ground is not verified');
assert(Number.isFinite(Number(current.lat))&&Number.isFinite(Number(current.lon)),
  'Gloucester current coordinates are missing');

function hav(a,b){
  const R=3958.7613,p=Math.PI/180;
  const dlat=(b.lat-a.lat)*p,dlon=(b.lon-a.lon)*p;
  const x=Math.sin(dlat/2)**2+
    Math.cos(a.lat*p)*Math.cos(b.lat*p)*Math.sin(dlon/2)**2;
  return 2*R*Math.asin(Math.sqrt(x));
}

const origin={lat:51.861614,lon:-2.221328}; // GL1 1AJ published postcode centroid
const ranked=eligible.map(club=>{
  const g=groundByName(club.name);
  const lat=Number(g.lat),lon=Number(g.lon);
  return Number.isFinite(lat)&&Number.isFinite(lon)
    ? {name:club.name,miles:hav(origin,{lat,lon}),ground:g.ground,postcode:g.postcode,verification:g.verification}
    : null;
}).filter(Boolean).sort((a,b)=>a.miles-b.miles);

const top3=ranked.slice(0,3);
assert.deepEqual(top3.map(x=>x.name),
  ['Longlevens FC','Gloucester City AFC','Tuffley Rovers FC'],
  'GL1 1AJ nearest-three canary drifted');
assert.equal(top3[1].postcode,'GL2 5HD');
assert.equal(top3[1].ground,'The KMM Energy Stadium');
assert.equal(String(top3[1].verification||'').toLowerCase(),'verified');

console.log('BETA GLOUCESTER CURRENT IDENTITY: PASS');
console.log('GL1 1AJ nearest three: '+top3.map(x=>x.name).join(' | '));
console.log('Gloucester City AFC: The KMM Energy Stadium • GL2 5HD • verified');
