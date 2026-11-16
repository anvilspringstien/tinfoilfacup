/* Tin Foil FA Cup opt-in, local-only Campaign/Challenges backup. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TffcMagicBackup=api;
})(typeof window==='object'?window:null,function(){
  'use strict';
  const KEYS=Object.freeze([
    'tinFoilFACupJourney_v7',
    'tffc.challengeDeck.v1',
    'tffc.clubfinderCampaign.v1',
    'tffc.clubfinderCampaignIdentity.v1'
  ]);
  const FORMAT='tffc-keep-the-magic';
  const MAX_BYTES=2000000;
  const has=(obj,key)=>Object.prototype.hasOwnProperty.call(obj,key);
  function isObject(x){return x!==null&&typeof x==='object'&&!Array.isArray(x);}
  function create(storage,at){
    const data={};
    for(const key of KEYS){
      const value=storage.getItem(key);
      if(value===null)continue;
      if(typeof value!=='string')throw Error('Unexpected saved data type');
      try{if(!isObject(JSON.parse(value)))throw Error('not an object')}catch(e){throw Error('Saved progress is not valid JSON: '+key)}
      data[key]=value;
    }
    const doc={format:FORMAT,version:1,created_at:(at||new Date()).toISOString(),data};
    if(JSON.stringify(doc).length>MAX_BYTES)throw Error('Backup exceeds the safety size limit');
    return doc;
  }
  function validate(input){
    if(typeof input==='string'&&input.length>MAX_BYTES)throw Error('File is too large');
    let doc;
    try{doc=typeof input==='string'?JSON.parse(input):input}catch(e){throw Error('Not a JSON backup file')}
    if(!isObject(doc)||doc.format!==FORMAT||doc.version!==1||!isObject(doc.data))throw Error('Not a supported Tin Foil FA Cup backup');
    const data=Object.create(null);
    for(const key of Object.keys(doc.data)){
      if(!KEYS.includes(key))throw Error('Unexpected storage key in backup');
      const value=doc.data[key];
      if(typeof value!=='string')throw Error('Unexpected storage value');
      try{if(!isObject(JSON.parse(value)))throw Error('not an object')}catch(e){throw Error('Invalid saved progress: '+key)}
      data[key]=value;
    }
    if(!Object.keys(data).length)throw Error('This backup contains no saved Campaign or Challenge progress');
    return data;
  }
  function restore(storage,input){
    const data=validate(input);
    const previous=Object.create(null);
    for(const key of KEYS)previous[key]=storage.getItem(key);
    try{
      for(const key of KEYS)storage.removeItem(key);
      for(const key of KEYS)if(has(data,key))storage.setItem(key,data[key]);
    }catch(e){
      try{
        for(const key of KEYS)storage.removeItem(key);
        for(const key of KEYS)if(previous[key]!==null)storage.setItem(key,previous[key]);
      }catch(ignore){}
      throw Error('Restore could not finish. Previous progress was retained where storage permits.');
    }
    return Object.keys(data).length;
  }
  return {KEYS,create,validate,restore};
});