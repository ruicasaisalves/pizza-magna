/* Pizza Magna — pixel-art sprites, generated in code.
   Every sprite is built once into an offscreen canvas and cached.
   Grid: 16 px tiles. Characters: 16x22. Palette below keeps everything coherent.
   To swap in a purchased pack later, replace the builders here and keep the same names. */
const SPR=(()=>{
  const PAL={
    out:'#2b1b14',
    woodL:'#c48a52',wood:'#9a5a2c',woodD:'#6e3c1a',woodDD:'#4a2a14',
    red:'#c0392b',redD:'#8c2a20',redL:'#e06a50',pink:'#eaa79c',cream:'#f6eedf',creamD:'#e2d4ba',
    green:'#3f8f3a',greenD:'#2a6328',greenL:'#7cc35a',
    stone:'#8f857a',stoneD:'#6c6359',stoneL:'#ada397',
    brick:'#b04a2e',brickD:'#7e3220',brickL:'#d06a44',
    glass:'#9ccbe6',glassL:'#d6edf8',
    gold:'#e0b048',goldD:'#a7771f',
    marble:'#ebe7df',marbleD:'#c9c3b8',
    crust:'#dc9b4e',crustD:'#b0702e',sauce:'#c9381f',cheese:'#f8e2a0',pep:'#8a2112',
    fire1:'#ffd35a',fire2:'#ff8a1e',fire3:'#e8461a'
  };
  const cache=new Map();
  const mk=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return [c,c.getContext('2d')]};
  const R=(x,col,a,b,w=1,h=1)=>{x.fillStyle=col;x.fillRect(a,b,w,h)};
  const hex=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
  function outline(c,col=PAL.out){
    const x=c.getContext('2d'),w=c.width,h=c.height,d=x.getImageData(0,0,w,h),a=d.data,o=new Uint8ClampedArray(a),[r,g,b]=hex(col);
    const op=(u,v)=>u>=0&&v>=0&&u<w&&v<h&&a[(v*w+u)*4+3]>0;
    for(let y=0;y<h;y++)for(let i=0;i<w;i++){const k=(y*w+i)*4;if(a[k+3])continue;if(op(i-1,y)||op(i+1,y)||op(i,y-1)||op(i,y+1)){o[k]=r;o[k+1]=g;o[k+2]=b;o[k+3]=255}}
    d.data.set(o);x.putImageData(d,0,0);return c;
  }
  function ascii(rows,pal){const h=rows.length,w=rows[0].length,[c,x]=mk(w,h);rows.forEach((row,y)=>{for(let i=0;i<w;i++){const col=pal[row[i]];if(col)R(x,col,i,y)}});return c}
  function mirror(c){const [m,x]=mk(c.width,c.height);x.translate(c.width,0);x.scale(-1,1);x.drawImage(c,0,0);return m}
  function disc(x,cx,cy,rx,ry,col){for(let y=Math.floor(cy-ry);y<=Math.ceil(cy+ry);y++)for(let i=Math.floor(cx-rx);i<=Math.ceil(cx+rx);i++){const dx=(i+.5-cx)/rx,dy=(y+.5-cy)/ry;if(dx*dx+dy*dy<=1)R(x,col,i,y)}}
  const inE=(i,y,cx,cy,rx,ry)=>{const dx=(i+.5-cx)/rx,dy=(y+.5-cy)/ry;return dx*dx+dy*dy<=1};
  const memo=(key,fn)=>{if(!cache.has(key))cache.set(key,fn());return cache.get(key)};

  /* ---------- floors & walls ---------- */
  const floorCheck=dark=>memo('fc'+dark,()=>{const [c,x]=mk(16,16);const base=dark?'#b03a2e':'#efe0c0',sh=dark?'#93301f':'#ddcaa3',hl=dark?'#c4513f':'#fbf1da';R(x,base,0,0,16,16);R(x,sh,0,15,16,1);R(x,sh,15,0,1,16);R(x,hl,0,0,15,1);R(x,hl,0,0,1,15);R(x,sh,5,6);R(x,sh,11,10);R(x,hl,9,3);return c});
  const floorKitchen=()=>memo('fk',()=>{const [c,x]=mk(16,16);for(let y=0;y<2;y++)for(let i=0;i<2;i++){const o=(i+y)%2;R(x,o?'#a3aaae':'#8f979c',i*8,y*8,8,8);R(x,o?'#b8bfc2':'#a0a7ab',i*8,y*8,7,1)}R(x,'#7c8388',0,15,16,1);R(x,'#7c8388',15,0,1,16);return c});
  const sidewalk=()=>memo('sw',()=>{const [c,x]=mk(16,16);R(x,'#cfc4aa',0,0,16,16);R(x,'#b6aa8e',0,15,16,1);R(x,'#b6aa8e',15,0,1,16);R(x,'#ddd3bb',0,0,15,1);R(x,'#bfb398',4,5);R(x,'#bfb398',10,11);return c});
  const curb=()=>memo('curb',()=>{const [c,x]=mk(16,16);R(x,'#cfc4aa',0,0,16,10);R(x,'#b6aa8e',15,0,1,10);R(x,'#a59a82',0,10,16,2);R(x,'#55585f',0,12,16,4);R(x,'#d8cf9c',4,14,8,1);return c});
  const wallDining=()=>memo('wd',()=>{const [c,x]=mk(16,32);
    R(x,PAL.woodDD,0,0,16,3);R(x,PAL.wood,0,1,16,1);
    R(x,'#ead6a6',0,3,16,17);for(let i=1;i<16;i+=4)R(x,'#dbbf8a',i,3,1,17);for(let y=6;y<20;y+=6){R(x,'#c9a56a',3,y);R(x,'#c9a56a',11,y+3)}
    R(x,PAL.woodL,0,20,16,1);R(x,PAL.wood,0,21,16,1);R(x,PAL.woodD,0,22,16,1);
    R(x,'#7a3a24',0,23,16,7);R(x,'#5e2a19',1,24,6,5);R(x,'#5e2a19',9,24,6,5);R(x,'#8f4a30',2,25,4,3);R(x,'#8f4a30',10,25,4,3);
    R(x,PAL.woodDD,0,30,16,2);return c});
  const wallKitchen=()=>memo('wk',()=>{const [c,x]=mk(16,32);R(x,PAL.woodDD,0,0,16,3);R(x,'#eef2f2',0,3,16,27);for(let y=3;y<30;y+=5){R(x,'#cfd6d8',0,y,16,1);const off=((y-3)/5)%2?4:0;for(let i=off;i<16;i+=8)R(x,'#cfd6d8',i,y,1,5)}R(x,'#6c7378',0,30,16,2);return c});
  const wallTop=()=>memo('wt',()=>{const [c,x]=mk(16,16);R(x,'#4a2c1c',0,0,16,16);R(x,'#6e4630',0,0,16,2);R(x,'#5a3624',0,2,16,1);R(x,'#3a2014',0,14,16,2);return c});
  const doorMat=()=>memo('dm',()=>{const [c,x]=mk(16,16);R(x,'#7a3a24',0,0,16,16);R(x,'#a85a34',1,1,14,14);for(let y=3;y<14;y+=3)R(x,'#8f4a2a',2,y,12,1);return c});

  /* ---------- furniture ---------- */
  const table=(candle)=>memo('tb'+candle,()=>{const [c,x]=mk(34,34);
    R(x,'rgba(0,0,0,.25)',3,30,30,3);
    R(x,PAL.woodDD,4,24,3,8);R(x,PAL.woodDD,27,24,3,8);
    for(let y=2;y<22;y++)for(let i=1;i<33;i++){const a=(i>>2)&1,b=(y>>2)&1;R(x,a&&b?PAL.red:(a||b)?PAL.pink:PAL.cream,i,y)}
    for(let y=22;y<27;y++)for(let i=1;i<33;i++){const a=(i>>2)&1;R(x,a?PAL.redD:'#c98478',i,y)}
    R(x,'#fff8ec',2,2,30,1);
    if(candle){R(x,PAL.cream,16,9,2,4);R(x,PAL.creamD,17,9,1,4);R(x,PAL.fire1,16,7,2,2);R(x,PAL.fire2,16,8,1,1);R(x,PAL.goldD,15,13,4,1)}
    else{R(x,'#5a8f3a',16,8,2,5);R(x,PAL.greenD,17,8,1,5);R(x,'#d8c060',16,6,2,2)}
    return outline(c)});
  const chairRows=["................","..oo............","..oBo...........","..oBbo..........","..oBbo..........","..oBbo..........","..oBbo..........","..oBbooooooooo..","..oBbRRRRRRRRRo.","..oBbRRRRRRRRRo.","..obbrrrrrrrrro.","..oBo.......oBo.","..oBo.......oBo.","..oBo.......oBo.","..ooo.......ooo.","................"];
  const chair=dir=>memo('ch'+dir,()=>{const s=ascii(chairRows,{o:PAL.out,B:PAL.wood,b:PAL.woodD,R:PAL.red,r:PAL.redD});return dir==='right'?s:mirror(s)});
  const oven=fr=>memo('ov'+fr,()=>{const [c,x]=mk(34,44);
    R(x,PAL.stoneD,9,0,6,1);R(x,'#5c5650',10,1,4,9);R(x,'#77706a',10,1,1,9);
    disc(x,17,30,15,22,PAL.brick);
    for(let y=8;y<30;y++)for(let i=2;i<33;i++){if(!inE(i,y,17,30,15,22))continue;if((y-8)%4===0)R(x,PAL.brickD,i,y);else if(((i+((y-8)>>2)*3)%7)===0)R(x,PAL.brickD,i,y)}
    for(let y=10;y<20;y++)for(let i=6;i<14;i++)if(inE(i,y,11,16,5,7)&&(i+y)%2)R(x,PAL.brickL,i,y);
    disc(x,17,31,8,10,'#1a0d08');
    disc(x,17,31,6,6,[PAL.fire3,PAL.fire2][fr]);disc(x,17+(fr?1:-1),31,4,4,PAL.fire2);disc(x,17,32,2,2,PAL.fire1);
    R(x,PAL.stone,1,30,32,13);R(x,PAL.stoneL,1,30,32,2);
    for(const [yy,off] of [[34,0],[38,5]]){R(x,PAL.stoneD,1,yy,32,1);for(let i=1+off;i<33;i+=10)R(x,PAL.stoneD,i,yy-3,1,3)}
    R(x,PAL.stoneD,1,42,32,1);
    R(x,PAL.woodD,9,30,16,2);R(x,PAL.wood,9,30,16,1);
    return outline(c)});
  const counter=n=>memo('ct'+n,()=>{const W=n*16,[c,x]=mk(W+2,28);
    R(x,PAL.marble,1,1,W,9);R(x,'#fbf9f4',1,1,W,1);for(let i=4;i<W;i+=11){R(x,PAL.marbleD,i,4,3,1);R(x,PAL.marbleD,i+3,5,2,1)}
    R(x,PAL.marbleD,1,9,W,1);
    R(x,PAL.wood,1,10,W,16);R(x,PAL.woodL,1,10,W,1);
    for(let i=1;i<W;i+=16){R(x,PAL.woodD,i+2,13,12,10);R(x,PAL.wood,i+3,14,10,8);R(x,PAL.woodL,i+3,14,10,1)}
    R(x,PAL.woodDD,1,25,W,1);
    return outline(c)});
  const plant=()=>memo('pl',()=>{const [c,x]=mk(18,30);
    R(x,'#b5562c',4,19,10,9);R(x,'#cf6f3e',3,18,12,3);R(x,'#9a4422',4,26,10,2);R(x,'#e08850',4,18,10,1);
    for(const [cx,cy,r,col] of [[9,10,6,PAL.greenD],[6,13,4,PAL.green],[12,12,4,PAL.green],[9,7,4,PAL.green],[7,9,2,PAL.greenL],[11,6,2,PAL.greenL],[13,10,1.5,PAL.greenL]])disc(x,cx,cy,r,r,col);
    R(x,PAL.greenD,8,15,2,4);return outline(c)});
  const windowS=night=>memo('win'+night,()=>{const [c,x]=mk(34,24);
    R(x,PAL.woodD,3,1,28,20);
    for(let y=3;y<19;y++)R(x,night?(y<11?'#2c3466':'#3e4a80'):(y<11?PAL.glass:PAL.glassL),5,y,24,1);
    if(!night){for(let k=0;k<6;k++){R(x,'#ffffff',8+k,14-k);R(x,'#ffffff',18+k,15-k)}}else{R(x,'#ffe9a0',9,6);R(x,'#ffe9a0',22,5)}
    R(x,PAL.woodD,16,3,2,16);R(x,PAL.woodD,5,10,24,2);
    R(x,PAL.wood,1,20,32,3);R(x,PAL.woodL,1,20,32,1);
    for(const sx of [1,27]){R(x,PAL.red,sx,1,6,19);R(x,PAL.redD,sx+2,1,1,19);R(x,PAL.redD,sx+4,3,1,17);R(x,PAL.redL,sx+1,1,1,19)}
    return outline(c)});
  const painting=()=>memo('pt',()=>{const [c,x]=mk(20,16);R(x,PAL.gold,1,1,18,14);R(x,PAL.goldD,1,14,18,1);R(x,PAL.goldD,18,1,1,14);
    R(x,'#8cc4e8',3,3,14,6);R(x,'#3a78b0',3,9,14,4);disc(x,8,10,5,5,'#6b5a4a');R(x,'#3a78b0',3,10,14,3);R(x,'#cfd6e0',7,4,2,1);R(x,'#ffe08a',14,4,2,2);R(x,'#2f5f8f',3,12,14,1);
    return outline(c)});
  const chalkboard=()=>memo('cb',()=>{const [c,x]=mk(34,24);R(x,PAL.wood,1,1,32,22);R(x,'#2f4a3a',3,3,28,17);
    for(const [y,w] of [[5,12],[8,18],[11,14],[14,20],[17,10]])R(x,'#dfe8df',5,y,w,1);
    disc(x,26,9,4,4,PAL.crust);disc(x,26,9,3,3,PAL.sauce);R(x,PAL.cheese,25,8);R(x,PAL.cheese,27,10);
    R(x,PAL.woodL,1,1,32,1);return outline(c)});
  const rack=()=>memo('rk',()=>{const [c,x]=mk(18,18);R(x,'#77706a',1,2,16,2);
    R(x,'#5c5650',4,4,1,6);disc(x,4.5,11,2.5,2.5,'#8f979c');R(x,'#5c5650',9,4,1,4);disc(x,9.5,10,3.5,3.5,'#3a3a3a');R(x,'#5c5650',14,4,1,9);R(x,'#c9c3b8',13,12,3,3);return outline(c)});

  /* ---------- props ---------- */
  const pizza=()=>memo('pz',()=>{const [c,x]=mk(12,12);disc(x,6,6,5,5,PAL.crust);disc(x,6,6,3.6,3.6,PAL.sauce);R(x,PAL.cheese,4,4,2,1);R(x,PAL.cheese,7,6,2,1);R(x,PAL.cheese,5,7);R(x,PAL.pep,7,4);R(x,PAL.pep,4,6);R(x,PAL.pep,6,8);R(x,'#f0bf78',3,2,3,1);return outline(c)});
  const plate=()=>memo('pt2',()=>{const [c,x]=mk(12,8);disc(x,6,4,5,3,'#fbf7ef');disc(x,6,4,3,1.6,'#e8e2d6');return outline(c)});
  const crumbs=()=>memo('cr',()=>{const [c,x]=mk(12,8);disc(x,6,4,5,3,'#fbf7ef');R(x,PAL.crust,4,3,2,1);R(x,PAL.sauce,7,4);return outline(c)});
  const register=()=>memo('rg',()=>{const [c,x]=mk(16,14);R(x,'#5a6470',2,5,12,8);R(x,'#7a8592',2,5,12,1);R(x,'#3a4048',4,1,8,5);R(x,'#7dff6a',5,2,6,2);for(let i=3;i<13;i+=3)R(x,'#c9cfd6',i,8,2,1);for(let i=3;i<13;i+=3)R(x,'#c9cfd6',i,10,2,1);return outline(c)});
  const boxes=()=>memo('bx',()=>{const [c,x]=mk(16,16);for(let k=0;k<3;k++){const y=10-k*4;R(x,'#e9d9b7',1,y,14,4);R(x,'#c7b38c',1,y+3,14,1);R(x,'#fbf1da',1,y,14,1);R(x,PAL.red,7,y+1,2,1)}return outline(c)});
  const logs=()=>memo('lg',()=>{const [c,x]=mk(16,10);for(const [a,b] of [[1,5],[6,5],[11,5],[3,1],[8,1]]){R(x,PAL.wood,a,b,5,4);R(x,PAL.woodL,a,b,5,1);R(x,'#e0b47a',a,b+1,1,2)}return outline(c)});
  const dough=()=>memo('dg',()=>{const [c,x]=mk(32,14);R(x,PAL.woodL,1,1,30,9);R(x,PAL.wood,1,9,30,3);R(x,'#e0b27a',1,1,30,1);disc(x,9,5,4,3,'#f6ead2');disc(x,20,5,5,3.2,'#f6ead2');disc(x,20,5,3.4,2,PAL.sauce);R(x,'#ffffff',8,3);return outline(c)});

  /* ---------- characters (16x22) ---------- */
  const TOP={
    down:["................",".....oooooo.....","....oHHHHHHo....","...oHHHHHHHHo...","...oHHHHHHHHo...","...oHhSSSShHo...","...oSSESSESSo...","...oSSSSSSSSo...","....osSSSSso....","...ooCCCCCCoo...","..oSoCCCCCCoSo..","..oSoCCCCCCoSo..","..ooocccccccoo..","....oPPPPPPo...."],
    up:  ["................",".....oooooo.....","....oHHHHHHo....","...oHHHHHHHHo...","...oHHHHHHHHo...","...oHHHHHHHHo...","...oHHHHHHHHo...","...ohHHHHHHho...","....ohhhhhho....","...ooCCCCCCoo...","..oSoCCCCCCoSo..","..oSoCCCCCCoSo..","..ooocccccccoo..","....oPPPPPPo...."],
    side:["................",".....ooooo......","....oHHHHHo.....","...oHHHHHHHo....","...oHHHHHHHo....","...oHHHhSSSo....","...oHHhSSESo....","...oHhSSSSSSo...","....ohsSSSso....",".....oCCCCo.....",".....oCCSCo.....",".....oCCSCo.....",".....occcco.....",".....oPPPPo....."]
  };
  const LEGS={
    down:{idle:["....oPPooPPo....","....oPPooPPo....","....oFFooFFo....",".....oo..oo.....","................"],
          a:["....oPPooPPo....","....oFFooPPo....",".....oo.oFFo....",".........oo.....","................"],
          b:["....oPPooPPo....","....oPPooFFo....","....oFFo.oo.....",".....oo.........","................"]},
    side:{idle:[".....oPPPPo.....",".....oPPPPo.....",".....oFFFFoo....","......ooooo.....","................"],
          a:["....oPPooPPo....","...oPPo..oPPo...","...oFFo..oFFFo..","....oo....ooo...","................"],
          b:[".....oPPPPo.....",".....oPPPo......",".....oFFFFo.....","......oooo......","................"]}
  };
  LEGS.up=LEGS.down;
  const LONG={down:[[3,9],[12,9],[3,10],[12,10]],up:[[4,9],[11,9],[4,10],[11,10],[5,9],[10,9]],side:[[4,9],[4,10],[5,9]]};
  const HAT=["....oooooooo....","...oWWWWWWWWo...","...oWWWWWWWWo...","....owwwwwwo...."];
  function char(o){
    const dir=o.dir||'down',fr=o.sit?'idle':(o.frame||'idle');
    const key=['c',dir,fr,o.body,o.hair,o.skin,o.long?1:0,o.hat?1:0,o.role||'',o.sit?1:0].join('|');
    return memo(key,()=>{
      const base=dir==='left'||dir==='right'?'side':dir;
      const rows=[...TOP[base],...(o.sit?["................","................","................","................","................"]:LEGS[base][fr])];
      const body=o.body,pal={o:PAL.out,E:PAL.out,H:o.hair,h:shadeHex(o.hair,-30),S:o.skin,s:shadeHex(o.skin,-28),C:body,c:shadeHex(body,-40),P:o.pants||'#3b3550',F:'#4a2c1c',W:'#ffffff'};
      const [c,x]=mk(16,22);
      x.drawImage(ascii(rows,pal),0,3);
      if(o.hat)x.drawImage(ascii(HAT,{o:PAL.out,W:'#ffffff',w:'#e4e0d8'}),0,1);
      if(o.long)for(const [i,y] of LONG[base])R(x,o.hair,i,y+3);
      if(o.role==='waiter'&&base!=='up'){if(base==='down'){R(x,'#ffffff',6,12,4,3);R(x,PAL.red,7,12,2,1)}else{R(x,'#ffffff',8,12,1,2)}}
      if(o.role==='cook'&&base!=='up'){if(base==='down')R(x,PAL.red,6,12,4,1);else R(x,PAL.red,7,12,2,1)}
      return dir==='left'?mirror(c):c;
    });
  }
  function shadeHex(h,a){const [r,g,b]=hex(h);return '#'+[r,g,b].map(v=>Math.max(0,Math.min(255,v+a)).toString(16).padStart(2,'0')).join('')}

  return {PAL,floorCheck,floorKitchen,sidewalk,curb,wallDining,wallKitchen,wallTop,doorMat,table,chair,oven,counter,plant,windowS,painting,chalkboard,rack,pizza,plate,crumbs,register,boxes,logs,dough,char,ascii,outline};
})();
