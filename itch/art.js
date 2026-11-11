/* Drawing helpers shared by itch/make_media.js and youtube/make_short.js. Loaded into the game page
   (p.addScriptTag), so they use its fonts and canvas. window.PMArt = { C, K, rng, mask, tint, up, title, wood, tile, vignette }. */
(() => {
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

  window.PMArt = { C, K, rng, mask, tint, up, title, wood, tile, vignette };
})();
