#!/usr/bin/env node
'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const dir='beta/assets/challenge-thumbs';
const expected=Array.from({length:27},(_,i)=>`mat-${String(i+1).padStart(2,'0')}-front.webp`);
const actual=fs.readdirSync(dir).filter(name=>name.endsWith('.webp')).sort();
assert.deepEqual(actual,expected,'Cabinet thumbnail set must be exactly mats 01-27');

let total=0;
for(const name of actual){
  const file=path.join(dir,name);
  const b=fs.readFileSync(file);
  total+=b.length;
  assert.equal(b.subarray(0,4).toString(),'RIFF',name+' is not RIFF');
  assert.equal(b.subarray(8,12).toString(),'WEBP',name+' is not WebP');
  assert.equal(b.subarray(12,16).toString(),'VP8 ',name+' must remain lossy VP8 WebP');
  assert.equal(b[23],0x9d,name+' VP8 start code mismatch');
  assert.equal(b[24],0x01,name+' VP8 start code mismatch');
  assert.equal(b[25],0x2a,name+' VP8 start code mismatch');
  const width=b.readUInt16LE(26)&0x3fff;
  const height=b.readUInt16LE(28)&0x3fff;
  assert.equal(width,200,name+' width');
  assert.equal(height,200,name+' height');
  assert(b.length<50000,name+' unexpectedly large: '+b.length);
}
assert(total<750000,'Cabinet thumbnail set unexpectedly heavy: '+total);
console.log('BETA CABINET THUMBNAILS: PASS');
console.log(`27 x 200px lossy WebPs | ${total} bytes total`);
