Status: open
# 212: Cover - the last uncovered sites, the final sync, the report
Depends on: 203a, 203b, 211
Touches: fit/cover.py, data/db/platefits/ (the loop's matcher writes docs; the line check may delete a pattern doc; the sync may stamp by:agent into an unmarked auto doc), data/review/, web/data/review.json, data/commons/files.jsonl, data/commons/classified.jsonl, web/data/plans.json, web/data/sites.json, web/data/sites/, docs/batch.md, tests/test_cover.py

## Goal
The last pass of GOAL.md point 1 and its evidence for the human. For every built site
still without a fit (after the batch, 203a/203b, and the new pictures, 211): a targeted
picture search (the site's QID Commons category, P180 depictions, a title search) with the
search recorded; a found picture becomes a candidate through the normal loop (fitkit sheet ->
model fit -> fit -> gate); a site where nothing is found gets a review item marked "no picture found"
with exactly what was searched. Then the one and only page-facing sync: every fit
document (the 20 hand fits, the automatic ones, the human-saved ones) becomes its site's
overlay and its drawings count in web/data/sites.json, through the existing plan_fit
machinery; web/data/review.json becomes the current open list for the page's review
section (201). Finally docs/batch.md: the report the human reads - counts per outcome,
the seeded 20-sample of automatically accepted fits (a page URL each) for the 18/20
check, and the "no picture found" list.

## Acceptance criteria
- [ ] fit/cover.py runs the targeted search for every built site without a fit and without
      a candidate: the searches (categories, P180 queries, date) are recorded; a found
      picture is staged in the canonical files (files.jsonl + classified.jsonl, with the
      200 evidence field) and its row added to web/data/plans.json; the site goes through
      the normal loop (fitkit sheet -> model fit -> fit -> gate) and ends with an automatic document or a
      review item.
- [ ] A site with nothing found gets a review item marked "no picture found" with exactly
      what was searched (assumption 3 of PLAN.md); the human can drop the site or name a
      source from the item.
- [ ] The page-facing sync (the only task that runs it): every fit document produces its
      site's overlay (web/data/sites/<id>/depictions.json) and its drawings count in
      web/data/sites.json, through the existing plan_fit machinery; the 25 hand fits'
      overlays are unchanged (000's golden test still passes).
- [ ] web/data/review.json is the current open list for the page's review section:
      resolved items out, new items in; the served page shows the right count (checked
      through the page, not the file).
- [ ] docs/batch.md: the final report - counts per outcome (fit: hand / automatic /
      human-saved; review item; no picture found), the seeded 20-sample of automatically
      accepted fits (page URL each, fixed and reproducible from the recorded seed) for
      the human's 18/20 check, and the "no picture found" list with what was searched per
      site.
- [ ] Test (no network, port 0): after the sync, every built site in the served
      sites.json has drawings >= 1 or an open review item (GOAL.md point 1, in full); the
      25 hand fits are intact (the golden test); the sample in docs/batch.md is
      reproducible from the recorded seed.

## Notes
- This task runs last on purpose: it alone writes web/data/review.json, the per-site
  depictions and the drawings counts, so no other in-flight task can collide with it.
- The sync runs plan_fit.main() by hand (the way serve.py's after_write does it in
  production); the tests never start the server's platefits path for this - they check
  the served result.
- The 20-sample must stay a fixed record: the human's 18/20 check (GOAL.md point 3) is
  the project's acceptance, and a moving sample would make it unrepeatable.

## Hand-over

(2026-10-13, iteration 210, agent a - D3 cost measurement done: the real-dir/
hard-link tree build is ~0.7s, the fallback is dropped; NO code changed. Next
step: write tests/test_cover.py.)

**Re-measured live state (current tree, unchanged since iter-209):** 499 built;
plans.json 1474 rows; 131 docs = 21 by:hand + 110 by:agent + 0 unmarked; nofit
402; search set 246 (204 qid + 42 no-qid); with-row nofit 156 = 52
all-rows-in-item + 1 partial (stonehenge-q39671, uncovered
c_61b86efb4511e099) + 103 no-item; all 246 search-set items carry the
batch-era no_picture mark. CHOOSE (first 4 with-row nofit, sorted):
aardenburg-q955 (1 commons row c_d0a020dec428fa00, NO item),
aesica-q4688554 (1 commons row c_e28ed261168b49c9, 1-cand item whose candidate
IS that row, stale recorded resolution), aire-sur-la-lys-q259903 (1 commons row
c_d1ca997e67377769, NO item), alauna-q4708853 (5 rows, first = BOOK
earthworkenglan01allcgoog_n0438_1 [local file present in the shared store],
5-cand item, resolved None). Seed (a) = first search-set sorted =
aalsum-q3902030 (item aalsum-q3902030.json, candidates [], no_picture True).

**Tree build (D3) - MEASURED, confirmed cheap:** shared store =
/home/agent/projects/ancient-works: data/raw is a real tree (2344 dirs + 11196
files, 0 symlinks, 0 .npy/.npz, 3.1G); its web/data/sites = 388 real site dirs,
2744 files, 514M. The checkout mirrors it: data/raw is a symlink to the
store's; web/data/sites is a real dir with 503 site entries = 382 per-site
symlinks to the store + 121 real dirs (followed view: 504 dirs, 3147 files).
Measured the exact build in a throwaway /tmp tree (os.makedirs every dir -
new inodes - os.link every existing file; nothing is ever written in place):
data/raw 0.47s, followed sites view 0.11s, rest of the tree (web/ + data/ +
docs/ + specs/ + tests/, 2005 files, minus raw/sites internals, minus
.npy/.npz) 0.14s. TOTAL ~0.7s, near-zero disk (hard links share the 3.6G).
The fallback (hard-link only existing dirs + a few known dirs) is DROPPED; the
builder walks the store's data/raw and the followed checkout sites view
unconditionally. Everything else in the tree stays as settled (hard-link every
file of web/ data/ docs/ specs/ tests/ EXCEPT data/raw [built as above] and the
3 in-place files; no .npy/.npz).

**NEW DELTAS (replace the iter-205 versions where they conflict):**
(D1) FAILURE SITE: state-aware - first sorted no-qid search-set site with an
existing files.jsonl title (currently: numancia; if that set is ever empty,
assert failed empty for all). numancia's record = qid "no qid", cat "none",
n_cat_files 0, n_p180 0, n_p180_gathered 0, n_title_hits 0, n_gathered 0,
n_kept 0, new [], failed ["title search: <the fake exception str, truncated
100>"].
(D2) AESICA'S ITEM CARRIES A STALE RECORDED RESOLUTION (resolved = {doc:
'aesica-q4688554.c_e28ed261168b49c9', at: ...} - the doc no longer exists).
The item is currently OPEN; AFTER the loop builds the doc on that same row,
review.export's write-once guard (`not (item.get('resolved') or {}).get('doc')`)
sees the stale rec.doc PRESENT and does NOT re-write the item file -> the
aesica item file stays BYTE-IDENTICAL through loop+export, yet the item drops
OFF the open list. Assert exactly that (the old at-timestamp stays - write-
once is the 201 contract).
(D3) See the measured tree build above.
(D4) THE PARTIAL SITE (STONEHENGE): the loop's need_fit branch calls
batch_us.run_sites, which processes EVERY non-pre-doc candidate row (no
knowledge of item entries) - on stonehenge all 14 rows (0 pre-docs). Expected
end state: all 14 entries re-upserted IN PLACE (the 13 audit entries
overwritten with "no model answer" + 202 proposal extras), item stays OPEN (no
doc on any). The only protection is that run_sites is called at all because
uncovered is non-empty. CONFIRM this by running the loop on the scratch tree
and reading the item, then assert per the 201 upsert contract (batch_us.
_entry shape + propose_for extras). The 52 all-in-item sites (incl.
bethlehem/shotwick) are the ONLY audit-why survivors (their uncovered is empty
-> run_sites never called) - item files BYTE-IDENTICAL; box 6 covers them via
their open items.
(D5) HAND-DOC IS_DONE: the test recomputes it (precondition: golden sha256
40/40 first, then per hand-doc plan_fit.is_done in the .venv); assert from the
recompute (keep maiden-castle c_c20ff6b1f16d173d as the expected stale one
only if the recompute says so).

**CHOOSE MATCHER-FAKE RECIPES (by position):** CHOOSE[0..2] (aardenburg /
aesica / aire-sur-la-lys, all commons first rows): well-spread non-pattern
pairs (validate at runtime: plan_fit.fabrication_pattern None AND
matchfit.spread ratio >= 0.1 and sd >= 20.0 and 4+ points; e.g. the iter-205
[[13.4,22.6],[27.9,55.1],[88.2,60.8],[121.7,134.3]] extended with real lon/lat
from the row's site corners - test_batch_us._corner_pairs), first candidate
row, then fitter:"matcher" re-saved -> doc built at loop sync (commons big
stand-in seeded for each of the 3 row ids: c_d0a020dec428fa00,
c_e28ed261168b49c9, c_d1ca997e67377769). CHOOSE[3] (alauna, book first row
n0438_1): near-collinear pairs (e.g. [[100.3,5.1],[130.7,7.9],[161.2,10.7],
[191.6,13.5]] + lon/lat; verify spread ratio < 0.1 or sd < 20 at runtime) ->
doc written by the fake, then the loop's per-site line check SENTS it: upsert
into alauna's item at n0438_1 (replaces the 5th candidate entry IN PLACE: why
= "line check: matcher points nearly on a line (spread {ratio:.2f}, {sd:.0f}
px): the scale is not pinned; the gate's 25.0 m measures internal consistency
of the anchors, not their truth" - recompute ratio/sd from the fake's exact
pairs via matchfit.spread at runtime, format like site_done._sync_doc/
_pattern_entry) + doc deleted; item stays OPEN (no doc on any of its 5
candidates); alauna drawings stays 0.

**ITEM END STATES:** aardenburg/aire: no item before, doc built after -> NO
item created (site_done's need_fit False: all rows covered by the doc) ->
covered. aesica: (D2) -> off the open list, file byte-identical. alauna: stays
open, 5 candidates (n0438_1 = line-check why; the other 4 = the pre-existing
entries untouched). 103 no-item with-row sites: fresh all-rows item, every
candidate "no model answer" (+ propose_for extras where answered) -> open. 52
all-in-item sites: item files BYTE-IDENTICAL.

**BETHLEHEM / SHOTWICK (measured at CORRECTION 4 - the risk did not
materialize):** bethlehem-q2523914: drawings 0, no docs; dep already map-only
(tmk1850 1850) -> sync's prune leaves it byte-identical; item (22 candidates
with 306a audit whys + detail fields) stays OPEN and on the open list.
shotwick-castle-q7502621: drawings 0, no docs; dep = map (six-inch-1st 1842)
+ the STALE plan_c_e6e5490609414bb9 entry and both webps still on disk -> the
sync's full prune drops the plan entry and BOTH webps (dep 2->1 entries),
drawings stays 0 (a map is not a DRAWING kind); item (2 audit candidates)
BYTE-IDENTICAL (site_done's skip guard). Both stay on the served open list.

**ALL OTHERS EXACTLY AS THE ITER-205 SETTLED DESIGN** (the 7 numbered sections
+ known-traps list; full text: `git show 953d9ab:tasks/212-cover-final.md`):
own module-scoped tree + own port-0 server (NOT conftest's session `served`);
state-aware world computed ONCE in setup; fakes monkeypatched on the SHARED
module objects (cover/site_done/batch_us/review/plan_fit/evidence/commons/
matchfit + the no_network socket guard + cover.time.sleep -> no-op); seeds
(a)/(b)/(c) ((a) unmarked-auto on aalsum-q3902030 with plan
c_a122212221222121 size [1280,960] score 25.0; (b) unmarked NON-AUTO on fake
cover-fake-unmarked-q0; (c) by:agent commons doc on fake cover-fake-fail-q0,
bare site dir, big stand-in ABSENT -> sync "failed" via the socket guard's
AssertionError escaping _sync_doc into cover.sync's except -> _fail_entry
upsert); drive in-process: fetch -> search -> stage (classifier fake,
live=False) -> loop() -> nopicture -> sync -> export -> report
(at="2026-10-12T00:00:00+00:00"); cover._regen_plans re-points
export_plans.ROOT/BOOKS + commons.OUT/RAW itself; assertions (i)
searches.json (per-site fields recomputed; resumable re-run) (ii) plans.json
growth-only (key-set diff rule: lost keys = fetch failure to record) (iii)
CHOOSE outcomes + the 4 populations (D4) (iv) sync results dict + golden 40
byte-identical + beth/shotwick (v) through the served page (port 0, GET):
/data/review.json == open items recomputed with review.resolved_doc;
/data/sites.json box 6: EVERY built site drawings>=1 OR in the served open
list; golden sites drawings>=1 (vi) docs/batch.md: sample ==
random.Random(20261012).sample(sorted auto-doc ids, min(20,n)) recomputed from
the FINAL docs; no-picture table == served open no_picture items; re-run
report byte-identical (vii) CHECKOUT INTEGRITY: sha256 every file under the
checkout's data/ (skip .npy/.npz; data/raw is a symlink - skip) + web/data/**
(follow the sites symlinks) + docs/ + specs/ + tests/ before and after the
phases.

**EXACT NEXT STEPS:**
(1) write tests/test_cover.py per THIS hand-over (design = iter-205 settled
    version + D1-D5 above). One big module-scoped fixture builds tree (~0.7s,
    real-dir/hard-link per the measured D3) + world + fakes; one test per
    assertion group (i)-(vii) sharing the fixture (7 test functions over ONE
    module-scoped run so the phase sequence runs once, ~5-6 min total).
    Remember: run under `.venv/bin/python -m pytest` (bare pytest has no
    numpy/PIL); tmp_path_retention_policy "failed" (the 48 GB box); the server
    starts AFTER the phases (right before the page checks), Popen [venv
    python, server/serve.py, --port 0] cwd=tree, parse "Ancient Works on
    (\S+)".
(2) run it alone (`.venv/bin/python -m pytest tests/test_cover.py -q`), fix
    what it exposes, then the full suite (`.venv/bin/python -m pytest tests/
    -q`; known merge-induced reds: 231's case-e pin, 232's two tests, 233's
    test, 234's test - they belong to those tasks, not this one; if my claim
    is rejected on them, add 231-234 to my Depends on line).
(3) the live run (network allowed) - unchanged from the iter-208 note: fetch
    (1/s, resumable, skips rows that already have a copy) -> search -> stage
    (ask_human ONLY if stage finds NEW files and clef 127.0.0.1:18083 is still
    down: tunnel, or approve the LLM on 8081 as one-off classifier) -> loop
    (ELoFTR 8091; RoMa 8092 down, skipped by design; LLM 8081 FORBIDDEN for
    placement) -> nopicture -> sync (check `ls data/raw/commons/big | wc -l`
    first) -> export (with the key-set diff rule below) -> report (seed
    20261012) -> commit everything -> `sha256sum -c
    tests/golden/hand_fit_docs.sha256` must pass 40/40 -> suite green.
    LIVE-RUN NOTE: the 103 no-item with-row sites gain fresh all-rows "no
    model answer" items; the 1 partial site's rows are re-upserted in place
    (D4); the 52 all-in-item sites' items (incl. bethlehem/shotwick's audit
    whys) stay byte-identical; all 246 search-set sites get the nopicture
    re-record with the exact searched string. EXPORT-PHASE RULE: a bare
    re-export on THIS machine yields 953d9ab's 1168-row plans.json
    byte-identical (numancia's c_0fa271e2444f7bfc in as a COMMONS row; the 307
    rows that exist only in HEAD's 1474 - the 211 pictures, the
    Civitates/Merian full pages - have no local copies here yet). The fetch
    phase fills every missing kept row BEFORE the re-export, so the live
    export regains both sides; before the final re-export record the committed
    (id, sites[0]) key set and diff it after - any LOST key is a fetch
    failure to record as a data finding (never silently drop or re-add),
    expected growth is pure adds.

**My Depends on line stays "203a, 203b, 211"** (203a/211 done, 203b in flight -
the live run genuinely needs the batch done; 232-234 depend on ME, not the
other way round). If the driver's done-claim check counts the merge-induced
reds (231's case e, 232's two tests, 233's test, 234's test) against my
claim, add them to the line.

---

### (superseded - iteration 209 hand-over, complete text in git:
`git show d31aaec:tasks/212-cover-final.md`; the iter-205 design text it
pointed to is `git show 953d9ab:tasks/212-cover-final.md`.)
