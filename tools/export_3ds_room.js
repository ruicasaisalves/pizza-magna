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
    const room=starterRoom(0);state.room=room;
    const K=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return [c,c.getContext('2d')]};
    // half size, aligned on even pixels first: returns the shrunk canvas and its place in half pixels
    const half=(img,x,y)=>{const ox=((x%2)+2)%2,oy=((y%2)+2)%2,w=img.width+ox,h=img.height+oy;const [a,ac]=K(w+w%2,h+h%2);ac.drawImage(img,ox,oy);
      const [s,sc]=K(a.width/2,a.height/2);sc.imageSmoothingEnabled=true;sc.imageSmoothingQuality='high';sc.drawImage(a,0,0,s.width,s.height);return {c:s,x:(x-ox)/2,y:(y-oy)/2}};
    const load=src=>new Promise(r=>{const i=new Image();i.onload=()=>r(i);i.src=src});
    // the room's base
    const [base,bc]=K(RW,RH);paintRoomBase(bc,room,0);const B=half(base,0,0);
    // the pieces that stand, at their depth (frame 0: the 3DS room does not animate them), and the ovens' frames
    const pieces=[];for(const it of room.items)for(const q of itemParts(it,0))pieces.push({key:'piece',img:q.img,x:q.x,y:q.y,z:q.z});
    const ovens=[];
    for(const [k,x,y,z,n] of ROOM_ART.layout.kitchen){if(k==='cook')continue;
      if(k==='k_oven'){for(let f=0;f<(n||1);f++)ovens.push({key:'oven'+f,img:rspr('k_oven_'+f),x,y,z});continue}
      pieces.push({key:'piece',img:rspr(n>1?k+'_0':k),x,y,z})}
    const spr=[...pieces,...ovens,{key:'pizza',img:rspr('pizza'),x:0,y:0,z:0},{key:'plate',img:rspr('plate'),x:0,y:0,z:0}].map(p=>({...p,h:half(p.img,p.x,p.y)}));
    // pack room.png: the base on top, the rest on shelves below it
    const [R,rc]=K(512,512);rc.drawImage(B.c,0,0);let cx=0,cy=B.c.height+1,sh=0;
    for(const s of [...spr].sort((a,b)=>b.h.c.height-a.h.c.height)){const c=s.h.c;if(cx+c.width>512){cx=0;cy+=sh+1;sh=0}rc.drawImage(c,cx,cy);s.q=[cx,cy,c.width,c.height];cx+=c.width+1;sh=Math.max(sh,c.height)}
    if(cy+sh>512)throw new Error('room.png is full');
    // people.png: every cast sheet at half size
    const [P,pc]=K(1024,1024);let px=0,py=0,ps=0;
    const put=async src=>{const im=await load(src),h=half(im,0,0).c;if(px+h.width>1024){px=0;py+=ps+1;ps=0}pc.drawImage(h,px,py);const q=[px,py];px+=h.width+1;ps=Math.max(ps,h.height);return q};
    const people={customers:[],waiters:[],cooks:[]};
    for(const c of cast.customers)people.customers.push({walk:await put(c.walk),seated:await put(c.seated)});
    for(const w of cast.waiters)people.waiters.push(await put(w));
    for(const c of cast.cooks)people.cooks.push(await put(c));
    if(py+ps>1024)throw new Error('people.png is full');
    // seats: where the sitter is drawn, the plate on the table, and the tile the customer walks to
    const map=buildMap(),L_=ROOM_ART.layout;
    const seats=map.seats.map(st=>{const it=st.t,s_=st.s,lay=L_.items[it.id],x0=it.c*T,y0=it.r*T,[tx,ty,rx,ry]=lay.top;
      const qx=s_.d==='right'?tx-rx+14:s_.d==='left'?tx+rx-14:(s_.chair?tx:s_.p[0]+16),qy=s_.d==='down'?ty-ry+9:s_.d==='up'?ty+ry-9:ty,tz=lay.parts.find(q=>q[0].startsWith('t_'))[3];
      return {cx:st.cx,cy:st.cy,d:s_.d,x:x0+s_.p[0],y:y0+s_.p[1],z:y0+s_.p[2],px:x0+Math.round(qx)-12,py:y0+Math.round(qy)-8,pz:y0+tz+.2}});
    const solid=[];for(let r=0;r<ROWS;r++){let s='';for(let c=0;c<COLS;c++)s+=map.solid[r*COLS+c]?'#':'.';solid.push(s)}
    const dx={};for(const k in PILOT_DX)dx[k]=PILOT_DX[k];
    return {room:R.toDataURL('image/png'),people:P.toDataURL('image/png'),
      sprites:spr.map(s=>({key:s.key,q:s.q,x:s.h.x,y:s.h.y,z:s.z})),people_q:people,seats,solid,
      T,COLS,ROWS,STREET_ROW,DOOR,DOOR_IN,PICK,QUEUE:map.queue,WAITER_HOME,COOK_POS,OVEN_STEP:58,
      GUEST_P,GUEST_WIZARD,GUEST_GOTH,VIPS,XMAS_SANTA_LOOK,XMAS_LOOKS,XMAS_HOODIE,XMAS_P,XMAS_SANTA,CAST_STAFF,STAFF_WOMEN:[...STAFF_WOMEN],MEH_BAND,PILOT_DX:dx,PILOT_HANDOFF}},cast);
  await b.close();
  for(const [name,url] of [['room.png',out.room],['people.png',out.people]]){const f=path.join(root,'3ds/game/gfx',name);fs.writeFileSync(f,Buffer.from(url.split(',')[1],'base64'));console.log('3ds/game/gfx/'+name+':',fs.statSync(f).size,'bytes')}
  // Lua
  const lua=v=>v===null||v===undefined?'nil':Array.isArray(v)?'{'+v.map(lua).join(',')+'}':typeof v==='object'?'{'+Object.entries(v).map(([k,x])=>(/^[A-Za-z_]\w*$/.test(k)?k:`[${JSON.stringify(k)}]`)+'='+lua(x)).join(',')+'}':typeof v==='string'?JSON.stringify(v):String(v);
  delete out.room;delete out.people;
  const body=Object.entries(out).map(([k,v])=>`  ${k} = ${lua(v)},`).join('\n');
  fs.writeFileSync(path.join(root,'3ds/game/roomdata.lua'),`-- Generated by tools/export_3ds_room.js from index.html, assets/room.js and assets/cast. Do not edit by hand.\n-- Positions (x, y, z) in the browser's 32 px units, except sprite places (x, y, q) in the half-size pictures.\nreturn {\n${body}\n}\n`);
  console.log('3ds/game/roomdata.lua:',out.sprites.length,'sprites,',out.seats.length,'seats,',out.people_q.customers.length,'customers');
})();
