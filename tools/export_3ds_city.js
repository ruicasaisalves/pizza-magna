#!/usr/bin/env node
/* Paints the city map of city.js (Porto Magno, the same pixel art as the browser game's City screen) and saves it
   for the 3DS port as 3ds/game/gfx/city.png, padded to 1024x1024 (the 3DS texture limit). The lots themselves go to
   data.lua with tools/export_3ds.js. Run both after changing city.js: node tools/export_3ds_city.js
   Uses the Chromium that Playwright drives (as tools/test_ingredients.js does). */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..');
(async()=>{
  const b=await chromium.launch(),pg=await b.newPage();
  await pg.setContent('<!doctype html><body></body>');
  await pg.addScriptTag({path:path.join(root,'city.js')});
  const url=await pg.evaluate(()=>{const map=CITY.paint([]),c=document.createElement('canvas');c.width=c.height=1024;
    c.getContext('2d').drawImage(map,0,0);return c.toDataURL('image/png')});
  await b.close();
  const out=path.join(root,'3ds/game/gfx/city.png');
  fs.writeFileSync(out,Buffer.from(url.split(',')[1],'base64'));
  console.log('3ds/game/gfx/city.png:',fs.statSync(out).size,'bytes');
})();
