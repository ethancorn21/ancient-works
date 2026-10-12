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

(2026-10-12, iteration 102, agent c - session 11 on the 309 lane. 804 is DONE this
session: the two written-but-unrun tests ran green (after three small tree-building
fixes), the README note landed, all five boxes ticked. Next in the lane: 805.)

Carve state: 309 box 1 (wiring) = 804 DONE; 309 box 3 (namesake tests) = 804 box 4 DONE;
309 box 2 (site_flow report + rebuild) = 805 NOT STARTED. When 805 is done the driver
returns 309 and I tick its three carved boxes.

WHAT CHANGED THIS SESSION (all in agent/c's worktree; 804's boxes 1+2 were already
committed as 077ccb8 before this session):
- tests/test_fit_queue.py: fixed three latent bugs in the written (unrun) code -
  (1) _build_namesake_tree unpacked the site dicts as pairs (`for s, _ in sites` ->
  `for s in sites: ... s["id"]`); (2) the namesake tree never created data/books/lists
  before _save_json (mkdir parents=True on lists); (3) test_fit_queue_real did
  shutil.copy2 into data/books/ before any copytree created that dir (explicit mkdir
  now). Plus one assertion fix: Path.glob is filesystem-ordered, not sorted - the
  namesake test's item-file list now sorts its glob.
- data/review/README.md (804 box 3): the pass-through line names 309's place_reason
  (after the 203a gate_score/why mention) and the Rules list gained a bullet
  (the reason string, written only by tools/fit_queue.py's build; the page's Review
  list shows it in 307c; neither the page nor a human save writes it). No test pins
  the README text (grep confirmed).

TEST STATE (verified by running):
- tests/test_fit_queue.py: 6/6 pass in 52 s (synthetic unmodified; namesake + real new;
  the slow Part-2 line test and both Part-3 browser tests pass).
- FULL SUITE: 83 passed / 1 skipped / 0 FAILED in 133 s. The three pre-existing
  main-side failures (test_fit_provenance::test_line_refuses_unmarked_non_auto_doc,
  test_fit_queue::test_save_runs_the_one_site_line, test_site_done::test_site_done_line)
  were FIXED MAIN-SIDE by the lead's matcher-fit commits (b22a2d2 "matcher fit
  wired into site_done", cf29be2 "matcher spread guard", ...) that landed in agent/c
  via the driver merge 9be7094 this session. Nothing I wrote touched those tests;
  the baseline for "no new failures" is now the green suite.

POST-MERGE BASELINE (re-verified this session, still the ground truth for 805):
- Read-only CLI on the checkout: 324 pairings checked, 15 flagged - identical to
  iterations 100/101. The 15 flags match 805's criteria list exactly (devil-s-dyke <-
  n0686_1 Brighton + n0599_1 Aysgarth; bokerley-dyke <- n0599_1; coria + vindomora <-
  n0354_1; eaton-socon <- n0285_1 + n0557_1 + n0558_1/2; windmill-hill <- n0557_1 +
  n0558_1/2; alauna + castle-neroche <- n0438_1; clun-castle <- n0575_1).
- The merge c5250a4 ("full review export under the current resolution rules", task 220
  on agent/a) touched SIX data/review/ item files (write-once resolved records) and
  web/data/review.json (340 -> 335 open of 341). It changed none of the flags, but
  805's rebuild must be re-derived against the POST-MERGE data: the iteration-100
  note's "5 new item files / 6 upserts" predates that export. The build's upserts
  never write `resolved` (write-once), so the six touched files are only at risk if
  they are also upsert targets - check on the run.

EXACT NEXT STEP (next session: take 805, `Depends on: 804` satisfied by the acceptance
merge of 804's work):
1. Re-run the wired build on the REAL checkout: `python3 tools/fit_queue.py --root .`
   (writes web/data/fit_queue.json + the item upserts into data/review/), then re-export
   in the same run window: `python3 fit/review.py export` (web/data/review.json). Do not
   hand-edit any item file or the page file.
2. Verify the rebuild: 15 flagged pairs disposed per 804's rule (the built right site
   devil-s-dyke-hillfort-q17674160 gains n0686_1 in its queue entry, sites narrowed;
   n0558_1/2 -> the unbuilt a-saucer-barrow item etc. - re-derive the exact list from
   THIS run's flags, do not trust the iteration-100 file list); second build run
   byte-identical (zero churn); export a no-op on re-run.
3. docs/site_flow.md: the namesake section (how many of the queue's entries were wrong
   and the list: site, caption, reason; which candidate moved where vs review; queue
   size before/after - report the ACTUAL numbers of this run; the criteria's "117" is
   the pre-split figure and the queue has moved under the batch tasks since, 803
   precedent: derive, never pin). State how the check decides (stored fields only;
   fail open; the --live Wikidata path is a human re-run, never in the build).
4. tests/test_right_place_drift.py: for each of the 17 top-level names between the two
   VERBATIM markers of tools/right_place.py (US_STATES, ABBR, UK_ABBR, UK_COUNTIES,
   GENERIC, norm, name_keys, tokens, place_of, site_place, site_toks,
   name_lookup_keys, row_inputs, score_candidate, BOOK_SCOPE, PLACE_WORDS, phrases),
   extract the block from both that file and pipeline/books_match.py and assert
   byte-identical. Do NOT edit either file: a real drift is fixed in books_match (the
   source of truth) - if that file is agent a's/lead's in flight, log in DECISIONS
   instead.
5. Full suite green (83/1/0 as of this session), commit "805: ...".

Worktree warning (still true): all three worktrees share one repo; commit only in
/home/agent/projects/ancient-works.c (branch agent/c); data/raw is a symlink into the
shared store - the build never opens images (sizes come from the json files), so a
rebuild cannot write through it, but never run the batch/line tools in the main
worktree.

Re-read (when touching the wiring again):
- tools/fit_queue.py: _apply_flags <-> tests/test_fit_queue.py: _derive_with_check
  must stay in lockstep (same two-phase, sorted flag order, `moved` set,
  pristine-item skip, eligible = built minus hand). A change to one needs the other.
- The six baked-in right_place spec deviations (DECISIONS, iteration 95) are pinned by
  the namesake test's outcomes - changing any rule changes the pinned bytes.
