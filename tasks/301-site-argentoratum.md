Status: done
# 301: Argentoratum (Strasbourg), finished on the map - the second site through the line
Depends on: 300
Touches: web/data/sites.json, web/data/sites/argentoratum-q2361353/, web/data/sites/stonehenge-q39671/, web/data/review.json, data/review/, data/db/platefits/, docs/site_flow.md, docs/site_flow/, tools/site_done.py, pipeline/plan_fit.py, tests/test_site_done.py, tests/golden/

## Goal
One site at a time, all the way to the map (owner, 2026-10-11). Stonehenge went through first and left the line
as one command (docs/site_flow.md). Argentoratum is next: the batch left 8 automatic fit documents for it
(data/db/platefits/argentoratum-q2361353.*.json, best gate 8.7 m). Take it all the way with the line, and look at
the result the way a visitor does before calling it done.

## Acceptance criteria
- [x] `tools/site_done.py argentoratum-q2361353` run; every picture of the site is synced to the map or an open
      review item, and its entry in web/data/sites.json counts the synced drawings. (All 42 candidates in the one
      open review item - 34 batch + 8 added by the line's pre-sync check; 0 synced; no picture left uncovered;
      entry stays at 0 drawings, exactly the synced count. Second run of the command is a no-op.)
- [x] Checked in a browser: each synced drawing opened over the ground. A drawing that is visibly in the wrong place
      (streets/walls of the drawing not on the real ones) goes to the review queue with the reason, even if its gate
      passed: a gate of 0.0 m means the points were not checked, not that the fit is right. Screenshot of the best
      drawing at docs/site_flow/argentoratum.png with one line on what it shows. (Vacuous first half: 0 drawings
      synced, so there is nothing to open over the ground - the headless probe confirms drawings 0 and the
      uncoloured marker. Second half: all 8 automatic documents, including the two with gate 0.0 m, were sent to the
      review queue with the line-check reason. Screenshot docs/site_flow/argentoratum.png with its one line in
      docs/site_flow.md.)
- [x] Anything that broke in the line on this site is fixed in the line (not by hand for this site), with a test,
      and one line under "What broke" in docs/site_flow.md. The full suite passes. (Nothing new broke on this site:
      the run behaved exactly as Stonehenge's did, and the pre-sync check it relied on is the existing "What broke"
      entry with its test (tests/test_site_done.py re-seeds and re-verifies the check). Suite 60 passed after the run.)

## Notes
- The 20 hand fits and their golden file stay untouched.
- Do not start 207 or any other task: the lead gives the next site when this one is done.

## Hand-over
(iteration 73, agent c - TASK DONE. Argentoratum went through the line exactly as Stonehenge did: all 8 automatic
documents were the model's fabrication class and were all caught by the pre-sync check, so the site ends with
0 drawings and 42 open review candidates. No code changed in this session.)

**The run (live checkout, `.venv/bin/python tools/site_done.py argentoratum-q2361353`, no model flag, exit 0):**
42 candidates = 8 docs + 34 in the item, none uncovered -> "no batch run needed" (no model, no network). All 8
pattern docs (gates 19.9/25.7/25.7/0.0/8.7/32.4/40.1/0.0 m) upserted into the item with "line check: ..." + gate
score + evidence, deleted, scoped prune (a no-op: the site has no plan overlays). Entry 0 -> 0. Item 34 -> 42:
the first 34 candidates byte-identical, the 8 new ones appended in sorted plan order. Page 339 open of 340
(unchanged - the item was already open). Second run: no docs, item file byte-identical, only the page's "at"
changes. A sha256 snapshot of data/review + data/db/platefits + web/data before/after showed exactly those three
files changed (8 docs deleted, item, review.json) and nothing else.

**Visitor check (box 2, vacuous but done the visitor's way):** `server/serve.py --port 0` (ephemeral port) +
`NODE_PATH=/home/agent/tools/shot/node_modules node tools/shot.mjs http://127.0.0.1:<port>/ docs/site_flow/argentoratum.png
1000 1200 800 "<probe>"`, probe polls `S.ready && S.sites.length`, `select('argentoratum-q2361353')`, awaits
`loadDeps`, POSTWAIT=8000 (4.5 s flyTo). The [eval] returned: drawings 0, marker class "marker plain ..."
(uncoloured), depFiles ["map:cassini.webp (1780)", "map:etatmajor.webp (1840)"] (the 1950 aerial is hidden by the
150-year rule), RV 339 open. The committed png shows the aerial of Strasbourg, the "Old maps and aerials" group
(None/Cassini/Etat-major), "42 old plans may show this site" in the panel, and the uncoloured marker - one line on
that in docs/site_flow.md next to the new Argentoratum paragraph. ArcGIS ERR_ABORTED lines in flight are normal.

**State left on disk:** argentoratum-q2361353: 0 docs in data/db/platefits (the 8 live in this commit's parent in git
history, e.g. `git show <parent>:data/db/platefits/argentoratum-q2361353.c_6ba6bb7b49a78014.json`); item
data/review/argentoratum-q2361353.c_6acfd94dec8c011b.json = 42 candidates (34 batch first in original order, then
the 8 line-check in sorted plan order), resolved None; web entry 0 drawings; depictions = 2 maps + 1 aerial
(unchanged). Stonehenge state untouched (0 docs, 13-candidate item). The line and its test are the reusable
machinery for the next site the lead names: same command, same expectations (see docs/site_flow.md, now with the
Argentoratum paragraph).

**Next step for whoever picks up the line:** nothing - the lead gives the next site as a new task. Reusable notes:
.venv/bin/python for anything importing pipeline/ or fit/; screenshot recipe as above (POSTWAIT>=8000); tests must
stay hermetic (tmp trees, socket guard) and must not bind fixed ports (the checkouts run in parallel).

**Re-read (carried over, still fresh-eyes due):**
- Re-read: fit/review.py:upsert_item - merges by plan; a same-plan candidate is REPLACED whole, so
  a later re-upsert (e.g. a batch run that re-fits the picture) overwrites the "line check:" entry -
  intended: the newest word wins until a human saves.
