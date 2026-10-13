Status: open
Depends on: none
# 302f: The matcher station end to end - the line on one hand-fit site's files, no network
Touches: tests/

## Hand-over

(2026-10-13, iteration 210, agent c - INVESTIGATION ONLY, no code written. The whole test design
is now fully traced and verified against the code; the next session writes the recorder, runs it
live once, and writes the test. All facts below were verified this session by reading/running code
on this branch, fresh eyes.)

**Environment (verified this session):** .venv current (py3.12.3, numpy 2.5.4, scipy 1.18.1,
PIL 12.3.0). ELoFTR LIVE: 127.0.0.1:8091/health -> {model: zju-community/matchanything_eloftr,
device: NVIDIA GeForce RTX 5060 Ti}. RoMa 8092 REFUSED (curl exit 7). tests/test_site_done.py
passes on this branch (5.3 s). No test suite run yet beyond that; the newest driver loop-start
note in PROGRESS is stale (4 tests, 2026-10-11) - the 306d-era baseline (10 failed/130 passed/1
skipped of 141, agent a's in-flight 307/211/224 work) is the practical yardstick; run the full
suite at the end of the next session and diff against whatever failures exist BEFORE adding the
new test (they are not mine to fix: my only new files are tests/test_matchfit_station.py +
tests/fixtures/matchfit_station/*).

**Site facts (all verified):**
- Hand doc data/db/platefits/badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json:
  by:"hand", auto:null, fitter:null, score:null, at 2026-10-10T17:38:04.576244+00:00, 4 pairs,
  crop [300,1380,2900,3330], size [3367,5050], ia earthworkenglan01allcgoog, file n0132.jpg.
  The image data/raw/books/earthworkenglan01allcgoog/full/n0132.jpg is EXACTLY 3367x5050 (L mode)
  -> every scale factor is 1.0.
- NO review item for badbury (ls data/review | grep badbury: empty). data/review has 481 files
  (2.2M); web/data/review.json has 457 items; data/db/platefits 70 files (296K); data/catalog/
  sites.jsonl 6.0M; data/books/index.jsonl 1.7M (badbury row HAS an evidence dict); data/commons/
  files.jsonl 2.2M.
- web/data/sites/badbury-rings-q798831 is a SYMLINK to /home/agent/projects/ancient-works/web/...
  (another checkout). Tmp tree: copy os.path.realpath(...) as a REAL dir (it is the writer).
  Site dir contents: relief.jpg (1600x1600 RGB), six-inch-1st.webp (1066x1066 RGBA),
  os1inch.webp (1600x1600 RGB), os1inch_ink.webp, six-inch-1st_ink.webp, block_h.png,
  block_top.jpg, depictions.json (2 kind:map depictions with corners + 1 kind:plan depiction,
  fit block: 4 pairs, at 2026-10-10T17:38:04.576244+00:00, doc = the key), NO imagery.jpg.
  data/sites/badbury.../site.json has no "plate" field (is_pre_fit -> False).
- sites.json badbury entry: drawings 1, score 1.45, oldest 1842, overlays 2 (six-inch 1842 is
  >= depict.MIN_AGE_YEARS=150 so it counts; os1inch c.1900 hidden; the 1 plan depiction counts
  for drawings). After the matcher rebuilds the SAME plan file, drawings stays 1.
- plans.json row (cols table format): title "Badbury Rings, Wimbome, Dorset", label "Fig. 21",
  book "Allcroft 1908", map_box [0.107,0.278,0.857,0.658], url null, view false, sites [badbury].
  _crop_px(row) -> [360,1404,2886,3323] (recompute via code, don't hardcode).

**Held-out checkpoint (data/matchfit/heldout/results.json, at 2026-10-12T02:58:37.021604+00:00,
"docs" is a DICT keyed by doc id, each doc has a "candidates" list in grounds-then-windows order:
relief, six-inch, os1inch x 1.0/0.7/0.5/0.35/0.25):** badbury's 15 candidates: relief 0/3/3/2/16
matches (7 inliers at x0.25, rot -0.93), six-inch 5/44/84/61/6 (x0.5: 15 inliers rot 2.98;
x0.7: 8 inliers rot -43.51; x0.35: 22 inliers, 61 matches, rot 3.62, resid_m 3.1, corner_m 58.6,
centre_m 2.9 = THE BEST), os1inch all 0. fit/matchfit_heldout.candidates() uses the IDENTICAL
request path as fit_row (mf.plan_image/mf.grounds/mf.WINDOWS/mf.match/mf.ransac, tol
0.01*max(W,H)*f) - importing it and patching matchfit.match to answer from records is a faithful
offline replay. matchfit_heldout imports inkfit_heldout -> inkfit -> scikit-image/scipy (all in
the .venv; verified the import chain's needs exist).

**Code traces (this is where the expected values come from):**
- fit_row(root, site, row, url): plan_image reads data/raw/books/<ia>/full/<file>, crops _crop_px;
  for each ground x window: match(plan, win, url) sends POST /match with body json.dumps(
  {"image0": _b64(a), "image1": _b64(b), "threshold": 0.2, "max_side": 1024}) - THE EXACT
  request whose sha256 keys the fixture. 15 requests per fit_row (3 grounds x 5 windows). Best =
  strict-greater inliers while iterating. Pairs: up to 8 (fit/matchfit._spread farthest-point
  selection), in the ROW SIZE frame, lon/lat from the ground's corners. Deterministic: same image
  bytes -> same PIL PNG bytes -> same request -> same key (the recording and the test subprocess
  both use the .venv's PIL 12.3.0).
- matchfit.run(root, [sid]): use_roma = reachable(ROMA_URL) FIRST (a guarded AssertionError is
  caught by its `except Exception` -> RoMa deterministically absent). ELoFTR confident ->
  prints `{sid}  {title}: FIT (eloftr) {inliers}/{matches} points on {ground} x{window}, rot
  {rot:.1f} deg, {m_per_px:.2f} m/px, residual {resid_m:.0f} m`, then batch_us.write_doc
  (book row: doc has ia/file/book but NO model/src fields; at = wall clock) + doc.update(
  fitter:"matcher", matcher:{model: MODELS[kind], inliers, matches, ground, window, rot_deg
  rounded 2dp, spread [3dp, 1dp]}), _save_json. Unsure -> prints `{sid}  {title}: {why}{extra}`
  where extra = ` [{ground} x{window}, rot {rot:.0f}]` and NO doc is written.
- site_done._fit: matcher reachable -> run; then re-reads docs/item. Confident: uncovered empty
  -> `fit  1 candidate picture(s): 1 fitted (doc), 0 in the review item -> no batch run needed`.
  Unsure: uncovered -> batch_us.run_sites(root,[sid], None): propose.propose_for (LOCAL: reads
  index.jsonl + the picture's scale bar/north arrow; row has scale_bar true "0 100 ... 500 Scale
  of Feet", north_arrow true) -> candidate entry via batch_us._entry (gets evidence from
  data/books/index.jsonl, plus coarse/ground/scale_m_px/rot_deg/scale_source/note from the
  proposal when it succeeds; why = "no model answer") -> review.upsert_item writes data/review/
  badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json (lead = cands[0].plan; indent=1,
  no trailing newline) -> prints `fit  {title}: sent to the review queue (no model answer)`. NO
  "no batch run needed" line in this branch (that line is only in the need_fit-False else).
- _sync_doc (confident only): who_placed -> agent (by=agent); fitter matcher -> spread guard on
  the DOC's 8 stored pairs (ratio>=0.1 AND sd>=20 px; expect PASS - verify in the replay and
  record in the fixture header); is_done compares the existing plan depiction's fit.at (2026-10-10)
  with the new doc's at -> False -> plan_fit.build: book load_picture local, similarity, writes
  plan_earthworkenglan01allcgoog_n0132_1.webp + _ink.webp (REPLACES the hand fit's same-named
  files), replaces the same-file depiction in depictions.json (both year 1908; sorted by year),
  prints `{sid} {plan}: 8 pairs, similarity, residuals m [...]`, build_site.set_drawings (locks
  sites.json.lock, local only).
- _entry: `entry  web/data/sites.json: drawings 1 -> 1` (both branches; entry values recompute
  identically).
- _review: confident -> item None -> `review no review item (every picture is a fit)` and the
  export is NEVER called (web/data/review.json byte-identical). Unsure -> export(root, site_id)
  -> publishes the WHOLE queue to web/data/review.json (reads all 481 item files + sites.json +
  data/catalog/sites.jsonl for names - COPY THE CATALOG, else stderr warnings and my test asserts
  stderr == ""); returns (n_open, n_total) over the tmp tree: 482 item files; the repo's current
  457-open may have DRIFTED (other tasks add docs/items since the last publish) so DO NOT assert
  equality with the repo's review.json: recompute the baseline by calling review.export in-process
  on a second clean tmp copy of the same inputs, then expected items =
  sorted(baseline_items + [badbury_entry], key=lambda e: (e["name"] or "").lower());
  badbury_entry = {site, name "Badbury Rings", lead = plan id, candidates: [the _entry result],
  no_picture_found: None}.
- _summary + `done` + exit 0 (both branches; unsure summary line: `  {title} ({pid}): sent to the
  review queue (no model answer)`).

**Next step (one session's worth, in order):**
1. Write tests/fixtures/matchfit_station/record.py (one-off, network phase only, .venv/bin/python):
   - monkeypatch urllib.request.urlopen to record every POST */match (body sha256 -> response
     JSON; return a small Resp wrapper with .read() so matchfit's json.load keeps working;
     skip bodyless GETs); call matchfit.fit_row(str(ROOT), site, row, MATCHER_URL) LIVE TWICE
     (stability: the two response sets must be byte-identical - record the verdict in the header).
   - Offline replay: patch matchfit.match to answer from the records (same request build ->
     same key; raise if a key is missing so a drift fails loudly), run matchfit.fit_row and
     matchfit_heldout.candidates; compare every candidate's (matches, inliers, rot, resid_m)
     with the frozen heldout entry; record both in the header ("heldout" frozen numbers incl.
     the 22/58.6 line, "live_replay", "replay_from_records"); if live drifted but is stable,
     keep the live numbers (box 1 allows it, with the discrepancy recorded) and note it.
   - Confident fixture records.json: header (generated utc, matcher_url, /health answer,
     site/plan, request {threshold 0.2, max_side 1024, key scheme}, heldout, live_replay,
     replay_from_records, doc_fields: the exact doc the test must find (site, plan, ia, file,
     book, title, label, cite, crop, auto true, by agent, fitter matcher, matcher block incl.
     spread, score, and doc_pairs = batch_us._norm_pairs(fit_row's 8 pairs) - do NOT record
     "at", it is wall-clock) + the exact expected stdout lines (the FIT line, the build
     residuals line computed with plan_fit.similarity on doc_pairs, the sync line with the gate
     score, the entry/summary lines) + the two spread values (fit_row all-inliers; doc 8-pairs)
     and the guard pass/fail + responses {15 keys}.
   - Unsure variant records_unsure.json: take the confident records; for every response whose
     offline candidate has inliers >= 10 (frozen: six-inch x0.5 and x0.35; determine from the
     LIVE replay in case it drifted) replace keypoints1 with a deterministic permutation
     (np.random.default_rng(7).permutation(len) - try the next seed if the perturbed best ever
     lands >= 10; the script asserts the final best has 3..9 inliers so a candidate exists) and
     re-run the offline replay; header: same as confident plus variant {best: {ground, window,
     inliers, rot}, exact "not sure: N consistent points (need 10) [G xW, rot R]" line, the exact
     remaining 4 expected stdout lines incl. the review line with NO/NT computed from the copied
     queue, and the expected item dict = batch_us._entry(checkout, row, [], "no model answer",
     None, propose.propose_for(SID, PLAN)) and expected_candidate}. Commit both fixtures + script.
2. Write tests/test_matchfit_station.py: conftest-style tmp tree (copy tools/, fit/, pipeline/
   code; web/data/{sites,plans,review}.json; REAL copy of the site dir; data/db/platefits all
   then DELETE the badbury doc; data/review all; data/books/index.jsonl; data/commons/files.jsonl;
   data/catalog/sites.jsonl; data/sites/<SID>/site.json; data/raw/books/<ia>/full/n0132.jpg);
   in-process ThreadingHTTPServer on 127.0.0.1:0 (GET /health -> header health; POST /match ->
   sha256(body) lookup, 500 {"error":...} if absent); dead ROMA_URL = bind-then-close ephemeral
   port; GUARD = the test_site_done one EXCEPT socket.socket.connect/connect_ex pass through
   (127.0.0.1, stub_port) (allowed port via env GUARD_ALLOW) and everything else raises
   AssertionError - do NOT patch socket.create_connection to dead (it must flow through to the
   patched instance connect); subprocess = [sys.executable, "-c", GUARD, tree/tools/site_done.py,
   SID] with env MATCHER_URL/ROMA_URL, cwd=tree, timeout 600. Two tests:
   - confident (records.json): exit 0, stderr == ""; stdout equals the 11 expected lines in
     order (list them in the test from the header); tmp store gained the doc byte-equal to the
     header's doc_fields except "at"; depictions.json: plan depiction replaced (fit.at == doc
     at, fit.pairs 8, fit.doc the key, the two map depictions unchanged), plan_*.webp pair
     rebuilt; sites.json badbury entry parsed-equal to the repo's (drawings still 1) and every
     OTHER site entry unchanged; web/data/review.json byte-identical to the repo's; data/review
     byte-identical (no new item); checkout hashes (site dir, the copied data files, the three
     web data files, tools/fit/pipeline) before == after.
   - unsure (fresh tree, records_unsure.json): exit 0, stderr == ""; stdout equals the 9
     expected lines (the not-sure line verbatim from the header); store has NO doc for the
     plan; the new item file parses equal to the header's expected item (resolved None, no_
     picture_found None); depictions.json byte-identical to the repo's and the plan_*.webp pair
     byte-identical (no overlay built); sites.json badbury entry unchanged; published
     web/data/review.json items == sorted(clean-copy baseline items + badbury entry); all other
     review items byte-identical; checkout hashes unchanged.
3. Run .venv/bin/python -m pytest tests/test_matchfit_station.py -q -p no:cacheprovider until
   green; then the FULL suite, diffing failures against the pre-change run; update memory;
   commit as "302f: ...". Tick boxes as verified (box 6 = no new reds vs the newest driver note;
   box 6's "git status clean" = the test itself proves the checkout untouched via the hash check).

**Pitfalls to remember:** results.json "docs" is a dict (docs[docid]["candidates"]); plans.json
is a cols/rows table, not a list; web/data/sites/<id> is a symlink - copy realpath; the batch
_entry candidate for a book row carries the evidence dict (copy index.jsonl into the tmp tree)
or the item won't match; pytest.ini keeps only FAILED tmp dirs (retention policy) so a failing
run's tree survives in /tmp/pytest-of-agent - useful for debugging.

**Re-read (next session, fresh eyes):** fit/matchfit.py fit_row/run (the request build is the
fixture key - if you change the test's stub, the key scheme must stay "sha256 of the exact
request body matchfit.match sends"); tools/site_done.py _fit (need_fit True vs else decides the
"no batch run needed" line - the unsure branch has NO such line); fit/review.py export (whole-
queue publish, site_id-scoped item writes, catalog name fallback); tests/test_site_done.py
(the tree-building and hash-check idiom this test copies).

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
- [ ] Committed fixture from a one-off working-phase run against the live ELoFTR
      (127.0.0.1:8091; verified reachable at iteration 208): the raw /match responses for
      every (plan image, ground image, window) pair of badbury's fit_row, keyed by the
      sha256 of the exact PNG bytes matchfit.match sends (plus threshold 0.2 / max_side
      1024), under tests/fixtures/matchfit_station/ (new directory; the JSON carries a
      header recording run date, matcher model, and the frozen held-out numbers the
      replay must reproduce - badbury 22 inliers / 58.6 m on six-inch x0.35). If the live
      replay disagrees with the frozen checkpoint, record the discrepancy; regenerate
      only if the matcher's output is stably different.
- [ ] tests/test_matchfit_station.py (new file): starts the stub in-process on an
      ephemeral loopback port (conftest.py's server idiom, bind port 0), points the
      subprocess's MATCHER_URL at it and ROMA_URL at a dead ephemeral port (RoMa
      deterministically absent: matchfit.run's second pass skips), and runs
      tools/site_done.py --root <tmp> as a subprocess. The tmp root copies badbury's
      files (the site dir, the site's sites.json entry, the plans row, the golden
      document) with the document DELETED so the single candidate is uncovered.
- [ ] Subprocess socket guard (a variant of tests/test_fit_queue.py's GUARD): any
      connection attempt to anything other than the stub's loopback port fails loudly -
      that is the "no network" proof.
- [ ] Confident branch: the stub replays the recorded 22-inlier six-inch candidate (and
      the rest of badbury's recorded responses). The test asserts: site_done exits 0;
      the subprocess stdout carries the matcher's FIT (eloftr) line for n0132_1; the tmp
      root gained a document badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1.json
      with by:"agent", auto:true, fitter:"matcher" and its matcher block (model, inliers,
      matches, ground, window, rot_deg, spread); the line's sync built it into the tmp map
      (the spread guard passes on the recorded spread, so no refusal); exit code 0.
- [ ] Unsure branch (a fresh tmp copy, fixture variant with the best candidate under 10
      inliers): the test asserts: the subprocess stdout carries the matcher's
      "not sure: N consistent points (need 10)" line for that candidate; no document is
      written for it; the candidate appears in the tmp review item with a reason (the
      batch's own, e.g. "no model answer", from the socket-dead vision pass); no map
      overlay for it; exit code 0 - that is the parent's box-3 contract "unsure goes to
      the queue with the reason, never to the map", end to end.
- [ ] The real checkout stays byte-identical after the test (the tmp root is the only
      writer; git status clean), and the suite has no new reds against the newest driver
      loop-start note.
