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

(2026-10-12, iteration 100, agent a - step 1 of the 8-step plan done: the queue generator.)

**Done this session:** (a) `web/fitqueue.js` added to the Touches line. (b) `tools/fit_queue.py`:
queue = built (a sites.json entry AND the web/data/sites/<id>/ dir, the site_done rule) + a
candidate (a plans.json row naming the site, OR a candidate of any data/review/ item, deduped by
plan; a plan in both resolves to the plans row) + no by:hand doc (the doc's `site` field, or the
filename prefix before the first dot). Best candidate: plan over view, then drawing area in page
px (map_box fraction x page/image size; a row with no box: the whole page/image; no size stored:
0; the synth row mirrors review.js rvResolveRow, sites narrowed to the site), then plan id.
One-word reason: "the only candidate" / "a true plan" (chosen while a view exists) / "the
clearest scan" / "the clearest view". Sites ordered by the same key on their best candidate, then
name. Stdlib-only (never opens an image), `--root DIR`, atomic indent=1 no-trailing-newline
write to web/data/fit_queue.json ({"at": iso, "entries": [{site, name, best: {plan, reason, row:
the 13 named fields}, candidates: [{plan, title, book, view, draw_px}] best first}]}). (c)
`web/data/fit_queue.json` committed: 117 entries, first = devil-s-dyke-q3307343 "The Devil's Dyke
Camp, near Brighton" (the clearest scan, Allcroft 1908); reason mix 72/37/7/1. (d)
`tests/test_fit_queue.py` part 1: a synthetic 12-site tree pinning every rule exactly (entry set;
agent-doc inclusion; hand-doc exclusion via both field shapes; a no-picture item creating no
candidate; unbuilt sites out; the dedupe; the synth row for a plan whose only row names another
site; the ranking and the four reasons; the order; the file bytes) and a real-population test
(entry set derived independently, never pinned - 803 precedent; per-entry invariants; checkout
byte-identical; dead-socket guard). Both green; the FULL suite under .venv/bin/python: 70 passed,
1 skipped (the loop-start failures are fixed by agent c's merges).

**Next step, in order:** (1) READ tests/test_serve.py WHOLE - never read by me; it owns the
doc-store roundtrip and "page data matches disk" and my worker change must keep it green;
ESPECIALLY test d: it serves a tree with NO tools/ dir and asserts the exact file set after
PUTs - the new worker's `import site_done` must raise ModuleNotFoundError there, be swallowed by
the existing except-BaseException-and-print, and create no new files. (2) web/fitqueue.js (the
card; design settled below). (3) index.html: one `<script src="fitqueue.js"></script>` after the
review.js tag (L1707, the last script). (4) serve.py worker (settled below). (5) tests part 2:
save -> the line (picture-copy solution below). (6) docs/site_flow.md section (queue rule,
ranking + reasons, the order, the card's semantics, the save->line wiring, what the headless
check shows) + headless screenshots into docs/site_flow/ (box 4's owner-Mac click-through is his
acceptance; note that).

**The card (web/fitqueue.js, loaded AFTER review.js, chaining the wrappers it installed - the
iteration-99 design, still valid):** home view (the sites tab of renderList): injected as the
NEXT SIBLING of the stats `<p class="fit">` containing "built in all" (index.html L573; do NOT
touch the tabs row or the stats line's own text - 201's tests pin them). Card: "Ready to fit
(N)" title, the next site's name, its best candidate (title . book) with the one-word reason,
buttons "Place the drawing" and "Skip" (+ a small reset link when the session has skips). Next
site = first entry not in done and skipped; done = localStorage `aw.fitQueue.done` (site ids,
self-healed against the file on load: a site that left the file is dropped), skipped =
session-only. "Place the drawing" = select(site.id) -> setGround(site.lidar===false ?
'imagery' : 'relief', site) -> await loadDeps(site) -> startFit(site) -> call the CURRENT global
openPlan (review.js's wrapper) with the entry's best row - do NOT set RV.pending (the queue's
row is the owner's clean slate; pre-placed machine pairs are the review flow's contract). "Skip"
adds to session skipped and re-renders. Hide the card when the file is missing/404 or has no
entries left; it must never break a page load. All existing fit-tool clicking untouched.

**serve.py worker (settled):** api() passes the method to after_write: PUT platefits -> job
("line", site), site = data.get("site") or doc_id.split(".")[0]; DELETE -> ("sweep",). The
worker drains a small job list on each wake (two PUTs to different sites while busy must both
run: keep list + lock, one event per enqueue as today). ("line", site) -> import site_done from
tools/ (sys.path.insert(ROOT/tools)) and call site_done.main([site]) IN-PROCESS - NO
--working/--model-json: with model=None uncovered candidates go to the review item as "no model
answer" and the whole line is network-free (303's dead-socket run proved it); it builds the hand
doc with no fabrication check (303), refreshes the site's drawings count (the square colour),
and resolves the review item scoped to the site. ("sweep",) keeps the OLD plan_fit.main([]) +
its global prune (a deleted doc's overlay must still leave the map; no page UI deletes
platefits today, but the API exists and 303's DELETE contract stands). The current worker
(after_write/_fit_wake, ~L229-252) runs plan_fit.main([]) for both PUT and DELETE - that is what
changes. Keep the PUT handler's existing data["by"]="hand" stamp (303). site_done.main(argv)
returns an int (0/1/2) and never sys.exits when called as a function.

**Tests part 2 (save -> the line):** conftest `served` (temp copy of web/server/data MINUS
data/raw, --port 0) PLUS tools/ + fit/ + pipeline/ copied in (unlike 303's d-tree, mine needs
the line to actually run). PUT a hand doc exactly as the page's saveFit builds it (copy the doc
recipe from test_review.py::test_save_resolves_the_item: row fields + crop from map_box x size +
candidate pairs, `at` a fixed string) for a site DERIVED (not hardcoded) from the real queue so
it has a resolvable row and a picture that exists in THIS checkout's data/raw/; first check
plan_fit.load_picture (L203-222) for the exact path per source (commons:
data/raw/commons/<site>/<hash>.jpg; book: data/raw/books/<ia>/full/<file>) and COPY that one
file into the temp tree's data/raw/. Then poll until the line's effects are in the tree: the
doc by:hand; the site's depictions.json gained an entry with fit.at == at; sites.json drawings
incremented; the item's resolved {doc, at} (write-once). The fit step (model=None) writes only
item files - no network (303's guard pattern: dead sockets). Headless page check (shot.mjs +
CHROME=/opt/google/chrome/chrome + NODE_MODULES=/home/agent/tools/shot/node_modules; the
_headless_or_skip pattern from test_review.py): boot, wait S.ready and the queue loaded; assert
the card (first entry's site + best title + reason + the (N) count); click "Place the drawing"
-> P.active && P.site.id == entry.site && P.plan == entry.best's row (the picture 404s in the
test tree - fine: assert the row/plan state and no page errors); back out, click Skip -> the
card advances; the save flow PUTs through the page's own saveFit (a real mouse click is box 4's
owner-Mac acceptance - say so in the docstring) -> the card advances. The 303 golden sha256
must stay green: test fits land in temp trees only, never in this checkout's store.

**Facts (verified this session, do not re-derive):** plans.json = {"cols", "rows"} with cols
[id, book, ia, file, title, label, size, map_box, sites, cite, url, view, ref] - 1166 rows, rows
are LISTS (batch_us._plans_rows converts to named dicts). sites.json = {"sites": [...]} - 385
entries, all with a web/data/sites/<id>/ dir here (389 dirs total). data/review/ = 341 item
files keyed by the `site` field (95 with candidates: coarse [pairs/why, some also size/map_box],
slim [plan/title/url/why/evidence/gate_score] or full [all stored fields]); a
no_picture_found-only item has candidates: []. data/db/platefits = 116 docs, ALL with a `site`
field (21 hand / 95 agent). The committed fit_queue.json is in sync with the data as of this
commit: if a merge moves the population (agent c's 203b/207), re-run tools/fit_queue.py and
commit; the page tolerates a stale/missing file and no test pins the committed file.
