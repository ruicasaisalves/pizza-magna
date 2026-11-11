/* Makes the YouTube Short (1080 x 1920, about 27 s, with the game's own music) and the channel art, from the game itself.
   Run from the repo root:  node youtube/make_short.js
   Output (next to this file): short.mp4, banner.png (2560 x 1440), avatar.png (800 x 800), watermark.png (150 x 150).
   Needs Playwright (preinstalled in the cloud sessions), ffmpeg and internet for the fonts.
   Frames are drawn at 540 x 960 and doubled with nearest-neighbour, so the pixels stay crisp. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), os = require('os'), { execFileSync } = require('child_process');
const OUT = __dirname, ROOT = path.resolve(__dirname, '..'), GAME = 'file://' + path.join(ROOT, 'index.html');
const FPS = 15, W = 540, H = 960;
const save = (file, url) => fs.writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(GAME); await p.waitForTimeout(1500);
  await p.addScriptTag({ path: path.join(ROOT, 'itch', 'art.js') });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-short-')); let n = 0;
  const frame = async (scene, a) => { const url = await p.evaluate(([s, a]) => SF(s, a), [scene, a]); save(path.join(tmp, `f${String(n++).padStart(5, '0')}.png`), url) };

  // ---- the scenes, drawn in the game page
  await p.evaluate(async () => {
    await document.fonts.load('bold 16px Silkscreen'); await document.fonts.ready;
    closeModal(); state = freshState(); Object.assign(state, { chef: 'Rui', shop: 'Pizza Magna', seenIntro: true, tier: 1, rep: 4.2, cooks: 3, ovens: 2, day: 6, lang: 'en' });
    state.room.items.push({ id: 'xadrez2', c: 1, r: 11 }, { id: 'xadrez2', c: 6, r: 11 }, { id: 'vaso', c: 12, r: 3 }, { id: 'vaso', c: 0, r: 13 });
    state.tab = 'dia'; render();                                                                    // loads the room art
    const A = PMArt, { C, K } = A, BG = (() => { const [c, x] = K(540, 960); x.drawImage(A.tile(540, 960, A.wood()), 0, 0); A.vignette(x, 540, 960, .65); return c })();
    const order = [['mozzarella', 12], ['pepperoni', 10], ['cogumelos', 6], ['manjericao', 6], ['azeitonas', 5]];
    const PIECES = []; order.forEach(([id, k], i) => PIECES.push(...spread(id, k, i ? .62 - .04 * (i % 3) : .74, i * 2 + 1)));
    const CLASH = [...spread('coxa', 4, .5, 3), ...spread('nutella', 6, .6, 7)];
    const fit = (t, maxW, kMax) => A.up(t, Math.max(1, Math.min(kMax, Math.floor(maxW / t.width))));
    const caption = (x, lines) => { if (!lines) return; const T = fit(A.title(lines, 'bold 14px Silkscreen'), 500, 4); x.drawImage(T, Math.round((540 - T.width) / 2), Math.round(150 - T.height / 2)) };
    const text = (x, s, cx, y, k, col, shadow = C.deep) => { const m = A.up(A.mask(s, 'bold 8px Silkscreen'), k), X = Math.round(cx - m.width / 2); if (shadow) x.drawImage(A.tint(m, shadow), X, y + k); x.drawImage(A.tint(m, col), X, y); return m.height };
    const band = x => { x.fillStyle = C.tlo; x.fillRect(0, 880, 540, 80); x.fillStyle = C.tomato; x.fillRect(0, 884, 540, 76); x.fillStyle = C.brass; x.fillRect(0, 880, 540, 4); text(x, 'PIZZAMAGNA.XYZ', 270, 902, 4, C.parch) };
    const pizza = (x, pieces, cx, cy, size, rot = 0) => {
      const im = composePizza({ dough: 'napo', sauce: 'tomate', pieces });
      x.save(); x.translate(cx, cy); x.rotate(rot); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      x.fillStyle = 'rgba(15,6,1,.45)'; x.beginPath(); x.ellipse(size * .04, size * .06, size * .5, size * .5, 0, 0, 7); x.fill();
      x.drawImage(im, -size / 2, -size / 2, size, size); x.restore(); x.imageSmoothingEnabled = false;
    };
    const lcd = (x, pieces, y, bad) => {                                                           // the bench's green screen: quality and cost
      const a = analyze({ dough: 'napo', sauce: 'tomate', pieces });
      x.fillStyle = C.deep; x.fillRect(80, y, 380, 64); x.fillStyle = '#081008'; x.fillRect(86, y + 6, 368, 52);
      x.font = '40px VT323, monospace'; x.textBaseline = 'middle'; x.textAlign = 'left'; x.fillStyle = bad ? '#ff6a50' : '#8cff73';
      x.fillText(bad ? 'BAD COMBO!' : 'QUALITY ' + a.q, 102, y + 33); x.textAlign = 'right'; x.fillStyle = '#8cff73'; x.fillText(eur(a.cost), 440, y + 33); x.textAlign = 'left';
    };
    const marble = (x, y, h) => { x.fillStyle = C.deep; x.fillRect(20, y - 6, 500, h + 12); x.fillStyle = '#ecebe6'; x.fillRect(26, y, 488, h);
      x.strokeStyle = 'rgba(150,145,135,.35)'; x.lineWidth = 2; for (let k = 0; k < 6; k++) { x.beginPath(); x.moveTo(26, y + 40 + k * 90); x.bezierCurveTo(150, y + k * 90, 300, y + 120 + k * 80, 514, y + 30 + k * 95); x.stroke() } };
    const bubble = (x, lines, X, Y, w) => {
      const h = lines.length * 30 + 26; x.fillStyle = C.deep; x.fillRect(X - 4, Y - 4, w + 8, h + 8); x.fillStyle = '#fffaf0'; x.fillRect(X, Y, w, h);
      x.fillStyle = C.deep; x.beginPath(); x.moveTo(X + 40, Y + h + 4); x.lineTo(X + 70, Y + h + 4); x.lineTo(X + 34, Y + h + 34); x.fill();
      x.fillStyle = '#fffaf0'; x.beginPath(); x.moveTo(X + 44, Y + h); x.lineTo(X + 64, Y + h); x.lineTo(X + 40, Y + h + 24); x.fill();
      lines.forEach((l, i) => text(x, l, X + w / 2, Y + 16 + i * 30, 3, C.deep, null));
    };
    window.SF = (scene, a) => {
      const [c, x] = K(540, 960); x.drawImage(BG, 0, 0);
      if (scene === 'intro') {                                                                      // a: 0..1
        caption(x, ['I MADE A', 'PIZZA GAME']);
        const s = Math.min(1, a * 4); pizza(x, PIECES, 270, 520, 420 * (.6 + .4 * (1 - (1 - s) ** 3)), a * 1.2);
        text(x, 'PIXEL ART', 270, 770, 3, C.hi); text(x, 'IN YOUR BROWSER', 270, 810, 3, C.hi);
      } else if (scene === 'build') {                                                              // a: pieces shown
        caption(x, ['TOPPING BY', 'TOPPING']); marble(x, 250, 520);
        const ps = PIECES.slice(0, a); pizza(x, ps, 270, 480, 400); lcd(x, ps, 790);
      } else if (scene === 'clash') {                                                              // a: {k: clash pieces, b: bubble on}
        caption(x, ['CUSTOMERS', 'HAVE OPINIONS']); marble(x, 250, 520);
        const ps = [...PIECES, ...CLASH.slice(0, a.k)]; pizza(x, ps, 270, 480, 400); lcd(x, ps, 790, a.k > 4);
        if (a.b) {
          const who = A.up(rspr('w4_down_0'), 4); x.drawImage(who, 400, 520);
          bubble(x, ['CHICKEN WITH NUTELLA?', 'NO, THANK YOU.'], 40, 300, 440);
        }
      } else if (scene === 'room') {
        caption(x, ['RUN THE WHOLE', 'PIZZERIA']);
        x.fillStyle = C.brass; x.fillRect(0, 262, 540, 560); x.fillStyle = C.deep; x.fillRect(0, 266, 540, 552);
        x.drawImage(room.low, 50, 0, 540, 544, 0, 270, 540, 544);
      } else {                                                                                      // the end card
        const T = fit(A.title(['PIZZA', 'MAGNA'], 'bold 24px Silkscreen'), 470, 5); x.drawImage(T, Math.round((540 - T.width) / 2), 60);
        pizza(x, PIECES, 270, 500, 300, a * .8);
        text(x, 'PLAY FREE', 270, 680, 4, C.hi); text(x, 'IN YOUR BROWSER', 270, 730, 3, C.parch); text(x, 'ALSO ON ITCH.IO', 270, 790, 3, C.hi);
      }
      band(x);
      return c.toDataURL('image/png');
    };
  });
  await p.waitForTimeout(1500);                                                                    // the room art loads

  const sec = s => Math.round(s * FPS);
  for (let i = 0, N = sec(2.5); i < N; i++) await frame('intro', i / N);
  for (let i = 0, N = sec(7); i < N; i++) await frame('build', Math.min(39, Math.floor(i * 39 / (N - sec(1)))));
  for (let i = 0, N = sec(4.5); i < N; i++) await frame('clash', { k: Math.min(10, Math.floor(i / 2)), b: i > sec(1.6) });
  // the dining room, in real time from the lunch rush
  await p.click('[data-act=open]'); await p.waitForTimeout(9500);
  for (let i = 0, N = sec(9); i < N; i++) { const t0 = Date.now(); await frame('room'); await p.waitForTimeout(Math.max(0, 1000 / FPS - (Date.now() - t0))) }
  for (let i = 0, N = sec(3.5); i < N; i++) await frame('end', i / N);
  const dur = n / FPS;

  // ---- the music: the Tarantella, rendered offline from music.js
  const mp = await b.newPage(); await mp.goto(GAME); await mp.waitForTimeout(800);
  const wav = await mp.evaluate(async ([src, dur]) => {
    const SR = 44100, LEN = Math.ceil(SR * (dur + 1)); let oc;
    window.AudioContext = function () { oc = new OfflineAudioContext(1, LEN, SR); return oc };
    const pend = []; window.setTimeout = f => { pend.push(f); return 0 }; window.clearTimeout = () => {};
    const M = new Function(src + ';return MUSIC')(); M.play('tarantella');
    for (let k = 1; k * .1 < LEN / SR; k++) oc.suspend(k * .1).then(() => { pend.splice(0).forEach(g => g()); oc.resume() });
    const x = (await oc.startRendering()).getChannelData(0), buf = new ArrayBuffer(44 + x.length * 2), v = new DataView(buf);
    const str = (o, s) => [...s].forEach((ch, i) => v.setUint8(o + i, ch.charCodeAt(0)));
    str(0, 'RIFF'); v.setUint32(4, 36 + x.length * 2, true); str(8, 'WAVEfmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, SR, true); v.setUint32(28, SR * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, 'data'); v.setUint32(40, x.length * 2, true);
    for (let i = 0; i < x.length; i++) v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, x[i])) * 32767, true);
    let s = ''; const u = new Uint8Array(buf); for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode(...u.subarray(i, i + 32768));
    return btoa(s);
  }, [fs.readFileSync(path.join(ROOT, 'music.js'), 'utf8'), dur]);
  fs.writeFileSync(path.join(tmp, 'music.wav'), Buffer.from(wav, 'base64'));

  // ---- the video: doubled with nearest-neighbour, 30 fps, loud enough for a phone
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(tmp, 'f%05d.png'), '-i', path.join(tmp, 'music.wav'),
    '-filter_complex', `[0:v]scale=${W * 2}:${H * 2}:flags=neighbor,fps=30,format=yuv420p[v];[1:a]atrim=0:${dur.toFixed(2)},loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.2,afade=t=out:st=${(dur - 1.5).toFixed(2)}:d=1.5[a]`,
    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-movflags', '+faststart', path.join(OUT, 'short.mp4')]);
  console.log('short.mp4', dur.toFixed(1), 's,', Math.round(fs.statSync(path.join(OUT, 'short.mp4')).size / 1024), 'KB');

  // ---- the channel art: banner (2560 x 1440; what every device shows is the middle 1546 x 423), avatar, watermark
  const art = await p.evaluate(() => {
    const A = PMArt, { C, K } = A, out = {};
    const mk = (list, sauce = 'tomate') => { const ps = [...spread('mozzarella', 12, .74, 0)]; list.forEach(([id, k], i) => ps.push(...spread(id, k, .62 - .04 * (i % 3), i * 2 + 1))); return composePizza({ dough: 'napo', sauce, pieces: ps }) };
    const pz = [mk([['pepperoni', 10], ['azeitonas', 5]]), mk([['manjericao', 7]]), mk([['fiambre', 7], ['ananas', 8]]), mk([['presunto', 6], ['rucula', 8], ['tomate', 5]], 'pesto')];
    const put = (x, im, cx, cy, s, r) => { x.save(); x.translate(cx, cy); x.rotate(r); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      x.fillStyle = 'rgba(15,6,1,.45)'; x.beginPath(); x.ellipse(s * .04, s * .06, s * .5, s * .5, 0, 0, 7); x.fill(); x.drawImage(im, -s / 2, -s / 2, s, s); x.restore() };
    {
      const [c, x] = K(2560, 1440); x.drawImage(A.tile(2560, 1440, A.wood()), 0, 0); A.vignette(x, 2560, 1440, .6);
      [[260, 300, 420, .3], [330, 1150, 380, 2], [2300, 280, 400, -.5], [2240, 1160, 420, 1.1], [150, 720, 260, 4], [2420, 720, 260, 2.4]].forEach(([cx, cy, s, r], i) => put(x, pz[i % 4], cx, cy, s, r));
      x.fillStyle = C.brass; x.fillRect(0, 488, 2560, 6); x.fillRect(0, 946, 2560, 6);
      const t = A.title(['PIZZA MAGNA'], 'bold 20px Silkscreen'), T = A.up(t, Math.floor(1300 / t.width)); x.drawImage(T, Math.round((2560 - T.width) / 2), 530);
      const m = A.up(A.mask('A PIZZERIA TYCOON IN 90s PIXEL ART · PLAY FREE AT PIZZAMAGNA.XYZ', 'bold 8px Silkscreen'), 3);
      x.drawImage(A.tint(m, C.deep), Math.round((2560 - m.width) / 2), 860 + 3); x.drawImage(A.tint(m, C.parch), Math.round((2560 - m.width) / 2), 860);
      out.banner = c.toDataURL('image/png');
    }
    {
      const [c, x] = K(800, 800); x.fillStyle = C.lo; x.fillRect(0, 0, 800, 800);
      const g = x.createRadialGradient(400, 400, 60, 400, 400, 420); g.addColorStop(0, '#a8692f'); g.addColorStop(1, C.deep); x.fillStyle = g; x.fillRect(0, 0, 800, 800);
      put(x, pz[0], 400, 400, 600, .2); out.avatar = c.toDataURL('image/png');
    }
    {
      const [c, x] = K(150, 150);
      put(x, pz[0], 75, 75, 140, .2); out.wm = c.toDataURL('image/png');
    }
    return out;
  });
  save(path.join(OUT, 'banner.png'), art.banner); save(path.join(OUT, 'avatar.png'), art.avatar); save(path.join(OUT, 'watermark.png'), art.wm);
  fs.rmSync(tmp, { recursive: true, force: true });
  await b.close(); console.log('done');
})();
