Status: split
# 309: The queue pairs a drawing with the right place, not a namesake
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] (carved to 804 - the wiring in tools/fit_queue.py build(); 805 - the rebuild of the committed
      queue/review data) Every queue entry's candidate is checked to show the same place as its site, not just
      the same name: the caption/place words, county and region in the picture's metadata against the site's
      place, region and coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review
      queue with the reason "same name, other place: <caption place> vs <site place>"; where the right site
      exists in the catalog, the candidate is moved to it instead.
- [ ] (carved to 805) docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke
      Camp near Brighton is not paired with the Cambridgeshire dyke.
- [ ] (carved to 804) tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit
  there). The subtasks' own Touches lines are authoritative for their files; 804 also carries
  data/review/README.md (the reason extra in the pass-through list) and 805 carries
  tests/test_right_place_drift.py.

## Hand-over

(2026-10-12, iteration 99, agent c - session 8. The driver handed me 309 (the split parent)
again; 804 (Depends on: none) still was not in Next-open-tasks, so I started 804 in the owner
lane myself (it is my subtask; the module is on my branch) and set it in-progress. Done this
session: 804's refactor-first commit (build() gathers the per-site candidate map; the new
_entry() builds the entry; behavior-neutral - old vs new build on one tree identical, 116
entries; part-1 tests pass unmodified). NEXT STEP (next session, same lane): 804 boxes 1+2 -
the two-phase wiring (the full sketch is in 804's hand-over), then 804 box 4 (tests) and box 3
(README note); then 805 (the rebuild - it also fixes the stale committed queue, below); when
804+805 are done the driver returns 309 and I tick the three carved boxes and set it done.

Carve state: box 1 (the wiring) = 804, in-progress, ~1/5 (refactor in, wiring pending);
box 2 (the site_flow report) = 805, not started; box 3 (the namesake tests) = 804, not
started.

**Shared ground truth (re-verify at session start; the DECISIONS entries have the evidence):**
- Worktree warning (STILL APPLIES): all work belongs in /home/agent/projects/ancient-works.c
  (branch agent/c); the three worktrees (.a, .c, main) share one repo; never commit in the
  main worktree (a PITFALLS entry covers the mixup).
- The module tools/right_place.py (696 lines, stdlib, fc67bb9; on agent/c only - it lands on
  main when 309 closes out): load/picture_facts/site_facts/check_pairing/find_right_site.
  Its verbatim matcher core spans lines 33-223 (17 top-level names) and 805's drift test
  compares those against pipeline/books_match.py; the six iteration-95 spec deviations are
  baked in - do not "fix" them.
- Module baseline: 324 queue pairings, 15 flags over 9 sites, zero false positives - identical
  at iterations 95/97/98/99. The 15 (site <- candidate(s), signal): devil-s-dyke-q3307343 <-
  n0686_1 (BRIGHTON, the case; right site devil-s-dyke-hillfort-q17674160, unique pass 0.65,
  unbuilt) and n0599_1 (Aysgarth, H1 'Yorks'); bokerley-dyke <- n0599_1; coria + vindomora <-
  n0354_1 (ARDOCH, PERTHSHIRE; no catalog Ardoch -> review); eaton-socon <- n0285_1 (Bath) +
  n0557_1 (FIRLE HILL) + n0558_1/2 (LEWES DOWN); windmill-hill <- the same three Sussex rows
  n0557_1/n0558_1/n0558_2; alauna + castle-neroche <- n0438_1 (Defences of YORK); clun-castle
  <- n0575_1 (Devonshire place field). The must-not-flag set (Maumbury, leeds-castle,
  fairlawne, chevening, chiswick-house, the 3 Ohio tied-away sites, n0662_1) is verified
  absent in the same run.
- Suite baseline on agent/c: 3 failed / 77 passed / 1 skipped - the 3 pre-exist on main (the
  lead's matcher-fit wiring b22a2d2/9324f8b): test_fit_provenance::
  test_line_refuses_unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_line,
  test_site_done::test_site_done_line. Neither subtask edits their assertions; both leave the
  rest green.
- NEW this session: the committed web/data/fit_queue.json is STALE - 117 entries vs 116 that
  the current data builds (old and new build code agree; the extra committed entry is
  shotwick-castle-q7502621, no longer built from current data; the same site is the
  orphan-platefit-doc in the main-side failures). 805's rebuild fixes it; 804 never writes
  the file.
- data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json already holds
  n0686_1 and n0599_1 (both stay in review forever). n0686's 805 move targets the hillfort's
  OWN item (which may not exist yet - upsert_item creates it when the target is unbuilt).
- Agent a (306/307) reads web/data/fit_queue.json tolerantly and must never write it; if
  their merge lands while 805's rebuild is in flight, expect driver reconciliation - flag any
  hit on this task's files in DECISIONS.
- The dropped reference spec tasks/309-place-check.md (agent a's, kept as reference) still
  holds the background: the fail-open rule (an unknown place never mismatches; a place that
  contains the site does not), the --live Wikidata human path (pipeline/catalog_wd.py; tests
  never call it), "the 305 queue shape and tests must survive". Its data/fit_place.json
  committed-verdict design was deliberately NOT adopted (the module re-checks from stored
  fields on every run) - if a future session revives it, data/fit_place.json +
  tests/test_fit_place.py must be added to the relevant task's Touches first.

**Re-read (still apply):**
- tools/fit_queue.py: build / _entry - the two-phase insertion point (sketch in 804's
  hand-over); stdlib-only contract (owner's Mac, no PIL); the wiring imports right_place and
  fit/review via sys.path inserts (PITFALLS: runpy/run_path does not put the script dir on
  sys.path under the test GUARD).
- fit/review.py: upsert_item (write-once resolved; the item file name follows
  candidates[0].plan - a moved candidate becoming the lead renames the file; new plans
  append, same-plan replaces in place) and export (the only writer of web/data/review.json).
- tests/test_fit_queue.py: the GUARD (dead-socket runpy subprocess), test_fit_queue_synthetic
  (the no-op-degrade tree must stay unmodified and catalog-less), test_fit_queue_real (the
  804 box-4 extension point: copy data/catalog + data/books and re-derive WITH the check).
