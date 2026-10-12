/* Review queue (task 201): the fits the machine could not place, and the sites with no
   picture at all - the human's drag is the last word. The item contract is
   data/review/README.md; fit/review.py's export publishes the open list to
   web/data/review.json, which this file reads.

   index.html takes no review footprint of its own, so this file loads after the page's
   one inline script and extends it by reassigning that script's globals:

   - renderList / setTabHome: a Review tab in the home view, drawn into #body like the
     Finder tab. Session-only on purpose: there is no #review hash route, and 'review'
     is never written to the aw.tab value index.html restores at boot, so a returning
     visitor still lands on the site list.
   - openPlan: once the picture loads, pre-place the item's proposed pairs (push, then
     addPairMarker, then refit - the map-click order, so the markers number 1..n).
     If the picture 404s the pre-placement is skipped silently; the list, count and
     stats line are all still served.
   - saveFit: after the existing save (PUT platefits/<site>.<plan>), if the doc exists
     and the saved plan is one of the item's candidates, the item counts as resolved
     in this browser (localStorage) and leaves the list. The page never writes
     data/review/: the durable record is the doc plus the item's `resolved` field,
     which the next export (212) catches up.
   - loadDeps: one fetch per site even when select() and this opener both ask, so
     select()'s async re-render lands before the fit sheet renders instead of
     clobbering it.

   Opening an item runs the existing fit tool in the fitkit convention:
   select(site) -> setGround(relief, or the aerial photograph where there is no LiDAR)
   -> startFit(site) -> openPlan(row); row is the plans.json row for (plan, site) -
   keyed by (id, sites[0]) in index.html, so the two pictures that depict two sites
   each open their own copy - or a synthesized one from the candidate's stored fields
   when the row is not there yet.
*/
const RV = { items: [], seen: lsGet('aw.reviewResolved', {}), loaded: false, fetching: false, pending: null };

function rvOpen() { return RV.items.filter(it => !RV.seen[it.site]); }

function rvTabLabel() {
  if (!RV.loaded) return 'Review';
  const n = rvOpen().length;
  return n ? `Review (${n})` : 'Review';
}

async function rvLoad() {
  if (RV.fetching || RV.loaded) return;
  RV.fetching = true;
  let items = [];
  try {
    const r = await fetch('data/review.json');
    if (r.ok) items = ((await r.json()).items) || [];
  } catch {}
  RV.loaded = true; RV.fetching = false;
  RV.items = items.filter(it => it.site && !RV.seen[it.site]);
  if (S.sites.length) {
    if (S.tab === 'review') rvRender();
    else { rvPatchTabs(); rvPatchStats(); }
  }
}

/* The home view keeps its own two tabs; the Review tab is added after them, spanning
   the row so the 1fr-1fr grid (and every other style) stays the page's own. */
function rvPatchTabs() {
  const tabs = $('#body .tabs');
  if (!tabs || $('#h-review')) return;
  const b = document.createElement('button');
  b.id = 'h-review';
  b.setAttribute('aria-pressed', 'false');
  b.textContent = rvTabLabel();
  b.onclick = () => setTabHome('review');
  tabs.appendChild(b);
}

/* The existing stats line, byte for byte, with a computed clause appended at the end. */
function rvPatchStats() {
  const p = [...document.querySelectorAll('#body .fit')].find(el => /built in all|laid on today/.test(el.textContent));
  if (!p || !RV.loaded) return;
  const n = rvOpen().length;
  let b = p.querySelector('#rvcount');
  if (!n) { if (b) b.remove(); return; }
  if (!b) {
    const nb = document.createElement('button');
    nb.id = 'rvcount';
    nb.onclick = () => setTabHome('review');
    p.appendChild(nb);
    b = nb;
  }
  b.textContent = `\u00A0\u00B7 ${n} review item${n === 1 ? '' : 's'} open`;
}

function rvItemHtml(it) {
  const cands = it.candidates || [];
  const head = cands.length ? `${cands.length} candidate picture${cands.length === 1 ? '' : 's'}` : 'no picture found';
  const nppf = it.no_picture_found;
  return `
  <p class="group-title"><button class="rv-site" data-item="${esc(it.site)}">${esc(it.name || it.site)}</button><span>${esc(head)}</span></p>
  ${cands.length ? `
  <ul class="plans">${cands.map(c => `
    <li><button data-item="${esc(it.site)}" data-cand="${esc(c.plan)}">${esc(c.title || c.plan)}<small>${esc([c.book, c.label].filter(Boolean).join(' \u00B7 '))}</small>${c.place_reason ? `<small>${esc(c.place_reason)}</small>` : ''}</button></li>`).join('')}
  </ul>` : `
  <p class="fit"><span class="chip missed">No picture found</span>&nbsp; ${esc(nppf ? nppf.searched : 'nothing has been searched yet')}</p>
  <button class="back rv-open" data-item="${esc(it.site)}">Open this site's plan search</button>`}`;
}

function rvRender() {
  const open = rvOpen();
  $('#body').innerHTML = `
    <div class="tabs" role="group" aria-label="Section">
      <button id="h-sites" aria-pressed="false">Sites</button>
      <button id="h-finder" aria-pressed="false">Finder</button>
      <button id="h-review" aria-pressed="true">${esc(rvTabLabel())}</button>
    </div>
    <p class="lede">Fits the machine could not place, and sites with no picture at all. Open one, put its points on today's ground, and save: your drag is the last word. Saved items leave the list.</p>
    ${open.length ? open.map(rvItemHtml).join('') : '<p class="status">Nothing left to review.</p>'}`;
  $('#h-sites').onclick = () => setTabHome('sites');
  $('#h-finder').onclick = () => setTabHome('finder');
  $('#body').querySelectorAll('[data-cand]').forEach(b => b.onclick = () => rvPick(b.dataset.item, b.dataset.cand));
  $('#body').querySelectorAll('.rv-site, .rv-open').forEach(b => b.onclick = () => rvOpenItem(b.dataset.item));
}

function rvResolveRow(siteId, c) {
  const row = P.rows.find(r => r.id === c.plan && (r.sites || []).includes(siteId));
  if (row) return row;
  // The row is not in this build's plans.json yet (a later task stages the picture and
  // adds the row): synthesize it from what the candidate stored, so the fit tool still
  // works. A missing map_box means the whole page loads and the human re-crops.
  return {
    id: c.plan, title: c.title || c.plan, url: c.url || null,
    ia: c.ia || null, file: c.file || null, book: c.book || null, label: c.label || null,
    cite: c.cite || null, ref: c.ref || null, map_box: c.map_box || null, view: c.view || false,
    sites: [siteId],
  };
}

async function rvStartFitAt(it, c) {
  const site = S.byId[it.site];
  if (!site) return;
  if (P.active) endFit(); // select() early-returns while a fit is active
  select(site.id); // forces the aerial photograph; the next line restores the fitkit ground
  setGround(site.lidar === false ? 'imagery' : 'relief', site);
  await loadDeps(site); // let select()'s async re-render finish before the sheet renders
  startFit(site);
  if (!c) return; // no picture: the plan search (including all the books) is the point
  RV.pending = (c.pairs || []).filter(p => Array.isArray(p) && p.length === 4)
    .map(p => ({ u: +p[0], v: +p[1], lon: +p[2], lat: +p[3] }));
  openPlan(rvResolveRow(site.id, c));
}

function rvPick(siteId, planId) {
  const it = RV.items.find(x => x.site === siteId);
  const c = it && (it.candidates || []).find(x => x.plan === planId);
  if (it && c) rvStartFitAt(it, c);
}

function rvOpenItem(siteId) {
  const it = RV.items.find(x => x.site === siteId);
  if (it) rvStartFitAt(it, (it.candidates || [])[0] || null);
}

function rvResolved(siteId, planId) {
  const it = RV.items.find(x => x.site === siteId);
  if (!it) return;
  if (!(it.candidates || []).some(c => c.plan === planId)) return; // export derives resolution the same way: any candidate's doc
  RV.seen[siteId] = { doc: siteId + '.' + planId, at: new Date().toISOString() };
  lsSet('aw.reviewResolved', RV.seen);
  RV.items.splice(RV.items.indexOf(it), 1);
}

/* ---- the wrappers: installed once, at load, after the page's script has defined the originals ---- */
const _renderList = renderList;
renderList = function () {
  _renderList();
  if (!S.sites.length) return;
  if (S.tab === 'review') rvRender();
  else { rvPatchTabs(); rvPatchStats(); }
  if (!RV.loaded) rvLoad();
};
const _setTabHome = setTabHome;
setTabHome = function (t) {
  if (t === 'review') {
    S.tab = 'review'; // session-only: aw.tab is not written, so a reload lands on the site list
    try { history.replaceState(null, '', location.pathname); } catch {}
    renderList();
    return;
  }
  _setTabHome(t);
};
const _openPlan = openPlan;
openPlan = async function (r) {
  const out = await _openPlan(r);
  if (RV.pending) {
    if (P.img) {
      for (const p of RV.pending) { P.pairs.push(p); addPairMarker(p); } // push first, like the map-click path: markers number 1..n
      refit();
    }
    RV.pending = null;
  }
  return out;
};
const _saveFit = saveFit;
saveFit = async function () {
  const siteId = P.site && P.site.id;
  const planId = P.plan && P.plan.id;
  const out = await _saveFit();
  if (siteId && planId && S.db) {
    try {
      const d = await S.db.doc(`platefits/${siteId}.${planId}`).get(); // a 200 means the human's save landed; both overlay-found and overlay-timeout paths reach here
      if (d && d.exists) rvResolved(siteId, planId);
    } catch {}
  }
  return out;
};
const _loadDeps = loadDeps;
const rvDepFlight = {};
loadDeps = function (s) {
  if (S.dep[s.id]) return Promise.resolve(S.dep[s.id]);
  if (!rvDepFlight[s.id]) rvDepFlight[s.id] = _loadDeps(s);
  return rvDepFlight[s.id];
};

(() => {
  const st = document.createElement('style');
  st.id = 'review-style';
  st.textContent = [
    '#h-review { grid-column: 1 / -1; border-left: 0; border-top: 1px solid var(--ink); }',
    '#rvcount { background: none; border: 0; padding: 0; margin-left: 2px; font: inherit; color: var(--survey); cursor: pointer; }',
    '#rvcount:hover { text-decoration: underline; }',
    '.rv-site { background: none; border: 0; padding: 0; cursor: pointer; color: inherit; font: inherit; letter-spacing: inherit; text-transform: inherit; }',
    '.rv-site:hover { color: var(--survey); }',
  ].join('\n');
  document.head.appendChild(st);
})();
