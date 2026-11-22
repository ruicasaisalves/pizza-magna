/* Makes the animated GIFs for the itch.io page description, from the real game.
   Run from the repo root:  node itch/make_gifs.js        (needs Playwright and ffmpeg; takes a few minutes)
   Output (next to this file): gif-pizza.gif (a pizza built piece by piece), gif-day.gif (the dining room at
   the dinner rush), gif-city.gif (a slow pan over Porto Magno).
   Full-size screenshots are slow, so while recording the page runs at a quarter of its speed (clocks, timers,
   requestAnimationFrame and CSS animations) and the frames are timed in the page's own time. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const OUT = __dirname, GAME = 'file://' + path.resolve(__dirname, '../index.html'), K = 0.25;
const TMP = fs.mkdtempSync(path.join(require('os').tmpdir(), 'pm-gifs-'));

async function page(b, viewport, scale) {
  const ctx = await b.newContext({ viewport, deviceScaleFactor: scale, locale: 'en-US' });
  const p = await ctx.newPage();
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.addInitScript(K => {
    try { localStorage.setItem('pm-music', '0') } catch (e) {}
    const pn = performance.now.bind(performance), t0 = pn(), dn = Date.now, d0 = dn();
    performance.now = () => t0 + (pn() - t0) * K; Date.now = () => d0 + (dn() - d0) * K;
    const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = cb => raf(ts => cb(t0 + (ts - t0) * K));
    const st = window.setTimeout.bind(window); window.setTimeout = (f, d, ...a) => st(f, (d || 0) / K, ...a);
    const si = window.setInterval.bind(window); window.setInterval = (f, d, ...a) => si(f, (d || 0) / K, ...a);
  }, K);
  await p.goto(GAME); await p.waitForTimeout(1500 / K);
  const cdp = await ctx.newCDPSession(p); await cdp.send('Animation.enable'); await cdp.send('Animation.setPlaybackRate', { playbackRate: K });
  // a quiet start: names given, no intro, an empty bench
  await p.evaluate(() => { ACT.quickstart(); closeModal(); const tt = $('#toast'); if (tt) tt.hidden = true });
  return { p, cdp, W: ms => p.waitForTimeout(ms / K) };
}
// grab the box of an element, in a loop, until stop(); returns the folder of frames and their times (page seconds)
function recorder({ p, cdp }, sel, scale) {
  const dir = fs.mkdtempSync(path.join(TMP, 'f-')), times = []; let on = true, n = 0;
  const loop = (async () => {
    await p.addStyleTag({ content: '.rzoom{display:none!important}' });   // no zoom buttons over the room or the map
    const r = await p.evaluate(s => { const b = document.querySelector(s).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, width: b.width, height: b.height } }, sel);
    while (on) {
      const t = Date.now(), s = await cdp.send('Page.captureScreenshot', { format: 'png', clip: { ...r, scale } });
      fs.writeFileSync(path.join(dir, String(n++).padStart(5, '0') + '.png'), Buffer.from(s.data, 'base64')); times.push(t * K / 1000);
    }
  })();
  return async () => { on = false; await loop; return { dir, times } };
}
// frames + times -> GIF at fps, width w, with its own palette; hold: seconds the last frame stays
function toGif({ dir, times }, name, fps, w, hold = 0) {
  let list = ''; times.forEach((t, i) => { const d = i < times.length - 1 ? times[i + 1] - t : 1 / fps + hold; list += `file '${String(i).padStart(5, '0')}.png'\nduration ${d.toFixed(4)}\n` });
  list += `file '${String(times.length - 1).padStart(5, '0')}.png'\n`; fs.writeFileSync(path.join(dir, 'list.txt'), list);
  const out = path.join(OUT, name);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'), '-vf',
    `fps=${fps},scale=${w}:-1:flags=neighbor,split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle`, '-loop', '0', out]);
  console.log(name, (fs.statSync(out).size / 1e6).toFixed(2) + ' MB', (times[times.length - 1] - times[0]).toFixed(1) + ' s');
}

(async () => {
  const b = await chromium.launch();

  // ---- 1. a pizza built on the bench (phone layout, zoomed bench), ending on the empty base so it loops
  {
    const g = await page(b, { width: 405, height: 720 }, 2), { p, W } = g;
    await p.evaluate(() => { state.zoom = true; state.draft = { ...state.draft, name: 'Diavola Suprema', dough: 'napo', sauce: 'tomate', pieces: [] }; ACT.cat({ dataset: { v: 'queijo' } }); ACT.ing({ dataset: { v: 'mozzarella' } }); setCut(1); render() });
    await W(500);
    const pick = async (id, cut) => { await p.evaluate(([id, cut]) => { ACT.cat({ dataset: { v: ingCat(id) } }); ACT.ing({ dataset: { v: id } }); if (cut) setCut(1) }, [id, cut]); await W(200) };
    const tap = async (x, y, ms) => { const pt = await p.evaluate(([x, y]) => { const r = $('#pz').getBoundingClientRect(); return [r.left + (PCX + x * PR) / BW * r.width, r.top + (PCY + y * PR) / BH * r.height] }, [x, y]); await p.mouse.click(pt[0], pt[1]); await W(ms) };
    const ring = (n, r, o = 0) => Array.from({ length: n }, (_, i) => [r * Math.cos(o + i / n * 6.283), r * Math.sin(o + i / n * 6.283)]);
    const stop = recorder(g, '#pz', 2); await W(600);
    for (const [x, y] of [[0, 0], ...ring(5, .36, .3), ...ring(8, .63, 0)]) await tap(x, y, 80);
    await pick('pepperoni', 0); for (const [x, y] of [...ring(5, .3, .6), ...ring(9, .6, .2)]) await tap(x, y, 90);
    await pick('cogumelos', 0); for (const [x, y] of ring(6, .47, 1)) await tap(x, y, 90);
    await pick('jalapenos', 0); for (const [x, y] of [...ring(4, .18, .3), ...ring(6, .68, .7)]) await tap(x, y, 90);
    await pick('manjericao', 0); for (const [x, y] of ring(5, .42, .1)) await tap(x, y, 110);
    await W(1800);
    await p.evaluate(() => { const tt = $('#toast'); if (tt) tt.hidden = true; ACT.clear() }); await W(400);
    toGif(await stop(), 'gif-pizza.gif', 20, 360);
    await p.context().close();
  }

  // ---- 2. the dining room at the dinner rush (desktop layout)
  {
    const g = await page(b, { width: 1280, height: 800 }, 1), { p, W } = g;
    await p.evaluate(() => { state.menu.forEach(m => m.price = Math.max(7, Math.round(m.price - 1))); state.tab = 'dia'; render() });
    await W(600); await p.click('[data-act=open]'); await W(300);
    await p.evaluate(() => { let n = 0; while (anim && anim.t < 18 && n++ < 9000) step(.05) }); await W(300);
    const stop = recorder(g, '#room', 1); await W(7000);
    toGif(await stop(), 'gif-day.gif', 15, 520);
    await p.context().close();
  }

  // ---- 3. a slow pan over the city
  {
    const g = await page(b, { width: 1280, height: 800 }, 1), { p, W } = g;
    await p.evaluate(() => { state.tab = 'cidade'; render() }); await W(800);
    await p.evaluate(() => { CV.cam.x = 0; CV.cam.y = 0; CV.draw() }); await W(200);
    const stop = recorder(g, '#city', 1);
    for (let i = 0; i < 90; i++) { await p.evaluate(() => { CV.cam.x += 3; CV.cam.y += 1.6; CV.draw() }); await W(60) }
    toGif(await stop(), 'gif-city.gif', 15, 520);
    await p.context().close();
  }
  await b.close(); fs.rmSync(TMP, { recursive: true, force: true }); console.log('done');
})();
