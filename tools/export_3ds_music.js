#!/usr/bin/env node
/* Records every tune of music.js for the 3DS port, which has no Web Audio: 3ds/game/music/<id>.ogg (mono, 32 kHz,
   Vorbis) and 3ds/game/musicdata.lua (id, title, lofi, calm, seconds, in the order of music.js).
   Each tune is played into an OfflineAudioContext in Chromium (Playwright) with the same voices as music.js
   (toneNow(), drumNow(), schedule(): the same waves, envelopes, drums, tape wobble, lo-fi warm filter, calm level,
   master low-pass and limiter), at the browser's loudest volume (level 5); the 3DS sets its own volume on top.
   If music.js's voices change, change them here too. Needs ffmpeg with libvorbis.
   Run after changing music.js: node tools/export_3ds_music.js */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');
const root=path.join(__dirname,'..'),out=path.join(root,'3ds/game/music'),SR=32000;
(async()=>{
  const b=await chromium.launch(),pg=await b.newPage();
  await pg.setContent('<!doctype html><body></body>');
  await pg.addScriptTag({path:path.join(root,'music.js')});
  const ids=await pg.evaluate(()=>MUSIC.songs.map(s=>s.id));
  fs.mkdirSync(out,{recursive:true});
  for(const f of fs.readdirSync(out))if(f.endsWith('.ogg'))fs.unlinkSync(path.join(out,f));
  const meta=[];
  for(const id of ids){
    const r=await pg.evaluate(async([id,SR])=>{
      const song=MUSIC.songs.find(s=>s.id===id);
      const NOTE={C:0,'C#':1,Db:1,D:2,'D#':3,Eb:3,E:4,F:5,'F#':6,Gb:6,G:7,'G#':8,Ab:8,A:9,'A#':10,Bb:10,B:11};
      const freq=n=>{const m=/^([A-G][#b]?)(\d)$/.exec(n);return m?440*Math.pow(2,(NOTE[m[1]]+(+m[2]+1)*12-69)/12):0};
      const parse=str=>{const toks=str.replace(/\|/g,' ').trim().split(/\s+/),o=[];let last=[];
        toks.forEach((tk,i)=>{if(tk==='-'){for(const n of last)if(n.start+n.len===i)n.len++;return}if(tk==='.'){last=[];return}last=tk.split('+').map(x=>({f:freq(x),start:i,len:1}));o.push(...last)});
        return {notes:o,steps:toks.length}};
      const step=60/song.bpm;let total=0;for(let l=0;l<song.loops;l++)for(const p of song.parts)total+=parse(song[p].lead).steps*step;
      const ctx=new OfflineAudioContext(1,Math.ceil((total+.6)*SR),SR);
      // the chain of music.js: bus (calm level, lo-fi warm filter) > master (level 5) > low-pass 3200 > limiter
      const lp=ctx.createBiquadFilter();lp.type='lowpass';lp.frequency.value=3200;lp.Q.value=.4;
      const master=ctx.createGain();master.gain.value=.16*2.3;
      const lim=ctx.createDynamicsCompressor();lim.threshold.value=-10;lim.knee.value=6;lim.ratio.value=12;lim.attack.value=.003;lim.release.value=.2;
      master.connect(lp);lp.connect(lim);lim.connect(ctx.destination);
      const wobble=ctx.createOscillator();wobble.frequency.value=.35;const depth=ctx.createGain();depth.gain.value=6;wobble.connect(depth);wobble.start();
      const bus=ctx.createGain();bus.gain.setValueAtTime(0,0);bus.gain.linearRampToValueAtTime(song.calm?.7:1,.1);
      if(song.lofi){const warm=ctx.createBiquadFilter();warm.type='lowpass';warm.frequency.value=1500;warm.Q.value=.5;bus.connect(warm);warm.connect(master)}else bus.connect(master);
      const waves={},pulseWave=duty=>{if(waves[duty])return waves[duty];const n=32,re=new Float32Array(n),im=new Float32Array(n);
        for(let k=1;k<n;k++)im[k]=2/(k*Math.PI)*Math.sin(k*Math.PI*duty);return (waves[duty]=ctx.createPeriodicWave(re,im))};
      const tone=(type,f,t0,dur,vol,opts={})=>{const o=ctx.createOscillator(),g=ctx.createGain();
        if(type==='pulse')o.setPeriodicWave(pulseWave(opts.duty||.25));else o.type=type;o.frequency.value=f;if(opts.wobble)depth.connect(o.detune);
        const att=Math.min(.012,dur/4),rel=Math.min(.04,dur/3);
        g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(vol,t0+att);g.gain.setValueAtTime(vol,t0+dur-rel);g.gain.linearRampToValueAtTime(0,t0+dur);
        o.connect(g);g.connect(bus);o.start(t0);o.stop(t0+dur+.02)};
      let noiseBuf=null;
      const drum=(kind,t0,sc)=>{
        if(kind==='k'){const o=ctx.createOscillator(),g=ctx.createGain();o.frequency.setValueAtTime(150,t0);o.frequency.exponentialRampToValueAtTime(45,t0+.12);
          g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(.55*sc,t0+.004);g.gain.exponentialRampToValueAtTime(.001,t0+.15);o.connect(g);g.connect(bus);o.start(t0);o.stop(t0+.16);return}
        if(!noiseBuf){noiseBuf=ctx.createBuffer(1,ctx.sampleRate*.2,ctx.sampleRate);const d=noiseBuf.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1}
        const s=ctx.createBufferSource(),g=ctx.createGain(),hp=ctx.createBiquadFilter();s.buffer=noiseBuf;hp.type='highpass';hp.frequency.value=kind==='h'?7000:1800;
        const len=kind==='h'?.03:.11,vol=(kind==='h'?.08:.22)*sc;
        g.gain.setValueAtTime(0,t0);g.gain.linearRampToValueAtTime(vol,t0+.003);g.gain.exponentialRampToValueAtTime(.001,t0+len);
        s.connect(hp);hp.connect(g);g.connect(bus);s.start(t0);s.stop(t0+len+.01)};
      let t=.15;
      for(let loop=0;loop<song.loops;loop++)for(const p of song.parts){const part=song[p],lead=parse(part.lead),bass=parse(part.bass),harm=parse(part.harm);
        for(const n of lead.notes){const dur=n.len*step;
          if(song.trem&&n.len>=2){const pick=step/2;for(let k=0;k<dur-.01;k+=pick)tone('pulse',n.f,t+n.start*step+k,Math.min(pick,dur-k)*.95,.22-(k/dur)*.06,{wobble:true})}
          else if(song.tone==='bell')tone('pulse',n.f,t+n.start*step,Math.min(dur*.9,step*1.5),.13,{duty:.125,wobble:true});
          else if(song.tone==='flute')tone('triangle',n.f,t+n.start*step,dur*.92,.22,{wobble:true});
          else if(song.lofi)tone('pulse',n.f,t+n.start*step,dur*.9,.15,{duty:.5,wobble:true});
          else tone('pulse',n.f,t+n.start*step,dur*.92,.24,{wobble:true})}
        for(const n of bass.notes)tone('triangle',n.f,t+n.start*step,n.len*step*.95,.38);
        if(song.lofi)for(const n of harm.notes)tone('triangle',n.f,t+n.start*step,n.len*step,.05);
        else for(const n of harm.notes)tone('pulse',n.f,t+n.start*step,n.len*step*.9,.07,{duty:.5});
        if(part.arp)for(const n of parse(part.arp).notes)tone('pulse',n.f,t+n.start*step,n.len*step*.9,.06,{duty:.5});
        const dr=(part.drums||song.drums).split(/\s+/);for(let i=0;i<lead.steps;i++){const d=dr[i%dr.length];if(d!=='.')drum(d,t+i*step,song.lofi?.45:1)}
        t+=lead.steps*step}
      const buf=await ctx.startRendering(),d=buf.getChannelData(0),pcm=new Int16Array(d.length);
      for(let i=0;i<d.length;i++)pcm[i]=Math.max(-32768,Math.min(32767,Math.round(d[i]*32767)));
      let s='';const u=new Uint8Array(pcm.buffer);for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));
      return {pcm:btoa(s),secs:total+.6,title:song.title,lofi:!!song.lofi,calm:!!song.calm,xmas:!!song.xmas}},[id,SR]);
    const raw=path.join(out,id+'.raw');fs.writeFileSync(raw,Buffer.from(r.pcm,'base64'));
    execFileSync('ffmpeg',['-loglevel','error','-y','-f','s16le','-ar',String(SR),'-ac','1','-i',raw,'-c:a','libvorbis','-q:a','2',path.join(out,id+'.ogg')]);
    fs.unlinkSync(raw);
    meta.push({id,title:r.title,lofi:r.lofi,calm:r.calm,xmas:r.xmas,secs:Math.round(r.secs*10)/10});
    console.log(id.padEnd(12),r.secs.toFixed(1)+' s',(fs.statSync(path.join(out,id+'.ogg')).size/1024).toFixed(0)+' KB');
  }
  await b.close();
  const q=s=>JSON.stringify(s);
  fs.writeFileSync(path.join(root,'3ds/game/musicdata.lua'),'-- Generated by tools/export_3ds_music.js from music.js. Do not edit by hand.\n-- The tunes recorded in music/<id>.ogg, in the order of music.js.\nreturn {\n'+
    meta.map(m=>`  { id = ${q(m.id)}, title = ${q(m.title)}, lofi = ${m.lofi}, calm = ${m.calm}, xmas = ${m.xmas}, secs = ${m.secs} },`).join('\n')+'\n}\n');
  const tot=fs.readdirSync(out).reduce((a,f)=>a+fs.statSync(path.join(out,f)).size,0);
  console.log(meta.length,'tunes,',(tot/1048576).toFixed(1),'MB');
})();
