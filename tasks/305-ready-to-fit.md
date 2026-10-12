Status: open
# 305: Ready to fit - the owner clicks the points, the line does everything else
Depends on: 303
Touches: web/index.html, server/serve.py, tools/fit_queue.py, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
The owner's hand fits are the only fits that land right (automatic ones: 301, 302b). He likes doing them ("clicking
three points on the diagram and then clicking the points on the map ... certified cool"). So the line becomes:
agents prepare a site all the way to the clicks, the owner places the drawing on the page, and the line takes it to
the map. One site at a time: the page shows him the next site to fit, and when he saves, that site is finished.

## Acceptance criteria
- [ ] tools/fit_queue.py writes web/data/fit_queue.json: built sites with at least one candidate plan or bird's-eye
      picture (web/data/plans.json, the review items) and no hand fit yet, one entry per site with its best
      candidate first (a true plan over a view, a clear scan over a faint one; the reason in a word), ordered so that
      the sites most worth seeing come first (say how in docs/site_flow.md). Finder/Amazon data never enters it.
- [ ] The page: a "Ready to fit" entry (from the start view) opens the next site in the queue with its best
      candidate already loaded in the existing "Place an old plan" tool; skip moves to the next site. The existing
      tool's clicking is not changed.
- [ ] When the owner saves a fit, server/serve.py runs the one-site line (tools/site_done.py) for that site, so the
      drawing is on the map, the site's square is coloured and its review item is resolved without any other step;
      the saved document carries "by": "hand" (303). The queue moves on to the next site.
- [ ] Checked in a browser the way the owner uses it: open the queue, place a candidate on one site with real clicks,
      save, see it on the map (screenshots in docs/site_flow/). Revert that test fit afterwards: only the owner's
      fits are hand fits. tests/test_fit_queue.py covers the queue and the save -> line step without network.

## Notes
- The page runs on the owner's Mac (server/serve.py --lan, port 8642); keep it stdlib like the rest of serve.py.
- Do not touch fit/inkfit.py, fit/surveyfit.py or the 302/304 tasks (agent c).

## Hand-over

(2026-10-11, iteration 99, agent a - FIRST session on 305; investigation only, NO code written yet. 303, my
dependency, is done. The suite was green for my files at loop start except the 3 known failures listed in
PROGRESS.md, all in agent c's territory - I never ran it.)

**Next step, in order:** (1) READ tests/test_serve.py WHOLE before touching serve.py (I never read it; it owns
the document-store roundtrip and the "page data matches disk" tests - the worker change must not break it). (2)
Add `web/fitqueue.js` to this task's Touches line (a NEW file, the review.js pattern - the one path my task needs
beyond its current list). (3) Write tools/fit_queue.py + run it + commit web/data/fit_queue.json. (4) index.html:
one `<script src="fitqueue.js"></script>` after the review.js tag. (5) web/fitqueue.js. (6) serve.py worker.
(7) tests/test_fit_queue.py. (8) docs/site_flow.md section. The design below is settled in my head; re-derive
nothing without a reason.

**Queue definition (my reading of box 1, settle it this way).** Entry per site where ALL hold:
- built: id in web/data/sites.json AND web/data/sites/<id>/ is a dir (the tools/site_done.py `_site_built` rule);
- >=1 candidate picture: a web/data/plans.json row whose `sites` contains the id, OR a candidate of one of the
  site's data/review/ items (ALL item files, open AND resolved - read data/review/, NOT web/data/review.json:
  201's contract says the item files are the source of truth; review.json holds open items only). Dedup by plan id.
- no hand fit yet: NO doc in data/db/platefits/ for the site has `by: "hand"` (doc's `site` field, fallback: id
  prefix before the first dot). Agent docs do not disqualify.
- Finder/Amazon data never enters: fit_queue.py reads exactly those four inputs, nothing else.

**Ranking (document it in docs/site_flow.md, box 1's "say how").** Candidate "clarity" = drawing area in page px:
book row with map_box: (x2-x1)*size[0] * (y2-y1)*size[1]; book row without map_box or a commons row (map_box
None): the whole page/image area; item candidate with no resolvable row: 0. Best candidate of a site: is-plan
over is-view (the row's `view` field; an item candidate's `view` only if present), then draw area desc, then
stable (plan id). One-word `reason`: single candidate -> "the only candidate"; a plan chosen while a view exists
-> "a true plan"; a plan chosen among plans -> "the clearest scan"; a view winner -> "the clearest view".
Sites ordered by the same rule applied to each site's best candidate: plan-best first, then best draw area
desc, then site name - "most worth seeing" = the cleanest, most ink to click on.

**fit_queue.json shape** (committed; the page + tests read it):
`{"at": <iso utc>, "entries": [{"site", "name" (from sites.json, id fallback), "best": {"plan", "reason",
"row": <the 13 plans.json fields as a NAMED object - id,book,ia,file,title,label,size,map_box,sites,cite,url,view,ref
- resolved like web/review.js rvResolveRow: first plans.json row with r.id==plan && r.sites.includes(site);
else synthesize from the candidate's stored fields, sites:[site]}}, "candidates": [{"plan","title","book",
"view","draw_px"}, ... best first]}]}`. fit_queue.py is stdlib-only (no PIL - never opens images; sizes come
from the json files) so the owner's Mac runs it with any python; CLI `tools/fit_queue.py [--root DIR]`, atomic
write (indent=1, no trailing newline - the store's convention).

**Page (web/fitqueue.js, loaded AFTER review.js - it chains the wrappers review.js installed).** Home view (the
sites tab of renderList): a card injected as the NEXT SIBLING of the stats `<p class="fit">` that contains
"built in all" (same anchor review.js's rvPatchStats uses; do NOT touch the tabs row or the stats line's own text -
201's tests pin them). Card: "Ready to fit (N)" title, the next site's name, its best candidate (title · book)
with the one-word reason, two buttons: primary "Place the drawing" and "Skip" (+ a small reset link when the
session has skips; skipped is SESSION-ONLY memory, done is localStorage `aw.fitQueue.done` [site ids], self-healed
against the file on load - a site that left the file is dropped from done). Next site = first entry not in
done∪skipped. "Place the drawing" = the review.js rvStartFitAt recipe on the queue's own row: select(site.id) ->
setGround(site.lidar===false?'imagery':'relief', site) -> await loadDeps(site) -> startFit(site) -> openPlan(row)
(call the CURRENT global openPlan = review.js's wrapper; do NOT set RV.pending - the queue row is the owner's
clean slate; pre-placed machine pairs are the review flow's contract, not this one's). "Skip" adds to session
skipped, re-renders. All existing fit-tool clicking untouched. Hide the card when the file is missing/404 or has
no entries left; it must never break a page load (the page is served without the file too).

**serve.py (the save -> line step).** Current: after_write(coll) is called from api() on PUT AND DELETE (no kind
passed); if coll=="platefits" it sets _fit_wake; one worker thread drains it: `sys.path.insert(pipeline); import
plan_fit; plan_fit.main([])` in try/except BaseException -> print (the in-process choice is documented in its
docstring - subprocesses died silently twice, 2026-10-10). CHANGE: api() passes the method; after_write gets a
job: PUT -> ("line", site) where site = data.get("site") or doc_id.split(".")[0]; DELETE -> ("sweep",). Worker
drains a job list on each wake (two PUTs to different sites while busy must both run: keep a small list + lock,
event per enqueue as today). ("line", site) -> import site_done from tools/ (sys.path.insert(ROOT/tools)) and
call site_done.main([site]) - NO --working/--model-json: the fit step with model=None puts uncovered candidates
into the review item as "no model answer" and is network-free (the 303 dead-socket GUARD proves the whole line
never opens a socket); sync builds the hand doc with no fabrication check (303); entry colours the square;
review resolves the item and publishes web/data/review.json scoped to the site. ("sweep",) keeps the OLD
plan_fit.main([]) + its global prune (a deleted doc's overlay must still leave the map - no page UI deletes
platefits today, but the API exists and 303's DELETE contract stands). site_done.main(argv) returns an int
(0/1/2), it does not sys.exit when called as a function. CRITICAL - 303's test d
(tests/test_fit_provenance.py::test_page_save_stamps_hand) serves a temp tree with NO tools/ dir and asserts the
EXACT file set after PUTs: {server/serve.py, server/relief_tiles.py, server/aibox/clef_server.py, the two doc
store files}. In that tree my worker's `import site_done` must raise ModuleNotFoundError and be swallowed by the
same except-BaseException-and-print (no new files, worker survives, server keeps answering) - then test d stays
byte-green. Also: the PUT handler in api() today does data["by"]="hand" for platefits (303) - keep that; the doc
the page saves already carries `site`, so the job's site is right even without parsing the id.

**Tests (tests/test_fit_queue.py, hermetic, no network, ephemeral ports only).**
1. The generator on a temp tree (copy plans.json, sites.json, data/review/, data/db/platefits/ like
test_site_done/test_fit_provenance do): built+candidate+no-hand-fit sites exactly; a site whose only doc is
`by: hand` is OUT; agent docs do not exclude; candidates union of plans rows and item candidates deduped by plan;
best = plan over view, then draw area, reason phrase; site order as above; no Finder/Amazon file read (a temp
tree without data/scans.json etc. still works). Run tools/fit_queue.py as a subprocess with --root (or import
module directly - the 303 test loads site_done via importlib; either is fine).
2. serve.py: served-fixture tree (conftest `served`) + tools/ + fit/ + pipeline/ COPIED in (unlike 303's d tree,
mine needs the line to actually run): PUT a hand doc for a chosen site exactly as the page's saveFit builds it
(copy the doc-construction recipe from test_review.py::test_save_resolves_the_item - row fields + crop from
map_box*size + candidate pairs, `at` a fixed string) -> poll until the line's effects are in the tree:
doc `by: hand`; the site's depictions.json gained a plan/view entry with fit.at==at; sites.json drawings
incremented; the site's review item records resolved {doc, at} (write-once) and left web/data/review.json. Pick
the test site from the real queue so it has a resolvable row and an item (derive, don't hardcode, like 803 did -
the population moves under 203b/207). Guard against network with the 303 GUARD? The line's sync DOWNLOADS the
big picture (data/raw/ is not in the conftest copy -> load_picture 404s/fails) - so pick a site whose picture is
already cached... simpler: use a COMMONS candidate with url only if data/raw/commons/<site>/<h>.jpg was copied -
NO: conftest strips all of data/raw. The safe pick: a site whose doc's picture is not needed because... it IS
needed (build loads the picture). SOLUTION (settled): copy the ONE big picture the chosen doc needs into the
temp tree's data/raw/ (the file is in THIS checkout's data/raw/; one file copy, no network) - or point the doc's
url at nothing and accept the line prints a failure for OTHER docs while the test site's doc builds from its
copied picture. Before writing, check plan_fit.load_picture for a commons doc (reads data/raw/commons/<site>/
<hash>.jpg) and for a book doc (data/raw/books/<ia>/full/<file>) and copy exactly that one file. The line's fit
step (model=None) writes only item files (no network - proven by 303's dead-socket run of the same code path).
3. The page, headless (shot.mjs + CHROME=/opt/google/chrome/chrome + NODE_MODULES=/home/agent/tools/shot/
node_modules; _headless_or_skip pattern from test_review.py): boot, wait S.ready && queue loaded; assert the
card is in the home view with the file's first entry's site + best title + reason and the (N) count; click the
primary button -> P.active && P.site.id == entry.site && P.plan == entry.best's row (openPlan loaded the page -
it will 404 for the picture in the test tree, that's fine: the row/plan state is what's asserted, and the page
must stay error-free); back out, click Skip -> card shows the next entry; save flow: PUT the doc like test 2
via the page's own saveFit (drive real clicks? NO - the box says "real clicks" for the OWNER's browser check in
step 8, the automated test PUTs the doc through the store like 201/303 do - document this in the test docstring),
assert the card advanced.
4. Box 4's browser check (screenshots in docs/site_flow/) is the OWNER's Mac - I can do a headless version here:
real clicks via shot.mjs are not possible (no mouse); do the headless state checks instead, put the headless
screenshots in docs/site_flow/, and note in site_flow.md that the owner's Mac click-through is his acceptance
(the test fit is reverted in the temp trees only - nothing in THIS checkout's store ever gains a hand doc from a
test; the 303 golden sha256 must stay green - assert it in the test if convenient).

**docs/site_flow.md**: new section "Ready to fit (task 305)" after the Shotwick section: the queue's rule, the
ranking with the one-word reasons, the order, the page's card + skip/saved semantics, the save -> line wiring
(serve.py PUT -> tools/site_done.py for that site, DELETE keeps the sweep), and what the headless check shows.

**Facts gathered (so the next agent does not re-read):** serve.py L229-252 = _fit_wake/after_write/worker (the
worker imports plan_fit from pipeline/ and runs plan_fit.main([]) per wake; plan_fit.main([]) = build every doc
(skip when is_done) + self-heal stamps + global prune at the end). site_done.main(argv=None): argparse site /
--root (default its own checkout ROOT) / --working|--model-json; returns 2 not-built, 1 sync failure, 0 done;
step prints: fit/sync/entry/review + per-picture report + "done". page: index.html ONE inline script, review.js
script tag last; home renderList -> #body: .tabs(h-sites,h-finder,[#h-review]), p.fit stats line, .kinds, .search,
#entries, .about; review.js wraps renderList/setTabHome/openPlan/saveFit/loadDeps and injects #h-review +
#rvcount into that line; rvStartFitAt = select -> setGround(lidar?'relief':'imagery') -> loadDeps -> startFit ->
openPlan (its wrapper pre-places RV.pending pairs). openPlan(r) reads r.url||books/<ia>/<file>, r.map_box, r.view;
saveFit PUTs platefits/<site>.<plan> with doc {site,plan,ia,file,crop,model,src,url,ref,size,pairs,label,title,
book,cite,at} and polls data/sites/<id>/depictions.json for fit.at==at up to 60x1.5s. plans.json 1166 rows, cols
[id,book,ia,file,title,label,size,map_box,sites,cite,url,view,ref] (book: size=full page px, map_box fractions;
commons: size=image px, map_box null, url media/commons/<site>/<h>.jpg). data/db/platefits: 116 docs (21 hand,
95 agent; 94 auto). sites.json 385 built sites. review item files data/review/<site>[.lead].json: {site,
candidates[{plan,title,url,pairs,why,evidence,gate_score}], no_picture_found, resolved} - candidates may be SLIM
after 803 (rvResolveRow is the shape-tolerant reader). test fixtures: conftest `served` (temp copy of web/server/data
MINUS data/raw, --port 0); 303's GUARD (dead sockets) and _build_tree_b copy recipe; test_review.py's PROBE_LIST
[eval]-json probe + _headless_or_skip. batch_us.run_sites(root, ids, model=None): per candidate propose_for
(stdlib, local) -> model None -> "no model answer" upsert; a site with ALL candidates covered (doc or item entry)
skips the batch run entirely (site_done._fit logic). AGENT c is concurrently on 203b/207/302a/304 - do NOT touch
his files; his 203b merge may move the queue population, so the test derives its expectations, never pins
counts (803 precedent).
