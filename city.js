/* Pizza Magna — the city: Porto Magno, a 6x5 grid of square blocks with a river, drawn pixel by pixel in code into
   one LW x LH map (no image files). Shared by the game (the City screen, renting and buying a shop) and by
   docs/drafts/city.html. The map, its lots and their figures are the same on every device: everything comes from
   fixed seeds.
   - HOODS: the four neighbourhoods: customer mix (students, families, tourists, gourmets, in %), rent factor and
     base foot traffic (1-5).
   - LOTS: every building; shop lots have kind (mine: the player's first shop, rival, rent, sale, taken, land),
     street address, traffic, rent per day, sale price and condition (new, good, works with its cost).
   - paint(owned): the still map (roads, blocks, roofs, landmarks, river) as a canvas; owned is the list of the
     lots (indices into LOTS) where the player has a pizzeria, painted with its red-and-white awning. It is drawn
     again only when that list changes.
   - life(ctx, dt): cars, boats and walkers, drawn on top every frame, at LIFE_SPEED of their own speed. */
const CITY=(()=>{
/* ================= CITY LAYOUT ================= */
const ROAD=24,BLK=112,STEP=BLK+ROAD,NBX=6,NBY=5,RIVER=64;
const LW=ROAD+NBX*STEP+RIVER, LH=ROAD+NBY*STEP;          // 904 x 704
const RX=ROAD+NBX*STEP;                                   // where the river starts
// customer mix (students, families, tourists, gourmets), rent factor, base foot traffic (1-5), roof colours
const HOODS={
  uni:{mix:[60,15,10,15],rent:1,traffic:3},
  baixa:{mix:[15,20,45,20],rent:1.5,traffic:4},
  resid:{mix:[8,67,10,15],rent:.8,traffic:2},
  chique:{mix:[5,22,18,55],rent:2.2,traffic:2}
};
const SEGS=[['est','#f08a3b'],['fam','#3d8ee0'],['tur','#24a067'],['gou','#8a55d0']];
const KCOL={mine:'#c4352a',rival:'#e0861e',rent:'#2e8b3a',sale:'#2f68c8',taken:'#7a6a55',land:'#94661a'};
const U='uni',B='baixa',S='resid',C='chique';
const HMAP=[[U,U,B,B,C,C],[U,U,B,B,B,C],[S,S,B,B,C,C],[S,S,S,B,S,C],[S,S,S,S,S,C]];
const SPECIAL={'1,0':'campus','0,1':'sports','3,0':'church','2,1':'square','1,3':'park','3,2':'market'};
const HSTREET=['Rua do Sol','Rua Larga','Avenida Central','Rua das Flores','Rua Nova','Rua do Mar'];
const VSTREET=['Rua das Escolas','Rua da Sé','Rua Direita','Avenida da Ribeira','Rua Velha','Rua do Cais','Rua do Rio'];
const AVENUE_H=2,AVENUE_V=3;
const RENT_BASE=38;   // $ a day: about 30 in Residential, 45 at the University, 75 in the Old Town, 85-95 by the river
function rngOf(seed){return()=>{seed|=0;seed=seed+0x6D2B79F5|0;let r=Math.imul(seed^seed>>>15,1|seed);r=r+Math.imul(r^r>>>7,61|r)^r;return((r^r>>>14)>>>0)/4294967296}}
const D=28,FH=14,RH=BLK-FH;   // perimeter wing depth, façade height, roof height of a perimeter block

/* ================= LOTS ================= */
const LOTS=[],BLOCKS=[];
function split(len,rnd){const out=[];let left=len;while(left>0){let w=left<=40?left:[26,30,34,38][Math.floor(rnd()*4)];if(left-w<24&&left-w>0)w=left;out.push(w);left-=w}return out}
for(let cy=0;cy<NBY;cy++)for(let cx=0;cx<NBX;cx++){
  const hood=HMAP[cy][cx],sp=SPECIAL[cx+','+cy],bx=ROAD+cx*STEP,by=ROAD+cy*STEP,rnd=rngOf(cx*97+cy*13+5);
  const blk={cx,cy,bx,by,hood,type:sp?'land':hood==='resid'?'houses':hood==='chique'?'villas':'perim',land:sp,lots:[]};
  BLOCKS.push(blk);
  const add=(x,y,w,h,side,extra={})=>{const l={blk,x:bx+x,y:by+y,w,h,side,hood,seed:Math.floor(rnd()*1e6),...extra};blk.lots.push(l);LOTS.push(l);return l};
  if(sp){add(0,0,BLK,BLK,'all',{land:sp});continue}
  if(blk.type==='perim'){
    let x=0;for(const w of split(BLK,rnd)){add(x,RH-D,w,D+FH,'S');x+=w}       // south wing: shopfronts on the street
    x=0;for(const w of split(BLK,rnd)){add(x,0,w,D,'N');x+=w}
    let y=D;for(const h of split(RH-2*D,rnd)){add(0,y,D,h,'W');add(BLK-D,y,D,h,'E');y+=h}
  }else if(blk.type==='houses'){
    for(let i=0;i<4;i++){add(2+i*27,2,26,30,'N');add(2+i*27,BLK-32,26,30,'S')}
    add(2,41,26,30,'W');add(BLK-28,41,26,30,'E');
  }else{
    for(let j=0;j<2;j++)for(let i=0;i<2;i++)add(i*56,j*56,56,56,j?'S':'N');
  }
}
// the player's first shop and the five rivals: [block x, block y, nth lot of the block, kind, name]
const PLACES=[[1,1,1,'mine'],[0,0,0,'rival','Pizza Rápida'],[3,1,1,'rival','Trattoria Bella'],[2,3,5,'rival','Forno do Zé'],[4,0,3,'rival','Casa Nápoles'],[2,2,0,'rival','La Brasa']];
const BIZ={uni:['cafe','books','bar','laundry','flats','gym','pharmacy'],baixa:['cafe','hotel','cinema','bakery','shoes','bank','florist','bar'],resid:['home'],chique:['villa']};
for(const l of LOTS){
  const r=rngOf(l.seed);
  if(l.land){l.kind='land';continue}
  const p=PLACES.find(p=>p[0]===l.blk.cx&&p[1]===l.blk.cy&&l.blk.lots[p[2]]===l);
  const shop=l.blk.type==='perim';
  l.kind=p?p[3]:r()<(shop?.17:.06)?'rent':r()<(shop?.12:.07)?'sale':'taken';
  if(p&&p[4])l.name=p[4];
  const pool=BIZ[l.hood];l.biz=pool[Math.floor(r()*pool.length)];
  const H=HOODS[l.hood];
  l.tables=Math.max(6,Math.min(30,Math.round(l.w*l.h/64*.8)));
  // the street in front: south side faces the road below, north the road above, west/east the side roads
  const {cx,cy}=l.blk;
  const hi=l.side==='S'?cy+1:l.side==='N'?cy:null, vi=l.side==='W'?cx:l.side==='E'?cx+1:null;
  l.street=hi!=null?HSTREET[hi]:VSTREET[vi];
  const onAvenue=hi===AVENUE_H||vi===AVENUE_V;
  const nearSquare=Math.abs(cx-2)+Math.abs(cy-1)===1;
  l.traffic=Math.max(1,Math.min(5,H.traffic+(onAvenue?1:0)+(nearSquare?1:0)-(r()<.3?1:0)-(shop?0:1)));
  l.rent=Math.round(RENT_BASE*H.rent*(.7+l.traffic*.15));   // by place only: the neighbourhood and the street's traffic
  l.price=Math.round(l.rent*90/500)*500;
  const c=r();l.cond=c<.3?'new':c<.7?'good':'works';l.works=Math.round((300+r()*900)/50)*50;
  l.addr=`${l.street}, ${2+Math.floor(((l.side==='W'||l.side==='E'?l.y:l.x)%STEP)/6)*2+(l.side==='N'||l.side==='E'?1:0)}`;
  l.paint=Math.floor(r()*5);l.tone=Math.floor(r()*3);
}
// every neighbourhood has a few free places (Riverside's villas came out all taken): two to rent and one for sale
for(const h in HOODS){const free=k=>LOTS.filter(l=>l.hood===h&&l.kind===k).length,pool=LOTS.filter(l=>l.hood===h&&l.kind==='taken');
  let i=0;while(free('rent')<2&&i<pool.length)pool[i++].kind='rent';while(free('sale')<1&&i<pool.length)pool[i++].kind='sale'}
const lotAt=(x,y)=>LOTS.find(l=>x>=l.x&&x<l.x+l.w&&y>=l.y&&y<l.y+l.h)||null;

/* ================= DRAWING ================= */
const mk=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return [c,c.getContext('2d')]};
const hex=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
const [BG,bg]=mk(LW,LH);let low=null;   // low: where life() draws (the caller's canvas)
let X=bg;const R=(col,a,b,w=1,h=1)=>{X.fillStyle=col;X.fillRect(a,b,w,h)};
function disc(cx,cy,r,col){for(let y=-r;y<=r;y++)for(let x=-r;x<=r;x++)if(x*x+y*y<=r*r+r*.8)R(col,cx+x,cy+y)}
function tree(x,y,s=5,dark){R('rgba(0,0,0,.28)',x-s+3,y+2,s*2,s);disc(x,y,s,dark?'#1f4d22':'#2a6328');disc(x-1,y-1,s-1,dark?'#2a6328':'#3f8f3a');disc(x-2,y-2,Math.max(1,s-3),'#7cc35a')}
function cypress(x,y){R('rgba(0,0,0,.28)',x+1,y+2,5,9);for(let i=0;i<10;i++){const w=i<2?1:i<4?2:i<8?3:2;R('#1f4d22',x-Math.floor(w/2),y-8+i,w+1,1)}R('#3f8f3a',x-1,y-5,1,5)}
function palm(x,y){R('rgba(0,0,0,.25)',x,y+8,7,2);for(let i=0;i<9;i++)R('#8a6236',x+(i>5?1:0),y+i,2,1);
  for(const [dx,dy] of [[-5,-1],[-4,-2],[-3,-3],[4,-1],[3,-2],[2,-3],[-2,1],[3,1],[0,-4],[1,-4]])R('#3f8f3a',x+dx,y+dy,2,1);R('#7cc35a',x-1,y-2,4,2)}

// Hipped roof, seen from above: every pixel belongs to the slope of its nearest edge, so ridges and hips
// appear by themselves. With `hole`, it is a ring of wings around a courtyard (the inner slopes face it).
const ROOFS={
  terra:['#4e1a0e','#94361c','#bb4d29','#d9683a','#f39a62'],
  terra2:['#4a1a10','#8a3a22','#ad5230','#c96a40','#e8946a'],
  brick:['#3a1810','#73301f','#90402c','#ab573f','#c9775b'],
  slate:['#1d2129','#363d49','#4a5260','#5f6979','#8a96a8'],
  marble:['#5c5850','#8f8a80','#aaa59a','#c9c3b8','#e6e1d6'],
  green:['#18301f','#2f5a3a','#3f7349','#558e5e','#7fb886']
};
function hip(w,h,ramp,hole){
  const [c,x]=mk(w,h),id=x.createImageData(w,h),a=id.data,P=ramp.map(hex);
  const LV={N:3,W:2,E:1,S:1};
  for(let y=0;y<h;y++)for(let i=0;i<w;i++){
    const cand=[[y,'N'],[h-1-y,'S'],[i,'W'],[w-1-i,'E']];
    if(hole){const [hx,hy,hw,hh]=hole;if(i>=hx&&i<hx+hw&&y>=hy&&y<hy+hh)continue;
      const dx1=hx-i,dx2=i-(hx+hw-1),dy1=hy-y,dy2=y-(hy+hh-1),m=Math.max(dx1,dx2,dy1,dy2);
      cand.push([m-1,m===dy1?'S':m===dy2?'N':m===dx1?'E':'W',1])}
    cand.sort((p,q)=>p[0]-q[0]);
    const [d,f,inner]=cand[0];
    let lv=LV[f];
    if(d%3===2)lv-=1;                                    // rows of tiles
    if(cand[1][0]-d<=1&&d>0)lv=4;                         // ridge and hips
    if(d===0)lv=0;                                       // eaves
    const k=(y*w+i)*4,[r,g,b]=P[Math.max(0,lv)];a[k]=r;a[k+1]=g;a[k+2]=b;a[k+3]=255;
  }
  x.putImageData(id,0,0);return c;
}
const WALLS={uni:['#b04a2e','#c9604a','#a0503a','#b86a4a','#9a4630'],baixa:['#f2d27a','#eaa79c','#9fc7d8','#f6eedf','#c9e0b0'],resid:['#f6eedf','#efe3c8','#f2d9c0','#e8eef0','#f6eedf'],chique:['#fbf6ec','#fbf6ec','#efe9dc','#fbf6ec','#f4efe4']};
// shop or house front: upper windows, then the ground floor (shopfront, boarded up, or door and windows)
let OWN=new Set();   // lots the player has opened a pizzeria in (set by paint)
const K=l=>OWN.has(l)?'mine':l.kind;
function facade(x,y,w,h,l,shop){
  const wall=WALLS[l.hood][l.paint];
  R(wall,x,y,w,h);R('rgba(255,255,255,.3)',x,y,w,1);R('rgba(0,0,0,.3)',x,y+h-1,w,1);
  R('rgba(0,0,0,.18)',x+w-1,y,1,h);                      // party wall between neighbours
  const up=h>=12;
  if(up)for(let i=x+3;i+3<=x+w-2;i+=6){R('#2b1b14',i,y+2,3,4);R('#9ccbe6',i,y+2,3,2);if(l.hood==='baixa')R('#2a6328',i-1,y+2,1,4)}
  const gy=up?y+7:y+2,gh=h-(up?8:3);
  const k=K(l),empty=k==='rent'||k==='sale';
  if(!shop){const dx=x+Math.floor(w/2)-2;R('#4a2a14',dx,gy,4,gh);if(w>12){R('#2b1b14',x+3,gy+1,3,3);R('#9ccbe6',x+3,gy+1,3,2);R('#2b1b14',x+w-6,gy+1,3,3);R('#9ccbe6',x+w-6,gy+1,3,2)}}
  else if(empty){for(let i=x+2;i<x+w-2;i+=3)R(i%2?'#6e3c1a':'#9a5a2c',i,gy,3,gh);R('#4a2a14',x+Math.floor(w/2)-2,gy,4,gh)}
  else{R('#2b1b14',x+2,gy,w-4,gh);R('#5b8fae',x+3,gy+1,w-6,gh-1);R('#9ccbe6',x+3,gy+1,Math.floor((w-6)/2),1);R('#4a2a14',x+Math.floor(w/2)-2,gy+1,4,gh-1);
    const aw=k==='mine'?['#c4352a','#f6eedf']:k==='rival'?['#e0861e','#4a2a14']:[['#2e7b2c','#f6eedf'],['#2f68c8','#f6eedf'],['#7a2e6e','#f2d27a'],['#c4352a','#2a6328']][l.tone+(l.paint%2)];
    for(let i=0;i<w-2;i++)R(i%4<2?aw[0]:aw[1],x+1+i,gy-2,1,3);R('rgba(0,0,0,.25)',x+1,gy+1,w-2,1);
    if(k==='mine'){disc(x+w-6,gy-5,2,'#dc9b4e');R('#c9381f',x+w-7,gy-6,2,2);R('#f8e2a0',x+w-6,gy-5,1,1)}}
  if(empty){R('#2b1b14',x+w-9,y+h-9,8,6);R(KCOL[k],x+w-8,y+h-8,6,4)}
}
function courtyard(x,y,w,h,hood,rnd){
  if(hood==='uni'){R('#6c6359',x,y,w,h);for(let i=x+3;i<x+w-3;i+=6){R('#e9e4d4',i,y+FH+3,1,6);R('#e9e4d4',i,y+h-9,1,6)}R('#e9e4d4',x+3,y+FH+9,w-6,1);R('#e9e4d4',x+3,y+h-10,w-6,1)}
  else{R('#e2d4ba',x,y,w,h);for(let yy=y;yy<y+h;yy+=4)for(let xx=x+((yy/4)%2)*4;xx<x+w;xx+=8)R('#cfbf9f',xx,yy,3,1);
    for(let i=0;i<2;i++)tree(x+12+Math.floor(rnd()*(w-24)),y+FH+8+Math.floor(rnd()*Math.max(1,h-FH-14)),4)}
  R('rgba(0,0,0,.28)',x,y,4,h);                          // the west wing's shadow
}
function blockPerim(b){
  const {bx,by}=b,rnd=rngOf(b.cx*31+b.cy*7);
  R('rgba(0,0,0,.3)',bx+4,by+4,BLK,BLK);                 // block shadow on the pavement
  courtyard(bx+D,by+D,BLK-2*D,RH-2*D,b.hood,rnd);
  const ramp=b.hood==='uni'?ROOFS.brick:ROOFS.terra;
  X.drawImage(hip(BLK,RH,ramp,[D,D,BLK-2*D,RH-2*D]),bx,by);
  // party walls between the buildings of the ring, and one roof in three a slightly different shade
  for(const l of b.lots){const x=l.x-bx,y=l.y-by;
    if(l.tone===1){X.globalAlpha=.18;R('#000',l.x,l.y,l.w,Math.min(l.h,RH-y));X.globalAlpha=1}
    if(l.side==='S'||l.side==='N'){if(x>0)R('rgba(40,10,4,.55)',l.x,l.y+(l.side==='N'?1:1),1,D-2)}
    else if(y>D)R('rgba(40,10,4,.55)',l.x+1,l.y,D-2,1);
    if(l.blk.hood==='baixa'&&l.paint===2){R('#2b1b14',l.x+l.w-9,l.y+(l.side==='S'?D-10:4),5,6);R('#7e3220',l.x+l.w-8,l.y+(l.side==='S'?D-9:5),3,4)}   // chimney
  }
  for(const l of b.lots)if(l.side==='S')facade(l.x,by+RH,l.w,FH,l,true);
  for(const l of b.lots)if(l.side==='N'){const x0=Math.max(l.x,bx+D),x1=Math.min(l.x+l.w,bx+BLK-D),mine=K(l)==='mine';if(x1-x0>3)facade(x0,by+D,x1-x0,FH,{...l,kind:mine?'mine':'taken'},mine)}
  // a pizzeria of the player's on a side street: its red-and-white awning along the wing's outer edge
  for(const l of b.lots)if((l.side==='W'||l.side==='E')&&K(l)==='mine'){const x=l.side==='W'?l.x:l.x+l.w-3;for(let y=l.y+1;y<l.y+l.h-1;y++)R((y>>1)%2?'#c4352a':'#f6eedf',x,y,3,1)}
}
function blockHouses(b){
  const {bx,by}=b,rnd=rngOf(b.cx*17+b.cy*29);
  R('#5f9a45',bx,by,BLK,BLK);for(let i=0;i<220;i++)R('#6faa50',bx+Math.floor(rnd()*BLK),by+Math.floor(rnd()*BLK),2,1);
  R('#2a6328',bx,by,BLK,2);R('#2a6328',bx,by+BLK-2,BLK,2);R('#2a6328',bx,by,2,BLK);R('#2a6328',bx+BLK-2,by,2,BLK);   // hedges
  R('#e2d4ba',bx+40,by+48,32,20);disc(bx+56,by+58,7,'#2f68c8');disc(bx+56,by+58,6,'#5fb6e0');                       // shared garden with a pond
  tree(bx+36,by+42,6);tree(bx+78,by+74,6);cypress(bx+80,by+44);
  for(const l of b.lots){
    const w=l.w-4,rh=16;R('rgba(0,0,0,.3)',l.x+5,l.y+5,w,rh+10);
    X.drawImage(hip(w,rh,[ROOFS.slate,ROOFS.terra2,ROOFS.terra][l.tone]),l.x+2,l.y+2);
    facade(l.x+2,l.y+2+rh,w,10,l,false);
    if(K(l)==='mine'||K(l)==='rival')facade(l.x+2,l.y+2+rh,w,10,l,true);
    R('#e2d4ba',l.x+l.w/2-1,l.y+28,3,2);
  }
}
function blockVillas(b){
  const {bx,by}=b;
  R('#6fae52',bx,by,BLK,BLK);
  for(const l of b.lots){
    R('#2a6328',l.x,l.y,l.w,2);R('#2a6328',l.x,l.y,2,l.h);R('#82c060',l.x+3,l.y+3,l.w-6,1);
    R('rgba(0,0,0,.3)',l.x+9,l.y+10,30,32);X.drawImage(hip(30,22,ROOFS.slate),l.x+6,l.y+7);facade(l.x+6,l.y+29,30,10,l,K(l)==='rival'||K(l)==='mine');
    R('#e2d4ba',l.x+39,l.y+7,13,26);R('#2f68c8',l.x+40,l.y+8,11,24);R('#5fb6e0',l.x+41,l.y+9,9,22);R('#d6edf8',l.x+43,l.y+12,3,1);R('#d6edf8',l.x+45,l.y+20,3,1);
    palm(l.x+44,l.y+38);R('#e2d4ba',l.x+20,l.y+39,3,15);
  }
}
function landmark(b){
  const {bx,by}=b,x0=bx,y0=by,w=BLK,h=BLK;
  if(b.land==='campus'){
    R('#5f9a45',x0,y0,w,h);for(let i=0;i<5;i++)tree(x0+10+i*23,y0+8,5);
    R('rgba(0,0,0,.3)',x0+18,y0+26,80,60);X.drawImage(hip(80,44,ROOFS.marble),x0+14,y0+22);
    R('#ebe7df',x0+14,y0+66,80,16);for(let i=x0+17;i<x0+92;i+=7){R('#c9c3b8',i,y0+66,3,16);R('#fbf6ec',i,y0+66,1,16)}
    R('#4a2a14',x0+49,y0+72,10,10);for(let i=0;i<3;i++)R(i%2?'#c9c3b8':'#ada397',x0+40-i*2,y0+82+i,28+i*4,1);
    R('#e2d4ba',x0+52,y0+86,4,26);tree(x0+20,y0+96,5);tree(x0+90,y0+96,5);
  }else if(b.land==='sports'){
    R('#5f9a45',x0,y0,w,h);R('#b0503a',x0+6,y0+8,w-12,h-16);R('#3f8f3a',x0+16,y0+18,w-32,h-36);
    for(let i=0;i<w-32;i+=8)R('#4f9a44',x0+16+i,y0+18,4,h-36);
    R('#f6eedf',x0+16,y0+18,w-32,1);R('#f6eedf',x0+16,y0+h-19,w-32,1);R('#f6eedf',x0+16,y0+18,1,h-36);R('#f6eedf',x0+w-17,y0+18,1,h-36);R('#f6eedf',x0+w/2,y0+18,1,h-36);
    for(let i=0;i<4;i++)R('rgba(255,255,255,.35)',x0+8,y0+10+i*2,w-16,1);
  }else if(b.land==='church'){
    R('#e2d4ba',x0,y0,w,h);for(let y=y0+2;y<y0+h;y+=5)for(let x=x0+((y/5|0)%2)*5;x<x0+w;x+=10)R('#a99876',x,y,4,1);
    R('rgba(0,0,0,.3)',x0+30,y0+20,56,80);X.drawImage(hip(40,70,ROOFS.terra),x0+36,y0+14);X.drawImage(hip(70,20,ROOFS.terra),x0+21,y0+36);
    R('#f6eedf',x0+36,y0+84,40,14);R('#4a2a14',x0+52,y0+88,8,10);disc(x0+56,y0+88,4,'#4a2a14');
    for(const tx of [x0+30,x0+70]){R('rgba(0,0,0,.3)',tx+3,y0+76,14,24);X.drawImage(hip(12,12,ROOFS.slate),tx,y0+72);R('#f6eedf',tx,y0+84,12,14);R('#2b1b14',tx+4,y0+87,4,5)}
    for(let i=0;i<4;i++)cypress(x0+10+(i%2)*92,y0+20+Math.floor(i/2)*70);
  }else if(b.land==='square'){
    R('#e2d4ba',x0,y0,w,h);for(let y=y0+2;y<y0+h;y+=5)for(let x=x0+((y/5|0)%2)*5;x<x0+w;x+=10){R('#a99876',x,y,4,1);R('#a99876',x+4,y+1,2,1)}
    const cx=x0+w/2,cy=y0+h/2;disc(cx+2,cy+3,18,'rgba(0,0,0,.2)');disc(cx,cy,18,'#8f857a');disc(cx,cy,16,'#ada397');disc(cx,cy,14,'#2f68c8');disc(cx,cy,13,'#5fb6e0');
    R('#ada397',cx-2,cy-8,4,11);R('#d6edf8',cx-1,cy-12,2,4);R('#d6edf8',cx-5,cy-4,1,3);R('#d6edf8',cx+4,cy-4,1,3);
    for(const [a,c] of [[12,12],[w-12,12],[12,h-14],[w-12,h-14],[w/2,10],[w/2,h-12],[10,h/2],[w-10,h/2]])tree(x0+a,y0+c,5);
    for(const [a,c] of [[26,26],[w-36,26],[26,h-28],[w-36,h-28]]){R('#2b1b14',x0+a,y0+c,10,4);R('#9a5a2c',x0+a+1,y0+c+1,8,2)}
  }else if(b.land==='park'){
    R('#4f8d3a',x0,y0,w,h);for(let i=0;i<w;i++){R('#e2d4ba',x0+i,y0+Math.floor(i*h/w),3,2);R('#e2d4ba',x0+i,y0+h-2-Math.floor(i*h/w),2,2)}
    disc(x0+w-26,y0+h-28,13,'#2f68c8');disc(x0+w-26,y0+h-28,12,'#5fb6e0');R('#d6edf8',x0+w-32,y0+h-32,4,1);
    for(const [a,c,s] of [[10,10,6],[30,8,7],[60,12,6],[86,9,6],[12,40,7],[36,60,6],[60,36,5],[12,80,6],[36,96,6],[64,92,5],[96,40,6],[80,60,4]])tree(x0+a,y0+c,s);
  }else if(b.land==='market'){
    R('#e2d4ba',x0,y0,w,h);R('rgba(0,0,0,.3)',x0+12,y0+12,96,86);X.drawImage(hip(96,72,ROOFS.green),x0+8,y0+8);
    R('#c9e0b0',x0+8,y0+80,96,18);for(let i=x0+11;i<x0+102;i+=9){R('#2b1b14',i,y0+83,6,15);R(i%2?'#e0b048':'#c4352a',i,y0+82,6,2)}
    for(let i=0;i<6;i++){R(['#c4352a','#e0b048','#3f8f3a'][i%3],x0+12+i*16,y0+102,10,6);R('#f6eedf',x0+12+i*16,y0+102,10,1)}
  }
}
function roads(){
  X=bg;R('#55585f',0,0,LW,LH);
  const rnd=rngOf(77);for(let i=0;i<2500;i++)R(rnd()<.5?'#5d6068':'#4d5057',Math.floor(rnd()*LW),Math.floor(rnd()*LH),1,1);
  // pavements around each block, with a kerb
  for(let cy=0;cy<NBY;cy++)for(let cx=0;cx<NBX;cx++){const x=ROAD+cx*STEP-6,y=ROAD+cy*STEP-6;R('#a59a82',x,y,BLK+12,BLK+12);R('#cfc4aa',x+1,y+1,BLK+10,BLK+10);
    for(let i=0;i<BLK+10;i+=6){R('#bdb196',x+1+i,y+1,1,5);R('#bdb196',x+1+i,y+BLK+6,1,5);R('#bdb196',x+1,y+1+i,5,1);R('#bdb196',x+BLK+6,y+1+i,5,1)}}
  // centre lines and zebra crossings
  for(let j=0;j<=NBY;j++){const y=j*STEP+11;for(let x=0;x<RX;x+=10){if(x%STEP<ROAD+2)continue;R('#d8cf9c',x,y,5,1)}}
  for(let i=0;i<=NBX;i++){const x=i*STEP+11;for(let y=0;y<LH;y+=10){if(y%STEP<ROAD+2)continue;R('#d8cf9c',x,y,1,5)}}
  for(let j=0;j<=NBY;j++)for(let i=0;i<=NBX;i++){const x=i*STEP,y=j*STEP;
    for(let k=2;k<ROAD-2;k+=3){if(y>0)R('#e9e4d4',x+k,y-5,2,4);if(y+ROAD<LH)R('#e9e4d4',x+k,y+ROAD+1,2,4);if(x>0)R('#e9e4d4',x-5,y+k,4,2);if(x+ROAD<RX)R('#e9e4d4',x+ROAD+1,y+k,4,2)}}
  // the river, its embankment and the bridges
  R('#2f68c8',RX+6,0,RIVER-6,LH);for(let i=0;i<600;i++)R(rnd()<.5?'#5f9ad8':'#2a5cb4',RX+8+Math.floor(rnd()*(RIVER-10)),Math.floor(rnd()*LH),3+Math.floor(rnd()*3),1);
  R('#a59a82',RX,0,6,LH);R('#cfc4aa',RX,0,5,LH);for(let y=0;y<LH;y+=6)R('#bdb196',RX,y,5,1);
  for(let j=0;j<=NBY;j++){const y=j*STEP;R('rgba(0,0,0,.35)',RX+6,y+ROAD,RIVER,4);R('#55585f',RX,y,RIVER,ROAD);R('#8f857a',RX,y,RIVER,3);R('#8f857a',RX,y+ROAD-3,RIVER,3);
    for(let x=RX;x<LW;x+=6){R('#ada397',x,y,3,1);R('#ada397',x,y+ROAD-3,3,1)}for(let x=RX+4;x<LW;x+=10)R('#d8cf9c',x,y+11,5,1)}
}
function drawBG(){
  roads();
  for(const b of BLOCKS){X=bg;if(b.type==='land')landmark(b);else if(b.type==='perim')blockPerim(b);else if(b.type==='houses')blockHouses(b);else blockVillas(b)}
}

/* ================= LIFE: cars, boats and walkers ================= */
const CARCOL=['#c0392b','#e0b048','#3d8ee0','#f6eedf','#3f8f3a','#8a55d0','#2b2b33','#e8705a'];
const cars=[],walkers=[],boats=[];
{const r=rngOf(4242);
  for(let i=0;i<70;i++){const v=r()<.45,line=Math.floor(r()*(v?NBX+1:NBY+1)),dir=r()<.5?1:-1;
    cars.push({v,c:line*STEP+(dir>0?14:5),dir,p:r()*(v?LH:LW),sp:18+r()*22,col:CARCOL[i%CARCOL.length]})}
  for(let i=0;i<160;i++){const v=r()<.5,line=Math.floor(r()*(v?NBX:NBY)),side=r()<.5;
    walkers.push({v,c:ROAD+line*STEP+(side?-4:BLK+2)+Math.floor(r()*2),p:r()*(v?LH:RX),sp:(4+r()*5)*(r()<.5?-1:1),col:['#c0392b','#3d8ee0','#e0b048','#3f8f3a','#f6eedf','#8a55d0','#f08a3b'][Math.floor(r()*7)]})}
  for(let i=0;i<3;i++)boats.push({x:RX+18+i*12,p:r()*LH,sp:(8+r()*6)*(i%2?1:-1)})}
const LIFE_SPEED=.08;   // a small part of the speeds above: a calm town seen from high up, cars and people barely moving
function drawLife(dt){
  dt*=LIFE_SPEED;
  X=low;
  for(const w of walkers){const lim=w.v?LH:RX;w.p=(w.p+w.sp*dt+lim)%lim;const x=w.v?w.c:w.p,y=w.v?w.p:w.c;
    R('rgba(0,0,0,.25)',x+1,y+3,2,1);R(w.col,x,y+1,2,2);R('#eaa79c',x,y,2,1)}
  for(const b of boats){b.p=(b.p+b.sp*dt+LH+20)%(LH+20)-10;const x=b.x,y=Math.round(b.p);if(((y%STEP)+STEP)%STEP<ROAD+6)continue;
    R('#d6edf8',x+1,y+(b.sp>0?-4:12),4,3);R('#2b1b14',x-1,y-1,8,12);R('#f6eedf',x,y,6,10);R('#c4352a',x+1,y+3,4,4)}
  for(const c of cars){const lim=c.v?LH:RX;c.p=(c.p+c.sp*c.dir*dt+lim+20)%(lim+20)-10;const p=Math.round(c.p);
    if(c.v){const x=c.c,y=p;R('rgba(0,0,0,.3)',x+1,y+2,6,10);R('#2b1b14',x-1,y-1,7,11);R(c.col,x,y,5,9);R('#9ccbe6',x+1,y+(c.dir>0?6:1),3,2);R('rgba(255,255,255,.35)',x,y,5,1)}
    else{const x=p,y=c.c;R('rgba(0,0,0,.3)',x+2,y+1,10,6);R('#2b1b14',x-1,y-1,11,7);R(c.col,x,y,9,5);R('#9ccbe6',x+(c.dir>0?6:1),y+1,2,3);R('rgba(255,255,255,.35)',x,y,9,1)}}
}
let paintedKey=null;
return {ROAD,BLK,STEP,NBX,NBY,LW,LH,RX,D,HOODS,SEGS,KCOL,BLOCKS,LOTS,lotAt,
  paint(owned=[]){const key=[...owned].sort((a,b)=>a-b).join(',');
    if(key!==paintedKey){OWN=new Set(owned.map(i=>LOTS[i]).filter(Boolean));drawBG();paintedKey=key}return BG},
  life(ctx,dt){low=ctx;drawLife(dt)}};
})();
