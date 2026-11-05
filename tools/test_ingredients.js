#!/usr/bin/env node
/* Pizza Magna: teste dos ingredientes no jogo, com o browser do Playwright.

   Uso: node tools/test_ingredients.js [ids separados por vírgulas] [pasta para a imagem]
   Sem ids, testa só a integridade de todos os ingredientes.

   Verifica:
   - erros na consola ao abrir o jogo e ao pôr peças;
   - cada ingrediente de ING tem sprite inteiro no atlas (ou _n se roda) e as 3 variantes picadas, se se pica;
   - ING.rot > 1 só onde há imagem _n no atlas, e vice-versa;
   - as traduções em inglês e português têm as mesmas chaves, e cada ingrediente e combo tem nome nas duas;
   - os combos só pedem ingredientes e molhos que existem;
   - para os ids dados: põe 2 peças de cada um na bancada, roda as que rodam,
     e mostra os combos ativados. Grava a bancada em <pasta>/bancada.png. */
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
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()) });
  await p.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await p.waitForTimeout(1500);

  const problems = await p.evaluate(() => {
    const P = [], F = ATLAS.frames, keys = o => Object.keys(o).sort().join('|');
    if (keys(I18N.en) !== keys(I18N.pt)) {
      const en = new Set(Object.keys(I18N.en)), pt = new Set(Object.keys(I18N.pt));
      P.push('traduções diferentes: só em en ' + [...en].filter(k => !pt.has(k)) + '; só em pt ' + [...pt].filter(k => !en.has(k)));
    }
    for (const id in ING) {
      const v = ING[id];
      if (!I18N.en['ing.' + id] || !I18N.pt['ing.' + id]) P.push(id + ': falta ing.' + id + ' nas traduções');
      if (!F[id + '_n'] && !F[id + '_0']) P.push(id + ': sem sprite inteiro no atlas');
      if ((v.rot || 1) > 1 && !F[id + '_n']) P.push(id + ': rot ' + v.rot + ' mas sem ' + id + '_n no atlas');
      if (F[id + '_n'] && !((v.rot || 1) > 1)) P.push(id + ': tem ' + id + '_n no atlas mas não tem rot');
      if (F[id + '_g0'] && !(F[id + '_g1'] && F[id + '_g2'])) P.push(id + ': picado incompleto');
      if (!PACKS[v.pack] && v.pack !== 'base') P.push(id + ': pack desconhecido ' + v.pack);
    }
    for (const c of COMBOS) {
      if (!I18N.en['combo.' + c.id] || !I18N.pt['combo.' + c.id]) P.push('combo ' + c.id + ': falta o nome nas traduções');
      if (c.quote && !(I18N.en['quote.' + c.id] && I18N.pt['quote.' + c.id])) P.push('combo ' + c.id + ': falta a frase nas traduções');
      for (const r of c.req) if (r.startsWith('s:') ? !SAUCES[r.slice(2)] : !ING[r]) P.push('combo ' + c.id + ': pede ' + r + ', que não existe');
    }
    return P;
  });

  const report = {ingredientes: 0, combos: 0, problemas: problems};
  if (ids.length) {
    const unknown = await p.evaluate(ids => ids.filter(i => !ING[i]), ids);
    if (unknown.length) report.problemas.push('ids desconhecidos: ' + unknown);
    await p.evaluate(() => { closeModal(); state.unlocked = ['base', 'local', 'gourmet']; state.draft.pieces = []; state.draft.sauce = 'tomate'; render() });
    await p.waitForTimeout(300);
    const bb = await (await p.$('#pz')).boundingBox();
    const L = (x, y) => [bb.x + x / 320 * bb.width, bb.y + y / 200 * bb.height];
    // pontos dentro da área permitida (raio 0.8 da pizza, centro em 97,100)
    const spots = []; for (let k = 0; k < 40; k++) { const a = k * 2.39996, r = 62 * Math.sqrt((k + .5) / 40); spots.push([97 + Math.cos(a) * r, 100 + Math.sin(a) * r]) }
    let si = 0;
    const rotated = {};
    for (const id of ids.filter(i => !unknown.includes(i))) {
      await p.click(`[data-act="ing"][data-v="${id}"]`);
      let [x, y] = L(256, 50); await p.mouse.click(x, y);                       // taça "inteiro"
      for (let k = 0; k < 2; k++) { [x, y] = L(...spots[si++ % spots.length]); await p.mouse.click(x, y) }
      const canRot = await p.evaluate(id => canRotate(id), id);
      const btnHidden = await p.$eval('[data-act="rotate"]', e => e.hidden);
      if (canRot === btnHidden) report.problemas.push(id + ': o botão Rodar devia estar ' + (canRot ? 'visível' : 'escondido'));
      if (canRot) { await p.click('[data-act="rotate"]'); rotated[id] = await p.evaluate(() => state.draft.pieces.at(-1).a) }
    }
    const a = await p.evaluate(() => { const a = analyze(state.draft); return {q: a.q, combos: a.combos, pecas: state.draft.pieces.length} });
    Object.assign(report, {pecas: a.pecas, qualidade: a.q, combos_ativos: a.combos, rodados: rotated});
    await (await p.$('#pz')).screenshot({path: path.join(out, 'bancada.png')});
    report.imagem = path.resolve(out, 'bancada.png');
  }
  Object.assign(report, await p.evaluate(() => ({ingredientes: Object.keys(ING).length, combos: COMBOS.length})));
  report.erros_consola = errs;
  console.log(JSON.stringify(report, null, 1));
  await b.close();
  process.exit(report.problemas.length || errs.length ? 1 : 0);
})();
