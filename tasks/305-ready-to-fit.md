Status: open
# 305: Ready to fit - the owner clicks the points, the line does everything else
Depends on: 303
Touches: web/index.html, web/fitqueue.js, server/serve.py, tools/fit_queue.py, web/data/fit_queue.json, tests/test_fit_queue.py, docs/site_flow.md

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

(2026-10-12, iteration 101, agent a - steps 2+3 of the plan done: the page card. test_serve.py was
read whole this session; the earlier hand-over's "test d" in it turned out to be a stale
description - see DECISIONS.)

**Done this session:** (1) READ tests/test_serve.py WHOLE (81 lines, 5 tests - page loads, sites
data >=384, golden hand fits, platefits docs match built sites, and a PUT/GET/DELETE roundtrip on
the SCRATCH collection "awtest" - never platefits, so the worker is not involved at all; the
exact file-set assertion that constrains the worker lives in
test_review.py::test_save_resolves_the_item: after the PUT, exactly one new platefits doc and
nothing else, with the worker dying on the pipeline/ import in that tools/-less tree - the server
stays up). (2) NEW `web/fitqueue.js` (loaded after review.js; the index.html L1708 script tag
added): `FQ` state {entries, loaded, fetching, done = localStorage `aw.fitQueue.done` (self-healed
against the file on load: a site that left the file drops out), skipped = session-only};
`fqPending()` = queue entries whose site is built in this build (S.byId), not done, not skipped;
the card renders as the NEXT SIBLING of the home "built in all" stats `p` (home sites view only -
the anchor is absent in the finder/review views, which also wipe the card with `#body.innerHTML`):
`.group-title` "Ready to fit" + span "N to go" (N = fqPending), `.fq-site` name, a `.fit`
candidate line (title · book · label — one-word reason), tools row [Place the drawing (primary),
Skip, Undo N skips]. Place = endFit-if-active -> select(site.id) -> setGround(site.lidar===false ?
'imagery' : 'relief', site) -> await loadDeps(site) -> startFit(site) -> await openPlan(entry.best.row);
RV.pending is NEVER set (the queue's row is the owner's clean slate; pre-placed machine pairs are
the review flow's contract). Wrappers chain review.js's: `_fqRenderList` (fqPatch when FQ.loaded,
else kick fqLoad, which fqPatches on completion) and `_fqSaveFit` (after the original, incl. the
review wrapper: a landed doc for a queued site -> FQ.done[siteId]=now, lsSet, fqPatch). Style
block #fitqueue-style (the card's .tools buttons get explicit border/background: the page's
.tools button rule is unstyled outside the fit pane). Two browser-only bugs found in the headless
smoke and fixed: redeclaring review.js's top-level consts `_renderList`/`_saveFit` (a page-wide
lexical-scope clash that makes Chrome reject the whole script - new PITFALLS.md `### web/`
section) and reassigning a const inside fqPatch.

**Verified headless this session** (shot.mjs on a conftest-style temp tree, real DOM button
clicks): card "Ready to fit 117 to go" / Devil's Dyke / "The Devil's Dyke Camp, near Brighton ·
Allcroft 1908 · Fig. 217 — the clearest scan"; Place -> P.active, P.site.id=devil-s-dyke-q3307343,
P.plan.id=earthworkenglan01allcgoog_n0686_1, S.ground='relief', fit pane open, #fitname header
correct (the page image 404s in the temp tree - openPlan sets its hint and keeps the row; assert
row state, not pixels); back to the sites tab -> card still on the same site; Skip -> Fort
Ancient, "116 to go", reset link appears; Undo -> back to Devil's Dyke, 117. No [pageerror], no
[reqfail]; a plain boot adds only the usual 200s (fit_queue.json is committed and answers 200 -
test_review's n404==2 stays green; the book-image 404 appears only after an openPlan). Full suite
after the change: 70 passed, 1 skipped - unchanged from loop start.

**Next step, in order:** (1) THE serve.py WORKER (design settled in the iteration-99/100
hand-overs, unchanged, now confirmed against test_serve.py): api() passes the method to
after_write; PUT platefits -> job ("line", site), site = data.get("site") or doc_id.split(".")[0];
DELETE -> ("sweep",). The worker drains a small job list on each wake (list + lock; one event per
enqueue - two PUTs to different sites while it is busy must both run). ("line", site) ->
sys.path.insert the tools/ dir, import site_done, call site_done.main([site]) IN-PROCESS, NO
--working/--model-json: model=None makes the fit step write only item files (network-free - 303's
dead-socket run proved it), uncovered candidates go to the review item as "no model answer", it
builds the hand doc with no fabrication check, refreshes the site's drawings count (the square
colour) and resolves the item scoped to the site. ("sweep",) keeps the OLD plan_fit.main([]) + its
global prune (a deleted doc's overlay must still leave the map). An import failure (no tools/ in
the tree: the conftest `served` fixture and 303's d-tree) must be swallowed by the existing
except-BaseException-and-print and create no files - test_review's snapshot assertion depends on
it. Keep the PUT handler's existing data["by"]="hand" stamp (303). The current worker
(after_write/_fit_wake, ~L229-252) runs plan_fit.main([]) for both PUT and DELETE - that is what
changes; the by:hand stamp and the API shape stay. site_done.main(argv) returns an int (0/1/2)
and never sys.exits when called as a function.
(2) tests/test_fit_queue.py part 2 (the iteration-100 plan, still valid): a served-style temp tree
PLUS tools/ + fit/ + pipeline/ copied in (unlike 303's d-tree, mine needs the line to actually
run); PUT a hand doc exactly as the page's saveFit builds it (recipe from
test_review.py::test_save_resolves_the_item: row fields + crop from map_box x size + candidate
pairs, `at` a fixed string) for a site DERIVED (not hardcoded) from the real queue so it has a
resolvable row and a picture that exists in THIS checkout's data/raw/ - check
plan_fit.load_picture (L203-222) first for the exact path per source (commons:
data/raw/commons/<site>/<hash>.jpg; book: data/raw/books/<ia>/full/<file>) and copy that ONE file
into the temp tree; then poll until the line's effects are in the tree: the doc by:hand; the
site's depictions.json gained an entry with fit.at == at; sites.json drawings incremented; the
item's resolved {doc, at} (write-once). The fit step (model=None) writes only item files - no
network (dead-socket guard, 303's pattern). Then the headless card test (shot.mjs +
CHROME=/opt/google/chrome/chrome + NODE_PATH=/home/agent/tools/shot/node_modules; the
_headless_or_skip pattern from test_review.py): boot, wait S.ready and FQ.loaded; assert the card
(first entry's site + best title + reason + the "N to go" count); DOM-click Place -> P.active &&
P.site.id == entry.site && P.plan.id == entry.best.plan; back out; DOM-click Skip -> the card
advances to entry 2; the save flow PUTs through the page's own saveFit (a real mouse click on the
owner's Mac is box 4's acceptance - say so in the docstring) -> the card advances. The 303 golden
sha256 must stay green: test fits land in temp trees only, never in this checkout's store.
(3) docs/site_flow.md section: the queue rule, ranking + one-word reasons, the order, the card's
semantics (done vs skipped, self-heal, clean-slate open, save -> done), the save->line wiring,
what the headless check shows (screenshots in docs/site_flow/).

**Facts (verified, do not re-derive):** card DOM = #fqcard (next sibling of the "built in all" p
in #body) with .group-title (span "N to go"), .fq-site, .fit, #fqplace/#fqskip/#fqreset; the
stats line and the tabs row are byte-identical (201's tests green, incl.
test_index_html_review_footprint - my tag is a distinct src string). web/data/fit_queue.json is
unchanged this session and in sync (117 entries; if a merge moves the population - agent c's
203b/207 - re-run tools/fit_queue.py and commit; the page tolerates a stale/missing file and no
test pins it). serve.py's worker is UNCHANGED this session (both PUT and DELETE still ->
plan_fit.main([]), ~L229-252; the by:hand stamp on PUT already exists from 303). The conftest
`served` fixture is session-scoped, ephemeral port, copies only web/ server/ data/ (minus
data/raw). The shot.mjs probe takes the JS as the 6th CLI arg (NODE_PATH makes its require work
on this machine; POSTWAIT=200 keeps runs fast). plans.json = {"cols","rows"} (13 cols: id, book,
ia, file, title, label, size, map_box, sites, cite, url, view, ref; rows are LISTS) - 1166 rows.
sites.json = {"sites": [...]} - 385 entries, all with a web/data/sites/<id>/ dir. data/review/ =
341 item files keyed by the `site` field. data/db/platefits = 116 docs, ALL with a `site` field
(21 hand / 95 agent).
