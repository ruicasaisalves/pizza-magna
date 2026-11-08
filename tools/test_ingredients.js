#!/usr/bin/env node
/* Pizza Magna: tests the toppings in the game, with Playwright's browser.

   Usage: node tools/test_ingredients.js [comma-separated ids] [folder for the image]
   Without ids, it only checks the integrity of every topping.

   Checks:
   - console errors when opening the game and placing pieces;
   - every topping in ING has a whole sprite in the atlas (or _n if it rotates) and the 3 chopped variants, if it is chopped;
   - ING.rot > 1 only where the atlas has an _n image, and vice versa;
   - the English and Portuguese translations have the same keys, and every topping and combo is named in both;
   - combos only ask for toppings and sauces that exist;
   - every topping has a weight in GRAMS;
   - for the given ids: places 2 pieces of each on the bench, turns the next piece of those that rotate (placed ones must not turn),
     and lists the combos triggered. Saves the bench to <folder>/bench.png. */
const {chromium} = require('playwright');
const path = require('path');

(async () => {
  const ids = (process.argv[2] || '').split(',').map(s => s.trim()).filter(Boolean);
  const out = process.argv[3] || '.';
  const b = await chromium.launch();
  const ctx = await b.newContext({viewport: {width: 1280, height: 900}, locale: 'pt-PT'});
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error' && !/net::ERR_/.test(m.text())) errs.push(m.text()) });   // network failures (e.g. analytics blocked offline) aren't game errors
  await p.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await p.waitForTimeout(1500);

  const problems = await p.evaluate(() => {
    const P = [], F = ATLAS.frames, keys = o => Object.keys(o).sort().join('|');
    if (keys(I18N.en) !== keys(I18N.pt)) {
      const en = new Set(Object.keys(I18N.en)), pt = new Set(Object.keys(I18N.pt));
      P.push('translations differ: only in en ' + [...en].filter(k => !pt.has(k)) + '; only in pt ' + [...pt].filter(k => !en.has(k)));
    }
    for (const id in ING) {
      const v = ING[id];
      if (!I18N.en['ing.' + id] || !I18N.pt['ing.' + id]) P.push(id + ': ing.' + id + ' missing from the translations');
      if (!F[id + '_n'] && !F[id + '_0']) P.push(id + ': no whole sprite in the atlas');
      if ((v.rot || 1) > 1 && !F[id + '_n']) P.push(id + ': rot ' + v.rot + ' but no ' + id + '_n in the atlas');
      if (F[id + '_n'] && !((v.rot || 1) > 1)) P.push(id + ': has ' + id + '_n in the atlas but no rot');
      if (F[id + '_g0'] && !(F[id + '_g1'] && F[id + '_g2'])) P.push(id + ': chopped variants incomplete');
      if (!PACKS[v.pack] && v.pack !== 'base') P.push(id + ': unknown pack ' + v.pack);
    }
    for (const c of COMBOS) {
      if (!I18N.en['combo.' + c.id] || !I18N.pt['combo.' + c.id]) P.push('combo ' + c.id + ': name missing from the translations');
      if (c.quote && !(I18N.en['quote.' + c.id] && I18N.pt['quote.' + c.id])) P.push('combo ' + c.id + ': quote missing from the translations');
      for (const r of c.req) if (r.startsWith('s:') ? !SAUCES[r.slice(2)] : !ING[r]) P.push('combo ' + c.id + ': asks for ' + r + ', which does not exist');
    }
    return P;
  });

  const report = {toppings: 0, combos: 0, problems};
  if (ids.length) {
    const unknown = await p.evaluate(ids => ids.filter(i => !ING[i]), ids);
    if (unknown.length) report.problems.push('unknown ids: ' + unknown);
    const noWeight = await p.evaluate(() => Object.keys(ING).filter(i => !(i in GRAMS)));
    if (noWeight.length) report.problems.push('no weight in GRAMS: ' + noWeight);
    await p.evaluate(() => { closeModal(); state.unlocked = ['base', 'local', 'gourmet']; state.draft.pieces = []; state.draft.sauce = 'tomate'; state.zoom = false; render() });
    await p.waitForTimeout(300);
    const G = await p.evaluate(() => ({BW, BH, PCX, PCY, OY}));   // bench geometry (it has the title strip on top)
    const bb = await (await p.$('#pz')).boundingBox();
    const L = (x, y) => [bb.x + x / G.BW * bb.width, bb.y + y / G.BH * bb.height];
    // spots inside the allowed area (radius 0.8 of the pizza, around the centre)
    const N = Math.max(8, ids.length * 2), spots = [];       // spread over the whole disc, depending on the number of pieces
    for (let k = 0; k < N; k++) { const a = k * 2.39996, r = 62 * Math.sqrt((k + .5) / N); spots.push([G.PCX + Math.cos(a) * r, G.PCY + Math.sin(a) * r]) }
    let si = 0;
    const rotated = {};
    for (const id of ids.filter(i => !unknown.includes(i))) {
      await p.evaluate(id => { state.cat = ingCat(id); const pe = $('.pantry'); pe.innerHTML = pantryHTML(); drawIngIcons() }, id);   // open the topping's tab
      await p.click(`[data-act="ing"][data-v="${id}"]`);
      let [x, y] = L(256, 50 + G.OY); await p.mouse.click(x, y);                       // "whole" bowl
      for (let k = 0; k < 2; k++) { [x, y] = L(...spots[si++ % spots.length]); await p.mouse.click(x, y) }
      const canRot = await p.evaluate(id => canRotate(id), id);
      const btnHidden = await p.$eval('[data-act="rotate"]', e => e.hidden);
      if (canRot === btnHidden) report.problems.push(id + ': the Rotate button should be ' + (canRot ? 'visible' : 'hidden'));
      if (canRot) {   // Rotate turns the next piece only: the last one put down must stay as it was
        const before = await p.evaluate(() => state.draft.pieces.at(-1).a);
        await p.click('[data-act="rotate"]');
        const [after, next] = await p.evaluate(id => [state.draft.pieces.at(-1).a, curAng()], id);
        if (after !== before) report.problems.push(id + ': Rotate turned a piece already on the pizza');
        rotated[id] = next;
      }
    }
    const a = await p.evaluate(() => { const a = analyze(state.draft); return {q: a.q, combos: a.combos, pieces: state.draft.pieces.length} });
    Object.assign(report, {pieces: a.pieces, quality: a.q, active_combos: a.combos, rotated});
    await (await p.$('#pz')).screenshot({path: path.join(out, 'bench.png')});
    report.image = path.resolve(out, 'bench.png');
  }
  Object.assign(report, await p.evaluate(() => ({toppings: Object.keys(ING).length, combos: COMBOS.length})));
  report.console_errors = errs;
  console.log(JSON.stringify(report, null, 1));
  await b.close();
  process.exit(report.problems.length || errs.length ? 1 : 0);
})();
