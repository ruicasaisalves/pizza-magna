/* Makes the images for the game's itch.io page, from the game's own art, fonts and colours.
   Run from the repo root:  node itch/make_media.js
   Output (next to this file): logo.png (transparent), banner.png, cover.png, background.png (seamless tile),
   shot-1..5.png (screenshots), cover.gif (the animated cover: the dining room at lunchtime, made with Python and Pillow). Needs Playwright (preinstalled in the cloud sessions) and internet for the fonts. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = __dirname, GAME = 'file://' + path.resolve(__dirname, '../index.html');
const save = (name, url) => fs.writeFileSync(path.join(OUT, name), Buffer.from(url.split(',')[1], 'base64'));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(GAME); await p.waitForTimeout(1500);
  await p.addScriptTag({ path: path.join(__dirname, 'art.js') });

  // ---- the art, drawn inside the game page (its fonts, sprites and palette)
  const art = await p.evaluate(async () => {
    await document.fonts.load('bold 16px Silkscreen'); await document.fonts.ready;
    const { C, K, rng, mask, tint, up, title, wood, tile, vignette } = PMArt;

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
  // ---- the animated cover (630 x 500): the title, the real dining room at lunchtime, the red band
  await p.evaluate(() => { anim = null; closeModal(); Object.assign(state, { tier: 1, rep: 4.2, cooks: 3, ovens: 2, day: 6 });
    state.room.items.push({ id: 'xadrez2', c: 1, r: 11 }, { id: 'xadrez2', c: 6, r: 11 }, { id: 'vaso', c: 12, r: 3 }, { id: 'vaso', c: 0, r: 13 });
    state.tab = 'dia'; render(); window.scrollTo(0, 0) });
  await p.waitForTimeout(1500);
  await p.click('[data-act=open]'); await p.waitForTimeout(10500);                         // into the lunch rush
  const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'pm-gif-')), N = 56, STEP = 110;
  for (let i = 0; i < N; i++) {
    const url = await p.evaluate(() => {
      const A = PMArt, R = room; if (!R) return null;
      const [c, x] = A.K(630, 500); x.drawImage(A.tile(630, 500, A.wood()), 0, 0); A.vignette(x, 630, 500, .6);
      const t0 = A.title(['PIZZA MAGNA'], 'bold 20px Silkscreen'), T_ = A.up(t0, Math.max(1, Math.floor(600 / t0.width))); x.drawImage(T_, Math.round((630 - T_.width) / 2), Math.round((92 - T_.height) / 2) + 2);
      const fy = 92, fh = 352;                                                              // the room in a wooden frame with a brass edge
      x.fillStyle = A.C.brass; x.fillRect(4, fy, 622, fh); x.fillStyle = A.C.deep; x.fillRect(8, fy + 4, 614, fh - 8);
      x.drawImage(R.low, 13, 120, 610, fh - 12, 10, fy + 6, 610, fh - 12);
      const band = 52; x.fillStyle = A.C.tlo; x.fillRect(0, 500 - band - 4, 630, band + 4); x.fillStyle = A.C.tomato; x.fillRect(0, 500 - band, 630, band); x.fillStyle = A.C.brass; x.fillRect(0, 500 - band - 4, 630, 4);
      const m = A.up(A.mask('PIZZERIA TYCOON · 90s PIXEL ART', 'bold 8px Silkscreen'), 2), tx = Math.round((630 - m.width) / 2), ty = 500 - band + Math.round((band - m.height) / 2) + 2;
      x.drawImage(A.tint(m, A.C.deep), tx, ty + 2); x.drawImage(A.tint(m, A.C.parch), tx, ty);
      return c.toDataURL('image/png');
    });
    if (url) fs.writeFileSync(path.join(tmp, `f${String(i).padStart(3, '0')}.png`), Buffer.from(url.split(',')[1], 'base64'));
    await p.waitForTimeout(STEP);
  }
  // one shared palette for every frame (no flicker), no dithering (crisp pixels)
  require('child_process').execFileSync('python3', ['-c', `
import glob, sys
from PIL import Image
fs = sorted(glob.glob(sys.argv[1] + '/f*.png')); ims = [Image.open(f).convert('RGB') for f in fs]
strip = Image.new('RGB', (630, 500 * 4)); [strip.paste(ims[k * len(ims) // 4], (0, 500 * k)) for k in range(4)]
pal = strip.quantize(colors=160, method=Image.Quantize.MEDIANCUT)
q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
q[0].save(sys.argv[2], save_all=True, append_images=q[1:], duration=${STEP}, loop=0, optimize=True, disposal=1)
`, tmp, path.join(OUT, 'cover.gif')], { stdio: 'inherit' });
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log('cover.gif', Math.round(fs.statSync(path.join(OUT, 'cover.gif')).size / 1024), 'KB');
  await b.close(); console.log('done');
})();
