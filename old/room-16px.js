/* The first dining-room model (16 px tiles, sprites from old/sprites.js), kept for reference.
   This is how index.html drew the room until it moved to the 32 px atlas (assets/room.js).
   To bring it back: load old/sprites.js, set T=16 in index.html and put these functions back
   in place of drawChar() and drawRoom() (speeds and bubble offsets were halved too). */
const FRAMES=['a','idle','b','idle'];
function drawChar(c,a,extra){
  const frame=a.walking?FRAMES[Math.floor(a.ph)%4]:'idle';
  const spr=SPR.char({...a.look,dir:a.dir,frame,sit:extra&&extra.sit});
  c.drawImage(spr,Math.round(a.x),Math.round(a.y)+(extra&&extra.sit?-3:-6));
}
function drawRoom(){
  const R=roomSize();if(!R)return;const c=R.lc;
  const sc=anim||(idleScene||(idleScene=makeScene()));const map=sc.map;
  const t=anim?Math.min(anim.t/DAY_SECONDS,1):0,night=t>.7,fr=anim?Math.floor(anim.t*6)%2:0;
  c.clearRect(0,0,RW,RH);
  // floors
  for(let r=2;r<14;r++)for(let col=0;col<COLS;col++)c.drawImage(col>=12&&r<=7?SPR.floorKitchen():SPR.floorCheck((col+r)%2),col*T,r*T);
  if(state.deco>=2){c.fillStyle='#7a1f2e';c.fillRect(10*T+2,8*T,2*T-4,6*T);c.fillStyle='#a8323f';c.fillRect(10*T+4,8*T+2,2*T-8,6*T-2);c.fillStyle='#e0b048';c.fillRect(10*T+5,8*T+3,1,6*T-3);c.fillRect(12*T-6,8*T+3,1,6*T-3)}
  // back wall
  for(let col=0;col<COLS;col++)c.drawImage(col>=12?SPR.wallKitchen():SPR.wallDining(),col*T,0);
  c.drawImage(SPR.windowS(night?1:0),2*T-1,4);c.drawImage(SPR.windowS(night?1:0),7*T-1,4);
  c.drawImage(SPR.chalkboard(),9*T+15,4);
  if(state.deco>=2){c.drawImage(SPR.painting(),5*T-2,6);c.drawImage(SPR.painting(),0,6)}
  c.drawImage(SPR.rack(),19*T-1,2);
  // divider + bottom wall
  for(let r=0;r<7;r++)c.drawImage(SPR.wallTop(),12*T-8,r*T);
  for(let col=0;col<COLS;col++)if(col!==DOOR[0]&&col!==DOOR[0]+1)c.drawImage(SPR.wallTop(),col*T,14*T);else c.drawImage(SPR.doorMat(),col*T,14*T);
  c.fillStyle='#4a2a14';c.fillRect(DOOR[0]*T-3,14*T-6,3,22);c.fillRect((DOOR[0]+2)*T,14*T-6,3,22);
  // street
  for(let col=0;col<COLS;col++){c.drawImage(SPR.sidewalk(),col*T,15*T);c.drawImage(SPR.curb(),col*T,16*T)}
  // depth-sorted drawables
  const L=[];const add=(y,p,fn)=>L.push({y,p,fn});
  for(let i=0;i<state.ovens;i++)add(4*T,0,()=>c.drawImage(SPR.oven((fr+i)%2),(13+i*2)*T-1,4*T-43));
  add(4*T,0,()=>c.drawImage(SPR.logs(),19*T,3*T+4));
  add(8*T,0,()=>{c.drawImage(SPR.counter(8),12*T-1,7*T-11);c.drawImage(SPR.register(),12*T+1,7*T-14);c.drawImage(SPR.boxes(),19*T-1,7*T-15);
    const ready=anim?Math.min(3,anim.jobs.length):0;for(let k=0;k<ready;k++)c.drawImage(SPR.pizza(),15*T+2+k*9,7*T-10)});
  for(const tb of map.tables){add((tb.r+2)*T,2,()=>{c.drawImage(SPR.table(state.deco>=3),tb.c*T-1,tb.r*T-2);
    for(const s of sc.seats){if(s.t!==tb||!s.occ)continue;const p=s.occ,dx=tb.c*T+(s.face==='right'?2:18),dy=tb.r*T+12;
      if(p.st==='wait')c.drawImage(SPR.plate(),dx,dy);else if(p.st==='eat')c.drawImage(p.timer>1?SPR.pizza():SPR.crumbs(),dx,dy-2)}})}
  for(const s of sc.seats)add((s.cy+1)*T-1,0,()=>c.drawImage(SPR.chair(s.face),s.cx*T,s.cy*T-2));
  for(const [pc,pr] of map.plants)add((pr+1)*T,1,()=>c.drawImage(SPR.plant(),pc*T-1,pr*T-14));
  for(const k of sc.cooks){add(k.y+T,1,()=>{const bob=anim&&Math.floor(anim.t*3+k.x)%2;drawChar(c,{...k,dir:bob?'up':'down',walking:false})})}
  for(const w of sc.waiters)add(w.y+T,1,()=>{drawChar(c,w);if(w.carry)c.drawImage(SPR.pizza(),Math.round(w.x)+2,Math.round(w.y)-14)});
  if(anim)for(const p of anim.people){const sit=p.st==='wait'||p.st==='eat';add(p.y+T+(sit?0:0),1,()=>drawChar(c,p,{sit}))}
  L.sort((a,b)=>a.y-b.y||a.p-b.p).forEach(d=>d.fn());
  if(t>.55){c.fillStyle=`rgba(30,22,70,${Math.min(.3,(t-.55)*.9)})`;c.fillRect(0,0,RW,RH)}
  // blit + overlay text
  const k=R.w/RW,m=R.c;m.imageSmoothingEnabled=false;m.clearRect(0,0,R.w,R.h);m.drawImage(R.low,0,0,R.w,R.h);
  const fs=Math.max(9,Math.round(k*7));m.font=`700 ${fs}px Silkscreen, monospace`;m.textBaseline='middle';m.textAlign='right';
  m.fillStyle='rgba(18,10,4,.75)';const lbl=(state.rival.promo&&anim?'2X1 · ':'')+state.rival.name.toUpperCase()+' →';const lw=m.measureText(lbl).width+10;m.fillRect(R.w-lw-4,R.h-fs*1.9,lw,fs*1.5);m.fillStyle='#ffcf4a';m.fillText(lbl,R.w-9,R.h-fs*1.15);
  m.textAlign='center';
  if(anim)for(const b of anim.bubbles){const tw=m.measureText(b.text).width+10,bx=clamp(b.x*k,tw/2+2,R.w-tw/2-2),by=Math.max(fs,b.y*k);m.globalAlpha=clamp(b.life*1.5,0,1);
    m.fillStyle='#120a04';m.fillRect(Math.round(bx-tw/2),Math.round(by-fs*.8),Math.round(tw),Math.round(fs*1.6));m.strokeStyle='#e3b34a';m.lineWidth=2;m.strokeRect(Math.round(bx-tw/2)+1,Math.round(by-fs*.8)+1,Math.round(tw)-2,Math.round(fs*1.6)-2);
    m.fillStyle=b.col;m.fillText(b.text,bx,by+1)}
  m.globalAlpha=1;
}

