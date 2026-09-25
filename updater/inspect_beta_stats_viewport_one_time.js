#!/usr/bin/env node
const fs=require('fs');
const s=fs.readFileSync('beta/clubfinder-beta.html','utf8');
console.log('META_HEAD',JSON.stringify(s.slice(0,10500).match(/<meta[^>]+>/gi)));
for(const needle of ['<!doctype html>','<meta name="viewport"','name="viewport"','name=\\\"viewport','const doc=\'<!doctype html','@media(max-width:650px)','tinFoilStatsRouteRequested','journeyCertificate(origin']){
 let p=s.indexOf(needle),offsets=[];
 while(p>=0&&offsets.length<7){offsets.push(p);p=s.indexOf(needle,p+needle.length)}
 console.log('TARGET',JSON.stringify({needle,offsets,around:offsets.map(p=>s.slice(Math.max(0,p-250),p+700))}));
}
console.log('SIZE',s.length);
