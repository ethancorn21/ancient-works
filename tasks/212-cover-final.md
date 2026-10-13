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

(2026-10-13, iteration 209, agent a - RE-VERIFICATION session on the current
merged tree (HEAD eb7f4e3, driver files above the iter-208 state; no data drift
since 56b4536). NO test file written; NO code changed. Every module the test
drives was re-read symbol-by-symbol (fit/cover.py 863 lines DONE at 55678e3,
tools/site_done.py, fit/review.py, fit/batch_us.py, fit/matchfit.py,
pipeline/plan_fit.py, pipeline/commons.py, fit/evidence.py, tools/export_plans.py,
pipeline/build_site.py, tests/conftest.py, tests/test_fit_provenance.py,
tests/test_batch_us.py) and all match the settled design. The settled iter-205
design (full text: `git show 953d9ab:tasks/212-cover-final.md`) stays in force,
with the iter-208 deltas AND this session's new deltas below.)

**Re-measured live state (current tree):** 499 built; plans.json 1474 rows;
131 docs = 21 by:hand + 110 by:agent + 0 unmarked; nofit 402; search set 246
(204 qid + 42 no-qid); with-row nofit 156 = 52 all-rows-in-item + 1 partial
(stonehenge-q39671, uncovered c_61b86efb4511e099) + 103 no-item; all 246
search-set items carry the batch-era no_picture mark. CHOOSE (first 4 with-row
nofit, sorted) CONFIRMED: aardenburg-q955 (1 commons row c_d0a020dec428fa00, NO
item), aesica-q4688554 (1 commons row c_e28ed261168b49c9, 1-cand item whose
candidate IS that row), aire-sur-la-lys-q259903 (1 commons row
c_d1ca997e67377769, NO item), alauna-q4708853 (5 rows, first = BOOK
earthworkenglan01allcgoog_n0438_1 [local file PRESENT in the shared store],
5-cand item, resolved None). Seed (a) = first search-set sorted = aalsum-q3902030
(item aalsum-q3902030.json, candidates [], no_picture True) - unchanged from
iter-205.

**NEW DELTAS (replacing the iter-205 versions where they conflict):**
(D1) FAILURE SITE: the no-qid search-set sites with an existing files.jsonl
title are now exactly ONE: numancia (the iter-205 five - burford-house-windsor,
kastell-buch, kastell-schirenhof, kings-weston-house, stoke-house - all fell out:
211/lead's port gave them plans rows). The test must be STATE-AWARE: failure
site = first sorted no-qid search-set site with an existing title (currently
numancia); if that set is ever empty, no site gets a failed route (assert failed
empty for all). numancia is no-qid: its record = qid "no qid", cat "none",
n_cat_files 0, n_p180 0, n_p180_gathered 0, n_title_hits 0, n_gathered 0,
n_kept 0, new [], failed ["title search: <the fake exception str, truncated
100>"].
(D2) AESICA'S ITEM CARRIES A STALE RECORDED RESOLUTION: resolved = {doc:
'aesica-q4688554.c_e28ed261168b49c9', at: '2026-10-12T03:13:35.590448+00:00'}
(the doc no longer exists - a deleted agent doc, 306-era audit). Consequences
(verified against review.resolved_doc/export): (i) the item is currently OPEN
(rec.doc file missing -> candidate loop finds no doc -> None); (ii) AFTER the
loop builds the doc on that same row, resolved_doc returns the candidate's doc
(same string), but review.export's write-once guard (`not (item.get('resolved')
or {}).get('doc')`) sees the stale rec.doc PRESENT and does NOT re-write the
item file -> the aesica item file stays BYTE-IDENTICAL through loop+export, yet
the item drops OFF the open list. Assert that: byte-identical file + off the
served open list. (The old at-timestamp stays - fine, write-once is the 201
contract.)
(D3) DATA/RAW TREE CONSTRUCTION - CORRECTION 2 IS WRONG AS WRITTEN AND MUST
CHANGE: the iter-205 note says data/raw subdirs are "hard-linked from the
shared store" - impossible and unsafe: (a) os.link on a DIRECTORY fails on
Linux (EPERM; test_batch_us's _link_tree only handles file hard-links and
re-creates data/raw as a SYMLINK - a symlink is transparent to WRITES, so
writes through it land in the shared store); (b) even if the dir could be
shared, any NEW file/dir entry created in a shared dir (staged jpgs, fetch
stand-ins, big/ stand-ins) is a write to the store, which agents b/c's
checkouts share (they run tests concurrently on the same /home/agent/projects/
ancient-works/data/raw). THE TEST MUST BUILD data/raw IN THE TREE AS: a real
tree of NEW directories (walk the store's data/raw: os.makedirs every dir,
NEW inodes), with every EXISTING FILE hard-linked (reads share inodes = zero
disk; all writes in the test are new inodes via .part+rename / new file
creation - a hard-linked file is never written in place). Then the shared
store is truly untouched (no new dir entries, no new files, no rewrites).
OPEN COST QUESTION (measure first, it's the only unverified number): count of
store dirs + files (data/raw tree) and web/data/sites (499 real site dirs +
~? files; the checkout's web/data/sites is a symlink to the store's - the tree
builder must FOLLOW it per correction 3 and make real site dirs with hard-linked
files; hard-linking a few thousand files is ~seconds, the dir-walk is the cost
- test_batch_us already hard-links the whole web/+data/ in ~1s, so this is
almost certainly fine). Same real-dir/hard-link-file treatment for
web/data/sites. Everything else in the tree stays as settled (hard-link every
file of web/ data/ docs/ specs/ tests/ EXCEPT data/raw [built as above] and the
3 in-place files; no .npy/.npz).
(D4) THE PARTIAL SITE (STONEHENGE) - VERIFY IN THE TEST, DO NOT ASSUME: the
iter-208 hand-over says the loop "upserts 'no model answer' only for the
uncovered rows, in place". But tools/site_done._fit's need_fit branch calls
batch_us.run_sites which processes EVERY non-pre-doc candidate row (it has no
knowledge of item entries) - on stonehenge that is all 14 rows (0 pre-docs),
so the 13 audit/other entries would be REPLACED in place with "no model
answer" + 202 proposal fields (upsert merges by plan, replaces the entry
whole - the PITFALLS entry filed last session documents exactly this). The
only protection is that run_sites is called at all because uncovered is
non-empty (1 row). So the EXPECTED end state is: stonehenge's item keeps 14
candidates, all 14 re-upserted (13 audit entries overwritten with "no model
answer" + proposal extras, c_61b86efb4511e099 likewise), item stays OPEN (no
doc on any of them). CONFIRM this is what the code does when writing the test
(it should - run the loop on the scratch tree and read the item), then assert
per the 201 upsert contract (entry shape from batch_us._entry with
propose.propose_for extras) rather than "only uncovered rows". This also means
the 52 all-in-item sites (incl. bethlehem/shotwick) are the ONLY audit-why
survivors (their uncovered is empty -> run_sites never called) - box 6 covers
them via their open items, unchanged.
(D5) HAND-DOC IS_DONE: the last session's "20 is_done / 1 stale (maiden-castle
c_c20ff6b1f16d173d)" could NOT be re-verified (python3 has no numpy; needs
.venv). The test recomputes it (precondition: golden sha256 40/40 first, then
per hand-doc plan_fit.is_done in the .venv); keep maiden-castle as the
expected stale one only if the recompute says so - assert from the recompute.

**CHOOSE MATCHER-FAKE RECIPES (by POSITION, per iter-208 delta):** CHOOSE[0..2]
(aardenburg/aesica/aire-sur-la-lys, all commons first rows): well-spread
non-pattern pairs (validate at runtime: plan_fit.fabrication_pattern None AND
matchfit.spread ratio >= 0.1 and sd >= 20.0 AND 4+ points; e.g. the
iter-205 [[13.4,22.6],[27.9,55.1],[88.2,60.8],[121.7,134.3]] extended with real
lon/lat from the row's site corners - see test_batch_us._corner_pairs), first
candidate row, then fitter:"matcher" re-saved -> doc built at loop sync (commons
big stand-in seeded for each of the 3 row ids: c_d0a020dec428fa00,
c_e28ed261168b49c9, c_d1ca997e67377769). CHOOSE[3] (alauna, book first row
n0438_1): near-collinear pairs (e.g. [[100.3,5.1],[130.7,7.9],[161.2,10.7],
[191.6,13.5]] + lon/lat; verify spread ratio < 0.1 or sd < 20 at runtime) ->
doc written by the fake, then site_done's per-site line check SENTS it:
upsert into alauna's item at n0438_1 (replaces the 5th candidate entry IN
PLACE: why = "line check: matcher points nearly on a line (spread {ratio:.2f},
{sd:.0f} px): the scale is not pinned; the gate's 25.0 m measures internal
consistency of the anchors, not their truth" - recompute ratio/sd from the
fake's exact pairs via matchfit.spread at runtime, format like
site_done._sync_doc/_pattern_entry) + doc deleted; item stays OPEN (no doc on
any of its 5 candidates); alauna drawings stays 0.

**ITEM END STATES (computed from the live items):** aardenburg/aire: no item
before, doc built after -> NO item created (site_done's need_fit False: all
rows covered by the doc) -> covered. aesica: item (D2) -> off the open list,
file byte-identical. alauna: stays open, 5 candidates (n0438_1 = line-check
why, other 4 = the PRE-EXISTING entries untouched - the matcher fake only
writes the doc; the upsert from _pattern_entry replaces only n0438_1's entry).
103 no-item with-row sites: fresh all-rows item, every candidate "no model
answer" (+ 202 proposal extras where propose_for answers) -> open. 52
all-in-item sites: item files BYTE-IDENTICAL (run_sites never called). Beth/shotwick
inside that 52: byte-identical items (D4), dep files per the CORRECTION 4
measurement (bethlehem dep already map-only; shotwick dep 2->1 entries at the
sync's final prune: the stale plan_c_e6e5490609414bb9 entry + both webps
pruned; drawings 0->0 both; both stay on the served open list via their items).

**ALL OTHERS EXACTLY AS THE ITER-205 SETTLED DESIGN** (the 7 numbered sections +
known-traps list in `git show 953d9ab:tasks/212-cover-final.md`): own module-
scoped tree + own port-0 server (NOT conftest's session `served`); state-aware
world computed ONCE in setup; fakes monkeypatched on the SHARED module objects
(cover/site_done/batch_us/review/plan_fit/evidence/commons/matchfit + the
no_network socket guard + cover.time.sleep -> no-op); seeds (a)/(b)/(c) ((a)
unmarked-auto on aalsum-q3902030 with plan c_a122212221222121 size [1280,960]
score 25.0; (b) unmarked NON-AUTO on fake cover-fake-unmarked-q0; (c) by:agent
commons doc on fake cover-fake-fail-q0, bare site dir, big stand-in ABSENT ->
sync "failed" via the socket guard's AssertionError escaping _sync_doc into
cover.sync's except -> _fail_entry upsert); drive in-process: fetch -> search ->
stage(classifier fake, live=False) -> loop() -> nopicture -> sync -> export ->
report(at="2026-10-12T00:00:00+00:00"); cover._regen_plans re-points
export_plans.ROOT/BOOKS + commons.OUT/RAW itself; assertions (i) searches.json
(per-site fields recomputed; resumable re-run) (ii) plans.json growth-only
(key-set diff rule: lost keys = fetch failure to record) (iii) CHOOSE outcomes
+ the 4 populations (D4) (iv) sync results dict + golden 40 byte-identical +
beth/shotwick (v) through the served page (port 0, GET): /data/review.json ==
open items recomputed with review.resolved_doc; /data/sites.json box 6: EVERY
built site drawings>=1 OR in the served open list; golden sites drawings>=1 (vi)
docs/batch.md: sample == random.Random(20261012).sample(sorted auto-doc ids,
min(20,n)) recomputed from the FINAL docs; no-picture table == served open
no_picture items; re-run report byte-identical (vii) CHECKOUT INTEGRITY:
sha256 every file under the checkout's data/ (skip .npy/.npz; data/raw is a
symlink - skip) + web/data/** (follow the sites symlink) + docs/ + specs/ +
tests/ before and after the phases.

**EXACT NEXT STEPS:**
(1) measure the one open cost number: store data/raw dir/file counts +
web/data/sites dir/file counts (`find /home/agent/projects/ancient-works/data/raw
d| wc -l` etc.), confirm the hard-link tree build is ~seconds (expect yes -
test_batch_us hard-links ~the same volume in ~1s). If it were minutes, fall
back to hard-linking files only under the dirs that exist in the store + a few
known dirs, still real dirs.
(2) write tests/test_cover.py per THIS hand-over (design = iter-205 settled
version + iter-208 deltas + D1-D5 above). One big module-scoped fixture builds
tree + world + fakes; one test per assertion group (i)-(vii) sharing the
fixture (or one long test - the iter-205 design lists 7 assertion groups; keep
them as 7 test functions over ONE module-scoped run so the phase sequence runs
once, ~5-6 min total). Remember: run under `.venv/bin/python -m pytest` (bare
pytest has no numpy/PIL); tmp_path_retention_policy "failed" (the 48 GB box);
the server starts AFTER the phases (right before the page checks), Popen
[venv python, server/serve.py, --port 0] cwd=tree, parse "Ancient Works on (\S+)".
(3) run it alone, fix what it exposes, then the full suite
(`.venv/bin/python -m pytest tests/ -q`; known merge-induced reds: 231's case-e
pin, 232's two tests, 233's test, 234's test - see DECISIONS 2026-10-13 entries
- they belong to those tasks, not this one; if my claim is rejected on them,
add 231-234 to my Depends on line). Then step (5) live run per the iter-208
note (network allowed; ask_human only if stage finds NEW files and clef 127.0.0.1:
18083 is still down).

**Measured this session (merged tree, HEAD f62d50c, plans.json 1474 rows, 499 built):**

bethlehem / shotwick (the CORRECTION 4 question) - box 6 is safe, no action needed:
- bethlehem-q2523914: drawings 0, no docs; dep already map-only (tmk1850 1850) -
  its plan entries were pruned on this machine ~1h after the 306a audit a858f48
  (dep mtime Oct 12 22:38 CDT), drawings reset with them. Item: 22 candidates with
  306a audit whys + detail fields (coarse/ground/rot_deg/scale/note), no_picture
  None, resolved None -> OPEN, published in the 333-item review.json. Sync's prune
  leaves it byte-identical (prune only drops kind plan/view entries).
- shotwick-castle-q7502621: drawings 0, no docs; dep = map (six-inch-1st 1842) +
  the STALE plan entry of the doc deleted at 6841f07 (after iter 136) -
  plan_c_e6e5490609414bb9.webp + its _ink.webp still on disk (dep mtime Oct 11
  18:47, never re-pruned here). Item: 2 candidates (audit whys), OPEN, published.
  The sync's full prune drops the plan entry and BOTH webps; set_drawings ->
  drawings stays 0 (map is not a DRAWING kind, no plate).
- Both are in the 52-site "all rows already item candidates" population: site_done
  fit() re-fits only rows with NEITHER doc NOR item entry (docstring: a blind
  re-run would swap the audit entries whole) -> the loop leaves both item files
  BYTE-IDENTICAL. New PITFALLS entry filed on this (### tools/site_done.py,
  fit/review.py). Neither site is in the search set (both have rows) -> nopicture
  does not touch them.

Re-measured population (PRODUCT definitions; the iter-205 numbers were the 1168
pre-merge tree): nofit (drawings 0 and no doc) = 402 (94 sites have docs); search
set (no plans row) = 246 - ALL already carry the batch-era no_picture mark -> the
nopicture phase re-records all 246 with the exact searched string, 0 bare. (fudge/
highbank/hopeton look bare under a looser no-doc definition but are drawings-1
site.json-plate sites -> covered, outside _no_fit_sites.) with-row nofit = 156 =
52 all-rows-in-item (item untouched) + 1 partial overlap (upsert "no model answer"
only for the uncovered rows, in place) + 103 no item (fresh all-rows item).

CHOOSE on THIS tree (first 4 with-row nofit, sorted) = aardenburg-q955 (1 commons
row, no item), aesica-q4688554 (1 commons row, 1-cand item), aire-sur-la-lys-
q259903 (1 commons row, no item), alauna-q4708853 (5 rows, first = BOOK Allcroft
1908 n0438_1, 5-cand item). alesia (withrow[4]) and angel-mounds (withrow[7]) fell
out of the first 4 (211 gave aardenburg/aire their rows; the lead's Mac port
20277f3 added 11 matcher docs on 11 newly built sites).

**EXACT NEXT STEPS:**
(3) write tests/test_cover.py per the settled iter-205 design (`git show
    953d9ab:tasks/212-cover-final.md`) WITH these deltas:
    - assertion (iv) is now concrete: bethlehem's dep + item byte-identical after
      the sync; shotwick's dep 2->1 entries (plan entry + both webps gone), item
      byte-identical; both items on the served open list. Correction 4's open
      question is resolved: no nopicture re-record for either.
    - CHOOSE stays state-aware (first 4 with-row nofit, sorted), but the matcher
      fake assigns the pair recipes by POSITION: CHOOSE[0..2] well-spread
      non-pattern pairs on their first candidate row (doc built; source = that
      row's own src - here 3 commons; the shared-store book file of a book first
      row must be hard-linked in the tree), CHOOSE[3] (here alauna, book first row
      n0438_1) near-collinear -> doc written, then sent+deleted by the loop's
      per-site line check; item why = the line-check string recomputed from
      matchfit.spread at runtime.
    - Item end states per 201's derivation, computed from the live item: doc on an
      in-item row -> item resolved write-once, OFF the open list (here: aesica);
      doc on a not-in-item row or no item -> item, if any, stays open (here:
      aardenburg/aire have no item; alauna stays open with the line-check why on
      n0438_1). Everything else stays exactly as settled (state-aware fakes and
      assertions; own tree + own port-0 server; checkout-integrity hashes; box 6
      through the served page; report re-run byte-identical).
(4) run it alone (`.venv/bin/python -m pytest tests/test_cover.py -q`), fix what it
    exposes, then the full suite.
(5) the live run (network allowed) - unchanged from the iter-207 hand-over: fetch
    (1/s) -> search -> stage (ask_human ONLY if new files are found and clef
    127.0.0.1:18083 is still down: tunnel, or approve the LLM on 8081 as one-off
    classifier) -> loop (ELoFTR 8091; RoMa 8092 down, skipped by design; LLM 8081
    FORBIDDEN for placement) -> nopicture -> sync (check `ls data/raw/commons/big |
    wc -l` first) -> export (with the key-set diff rule) -> report (seed 20261012)
    -> commit everything -> `sha256sum -c tests/golden/hand_fit_docs.sha256` must
    pass 40/40 -> suite green. LIVE-RUN NOTE from this session: the 103 no-item
    with-row sites gain fresh all-rows "no model answer" items; the 1 partial site's
    uncovered rows are upserted in place; the 52 all-in-item sites' items (incl.
    bethlehem/shotwick's audit whys) stay byte-identical; all 246 search-set sites
    get the nopicture re-record with the exact searched string.
    EXPORT-PHASE RULE (still in force, from the iter-207 hand-over): a bare
    re-export on THIS machine yields 953d9ab's 1168-row plans.json byte-identical
    (numancia's c_0fa271e2444f7bfc in as a COMMONS row; the 307 rows that exist only
    in HEAD's 1474 - the 211 pictures, the Civitates/Merian full pages - have no
    local copies here yet). The fetch phase (1/s, resumable, skips rows that already
    have a copy) fills every missing kept row BEFORE the re-export, so the live
    export regains both sides; before the final re-export record the committed
    (id, sites[0]) key set and diff it after - any LOST key is a fetch failure to
    record as a data finding (never silently drop or re-add), expected growth is
    pure adds.

**My Depends on line stays "203a, 203b, 211"** (203a/211 done, 203b in flight - the
live run genuinely needs the batch done; 232-234 depend on ME, not the other way
round). If the driver's done-claim check counts the merge-induced reds (231's case
e, 232's two tests, 233's test, 234's test) against my claim, add them to the line.

---

### (superseded - iteration 207 hand-over; its step (1) is done: 231 corrected,
232/233/234 written, probe worktrees removed. Complete text in git:
`git show 2eef3ce:tasks/212-cover-final.md`; the iter-205 design text it pointed to
is `git show 953d9ab:tasks/212-cover-final.md`.)
