#!/usr/bin/env node
/* Paints the city map of city.js (Porto Magno, the same pixel art as the browser game's City screen) and saves it
   for the 3DS port as 3ds/game/gfx/city.png, padded to 1024x1024 (the 3DS texture limit), and the same map shrunk
   smoothly to MINI_W wide for the touch screen's navigator, 3ds/game/gfx/city_mini.png (padded to 256x128). The lots themselves go to
   data.lua with tools/export_3ds.js. Run both after changing city.js: node tools/export_3ds_city.js
   Uses the Chromium that Playwright drives (as tools/test_ingredients.js does). */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..');
(async()=>{
  const b=await chromium.launch(),pg=await b.newPage();
  await pg.setContent('<!doctype html><body></body>');
  await pg.addScriptTag({path:path.join(root,'city.js')});
  const MINI_W=152;   // the navigator's width on the 3DS touch screen (CITY_MINI_W in 3ds/game/main.lua)
  const [big,mini]=await pg.evaluate(W=>{const map=CITY.paint([]),c=document.createElement('canvas');c.width=c.height=1024;
    c.getContext('2d').drawImage(map,0,0);
    const m=document.createElement('canvas');m.width=256;m.height=128;const mc=m.getContext('2d');mc.imageSmoothingEnabled=true;mc.imageSmoothingQuality='high';
    mc.drawImage(map,0,0,W,Math.round(W*map.height/map.width));
    return [c.toDataURL('image/png'),m.toDataURL('image/png')]},MINI_W);
  await b.close();
  for(const [name,url] of [['city.png',big],['city_mini.png',mini]]){
    const out=path.join(root,'3ds/game/gfx',name);
    fs.writeFileSync(out,Buffer.from(url.split(',')[1],'base64'));
    console.log('3ds/game/gfx/'+name+':',fs.statSync(out).size,'bytes');
  }
})();
