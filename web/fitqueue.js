/* Ready to fit (task 305): the owner's hand fits are the ones that land right, so the line
   queues them - the built sites that still have a candidate picture and no hand fit yet,
   one site at a time, the most worth seeing first. tools/fit_queue.py publishes the queue
   to web/data/fit_queue.json: {"at", "entries": [{site, name, best: {plan, reason, row},
   candidates: [{plan, title, book, view, draw_px}]}]}; the page never writes it and
   tolerates it missing, stale or 404.

   index.html takes no queue footprint of its own, so this file loads after review.js and
   extends the page the same way review.js does - by reassigning the page's globals:

   - renderList: a "Ready to fit" card, drawn into #body as the next sibling of the home
     stats line (the "built in all" p) - the tabs row and that line's own text stay byte
     for byte (201 pins them). The card names the next site (the first entry not yet done
     and not skipped this session), its best candidate and the one-word reason it won,
     with a "Place the drawing" button and a Skip. No card when the file is missing or
     no site is left; a failed fetch never breaks a page load.
   - The card's buttons drive the existing fit tool in the fitkit convention:
     select(site) -> setGround(relief, or the aerial photograph where there is no LiDAR)
     -> loadDeps -> startFit(site) -> openPlan(row); row is the queue entry's best row
     (a plans.json row, or its documented synthesis). RV.pending is deliberately NOT set:
     the queue's row is the owner's clean slate - pre-placed machine pairs are the
     review flow's contract, not this one's.
   - saveFit: after the page's own save, if the doc landed and the site is in the queue,
     the site counts as done in this browser (localStorage aw.fitQueue.done) and the card
     moves on to the next site. The done map is self-healed against the file on load: a
     site that left the file (a hand fit saved from another window, or a regenerated
     queue) drops out. skipped is session-only, with a small reset in the card.
*/
const FQ = { entries: [], loaded: false, fetching: false, done: lsGet('aw.fitQueue.done', {}), skipped: [] };

async function fqLoad() {
  if (FQ.fetching || FQ.loaded) return;
  FQ.fetching = true;
  try {
    const r = await fetch('data/fit_queue.json');
    if (r.ok) {
      FQ.entries = ((await r.json()).entries) || [];
      // self-heal: a site that left the file has nothing left to do in this browser
      const ids = new Set(FQ.entries.map(e => e && e.site));
      FQ.done = Object.fromEntries(Object.entries(FQ.done).filter(([id]) => ids.has(id)));
    }
  } catch {}
  FQ.loaded = true; FQ.fetching = false;
  if (S.sites.length) fqPatch();
}

/* The queue entries this browser still has to fit, in the file's (most worth seeing
   first) order: not done in this browser, not skipped this session, and still a built
   site in this build (a stale file row names nothing: it never becomes "next"). */
function fqPending() {
  return FQ.entries.filter(e => e && e.site && S.byId[e.site] && !(e.site in FQ.done) && !FQ.skipped.includes(e.site));
}

/* The card, in place: the next sibling of the home stats line, or gone when nothing is left. */
function fqPatch() {
  const p = [...document.querySelectorAll('#body .fit')].find(el => el.textContent.includes('built in all'));
  let card = document.getElementById('fqcard');
  const e = fqPending()[0];
  if (!p || !e || !(e.best && e.best.row)) { if (card) card.remove(); return; }
  if (!card) {
    card = document.createElement('div');
    card.id = 'fqcard';
    p.insertAdjacentElement('afterend', card);
  }
  const row = e.best.row, n = fqPending().length;
  const mid = [row.book, row.label].filter(Boolean).join(' \u00B7 ');
  card.innerHTML = `
    <p class="group-title">Ready to fit <span>${n} to go</span></p>
    <p class="fq-site"><b>${esc(e.name || e.site)}</b></p>
    <p class="fit">${esc(row.title || row.id)}${mid ? ` <small>${esc(mid)}</small>` : ''} \u2014 ${esc(e.best.reason || '')}</p>
    <div class="tools">
      <button class="primary" id="fqplace">Place the drawing</button>
      <button id="fqskip">Skip</button>
      ${FQ.skipped.length ? `<button id="fqreset">Undo ${FQ.skipped.length} skip${FQ.skipped.length === 1 ? '' : 's'}</button>` : ''}
    </div>`;
  $('#fqplace').onclick = fqPlace;
  $('#fqskip').onclick = fqSkip;
  if ($('#fqreset')) $('#fqreset').onclick = fqReset;
}

async function fqPlace() {
  const e = fqPending()[0];
  const site = e && S.byId[e.site];
  if (!site) return;
  if (P.active) endFit(); // select() early-returns while a fit is active
  select(site.id);
  setGround(site.lidar === false ? 'imagery' : 'relief', site);
  await loadDeps(site); // let select()'s async re-render finish before the sheet renders
  startFit(site);
  await openPlan(e.best.row); // RV.pending stays null: the owner's clean slate
}

function fqSkip() {
  const e = fqPending()[0];
  if (e && !FQ.skipped.includes(e.site)) FQ.skipped.push(e.site);
  fqPatch();
}

function fqReset() {
  FQ.skipped = [];
  fqPatch();
}

/* ---- the wrappers: installed once, at load, after review.js has wrapped the originals.
   The _fq-prefixed names are the only free lexical slots: review.js's top-level consts
   (_renderList, _saveFit, ...) live in the page's global lexical scope and a second script
   may not redeclare them. ---- */
const _fqRenderList = renderList;
renderList = function () {
  _fqRenderList();
  if (!S.sites.length) return;
  if (FQ.loaded) fqPatch();
  else if (!FQ.fetching) fqLoad();
};

const _fqSaveFit = saveFit;
saveFit = async function () {
  const siteId = P.site && P.site.id;
  const planId = P.plan && P.plan.id;
  const out = await _fqSaveFit();
  if (siteId && planId && S.db && FQ.entries.some(e => e && e.site === siteId)) {
    try {
      const d = await S.db.doc(`platefits/${siteId}.${planId}`).get(); // a 200 means the owner's save landed
      if (d && d.exists) {
        FQ.done[siteId] = new Date().toISOString();
        lsSet('aw.fitQueue.done', FQ.done);
        fqPatch();
      }
    } catch {}
  }
  return out;
};

(() => {
  const st = document.createElement('style');
  st.id = 'fitqueue-style';
  st.textContent = [
    '#fqcard { margin: 10px 0; padding: 10px 12px; border: 1px solid var(--ink); background: var(--sheet); }',
    '#fqcard .group-title { margin: 0 0 8px; }',
    '#fqcard .fq-site { margin: 0 0 2px; font-size: 16.5px; }',
    '#fqcard .fit { margin: 0 0 8px; }',
    '#fqcard .tools { margin: 0; gap: 8px; }',
    '#fqcard .tools button { background: var(--sheet); border: 1px solid var(--rule); cursor: pointer; }',
    '#fqcard .tools button.primary { background: var(--ink); color: var(--sheet); border-color: var(--ink); }',
  ].join('\n');
  document.head.appendChild(st);
})();
