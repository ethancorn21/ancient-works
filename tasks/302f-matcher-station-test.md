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
