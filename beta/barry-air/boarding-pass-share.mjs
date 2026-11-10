// Draw from the public fields only. The private pass and its postcode never
// enter the image, including its pixels, filename or metadata.
const postcode=/\b(?:GIR\s*0AA|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\b/gi;

export function boardingPassImage({passenger,callSign,miles,campaign,nextFlight,date,ground,flight}){
 const canvas=document.createElement('canvas');
 canvas.width=960;canvas.height=640;
 const ctx=canvas.getContext('2d');
 if(!ctx)return Promise.reject(new Error('Image rendering is unavailable'));
 function text(value,x,y,font,colour,max=840){
  ctx.font=font;ctx.fillStyle=colour;
  ctx.fillText(String(value??'').replace(postcode,'').trim(),x,y,max);
 }
 function field(label,value,x,y,max){
  text(label,x,y,'bold 17px monospace','#50635c',max);
  text(value,x,y+38,'30px Georgia','#1e2c2d',max);
 }
 ctx.fillStyle='#f2eddd';ctx.fillRect(0,0,960,640);
 ctx.fillStyle='#084c61';ctx.fillRect(0,0,960,100);
 text('BARRY AIR',54,65,'bold 42px Georgia','#f6edcf',380);
 text('BOARDING PASS',638,63,'bold 22px monospace','#f6edcf',270);
 field('PASSENGER',passenger,54,145,475);
 field('CALL SIGN',callSign,594,145,312);
 field('CAMPAIGN',campaign,54,250,475);
 field('MILES FLOWN',miles,594,250,312);
 field('NEXT FLIGHT',nextFlight,54,366,852);
 text(date,54,447,'21px monospace','#48554e');
 text(ground,54,486,'21px monospace','#48554e');
 ctx.fillStyle='#e9e3d2';ctx.fillRect(0,528,960,112);
 ctx.strokeStyle='#879487';ctx.lineWidth=2;ctx.setLineDash([9,8]);
 ctx.beginPath();ctx.moveTo(0,528);ctx.lineTo(960,528);ctx.stroke();
 text(flight,54,595,'bold 20px monospace','#1e2c2d',540);
 text('tinfoilfacup.com',670,595,'20px monospace','#48554e',236);
 return new Promise((resolve,reject)=>{
  canvas.toBlob(blob=>blob?resolve(blob):reject(new Error('PNG encoding failed')),'image/png');
 });
}
