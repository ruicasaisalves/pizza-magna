#!/usr/bin/env node
/* Exports the browser game's dining room to the 3DS port, at half size (16 px tiles), so the touch screen shows the
   same room as the browser's day: the starter room (the 3DS has no room editor), its people and its paths.
   - 3ds/game/gfx/room.png (512x512): the room's floor, walls, front wall and street (320x272, at 0,0), then every
     piece that stands (tables, chairs, the kitchen, the ovens' frames, the pizza and the plate), each cut to its box.
   - 3ds/game/gfx/people.png (1024x1024): the characters of assets/cast (customers walk and seated, waiters' service,
     cooks' idle), each sheet shrunk to half (cells 16x29, seated 16x24).
   - 3ds/game/roomdata.lua: where each of those is, the pieces' depth, the seats, the walking grid, the queue, the
     waiters' corner, the counter, the cooks' places, the guests and VIPs, CAST_STAFF and STAFF_WOMEN.
   Depths (z) and positions on the grid stay in the browser's 32 px units; pictures are placed in half pixels.
   Shrinking is smooth (the canvas's high quality), each sprite first aligned on even pixels so nothing shifts.
   Uses the Chromium that Playwright drives. Run after changing the room atlas, the starter room or the cast sheets:
   node tools/export_3ds_room.js */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..');
const png=f=>'data:image/png;base64,'+fs.readFileSync(path.join(root,f)).toString('base64');   // file:// images would taint the canvas
const NN=n=>String(n).padStart(2,'0'),dirs=d=>fs.readdirSync(path.join(root,'assets/cast',d)).filter(x=>/^\d\d$/.test(x)).length;
const cast={customers:[],waiters:[],cooks:[]};
for(let i=1;i<=dirs('customers');i++)cast.customers.push({walk:png(`assets/cast/customers/${NN(i)}/walk.png`),seated:png(`assets/cast/customers/${NN(i)}/seated.png`)});
for(let i=1;i<=dirs('waiters');i++)cast.waiters.push(png(`assets/cast/waiters/${NN(i)}/service.png`));
for(let i=1;i<=dirs('cooks');i++)cast.cooks.push(png(`assets/cast/cooks/${NN(i)}/idle.png`));
(async()=>{
  const b=await chromium.launch(),pg=await b.newPage();
  await pg.goto('file://'+path.join(root,'index.html'));
  await pg.waitForFunction(()=>typeof roomArt==='function');
  await pg.evaluate(()=>roomArt());await pg.waitForFunction(()=>roomArt());
  const out=await pg.evaluate(async cast=>{
    const K=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return [c,c.getContext('2d')]};
    // half size, aligned on even pixels first: returns the shrunk canvas and its place in half pixels
    const half=(img,x,y)=>{const ox=((x%2)+2)%2,oy=((y%2)+2)%2,w=img.width+ox,h=img.height+oy;const [a,ac]=K(w+w%2,h+h%2);ac.drawImage(img,ox,oy);
      const [s,sc]=K(a.width/2,a.height/2);sc.imageSmoothingEnabled=true;sc.imageSmoothingQuality='high';sc.drawImage(a,0,0,s.width,s.height);return {c:s,x:(x-ox)/2,y:(y-oy)/2}};
    const load=src=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=src});
    // room.png: every piece of the room atlas (not its people) at half size, packed on shelves; the 3DS draws the
    // room from state.room like paintRoomBase() and drawRoom() (floors and walls tile, pieces sorted by depth)
    const keys=Object.keys(ROOM_ART.frames).filter(k=>!/^(w\d+_|p\d+_|waiter|cook)/.test(k));
    const spr=keys.map(k=>({key:k,h:half(rspr(k),0,0)})).sort((a,b)=>b.h.c.height-a.h.c.height||b.h.c.width-a.h.c.width);
    const RWIDTH=1024;let cx=0,cy=0,sh=0;const placed=[];
    for(const s of spr){const c=s.h.c;if(cx+c.width>RWIDTH){cx=0;cy+=sh+1;sh=0}placed.push([s,cx,cy]);cx+=c.width+1;sh=Math.max(sh,c.height)}
    let RH2=64;while(RH2<cy+sh)RH2*=2;if(RH2>1024)throw new Error('room.png is full');
    const [R,rc]=K(RWIDTH,RH2);const SPR={};for(const [s,x,y] of placed){rc.drawImage(s.h.c,x,y);SPR[s.key]=[x,y,s.h.c.width,s.h.c.height]}
    // people.png: every cast sheet at half size
    const [P,pc]=K(1024,1024);let px=0,py=0,ps=0;
    const put=async src=>{const im=await load(src),h=half(im,0,0).c;if(px+h.width>1024){px=0;py+=ps+1;ps=0}pc.drawImage(h,px,py);const q=[px,py];px+=h.width+1;ps=Math.max(ps,h.height);return q};
    const people={customers:[],waiters:[],cooks:[]};
    for(const c of cast.customers)people.customers.push({walk:await put(c.walk),seated:await put(c.seated)});
    for(const w of cast.waiters)people.waiters.push(await put(w));
    for(const c of cast.cooks)people.cooks.push(await put(c));
    if(py+ps>1024)throw new Error('people.png is full');
    // what a piece is (ITEMS), its layout in the atlas (parts, chairs, sitters, table top), the floors and walls
    const L_=ROOM_ART.layout,items={};
    for(const id in ITEMS){const d=ITEMS[id];items[id]={...d,layout:L_.items[id]||null,wallpiece:L_.walls[id]||null}}
    const dx={};for(const k in PILOT_DX)dx[k]=PILOT_DX[k];
    return {room:R.toDataURL('image/png'),people:P.toDataURL('image/png'),
      SPR,people_q:people,ITEMS:items,FLOORS,WALLS,STYLE_BONUS,SEGK,WALL_SLOTS,TABLES,KITCHEN:L_.kitchen,STARTER:starterRoom(0),
      T,COLS,ROWS,STREET_ROW,DOOR,DOOR_IN,PICK,QUEUE,WAITER_HOME,COOK_POS,OVEN_STEP:58,
      GUEST_P,GUEST_WIZARD,GUEST_GOTH,VIPS,XMAS_SANTA_LOOK,XMAS_LOOKS,XMAS_HOODIE,XMAS_P,XMAS_SANTA,CAST_STAFF,STAFF_WOMEN:[...STAFF_WOMEN],MEH_BAND,PILOT_DX:dx,PILOT_HANDOFF}},cast);
  await b.close();
  for(const [name,url] of [['room.png',out.room],['people.png',out.people]]){const f=path.join(root,'3ds/game/gfx',name);fs.writeFileSync(f,Buffer.from(url.split(',')[1],'base64'));console.log('3ds/game/gfx/'+name+':',fs.statSync(f).size,'bytes')}
  // Lua
  const lua=v=>v===null||v===undefined?'false':Array.isArray(v)?'{'+v.map(lua).join(',')+'}':typeof v==='object'?'{'+Object.entries(v).map(([k,x])=>(/^[A-Za-z_]\w*$/.test(k)?k:`[${JSON.stringify(k)}]`)+'='+lua(x)).join(',')+'}':typeof v==='string'?JSON.stringify(v):String(v);
  delete out.room;delete out.people;
  const body=Object.entries(out).map(([k,v])=>`  ${k} = ${lua(v)},`).join('\n');
  fs.writeFileSync(path.join(root,'3ds/game/roomdata.lua'),`-- Generated by tools/export_3ds_room.js from index.html, assets/room.js and assets/cast. Do not edit by hand.\n-- Positions (x, y, z) in the browser's 32 px units, except sprite places (x, y, q) in the half-size pictures.\nreturn {\n${body}\n}\n`);
  console.log('3ds/game/roomdata.lua:',Object.keys(out.SPR).length,'sprites,',Object.keys(out.ITEMS).length,'pieces,',out.people_q.customers.length,'customers');
})();
