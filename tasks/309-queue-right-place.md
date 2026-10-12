Status: open
# 309: The queue pairs a drawing with the right place, not a namesake
Depends on: 305
Carved from: 307 (box 1)
Touches: tools/fit_queue.py, tools/right_place.py, web/data/fit_queue.json, data/review/, web/data/review.json, tests/test_fit_queue.py, docs/site_flow.md

## Goal
307 box 1, carved out so it runs in parallel with 307's page work (agent a). The queue's first entry paired
Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort), with devil-s-dyke-q3307343, the
Devil's Dyke in Cambridgeshire, 150 km away. The owner could not find it on the map.

## Acceptance criteria
- [ ] Every queue entry's candidate is checked to show the same place as its site, not just the same name: the
      caption/place words, county and region in the picture's metadata against the site's place, region and
      coordinates (Wikidata where it helps). A mismatch leaves the queue and goes to the review queue with the reason
      "same name, other place: <caption place> vs <site place>"; where the right site exists in the catalog, the
      candidate is moved to it instead.
- [ ] docs/site_flow.md: how many of the queue's entries were wrong, and the list. Devil's Dyke Camp near Brighton is
      not paired with the Cambridgeshire dyke.
- [ ] tests/test_fit_queue.py covers a namesake mismatch (no network).

## Notes
- Do not touch web/index.html, web/fitqueue.js (agent a, 307) or fit/ (the lead is building the matcher fit there).

## Hand-over

(2026-10-12, iteration 109, agent c - session 5. Re-baseline session: verified the committed module against the
current data and re-established the suite baseline. NO code changes this session. All work belongs in my
worktree /home/agent/projects/ancient-works.c (branch agent/c) - this session's harness start was in the
MAIN worktree (/home/agent/projects/ancient-works), which does NOT contain my branch's files; the three
worktrees (.a = agent a the lead, .c = me, plus main) share one repo (git-common-dir ancient-works/.git).
Never commit in the main worktree; a PITFALLS entry covers the mixup.)

**State now:**
- The module tools/right_place.py is COMMITTED on agent/c (driver commit fc67bb9 after iteration 95; main
  does not have it yet). It is the complete offline right-place check: H1 explicit county/state words,
  H2 town words (book rows only), find_right_site (min_score 0.5), fail-open on unknown site county.
  `python3 tools/right_place.py [--all] [filter]` (stdlib only; system python3 runs it - no PIL needed).
- My data area is UNCHANGED since iteration 95 (git diff fc67bb9..HEAD empty for every file I touch):
  117 queue entries, 324 (site, candidate) pairings, entry 1 = devil-s-dyke-q3307343 with the Brighton row
  n0686_1. The lead's 14 iterations (306/307/308 + the matcher fit) never touched my files.
- CLI re-run on current data: IDENTICAL 15 flags as iteration 95 - all verified true, zero false positives:
  devil-s-dyke <- n0686_1 (BRIGHTON - THE case; right site: the Sussex hillfort devil-s-dyke-hillfort-
  q17674160, unique pass at 0.65) and <- n0599_1 (Aysgarth, H1 'Yorks'); bokerley-dyke <- n0599_1 (same
  row); coria + vindomora <- n0354_1 (ARDOCH, PERTHSHIRE; no catalog Ardoch, so no right site - review);
  eaton-socon <- n0285_1 (Bath) + n0557_1 (FIRLE HILL) + n0558_1/2 (LEWES DOWN); windmill-hill <- n0557_1 +
  n0558_1/2 (same three rows, second built site); alauna + castle-neroche <- n0438_1 (Defences of YORK);
  clun-castle <- n0575_1 (Devonshire place field). 15 pairs over 9 sites. The must-not-flag set (Maumbury,
  leeds-castle, fairlawne, chevening, chiswick-house, the 3 Ohio tied-away sites, n0662_1) verified absent.
- Full suite on agent/c: 3 failed / 77 passed / 1 skipped. The 3 failures are the SAME 3 as iteration 95,
  all pre-existing on main (the lead's matcher-fit fallout): test_fit_provenance::test_line_refuses_
  unmarked_non_auto_doc, test_fit_queue::test_save_runs_the_one_site_line, test_site_done::test_site_done_
  line. The only main commit since iteration 95 is cf29be2 (matchfit spread guard, site_done, two
  castle-neroche review items) - it touches none of those test files, and my sole non-task commit adds a
  module nothing imports yet, so the failures cannot be mine. NOT mine to fix (the lead's 307 work may
  land the fix on merge).
- The 309 double-claim is closed: the driver's queue names tasks/309-queue-right-place.md (the lead's
  short spec) as MY task - this file is the one I maintain (the main-side copy has no Hand-over section
  and no tools/right_place.py in Touches; my copy keeps both - that difference is mine to keep, not a
  conflict to resolve). tasks/309-place-check.md (the lead's DETAILED spec, dropped by agent a at
  iteration 109, kept as reference) holds: the fail-open rule (an unknown place never mismatches; a place
  that contains the site does not), the committed-verdict design data/fit_place.json (re-verify on every
  build; a stale record is flagged, not kept), the --live Wikidata human path (pipeline/catalog_wd.py;
  tests never call it), the measured cases, and "the 305 queue shape and tests must survive". My module
  satisfies the short spec's three boxes without fit_place.json; the verdict-record design is an optional
  extension (would need data/fit_place.json + tests/test_fit_place.py added to Touches first).
- 800-803 are all Status: done -> the next free 800-range numbers for my split are 804 and 805 (re-check
  `ls tasks/` at split time; the team rule takes the two lowest free).

**NEXT SESSION (one step) - SPLIT this task** (team mode: new top-level tasks in 800-1099, one module per
task, each with `Depends on: 309` and its own `Touches:` line):
- 804 (wire + tests): apply the per-build check in tools/fit_queue.py build() over every (site, candidate)
  of _candidates(): a flagged candidate is dropped from that site's queue (best recomputed over the rest;
  a site with no candidates left leaves the queue entirely); it is recorded in the site's review item via
  fit/review.py upsert (stdlib) with why="same name, other place: <caption place> vs <site place>"; when
  find_right_site passes a BUILT site (score >= 0.5) the candidate is moved there instead (its queue entry
  as a _synth_row with sites=[target]; the target's review item when the target is unbuilt - n0686 moves to
  devil-s-dyke-hillfort-q17674160's item). Loop avoidance: a candidate already in the site's own item stays
  out of that site's queue (re-flagged every build - intended). The no-op degrade (catalog/books/index/
  lists absent -> no flags) keeps test_fit_queue_synthetic green UNMODIFIED. test_fit_queue_real must
  re-derive its expected entry set WITH the check. Re-check _pick_site after entry 1 (devil-s-dyke) loses
  its Brighton row. Do NOT touch the lead's three failing assertions (main-side fallout).
- 805 (rebuild + report + drift test): rebuild web/data/fit_queue.json with the wired build; re-export the
  touched data/review/ items and web/data/review.json via fit/review.py export (in-process from the build;
  never hand-edit the page file); write the docs/site_flow.md section (how many of the queue's 117 entries
  were wrong: 15 pairs over 9 sites, with the list; which candidates moved and which went to review with
  the reason; how the check decides - stored fields only, fail-open); add the venv-only drift test (the
  verbatim matcher core in tools/right_place.py stays byte-identical to pipeline/books_match.py - extract
  the shared blocks and compare; system python3 cannot run it, .venv can).
- Then: set this task's Status to split, move its three unticked boxes into the subtasks (box 1 split
  between 804/805, box 2 to 805, box 3 to 804), and leave a short parent hand-over pointing at them.

**Re-read (still apply):**
- tools/right_place.py: load / picture_facts / site_facts / check_pairing / find_right_site / main - the
  six iteration-95 spec deviations (DECISIONS entry) are baked in; do not "fix" them back to the spec.
- tools/fit_queue.py: build / _plans_rows / _item_candidates / _built_sites / _hand_sites / _candidates /
  _synth_row - where the 804 wiring goes; stdlib-only contract (owner's Mac, no PIL).
- fit/review.py: upsert_item (write-once resolved; the item file name follows candidates[0].plan - a moved
  lead candidate can rename the item file, check for clashes) and export (rebuilds web/data/review.json).
- data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json - already holds n0686_1 and
  n0599_1; after 804/805 it must still hold them (they stay in review, never re-enter the queue).
- The lead's in-flight 307b/307c/307d (page work) reads the queue file tolerantly and must never write it;
  if their merge lands after my 805, only the queue file's contents change (not its shape) - expect the
  driver to reconcile, and flag any hit on this task's files.
