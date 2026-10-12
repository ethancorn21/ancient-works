Status: split
# 309: The queue pairs a drawing with the right place, not a namesake
Depends on: 305
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

(2026-10-12, iteration 97, agent c - session 6. SPLIT this task: the parent's deliverable (the module
below) is done and committed; the remaining boxes are carried by 804 (wiring + tests) and 805
(rebuild + report + drift test), each with its own Touches and Depends lines. Box map: box 1 -> 804
(the build wiring) + 805 (the committed rebuild); box 2 -> 805; box 3 -> 804. One deliberate deviation
from the session-5 plan: 805 depends on 309 AND 804 (a rebuild with the wired build cannot run before
804 merges; session 5 had both on `Depends on: 309` only, which would let the driver hand 805 out
early). What each subtask must do is in its own file; this hand-over is the shared ground truth both
read.)

**Shared ground truth (verified this session against the current tree; the DECISIONS entry has the
evidence):**
- Worktree warning (STILL APPLIES): all work belongs in /home/agent/projects/ancient-works.c (branch
  agent/c). The harness once started me in the MAIN worktree (/home/agent/projects/ancient-works),
  which does not contain my branch's files; the three worktrees (.a, .c, main) share one repo
  (git-common-dir ancient-works/.git). Never commit in the main worktree (a PITFALLS entry covers
  the mixup).
- The module tools/right_place.py (696 lines, stdlib only) is COMMITTED on agent/c (fc67bb9; not yet
  on main - it lands when this task closes out as split, which is why 804 depends on 309). API:
  load(root) (catalog/book index/lists all optional - none present = no-op degrade), picture_facts
  (data, plan, row), site_facts(data, site), check_pairing(site, facts) -> (flagged, "same name,
  other place: <caption place> vs <site place>"), find_right_site(data, facts, exclude, top=3,
  min_score=0.5) -> [(score, catalog_rec, words)]; CLI `python3 tools/right_place.py [--all]
  [filter]`. Re-read its docstring first; the six iteration-95 spec deviations (DECISIONS) are baked
  in - do not "fix" them. The verbatim matcher core spans its lines 33-223 (top-level names
  US_STATES, ABBR, UK_ABBR, UK_COUNTIES, GENERIC, norm, name_keys, tokens, place_of, site_place,
  site_toks, name_lookup_keys, row_inputs, score_candidate, BOOK_SCOPE, PLACE_WORDS, phrases) - the
  805 drift test compares those against pipeline/books_match.py; books_match's load_catalog /
  match_row / _key / main are NOT copied (right_place has its own load()).
- Verified on current data (re-ran this session: identical to iterations 95/109): 324 queue
  pairings, 15 flagged over 9 sites, zero false positives - devil-s-dyke <- n0686_1 (BRIGHTON, the
  case; right site devil-s-dyke-hillfort-q17674160, unique pass 0.65, unbuilt as of today) and
  <- n0599_1 (Aysgarth, H1 'Yorks'); bokerley-dyke <- n0599_1; coria + vindomora <- n0354_1 (ARDOCH,
  PERTHSHIRE; no catalog Ardoch -> review); eaton-socon <- n0285_1 (Bath) + n0557_1 (FIRLE HILL) +
  n0558_1/2 (LEWES DOWN); windmill-hill <- the same three Sussex rows; alauna + castle-neroche <-
  n0438_1 (Defences of YORK); clun-castle <- n0575_1 (Devonshire place field). Must-not-flag set
  (Maumbury, leeds-castle, fairlawne, chevening, chiswick-house, the 3 Ohio tied-away sites,
  n0662_1) verified absent. Queue file: {at, entries}, 117 entries, entry 1 = devil-s-dyke-q3307343
  with n0686_1 best. My data area is unchanged since fc67bb9 (the only post-fc67bb9 delta is the
  lead's cf29be2 in tools/site_done.py).
- Suite baseline on agent/c: 3 failed / 77 passed / 1 skipped - the 3 failures pre-exist on main
  (the lead's matcher-fit wiring: test_fit_provenance::test_line_refuses_unmarked_non_auto_doc,
  test_fit_queue::test_save_runs_the_one_site_line, test_site_done::test_site_done_line). Neither
  subtask may edit their assertions or "fix" them; both must leave the rest of the suite green.
- data/review/devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0599_1.json already holds n0686_1 and
  n0599_1 (both stay in review forever). n0686's 805 move targets the hillfort's OWN item (which may
  not exist yet - the upsert creates it when the target is unbuilt); n0599_1 stays where it is.
- The dropped reference spec tasks/309-place-check.md (agent a's, kept as reference) still holds the
  background: the fail-open rule (an unknown place never mismatches; a place that contains the site
  does not), the --live Wikidata human path (pipeline/catalog_wd.py; tests never call it), and "the
  305 queue shape and tests must survive". Its data/fit_place.json committed-verdict design was
  deliberately NOT adopted: the module re-checks from stored fields on every run, which makes a
  separate verdict store unnecessary (DECISIONS iteration 95). If a future session revives that
  design, data/fit_place.json + tests/test_fit_place.py must be added to the relevant task's
  Touches first.

**Re-read (still apply):**
- tools/fit_queue.py: build / _plans_rows / _item_candidates / _built_sites / _hand_sites /
  _candidates / _synth_row - where the 804 wiring goes; stdlib-only contract (owner's Mac, no PIL);
  it imports fit/review the way tools/site_done.py does (sys.path insert of ROOT/fit, then
  `import review`).
- fit/review.py: upsert_item (write-once resolved; the item file name follows candidates[0].plan - a
  moved candidate becoming the lead renames the file; new plans append, same-plan replaces in
  place) and export (the only writer of web/data/review.json; open items only; a one-site run
  records resolution into that item only).
- tests/test_fit_queue.py part 1: the GUARD (dead-socket subprocess), test_fit_queue_synthetic (the
  no-op degrade must keep it UNMODIFIED), test_fit_queue_real (today copies only the four 305
  inputs - no catalog/books - so the check is a no-op in that tree; 804 extends the copy and the
  derivation).
- Agent a's in-flight 307b/307c/307d (page work) reads web/data/fit_queue.json tolerantly and must
  never write it; if their merge lands after 805, only the queue file's contents change (not its
  shape) - expect the driver to reconcile, flag any hit on this task's files in DECISIONS.
