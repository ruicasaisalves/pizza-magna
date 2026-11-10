/* Makes the images for the game's itch.io page, from the game's own art, fonts and colours.
   Run from the repo root:  node itch/make_media.js
   Output (next to this file): logo.png (transparent), banner.png, cover.png, background.png (seamless tile),
   shot-1..5.png (screenshots). Needs Playwright (preinstalled in the cloud sessions) and internet for the fonts. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = __dirname, GAME = 'file://' + path.resolve(__dirname, '../index.html');
const save = (name, url) => fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(',')[1], 'base64'));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(GAME); await p.waitForTimeout(1500);

  // ---- the art, drawn inside the game page (its fonts, sprites and palette)
  const art = await p.evaluate(async () => {
    await document.fonts.load('bold 16px Silkscreen'); await document.fonts.ready;
    const C = { deep: '#2a1407', lo: '#4a260f', wood: '#7a4520', brass: '#e3b34a', hi: '#fbe39a', tomato: '#c4352a', tlo: '#7e1d14', parch: '#f3e6c6' };
    const K = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.imageSmoothingEnabled = false; return [c, x] };
    const rng = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296 };
    // crisp 1-bit text, so the title has real pixels
    const mask = (text, font) => {
      const [m, mx] = K(8, 8); mx.font = font; const w = Math.ceil(mx.measureText(text).width) + 6, px = +font.match(/(\d+)px/)[1], h = px + 8;
      const [c, x] = K(w, h); x.font = font; x.textBaseline = 'top'; x.fillStyle = '#fff'; x.fillText(text, 3, 4);
      const d = x.getImageData(0, 0, w, h); for (let i = 3; i < d.data.length; i += 4) d.data[i] = d.data[i] > 110 ? 255 : 0; x.putImageData(d, 0, 0); return c;
    };
    const tint = (c, col) => { const [o, x] = K(c.width, c.height); x.drawImage(c, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, o.width, o.height); return o };
    const up = (c, k) => { const [o, x] = K(c.width * k, c.height * k); x.drawImage(c, 0, 0, o.width, o.height); return o };
    // a title in two tones with a dark outline and a red drop shadow, at 1x
    function title(lines, font, gap = 0) {
      const ms = lines.map(l => mask(l, font)), px = +font.match(/(\d+)px/)[1], lh = px + 2 + gap;
      const w = Math.max(...ms.map(m => m.width)) + 6, h = lh * lines.length + 8, [c, x] = K(w, h);
      ms.forEach((m, i) => {
        const ox = Math.round((w - m.width) / 2), oy = 2 + i * lh, red = tint(m, C.tlo), dark = tint(m, C.deep);
        for (let dy = 1; dy <= 3; dy++) for (let dx = -1; dx <= 1; dx++) x.drawImage(red, ox + dx, oy + dy);
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) x.drawImage(dark, ox + dx, oy + dy);
        const [f, fx] = K(m.width, m.height); fx.drawImage(tint(m, C.hi), 0, 0); fx.globalCompositeOperation = 'source-atop'; fx.fillStyle = C.brass; fx.fillRect(0, Math.round(m.height * .56), m.width, m.height);
        x.drawImage(f, ox, oy);
      });
      return c;
    };
    // seamless wooden planks, like the game's panels
    function wood(n = 128, k = 4) {
      const [c, x] = K(n, n), r = rng(7), pw = n / 4;
      for (let p = 0; p < 4; p++) {
        const base = [[76, 42, 19], [88, 49, 23], [70, 38, 17], [82, 45, 21]][p], joint = 20 + Math.floor(r() * (n - 40));
        for (let y = 0; y < n; y++) for (let xx = 0; xx < pw; xx++) {
          const g = Math.sin((y + p * 17) * .22 + Math.sin(xx * .4 + p) * 1.3) * 5 + (r() - .5) * 7, edge = xx === 0 || xx === pw - 1 ? -16 : 0, jn = (y === joint || y === joint + 1) ? -18 : 0;
          const v = g + edge + jn; x.fillStyle = `rgb(${base[0] + v},${base[1] + v * .6},${base[2] + v * .35})`; x.fillRect(p * pw + xx, y, 1, 1);
        }
        for (const ny of [joint - 4, joint + 5]) { x.fillStyle = '#1d0e05'; x.fillRect(p * pw + 3, ny, 1, 1); x.fillRect(p * pw + pw - 4, ny, 1, 1) }
      }
      return up(c, k);
    }
    const tile = (w, h, t) => { const [c, x] = K(w, h); for (let yy = 0; yy < h; yy += t.height) for (let xx = 0; xx < w; xx += t.width) x.drawImage(t, xx, yy); return c };
    const vignette = (x, w, h, a = .55) => { const g = x.createRadialGradient(w / 2, h / 2, Math.min(w, h) * .3, w / 2, h / 2, Math.max(w, h) * .75); g.addColorStop(0, 'rgba(20,8,2,0)'); g.addColorStop(1, `rgba(20,8,2,${a})`); x.fillStyle = g; x.fillRect(0, 0, w, h) };

    // the pizzas
    const mk = (dough, sauce, list, base = 'mozzarella') => { const pieces = [...spread(base, 12, .74, 0)]; list.forEach(([id, n], k) => pieces.push(...spread(id, n, .66 - .04 * (k % 3), k * 2 + 1))); return { dough, sauce, pieces } };
    const PZ = {
      margherita: mk('napo', 'tomate', [['manjericao', 7]]),
      pepperoni: mk('napo', 'tomate', [['pepperoni', 10], ['azeitonas', 5], ['oregaos', 4]]),
      hawaii: mk('napo', 'tomate', [['fiambre', 7], ['ananas', 8]]),
      quatro: mk('lenta', 'tomate', [['cogumelos', 6], ['fiambre', 5], ['pimento', 5], ['azeitonas', 5]]),
      gourmet: mk('lenta', 'pesto', [['presunto', 6], ['rucula', 8], ['parmesao', 5], ['tomate', 5]]),
    };
    const pz = {}; for (const k in PZ) pz[k] = composePizza(PZ[k]);
    const shadowed = (x, img, cx, cy, s, rot = 0) => {   // a pizza with a soft drop shadow
      x.save(); x.translate(cx, cy); x.rotate(rot); x.imageSmoothingEnabled = true; x.imageSmoothingQuality = 'high';
      x.fillStyle = 'rgba(15,6,1,.45)'; x.beginPath(); x.ellipse(s * .05, s * .07, s * .5, s * .5, 0, 0, 7); x.fill();
      x.drawImage(img, -s / 2, -s / 2, s, s); x.restore();
    };
    const icon = (id, k) => { const [c, x] = K(32, 32); sprFit(x, wholeKey(id, 0, 0), 16, 16, 30); return up(c, k) };
    const out = {};

    // logo (transparent): the pizza and the two-line title
    {
      const t = title(['PIZZA', 'MAGNA'], 'bold 24px Silkscreen', 0), k = 6, T = up(t, k), P = 330;
      const [c, x] = K(P + 40 + T.width, Math.max(P, T.height) + 20);
      shadowed(x, pz.margherita, P / 2 + 10, c.height / 2, P, -.2);
      x.drawImage(T, P + 30, Math.round((c.height - T.height) / 2));
      out.logo = c.toDataURL('image/png'); out.logoSize = [c.width, c.height];
    }
    // banner 1920x480: planks, title on the left, a spread of pizzas on the right
    {
      const [c, x] = K(1920, 480); x.drawImage(tile(1920, 480, wood()), 0, 0); vignette(x, 1920, 480, .6);
      const t = up(title(['PIZZA', 'MAGNA'], 'bold 24px Silkscreen', 0), 6);
      x.drawImage(t, 150, Math.round((480 - t.height) / 2) - 8);
      const tag = up(title(['A PIZZERIA TYCOON'], 'bold 8px Silkscreen'), 4); x.drawImage(tag, 150 + Math.round((t.width - tag.width) / 2), 480 - 92);
      shadowed(x, pz.pepperoni, 1130, 250, 360, .5); shadowed(x, pz.hawaii, 1460, 160, 270, -.4); shadowed(x, pz.gourmet, 1680, 340, 300, .9); shadowed(x, pz.quatro, 1320, 400, 230, 1.7);
      x.fillStyle = C.brass; x.fillRect(0, 0, 1920, 8); x.fillRect(0, 472, 1920, 8); x.fillStyle = C.lo; x.fillRect(0, 8, 1920, 4); x.fillRect(0, 468, 1920, 4);
      out.banner = c.toDataURL('image/png');
    }
    // cover 630x500 (itch shows it at 315x250 in lists)
    {
      const [c, x] = K(630, 500); x.drawImage(tile(630, 500, wood()), 0, 0); vignette(x, 630, 500, .65);
      // a warm glow behind the pizza
      const g = x.createRadialGradient(315, 285, 40, 315, 285, 260); g.addColorStop(0, 'rgba(255,190,80,.35)'); g.addColorStop(1, 'rgba(255,190,80,0)'); x.fillStyle = g; x.fillRect(0, 0, 630, 500);
      shadowed(x, pz.pepperoni, 315, 285, 330, .15);
      [['pepperoni', 70, 215, 100], ['cogumelos', 535, 190, 96], ['manjericao', 70, 395, 96], ['tomate', 548, 380, 96]].forEach(([id, cx, cy, s]) => { try { const i = icon(id, 3); x.drawImage(i, cx - s / 2 - 2, cy - s / 2 + 4, s, s) } catch (e) {} });
      const t = title(['PIZZA MAGNA'], 'bold 20px Silkscreen'), k = Math.floor(580 / t.width), T = up(t, k);
      x.drawImage(T, Math.round((630 - T.width) / 2), 22);
      const band = 42; x.fillStyle = C.tlo; x.fillRect(0, 500 - band - 4, 630, band + 4); x.fillStyle = C.tomato; x.fillRect(0, 500 - band, 630, band); x.fillStyle = C.brass; x.fillRect(0, 500 - band - 4, 630, 4);
      const tg = up(title(['PIZZERIA TYCOON · 90s PIXEL ART'], 'bold 8px Silkscreen'), 2);
      // plain cream text on the red band (the title() colours are for the big letters)
      const m = up(mask('PIZZERIA TYCOON · 90s PIXEL ART', 'bold 8px Silkscreen'), 2), d = tint(m, C.deep), f = tint(m, C.parch), tx = Math.round((630 - m.width) / 2), ty = 500 - band + Math.round((band - m.height) / 2) + 2;
      x.drawImage(d, tx, ty + 2); x.drawImage(f, tx, ty);
      out.cover = c.toDataURL('image/png');
    }
    // background tile: dark planks, seamless
    {
      const w = wood(128, 4), [c, x] = K(512, 512); x.drawImage(w, 0, 0); x.fillStyle = 'rgba(10,4,1,.25)'; x.fillRect(0, 0, 512, 512);
      out.background = c.toDataURL('image/png');
    }
    // the pizza images, for the screenshots' menu
    out.sizes = { logo: out.logoSize };
    return out;
  });
  save('logo.png', art.logo); save('banner.png', art.banner); save('cover.png', art.cover); save('background.png', art.background);
  console.log('art done', art.sizes);

  // ---- screenshots of the real game (desktop size)
  await p.evaluate(() => {
    closeModal(); state = freshState(); Object.assign(state, { chef: 'Rui', shop: "Pizza d'Italia", seenIntro: true, money: 2350, day: 19, rep: 3.4, tier: 3, lastSales: {} });
    const mk = (dough, sauce, list) => { const pieces = [...spread('mozzarella', 12, .74, 0)]; list.forEach(([id, n], k) => pieces.push(...spread(id, n, .66 - .04 * (k % 3), k * 2 + 1))); return { dough, sauce, pieces } };
    const L = [['Margherita da Casa', 'napo', 'tomate', [['manjericao', 7]]], ['Pepperoni Picante', 'napo', 'tomate', [['pepperoni', 10], ['azeitonas', 5], ['oregaos', 4]]],
      ['Hawaii', 'napo', 'tomate', [['fiambre', 7], ['ananas', 8]]], ['Quattro Gusti', 'lenta', 'tomate', [['cogumelos', 6], ['fiambre', 5], ['pimento', 5], ['azeitonas', 5]]],
      ['Prosciutto e Rucola', 'lenta', 'pesto', [['presunto', 6], ['rucula', 8], ['parmesao', 5], ['tomate', 5]]]];
    state.menu = L.map(([name, d, s, l], i) => { const pz = { id: 'm' + i, name, ...mk(d, s, l), from: { c: 'Rui', s: "Pizza d'Italia" } }; pz.price = suggestPrice(analyze(pz)); state.lastSales[pz.id] = [31, 24, 17, 22, 12][i]; return pz });
    state.draft = { name: 'Quattro Gusti', ...mk('lenta', 'tomate', [['cogumelos', 6], ['fiambre', 5], ['pimento', 5], ['azeitonas', 5]]), editing: null };
    state.contestLog = [{ day: 15, theme: 'veg', pizza: 'Quattro Gusti', pos: 1, prize: 600 }, { day: 10, theme: 'classica', pizza: 'Margherita da Casa', pos: 2, prize: 250 }];
    state.sel = 'fiambre';
  });
  const shot = async (n, tab) => { await p.evaluate(t => { closeModal(); state.tab = t; render() }, tab); await p.waitForTimeout(1800); await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300); await p.screenshot({ path: path.join(OUT, `shot-${n}.png`) }) };
  await shot(1, 'cozinha');
  await p.evaluate(() => { state.tier = 3 }); await shot(2, 'menu');
  await p.evaluate(() => { state.tier = 1 });
  await p.evaluate(() => { closeModal(); state.tab = 'dia'; render() }); await p.waitForTimeout(1500);
  await p.click('[data-act=open]'); await p.waitForTimeout(500); await p.click('[data-act=speed][data-v="4"]').catch(() => {}); await p.waitForTimeout(6500);
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(OUT, 'shot-3.png') });
  await p.evaluate(() => { try { anim = null } catch (e) {} closeModal() });
  await shot(4, 'sala');
  await shot(5, 'concurso');
  await b.close(); console.log('done');
})();
