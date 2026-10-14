Status: done
Depends on: none
# 302f: The matcher station end to end - the line on one hand-fit site's files, no network
Touches: tests/

## Hand-over

(2026-10-14, iteration 127, agent c - **DONE, all six boxes ticked, verified.**
- tests/fixtures/matchfit_station/record.py + records.json + records_unsure.json: committed
  (fde3954, from the iteration-126 live run against ELoFTR 127.0.0.1:8091): 15 /match responses
  each, keyed by sha256 of the exact request body; offline replay identical to live; 0
  live-vs-frozen discrepancies (frozen best six-inch-1st.webp x0.35 61/22/3.62 deg/3.1 m, corner
  58.6 / centre 2.9; the two live runs' response BYTES drifted slightly but parsed candidates
  identical - recorded in the header). Unsure variant: seed 7 permutation lands 8 inliers, page
  457/481.
- tests/test_matchfit_station.py (340 lines, committed 330a9f4): two tests (confident 11-line
  FIT at 22/61 / unsure 8-line "not sure: 8 consistent points (need 10)") run site_done as a
  subprocess on tmp trees, in-process stub on an ephemeral loopback port serving only the
  fixture, RoMa at a dead ephemeral port, pass-through GUARD allowing only the stub port. Both
  pass (55.6 s, zero changes needed on first run this session). Checkout untouched by my test
  (before/after git status identical; in-test hash-surface asserts).
- Full suite: **168 passed, 1 skipped, 0 failed** (499.89 s) - strictly better than the baseline
  /tmp/aw302f_baseline.log (1 failed placement_gestures / 157 passed / 1 skipped): that red was
  agent a's 307bb and is green on main now. No new reds.
- ONE TEAM-NOTE for anyone reading this branch's `git status`: the six modified docs/site_flow/
  PNGs in the working tree are agent a's 307d screenshots (test_owner_check regenerates them on
  every full-suite run); they belong to 307d (its Touches), were left uncommitted here and MUST
  NOT be committed from this branch (my commit covers only the task file + DECISIONS.md).
- If this test ever fails with "the fixture's inputs drifted ... (rerun record.py)": the drift
  detector detected a repo change since the recording - rerun `record.py` in the working phase
  (live ELoFTR at 127.0.0.1:8091 required), commit the refreshed fixtures; the test's expected
  stdouts/counts live in the fixture headers, nothing is hardcoded here. The 210/211/125
  design-trace text below is preserved for reference only.)

**State of iteration 125 (fresh-eyes re-verification, all on the current tree):**
- ELoFTR UP: 127.0.0.1:8091/health = {model: zju-community/matchanything_eloftr, device: RTX
  5060 Ti}; RoMa :8092 REFUSED (exit 7). .venv current (PIL, numpy, skimage all import).
- Inputs verified: n0132.jpg 3367x5050 (mode L); grounds relief.jpg 1600x1600 RGB,
  six-inch-1st.webp 1066x1066 RGBA, os1inch.webp 1600x1600 RGB (3 grounds x 5 windows = 15
  requests); hand doc (4 pairs, by: hand, size present, crop [300,1380,2900,3330],
  at 2026-10-10T17:38:04); plans row (map_box [0.107,0.278,0.857,0.658], size [3367,5050]);
  index row (evidence present, scale_bar true, north 0.0); **propose_for SUCCEEDS in-process
  (coarse False, ground relief, scale_m_px 0.1902, rot_deg 0.0, scale_source bar, note about the
  scale bar, 5 pairs) -> the unsure item candidate carries all six proposal fields, pairs [];**
  site entry drawings 1 / score 1.45 / oldest 1842 / overlays 2; depictions = 3 entries (six-inch
  1842, os1inch 1900, hand plan 1908); NO badbury review item (481 item files, 480 with a site
  field); NO badbury in the published review.json (456 open).
- Frozen held-out (data/matchfit/heldout/results.json, at 2026-10-12T02:58:37) ALL HOLDS: 15
  candidates; best six-inch-1st.webp x0.35 = 61 matches / 22 inliers / rot 3.62 / resid 3.1;
  the EXACT two >=10-inlier responses to permute for the unsure variant: six-inch x0.5 (15) and
  x0.35 (22); the unperturbed six-inch x0.7 (8, rot -43.51) and relief x0.25 (7) keep the best
  at 3..9, so the expected unsure line is "not sure: 8 consistent points (need 10) [six-inch-1st
  .webp x0.7, rot -44]" (unless a seed pushes a perturbed one to 9 - the recorder loops seeds
  7..36 and records the one that lands).
- PRE-CHECK RAN: review.export on a scratch tree (all 481 item files + platefits store +
  sites.json + catalog) = 456 open of 480, **stderr clean** -> the recorder's err=="" asserts
  should hold (n_total counts only items WITH a site field: 480, not 481 - one repo item has no
  site field; the unsure run's counts will be 457/481, the test's baseline export 456/480).
- Full-suite baseline COMPLETE: /tmp/aw302f_baseline.log = **1 failed (test_fit_queue.py::
  test_placement_gestures_and_save_in_the_browser - agent a's 307bb work, on main, NOT mine),
  157 passed, 1 skipped, 324.50 s**. That is the yardstick for "no new reds" (the driver's
  159-passed note is from the pre-eb12e59 tree).

**record.py on disk (read it before running; it is complete):** ROOT = parents[3] (the 124
  correction); the site dir is copied from os.path.realpath (symlink to the lead's
  /home/agent/projects/ancient-works - the 124 correction); build_tree lists in lockstep with
  the test's (tools/, fit/, pipeline/, web/data/{sites,plans,review}.json, web/data/sites/SID
  real copy, data/review all, data/books/index.jsonl, data/commons/files.jsonl,
  data/catalog/sites.jsonl, data/sites/SID/site.json, data/raw/books/.../n0132.jpg,
  data/db/platefits all, unlink badbury doc when delete_hand_doc); live phase patches
  urllib.request.urlopen (records sha256(body)->response JSON AND response-bytes hash per run,
  for the stability verdict) and runs mfh.candidates TWICE; offline replay patches mf.match
  with a fake that rebuilds the exact body (mf._b64 + json.dumps, same key) and patches
  mf.reachable (True only for None/MATCHER_URL) and mf.ROMA_URL (dead ephemeral port);
  in-process site_done runs (importlib, same module objects) on fresh trees T1 (confident) / T2
  (unsure) with contextlib capture; _save uses default=float (ransac rot is np.float64);
  header records input_hashes (hand doc, plan image, site dir, sites/plans/index/catalog rows,
  site.json, data/review combined) for the test's drift detector. Known risks at run time:
  (a) live GPU drift vs frozen (recorded, not fatal - box 1 allows it); (b) the confident run's
  11-line shape / unsure 8-line shape (asserts fail loudly with the actual stdout printed -
  read it, correct the expected shape in the header, re-run); (c) site_entry_equal (score
  1.4535 -> 1.45 is a narrow margin - if False, the test relaxes to field asserts and the
  header records actuals); (d) seed 7 may not land 3..9 (the loop tries up to 36).

**EXACT NEXT STEPS (one or two sessions):**
1. `.venv/bin/python tests/fixtures/matchfit_station/record.py` (needs ELoFTR up; ~2-5 min;
   prints a live-vs-frozen table and both stdouts; on failure it keeps the scratch tree and
   prints the actual stdout). Verify the two fixture JSONs land in tests/fixtures/
   matchfit_station/ (records.json: header.confident; records_unsure.json: header.unsure;
   both: header.frozen_heldout/live_runs/offline_replay/input_hashes + 15 responses).
2. `git add tests/fixtures/matchfit_station && git commit` the recorder + fixtures.
3. Write tests/test_matchfit_station.py per the TEST DESIGN in the preserved 211 block below
   (ephemeral-port ThreadingHTTPServer stub keyed by sha256(body); GUARD passes through only
   (127.0.0.1, GUARD_ALLOW port) - patch socket.socket.connect AND connect_ex, NOT
   create_connection; subprocess [sys.executable, "-c", GUARD, tree/tools/site_done.py, SID],
   cwd=tree, env MATCHER_URL/ROMA_URL(dead)/GUARD_ALLOW; two tests, confident + unsure, with
   the drift-detector preconditions and the file-effect asserts as designed; the unsure test's
   baseline = build_tree WITHOUT doc deletion, in-process review.export must give
   (n_open-1, n_total-1) of the fixture's recorded 457/481, i.e. 456/480).
4. Run my test until green; FULL suite (`.venv/bin/python -m pytest -q -p no:cacheprovider`);
   diff failures against /tmp/aw302f_baseline.log (only the placement_gestures red allowed);
   tick the six boxes as verified; commit "302f: ...".

**Preserved 210/211 design (valid unless superseded above):**

(2026-10-14, iteration 124, agent c - re-verified the ENTIRE 210/211 design against the current
merged tree (eb12e59: agent a's 212/236a/307d work on main): every line-shape, module behavior
and data fact holds; TWO corrections found (below). No code written this session (context limit
before the rewrite). ON DISK NOW: only

(2026-10-13, iteration 211, preserved for the complete design - the recorder design in the next
paragraph and the test design that follows are still valid and were re-verified this session;
detail entries 210/211 in DECISIONS.md carry the full trace.)

**Corrections from this session (apply when writing record.py):**
1. ROOT in record.py must be `Path(__file__).resolve().parents[3]` - the old note's `parents[2]`
   is tests/ (the file sits in tests/fixtures/matchfit_station/). The committed stub has the
   parents[2] bug; rewrite it, don't patch it.
2. web/data/sites/badbury-rings-q798831 symlinks to /home/agent/projects/ancient-works (the
   lead's original project dir): copy os.path.realpath of it (a real dir lands in the tree).
   (The 210 note's "another checkout" = this dir; same fact.)

**Re-verified this session (fresh eyes, current tree):**
`tests/fixtures/matchfit_station/record.py` as a TRUNCATED STUB - it ends with a bogus line
`import matchfit_holdout_dummy  # noqa: F401` and has no body: REWRITE IT FROM SCRATCH (the
design is complete below; the stub is worthless except for its docstring). No tests run yet;
I started the full-suite baseline in the background (nohup, log /tmp/aw302f_baseline.log, was
still running at session end - CHECK IT; if incomplete, rerun: `.venv/bin/python -m pytest -q
-p no:cacheprovider > /tmp/aw302f_baseline.log 2>&1` ~5 min) before adding my test, so I can
diff new reds. Nothing else in the tree changed.)

**Re-verified this session (fresh eyes, current tree) - all of the following still true:**
- matchfit_heldout.candidates(root, site, row, url) returns ALL 15 candidates (matches, inliers,
  rot, resid_m, pairs in row frame; rot/resid only when ransac kept >=3; seconds each). It calls
  mf.match/mf.ransac/mf._merc - patching mf.match makes it a faithful offline replay. Importing
  it is safe (it imports inkfit_heldout, which 302e fixed; no golden_docs call at import).
- batch_us.write_doc book row: {site, plan, crop: _crop_px(row), pairs: _norm_pairs(8), label,
  title, cite, at(_now), auto:True, score:round(resid_m,1), by:"agent", ia, file, book} then
  matchfit.run appends fitter:"matcher", matcher:{model, inliers, matches, ground, window,
  rot_deg 2dp, spread [3dp,1dp]} (the fit_row all-inliers spread, in the pairs frame). Key order
  as written; the test compares dicts (order-free) with "at" removed.
- plan_fit.build(doc, root): book doc without "size" key -> size = image size (3367x5050) ->
  fs=1.0; crop _crop_px [360,1404,2886,3323] (2526x1919 > MAX_PX 2400 -> LANCZOS-resized ~
  2400x1818); saves plan_<plan>.webp (quality=80, method=6) + _ink.webp (depict.make_ink,
  quality=85); REPLACES the same-file depiction in depictions.json (remove-then-append, stable
  sort by year); prints `{sid} {plan}: 8 pairs, similarity, residuals m [...]` (one residual per
  pair, 1dp); set_drawings. The matcher doc has NO "model" key -> build prints "similarity" via
  the default; source_line for agent+auto+score -> "Fitted automatically by the batch on 8
  matching points; one rotation and scale fits them within {ceil(resid.max())} m (gate score
  {score} m)".
- build_site.marks(s, root): recomputes drawings/score/oldest/overlays from depictions. I
  hand-computed: overlays = six-inch (1842 <= 2026-150, err 8, not drawing) + plan (1908, rms of
  its resid_m, drawing); score = round(best + 0.25*rest, 2). Hand fit rms 5.99 -> score 1.45
  (= repo's value). Matcher residuals ~3 m -> rms ~3.2 -> 1.18/(1+0.001) + 0.25*1.0989 =
  1.4535 -> round -> 1.45 STILL. But this is a narrow margin: THE RECORDER MUST ASSERT the
  post-run tree site entry == the repo entry (parsed); if score/oldest/overlays move, relax the
  test to field-level asserts (drawings==1, others recorded in the fixture) and say why in the
  header.
- propose.propose_for(site_id, plan_id, root=ROOT): ROOT is the MODULE constant of whichever
  copy is imported. In the recorder's IN-PROCESS site_done run, fit/propose.py is the CHECKOUT's
  (site_done inserts checkout fit/ on sys.path; my recorder's import is the same module object)
  -> it reads checkout data/books/index.jsonl + plans.json + sites.json; the subprocess reads
  the tree copies. Same bytes (copied at the same moment) -> same result. The index row has
  scale_bar true + scale_text "0 100 200 300 400 500 Scale of Feet" + a scale_bar blank_box +
  north_arrow true angle 0.0 + evidence dict -> propose succeeds (verify in recorder; run_sites
  wraps it in try/except (ValueError, KeyError) -> prop None -> entry coarse:True either way -
  the fixture records whatever actually happens).
- review.export(root, site_id): reads EVERY item file + sites.json + catalog for names; records
  "resolved" into item files ONLY when a resolving doc exists without a recorded resolution AND
  (site_id is None or the item's site == site_id); publishes open items (name-sorted) to
  web/data/review.json {"at", "items"}; returns (n_open, n_total). Repo state is consistent
  (306d ended with an export), so the scoped export writes NO item files - the recorder must
  verify (hash all item files before/after its in-process unsure run) and the test asserts it.
- Exact expected stdout, CONFIDENT (11 lines, in order):
  1 `fit  no model given: unfitted pictures (if any) go to the review item as "no model answer"`
  2 `site badbury-rings-q798831: the one-site line (fit -> sync -> entry -> review)`
  3 `{sid}  {title}: FIT (eloftr) 22/61 points on six-inch-1st.webp x0.35, rot 3.6 deg, {m:.2f} m/px, residual 3 m`
  4 `fit  matcher: fit written (badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json)`
  5 `fit  1 candidate picture(s): 1 fitted (doc), 0 in the review item -> no batch run needed`
  6 `badbury-rings-q798831 earthworkenglan01allcgoog_n0132_1: 8 pairs, similarity, residuals m [...]`
  7 `sync Badbury Rings, Wimbome, Dorset: synced to the map (plan_earthworkenglan01allcgoog_n0132_1.webp, 8 pairs, gate 3.1 m)`
  8 `entry  web/data/sites.json: drawings 1 -> 1`
  9 `review no review item (every picture is a fit)`
  10 `  Badbury Rings, Wimbome, Dorset (earthworkenglan01allcgoog_n0132_1): synced to the map, gate 3.1 m`
  11 `done`
  (3 and 7/10 numbers come from the LIVE replay; 3-5 order verified in code: run() prints FIT
  before returning paths; _fit prints "fit written" after; the no-batch line is the
  need_fit-False branch. Lines 6-7: build prints before _sync_doc's synced line. Line 10: the
  summary's `pid in docs` branch, sc from doc["score"].)
- Exact expected stdout, UNSURE (8 lines - CORRECTION: the 210 note said 9; the trace gives 8):
  1, 2 as above; 3 `{sid}  {title}: not sure: {N} consistent points (need 10) [{ground} x{window}, rot {rot:.0f}]`
  (N 3..9, frozen expectation 8 from six-inch x0.7 rot -44); 4 `fit  Badbury Rings, Wimbome, Dorset: sent to the review queue (no model answer)`;
  5 `entry  web/data/sites.json: drawings 1 -> 1`; 6 `review badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json: 1 candidate(s), open; page now has {n_open} open of {n_total} items`;
  7 `  Badbury Rings, Wimbome, Dorset (earthworkenglan01allcgoog_n0132_1): sent to the review queue (no model answer)`;
  8 `done`. (No "fit written", no no-batch line, no build/sync lines: the batch runs because
  uncovered is non-empty; _sync loops over zero docs.)

**RECORDER DESIGN (write it from scratch; .venv/bin/python, working phase only):**
- Header constants: ROOT = Path(__file__).resolve().parents[2]; SID/PLAN; MATCHER_URL = env or
  http://127.0.0.1:8091; sys.path.insert fit/ and pipeline/; import matchfit as mf,
  matchfit_heldout as mfh, batch_us, propose, review (all the same module objects site_done
  gets, so patches apply). GET live /health first (record the answer).
- build_tree(dest, delete_hand_doc): copy tools/ fit/ pipeline/ (ignore __pycache__); web/data/
  {sites,plans,review}.json; web/data/sites/SID via os.path.realpath (real copy - it is a
  symlink to another checkout); data/review (all); data/books/index.jsonl; data/commons/
  files.jsonl; data/catalog/sites.jsonl; data/sites/SID/site.json; data/raw/books/
  earthworkenglan01allcgoog/full/n0132.jpg; data/db/platefits (all), unlink the badbury doc if
  delete_hand_doc. (Same list the test uses - keep them in lockstep.)
- LIVE phase (run on a scratch tree so live and offline read identical files): patch
  urllib.request.urlopen: on POST */match record {sha256(req.data): parsed response JSON} and
  also the raw bytes (for the byte-stability verdict), return a wrapper with .read() -> raw
  bytes (matchfit's json.load keeps working); everything else passes through to the original.
  Run mfh.candidates(tree, site, row, MATCHER_URL) TWICE. Assert: same 15 keys in the same
  order both runs; record byte-identical verdict (expect True: same weights/GPU/inputs).
  Pair the i-th request (call order) with the i-th candidate to get key -> (ground, window).
- Offline replay: mf.match = fake(records) - rebuilds the body EXACTLY as match() does
  (json.dumps({"image0": mf._b64(a), "image1": mf._b64(b), "threshold": 0.2, "max_side":
  1024}).encode(); same key), KeyError if absent, else np.array(r["keypoints0"]).reshape(-1,2),
  same for 1. Also mf.reachable = lambda url=None: (url is None or url == MATCHER_URL) and
  mf.ROMA_URL = "http://127.0.0.1:%d" % dead_port (bind-then-close; reassign the module attr -
  env is read at import time). Run mfh.candidates offline -> must equal live run1 per
  candidate (record). Compare each of the 15 with the frozen heldout (ground, window, matches,
  inliers, rot, resid_m; frozen file has rot/resid only when present) -> discrepancies list;
  live==frozen expected (22/61/x0.35/3.62/3.1 at six-inch x0.35; if the GPU drifted, record and
  proceed with live numbers - box 1 allows it).
- CONFIDENT in-process run: fresh tree T1 (doc deleted). Import site_done via importlib from
  ROOT/tools/site_done.py; mf.match=confident-fake, mf.reachable as above; capture
  sd.main([SID, "--root", str(T1)]) rc/out/err with contextlib.redirect_stdout/stderr; restore
  patches after. ASSERT rc==0 and err=="" (if err non-empty: likely a missing catalog name -
  check what it says; the catalog copy should prevent it). Then record: doc_fields = parsed
  tree doc minus "at" (assert it has auto/by/fitter/matcher and at is present); spreads:
  fit_row's = doc matcher.spread (unrounded values: recompute mf.spread on the 8 pairs and on
  all inliers via the offline fit_row) + the _sync_doc guard values (ratio, sd on the doc's 8
  pairs) + pass/fail (expect pass: 22 inliers spread over the plan); expected_stdout =
  out.splitlines() (assert == the 11-line shape above, esp. lines 3 and 7 values); expected_
  depiction = tree depictions.json plan entry minus fit.at; repo input hashes (hand doc,
  n0132.jpg, depictions.json, site-dir file list, extracted plans row, extracted site entry,
  extracted index row, data/catalog/sites.jsonl, data/review as one combined hash of the
  sorted (name, sha256) list) for the test's drift detector.
- UNSURE: from the confident records, for EVERY response whose live candidate has inliers >= 10
  (expect exactly two: six-inch x0.5=15, x0.35=22), keypoints1 = [k1[i] for i in
  np.random.default_rng(seed).permutation(len(k1))], seed 7 first (next seed if the final best
  still >= 10; record the seed). Offline fit_row -> best must land 3..9 inliers (frozen
  expectation: 8, six-inch x0.7, rot -43.51; the unperturbed x0.7 stays 8, relief x0.25 stays
  7, os1inch 0). Fresh tree T2 -> in-process run -> ASSERT rc==0, err=="", and that NO item
  file changed except the new data/review/SID.PLAN.json (hash all before/after - if another
  changed, the repo queue is inconsistent: record and adjust the test's item assertions). From
  T2: expected_item = parsed new item (site, candidates [the one _entry: plan, title, url
  books/ia/file, evidence from index.jsonl, pairs [] or proposal pairs? - _entry with pairs=[]
  writes e["pairs"]: [], plus the proposal's coarse/ground/scale_m_px/rot_deg/scale_source/
  note fields when not None, why "no model answer"], no_picture_found None, resolved None);
  expected_review_counts = n_open/n_total parsed from the review line (over the 482-file tree);
  expected_stdout = out.splitlines() (8 lines). Both fixtures: {"header": {...},
  "responses": {15 keys -> response JSON}}, indent=1, no trailing newline (project _save_json
  convention), committed under tests/fixtures/matchfit_station/.

**TEST DESIGN (tests/test_matchfit_station.py):** tmp tree = recorder's build_tree; in-process
ThreadingHTTPServer on 127.0.0.1:0 (handler: GET /health -> header's health JSON; POST /match
-> sha256(body) lookup in the fixture, 500 {"error": ...} if absent; count every request for
assertions; log_message silenced); dead RoMa port = bind-then-close; GUARD = the test_site_done
one EXCEPT: patch socket.socket.connect AND connect_ex (NOT create_connection - it must flow
to the patched instance method) to pass through only ("127.0.0.1", stub_port) (port via env
GUARD_ALLOW; the guard reads it) and raise AssertionError otherwise - RoMa's dead-port connect
raises inside reachable()'s try -> except Exception -> False, deterministically. Subprocess =
[sys.executable, "-c", GUARD, tree/tools/site_done.py, SID], cwd=tree, env MATCHER_URL/
ROMA_URL/GUARD_ALLOW + PYTHONIOENCODING, timeout 600.
- confident test: preconditions (repo has the hand doc, no badbury review item, no badbury entry
  in repo review.json, fixture's input hashes match the repo now - else "drift: rerun
  record.py"); before = _hash_all(checkout: site dir via realpath, data/db/platefits, data/
  review, data/books/index.jsonl, data/commons/files.jsonl, data/catalog/sites.jsonl, data/
  sites/SID/site.json, web/data 3 files, tools/fit/pipeline) (test_site_done's _hash_all
  idiom); run; assert rc 0, stderr == "", stdout == header expected_stdout; tree doc minus at
  == doc_fields (+ at present); depictions plan entry minus fit.at == expected_depiction and
  fit.at == doc's at, map entries parsed-equal to the repo's; plan_*.webp pair exists and
  DIFFERS from the repo copies (rebuilt, different crop/pairs); tree sites.json parsed-equal to
  repo's; tree web/data/review.json BYTE-identical to repo's (export never ran); data/review:
  same file set + every file byte-identical (no new item); stub served exactly 15 /match (all
  fixture keys) + >=1 /health and nothing else; _hash_all(checkout) == before.
- unsure test (fresh tree, records_unsure): baseline = build_tree WITHOUT doc deletion; in-
  process: import checkout fit/review.py, n_open, n_total = review.export(str(baseline))
  (baseline items = its published review.json); assert no badbury in baseline items, and (n_
  open, n_total) == fixture's recorded counts (drift detector: fail with "queue drifted since
  the fixture: rerun record.py" if not); run subprocess; assert rc 0, stderr == "", stdout ==
  header expected_stdout (the not-sure line verbatim); NO doc for the plan in the tree store;
  new item file parses equal to expected_item; depictions.json and both plan_*.webp BYTE-
  identical to the repo's (no build); tree sites.json parsed-equal to repo's; published review
  items == sorted(baseline_items + [{site, name (repo's), lead PLAN, candidates, no_picture_
  found}], key=name.lower) (assert the name is unique in the queue first); data/review: all
  repo files byte-identical + exactly one new file; checkout hashes unchanged.

**Then:** run my test until green; FULL suite; diff failures against /tmp/aw302f_baseline.log
(the 306d-era baseline 10 failed/130 passed/1 skipped of 141 is the yardstick; agent a's
212/307d in-flight work is on main - reds in their files are not mine); tick boxes as verified
(box 1 fixture + header incl. frozen 22/58.6; box 2 ephemeral stub + dead RoMa + deleted doc;
box 3 guard variant; box 4 confident; box 5 unsure; box 6 checkout untouched + no new reds);
commit "302f: ...". The 210 hand-over's detail blocks (site facts, code traces) are still true
where this one does not supersede them; its "9 expected lines" is corrected to 8 above.

**Pitfalls:** results.json "docs" is a DICT keyed by doc id (candidates in grounds-then-
windows order); plans.json is a cols/rows table; web/data/sites/<id> is a symlink - copy
realpath; the batch _entry for a book row carries the evidence dict (copy index.jsonl) or the
item won't match; MATCHER_URL/ROMA_URL are read at matchfit IMPORT time (reassign the module
attributes in the recorder; env works in the subprocess); site_done's imports yield the SAME
matchfit/batch_us/... module objects the recorder imported (sys.path same paths) - patches
apply to both; pytest.ini keeps only FAILED tmp dirs (a failing run's tree survives in
/tmp/pytest-of-agent for debugging); the in-process baseline export in the test writes only
into its own baseline tree (never the repo).

**Re-read (fresh eyes):** fit/matchfit.py match/fit_row/run (request build = fixture key);
tools/site_done.py _fit/_sync_doc/_review (branch line shapes); fit/review.py export (scoped
writes, name fallback, resolved side-effect); tests/test_site_done.py (tree + hash idiom);
fit/propose.py propose_for (what fields the entry gains when it succeeds).

## Goal
Parent box 4: "Wired into tools/site_done.py's fit step; a test runs it end to end on one
hand-fit site's files (no network)". The wiring exists (site_done._fit calls matchfit.run
first on every undocumented picture when ELoFTR answers /health - tools/site_done.py:78-84;
_sync_doc applies the spread guard to fitter:"matcher" docs before any build), but it has
never been tested: `grep matchfit tests/` is empty, and tests/test_site_done.py runs the
line on stonehenge (not a hand-fit site) with the matcher unreachable. This task adds the
test: a throwaway copy of one hand-fit site's files in a tmp root, an in-process stub
serving recorded ELoFTR responses on an ephemeral loopback port (team rule: no fixed
ports), and `tools/site_done.py --root <tmp>` driven as a subprocess whose sockets die
loudly except to the stub.

The site is badbury-rings-q798831: a hand-fit site (the golden's 21 include
badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1) with exactly one candidate
picture (earthworkenglan01allcgoog_n0132_1, n0132.jpg) and no review item. All ground
images are local (web/data/sites/badbury-rings-q798831/: relief.jpg, six-inch-1st.webp,
os1inch.webp). Its frozen ELoFTR held-out run (data/matchfit/heldout/results.json, at
2026-10-12T02:58:37.021604+00:00) gave this plate the best matcher result of the 21:
six-inch-1st.webp x0.35, 61 matches, 22 inliers, rot 3.62 deg, 58.6 m corner / 2.9 m
centre - far past judge()'s bar (10 inliers, 30 deg). Because the site has ONE candidate,
a confident fit empties `uncovered`, so the vision batch never runs at all: the only
network the line touches in the test is the stub itself.

## Acceptance criteria
- [x] Committed fixture from a one-off working-phase run against the live ELoFTR
      (127.0.0.1:8091; verified reachable at iteration 208): the raw /match responses for
      every (plan image, ground image, window) pair of badbury's fit_row, keyed by the
      sha256 of the exact PNG bytes matchfit.match sends (plus threshold 0.2 / max_side
      1024), under tests/fixtures/matchfit_station/ (new directory; the JSON carries a
      header recording run date, matcher model, and the frozen held-out numbers the
      replay must reproduce - badbury 22 inliers / 58.6 m on six-inch x0.35). If the live
      replay disagrees with the frozen checkpoint, record the discrepancy; regenerate
      only if the matcher's output is stably different.
- [x] tests/test_matchfit_station.py (new file): starts the stub in-process on an
      ephemeral loopback port (conftest.py's server idiom, bind port 0), points the
      subprocess's MATCHER_URL at it and ROMA_URL at a dead ephemeral port (RoMa
      deterministically absent: matchfit.run's second pass skips), and runs
      tools/site_done.py --root <tmp> as a subprocess (the guard runs the tree copy of the
      script with cwd=tree, so the tree IS the root). The tmp root copies badbury's
      files (the site dir, the site's sites.json entry, the plans row, the golden
      document) with the document DELETED so the single candidate is uncovered.
- [x] Subprocess socket guard (a variant of tests/test_fit_queue.py's GUARD): any
      connection attempt to anything other than the stub's loopback port fails loudly -
      that is the "no network" proof.
- [x] Confident branch: the stub replays the recorded 22-inlier six-inch candidate (and
      the rest of badbury's recorded responses). The test asserts: site_done exits 0;
      the subprocess stdout carries the matcher's FIT (eloftr) line for n0132_1; the tmp
      root gained a document badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json
      with by:"agent", auto:true, fitter:"matcher" and its matcher block (model, inliers,
      matches, ground, window, rot_deg, spread); the line's sync built it into the tmp map
      (the spread guard passes on the recorded spread, so no refusal); exit code 0.
- [x] Unsure branch (a fresh tmp copy, fixture variant with the best candidate under 10
      inliers): the test asserts: the subprocess stdout carries the matcher's
      "not sure: N consistent points (need 10)" line for that candidate (N=8, verbatim from
      the fixture header, never hardcoded); no document is written for it; the candidate
      appears in the tmp review item with a reason (the batch's own, "no model answer",
      from the socket-dead vision pass) plus the scale-bar proposal; no map overlay for it;
      exit code 0 - that is the parent's box-3 contract "unsure goes to the queue with the
      reason, never to the map", end to end.
- [x] The real checkout stays byte-identical after the test (the tmp root is the only
      writer: before/after `git status` of a lone test run identical, in-test hash-surface
      asserts on every data surface), and the suite has no new reds against the newest
      driver loop-start note - it has NO reds: 168 passed / 1 skipped / 0 failed vs the
      baseline's 1 failed (agent a's 307bb placement_gestures, since fixed on main) / 157
      passed / 1 skipped. (The six modified docs/site_flow/ PNGs in the full-suite working
      tree are agent a's 307d screenshots, regenerated by the merged 307d test, not by mine.)

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/207a-horsley.md` (blocked) - hand-over: (2026-10-13, iteration 203, agent c - the main merge brought the owner's "Stop 207" onto this
- `tasks/207b-maclauchlan.md` (blocked) - hand-over: (2026-10-13, iteration 204, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207c-roy.md` (blocked) - hand-over: (2026-10-13, iteration 205, agent c - NO work on this task. The driver auto-put it back to
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/212-cover-final.md` (split) - hand-over: (2026-10-13, iteration 234, agent a - **212a done, 212b done (lead), 212c done - the
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-13, iteration 208, agent c - the driver returned the parent: all existing subtasks
- `tasks/306-agent-fits-look.md` (split) - hand-over: (2026-10-12, iteration 134, agent c - FIRST session; investigation only, then SPLIT. Session hit the
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/230-roman-merge-rerun.md`
- `tasks/235-placement-test-dep-pick.md`
- `tasks/302f-matcher-station-test.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 302 DECISION: split into 302a (method module), 302b (one-shot held-out table), 302c (decision + site_done wiring + e2e test), 302d (Stonehenge run) - the method is ink-vs-relief, never model coordinates
    First session on this task (iteration 74): investigation only, no code written. The split files carry the
    per-step acceptance boxes; the parent hand-over carries the verified facts and the frozen design.
    Method choice (evidence, not hope): matching points = the plate's own ink (autowalls' frozen extractor,
    docs/autofit.md section 3) matched against the site's bare-earth relief with fit_plate's ridge-contrast
    objective (the 2026-10-09 Fudge proof: commit 16c6b9a) and autofit.py's coarse-FFT + refine search from a
    fit/propose.py seed (scale bar / ratio text / picture size, north arrow / north-up, catalog centre). The
    2026-10-10 pre-registered run (docs/autofit.md, FAIL 0/40 seeds) showed: the search works, the relief score
    has false peaks, random-placement nulls cannot accept/reject, and template junk is the binding problem -
    so the design keeps the proven machinery, adds a per-piece keep/drop step (model-classified where the AI
    box is reachable, deterministic no-model fallback otherwise), a search-matched null (same search on a
    scrambled template and a shifted DEM box, whichever scores higher), and the frozen gate + fabrication
    check on the method's own ink pairs as acceptance layers. The 10-10 test sites (US 1848 plates) are none
    of the 19 held-out sites, so their failures are warnings, not predictions.
    Verified by running this session:
    - All 19 hand-fit sites have 0.5-1 m DEMs reachable from this VM: dem_sources probe -> ea (13 England
      sites, EA composite DTM 1 m), usgs (serpent-mound, cahokia, aztalan, mound-bottom), ign (bergues,
      camp-d-attila); all returned finite data for the site box.
    - Plate images: 20 of 21 present in this VM's data/raw (9 books pages under data/raw/books/<ia>/full/,
      11 commons bigs under data/raw/commons/big/); the lead's new maiden-castle c_c20ff6b1f16d173d has only
      its 1280 px thumbnail here - plan_fit.load_picture fetches the big on demand (network, working phase).
    - The AI box is NOT reachable from this VM (127.0.0.1:18080/18083 refused; the 10-10 Qwen calls ran on
      the Mac through its tunnel). Consequence: the model step (page-triage boxes, piece labels) must be
      injectable with a deterministic no-model fallback; the held-out run here is the no-model variant.
    - scikit-image is missing from requirements.in/.txt and from this .venv, but autowalls.py needs it
      (Frangi + skeletonize); 302a pins it (001's archive note anticipated exactly this). .npy is
      gitignored globally, so committed relief seeds are .npz under data/inkfit/ (only data/autofit/*.npz
      is ignored); data/sites/<id>/dem.npy stays a local cache built in the working phase.
    - The lead's 21st hand fit (main 984b1b4, merged from vm/main) is the no-auto version of
      maiden-castle-q1232816.c_c20ff6b1f16d173d.json (3 hand pairs, crop [165,256,895,663]); my branch still
      carries the pre-merge auto version until the driver's next sync. Held-out set = the original 20 golden
      docs + this one = 21 rows over 19 sites (old-sarum and maiden-castle each have 2). The golden files
      (hand_fit_docs.sha256, hand_fit_sites.txt) stay at the original 20/19 and are never edited.
    One trap recorded for the builders: plan_fit.fabrication_pattern clause (b) (1D ladder) fires on >=3
    anchors sharing one coordinate (spread <= 2 px) with near-arithmetic spacing on the other - evenly
    stepped points along one straight wall would trigger it, so emitted ink pairs use irregular steps or
    junction/feature points, never a fixed stride on a straight run.

### 2026-10-13 302 DECISION: iteration 208 - the driver returned the parent (all existing subtasks terminal); fresh verification ticked boxes 1-3 and left 4/5 to subtasks 302e/302f/302g, which this session actually WROTE (the 207 hand-over claimed they were created, but no such files existed on disk)
    The driver's post-207 commit 745056e touched only tasks/302-autofit-real.md, so the 207 hand-over's "created subtasks 302e/302f/302g" was a false claim (the session was cut before the writes landed). This session re-verified all five boxes from the current tree and ticked 1-3:
    - Box 1 met: fit/inkfit.py (302a: ink skeleton vs LiDAR relief, ridge-contrast objective, frozen no-model variant, model injectable) + the lead's fit/matchfit.py (pretrained MatchAnything ELoFTR/RoMa correspondences between the plan and relief/aerial/OS sheets - points computed from the images, never a vision-model list). The line is matcher-first (site_done._fit:78-84). The lead's newer fit/matchfit2.py (two-stage located windows), fit/matchfit_queue.py (rule sweep) and fit/surveyfit* are lead work, outside the boxes.
    - Box 2 met: docs/site_flow.md line 129 (pre-registered protocol, "the method never sees the hand fits", the 21 docs, frozen config) + the 21-row table at lines 226-248 (corner errors 231.2-2203.6 m as measured; fabrication column silent on every placed fit; the lone non-silent cell is camp-d-attila "not enough wall ink (2 candidate points, need 4)"). Checkpoint re-verified by script: 21 entries == the golden's 21 exactly, 0 errors, 0 re-runs, all "no-model", fixed at 2026-10-11T22:47:37.081160+00:00. The matcher's own held-out tables (data/matchfit/heldout{,_located,_roma}; docs/matchfit.md: ELoFTR 7/21 accepted, 0 wrong, worst centre 55 m) re-verified present.
    - Box 3 met: fit/matchfit.judge() - ELoFTR inliers>=10 & |rot|<=30, RoMa fraction>=0.4 (set on the held-out + queue tables, docstring cites docs/matchfit.md sections 7-8), both plus the spread guard (ratio>=0.1, sd>=20 px); "not sure: ..." reasons; matchfit.run writes a document only when judge is silent, so unsure fits never become docs and never build; second line of defence at site_done._sync_doc:204-206 (spread guard on fitter:"matcher" docs before build).
    - Box 4 half-met -> 302f (file written): wiring met (site_done._fit:78-84) but `grep matchfit tests/` is empty - the matcher station has never been exercised by a test. 302f's site is badbury-rings-q798831: exactly one candidate picture (a confident fit empties uncovered, so the vision batch never runs in the test - the only network is the ephemeral-port stub), all ground images local, its ELoFTR held-out best re-verified this session (six-inch-1st.webp x0.35, 61 matches, 22 inliers, rot 3.62, 58.6 m corner / 2.9 m centre from data/matchfit/heldout/results.json).
    - Box 5 not met -> 302g (file written): no post-matcher Stonehenge run anywhere; stonehenge-q39671 = 0 drawings / 1 overlay / 14 candidates (7 fabricated-line, 4 median-residual, 2 feature-based, 1 no-model-answer), no matcher doc; the only screenshot (stonehenge.png, 2026-10-11) predates the matcher. 302g runs the current line live (ELoFTR up, RoMa down -> ELoFTR-only run), checks whatever lands in a browser against the sarsens (301/306 shot.mjs pattern), and records it plainly - "places nothing" is a passing answer.
    Live defect re-confirmed by running: fit/inkfit_heldout.py table dies "expected the 20 golden hand-fit documents, found 21" (303's re-key 1f562ca); run/selfcheck share the function. Resolution of the 207 Re-read: matchfit_heldout does NOT call golden_docs() (it uses ih.GOLDEN, ih.MAIDEN, ih.hand_similarity, ih.corner_metrics, ih.precheck; its own doc_ids reads the golden directly) - so the 302e fix scope is exactly inkfit_heldout's golden_docs/doc_ids/precheck; matchfit_heldout's one-shots are spent too and its data/matchfit/ checkpoints stay read-only.
... (0.4 KB more: `grep -n -A 200 -F '## 2026-10-13 302 DECISION: iteration 208 - the driver returned the parent (all existing subtasks terminal); fresh verification ticked boxes 1-3 and left 4/5 to subtasks 302e/302f/302g, which this session actually WROTE (the 207 hand-over claimed they were created, but no such files existed on disk)' DECISIONS.md`)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)
- Re-verified the 160 hand-over's numbers with fresh measurements BEFORE deleting (AGENTS.md: check facts by running code). Confirmed: 8 pairs = 4 distinct points on a 100-px grid ladder (three on u=100; the 200-px and 100-px lat steps span 0.0053896/0.0017967 deg = 1.5:1 per pixel, no similarity can hit; the page's simFit (exact port) gives resid 10.9-39 m, 2.634 m/px, +1.06 deg - identical to the committed shot's [eval] line). CORRECTIONS to the 160 hand-over: the real hillfort is ~20 m NW of the site point (not '+22 E / -55 N'), its hachured ring is ~80-90 m across (not ~130 m), so the drawn ring (277-342 m at 2.634 m/px, centred at raw (240-248,115) -> (-3.5187, 51.0370) = E -218..-239, N +531) is ~3.5x too big and 554-582 m N-NW (N23-25W) of the real one - on a small hachured wood hill. The 160 '~2x / 535-576 m' survives as a range (540-576 -> 554-582), the direction and the verdict are unchanged. Extra independent check: the plate's own 'SCALE OF FEET 0-300' bar measures ~1.45 m/px vs the fit's 2.634 (1.8x). Distances must be geographic (dx=dlon*111194.9266*cos(lat0), dy=dlat*110900), NOT raw Mercator units (my first pass computed 916 m for the 576 m distance that way).
- Executed the 303 way exactly as 306c did (fit/review.py API, no hand-edited JSON): upsert_item(root,'bury-castle-q5001077',[entry]) with entry = {plan, title, url, pairs (the doc's 8), coarse:false, evidence (from the data/commons/files.jsonl row: rec evidence/1, kind category, checked 2026-10-10, site_cat/file_cat 'Bury Castle, Somerset'), label '1911', cite, ref, size, place_reason '306d audit 2026-10-12: ... Document deleted.'} appended to the existing item (lead n0136_1 kept first, filename unchanged), then deleted data/db/platefits/bury-castle-q5001077.c_de779031cda8a0dc.json, then export(root,'bury-castle-q5001077') (333 open of 346). Only 3 files changed (D doc, M item, M web/data/review.json) - no other site's item touched; the site was already covered for the union check (its item was already open in the page file before the upsert).
- Wrote the 306d block (header + the bury-castle line) into docs/site_flow.md after the 306c block (header is tense-neutral: 17 more lines to come in batches; box 1 ticked - 36 shots re-listed this session).
- TESTS (full suite, main checkout, --ignore=tests/test_gate.py, -p no:cacheprovider, with my changes): 10 failed, 130 passed, 1 skipped (251 s). The 10: test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (FAILED at the seed check, dep:null) + 9 that are agent a's in-flight work already on main (test_merge new_sites_are_complete/new_site_golden_samples = 211's open 222-228 gate; src_artists/limes/mackenzie/numancia/wiltshire_stukeley stage+check tests = the 224 family). Baseline in my task file (123/1, 2026-10-12) is STALE - main has since merged 211/223/224/307 work and the suite grew to 141 tests.
- A/B attempt 1 (worktree at HEAD in /tmp/aw306d_ab): INVALID - web/data/sites/ is mostly gitignored (58 tracked files vs 389 site dirs in the main checkout; the per-site web data + data/raw are local build artifacts), so a fresh worktree lacks stonehenge etc. and fails 3 tests deterministically (site_done_line FileNotFoundError '/tmp/aw306d_ab/web/data/sites/stonehenge-q39671', fit_provenance line_refuses_unmarked_non_auto_doc, fit_queue save_runs) that pass in the main checkout; its placement_gestures 'vacuous ERROR' there is also unprovable (no local depictions). PITFALLS candidate: never A/B this project in a bare worktree/checkout - do it in the main checkout with the changed files temporarily at HEAD. (The worktree is still registered; remove it: git worktree remove --force /tmp/aw306d_ab && git worktree prune.)
... (1.9 KB more: `grep -n -A 200 -F '## 2026-10-12/13 306d DECISION: iteration 161 - bury-castle judged WRONG and removed the 303 way (line written, removal executed, then reverted for a true A/B); the 306c-style worktree A/B is INVALID in this project (locally-built site data is not in git)' DECISIONS.md`)

### 2026-10-13 302f HAND-OVER (iteration 210, agent c, context-limit save)
    Task 302f (matcher station e2e test) - INVESTIGATION ONLY, no code written yet. The complete
    test design is traced in tasks/302f-matcher-station-test.md's ## Hand-over (fixture keyed by
    sha256 of the exact /match request body; in-process ephemeral-port stub; guard variant that
    allows only the stub port; exact expected stdout for both branches; unsure variant =
    permuted ground keypoints of the >=10-inlier responses). NEXT STEP (one session): write
    tests/fixtures/matchfit_station/record.py, run it live once against 127.0.0.1:8091 (ELoFTR
    verified reachable this session; RoMa dead), commit the two fixtures, write
    tests/test_matchfit_station.py (two tests: confident + unsure), run it, then the full suite
    (baseline yardstick: 306d-era 10 failed/130 passed/1 skipped of 141; agent a's 212/307d work
    is in flight - new failures in their files are not mine). tests/test_site_done.py passes on
    this branch (5.3 s, .venv current). Nothing else in the working tree was changed this session
    except the task file (git status: only tasks/302f-... modified before this note).
