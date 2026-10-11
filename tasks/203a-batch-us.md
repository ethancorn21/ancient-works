Status: open
# 203a: The batch, US - the 90 US built sites
Depends on: 001, 200, 201, 202
Touches: fit/batch_us.py, data/db/platefits/, data/review/, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256

## Goal
GOAL.md point 2: the local model does the fitting itself, the way the 25 hand fits were made. For
every US built site in web/data/sites.json (region "US", 90 of 384): candidates = the plans.json
rows whose "sites" contains the site (with 200's evidence field where present). For each candidate
picture: build the fitkit sheet (`tools/fitkit.py sheet` - the picture's crop next to the site's
ground, relief or the aerial photograph where there is no LiDAR, both gridded) and let the local
vision model (`pipeline/llm.py`) read the grid labels, find the same features on both sides (wall
corners, gate gaps, bastion tips, road junctions, church footprints, river crossings), and record at
least four point pairs (202's seed is its starting point where one exists; a
code/north/centre-only placement is never the fit). The pairs go through the existing `plan_fit`
similarity solver and then the gate (001): accepted fits become automatic platefit documents in
data/db/platefits/ with the gate's score and an "auto" mark; a gate refusal, or a picture the model
could not fit (fewer than four pairs), becomes a review item in data/review/ in 201's format
carrying those pairs; a site with no candidate at all gets an item marked "no picture found"
(point 1: fit or item). The 20 existing hand-fit documents are never touched. 203b (the rest of
the world) reuses this module's loop.

## Acceptance criteria
- [x] Before the first batch write: tests/golden/hand_fit_docs.sha256 is committed, listing all
      20 pre-batch platefit documents (file name + sha256) and the 19 hand-fit sites'
      data/sites/<id>/site.json files.
- [ ] fit/batch_us.py runs the loop for a set of US sites: for each site, every candidate picture
      goes fitkit sheet -> model (>= 4 matched-feature pairs, 202's seed as starting point) -> fit
      -> gate; the accepted ones write automatic platefit documents (existing format + score +
      "auto" mark) and the rest become review items (the model's pairs where it made any); a site
      with no candidate at all gets an item marked "no picture found". The loop is a function 203b
      can import and point at its own site list, with the model step injectable.
- [ ] In the full working-phase run (all 90 US sites, recorded in the report), every US site
      ends with at least one automatic document or an open review item - or an existing hand
      fit.
- [ ] After the run the 20 hand-fit documents and the 19 site files are byte-identical to the
      golden hashes; the batch added files, it rewrote none.
- [ ] docs/batch_us.md: counts (automatic fit / review item / already hand-fitted / no picture
      found), the recorded seed, and the seeded sample of automatically accepted fits (20 where
      there are at least 20; a page URL each) for the human's 18/20 check.
- [ ] Test (no network, port 0, no model-server call): the loop run on a fixed sample of US sites
      with in-repo ground, the model step supplied a fixed recorded answer, produces, per site, a
      document or an item in the right format; the hand-fit files are byte-identical; the report's
      sample is reproducible from the recorded seed.

## Notes
- Ground: the in-repo images (web/data/sites/<id>/) carry the test fits (fitkit convention:
  relief where there is, aerial otherwise). The full run uses the same convention per site;
  fetches happen only in the working phase, never in tests.
- The page-facing sync (overlays, drawings counts) is NOT this task's job: the documents sit
  in data/db/platefits/ and 212 syncs them to the page in one pass.
- The golden hashes cover the pre-batch state of THIS checkout; regenerate them if the batch
  has already been partially run, but never edit them to make a failure pass.
- The model call is injectable by design: the working phase calls `pipeline/llm.py` on the fitkit
  sheet; tests supply a fixed recorded answer so no test touches the model server (GOAL: what the
  model says is a lead to check, not a fact — the gate is the check).

## Hand-over
Session 1 done (2026-10-11): box 1 committed, module built and smoke-verified. State of this checkout:

- `tests/golden/hand_fit_docs.sha256` committed (fe84152): 39 lines, sha256sum -c format, 20 pre-batch
  `data/db/platefits/*.json` + the 19 hand-fit `data/sites/<id>/site.json`. NEVER write a batch doc into
  this checkout before the working phase; `fit/batch_us.py --golden` regenerates it (excludes auto docs).
- `fit/batch_us.py` (6003416): `us_sites`, `candidates`, `gate_placement` (the 001 adapter: score = gate's
  median residual m, `why` names the clause; NaN-safe), `write_doc` (existing platefit format +
  `"auto": true` + `"score"`; skips existing files), `write_item` (201's `upsert_item`), `run_sites(root,
  site_ids, model)` (THE loop 203b imports), `classify`, `write_report(root, records, title, path, at)`
  (SEED = 20261010 constant; deterministic for same records/at), `write_golden`, `llm_model` (the working
  LLM step: fitkit sheet -> llm.ask_json -> pairs; notes failures into the item, never raises),
  `recorded_model` (answers file {"<site>": {"<plan>": {"pairs": [...], "note": ...}}), CLI
  `--root/--golden/--sites/--working/--model-json/--report`.
- Smoke (temp tree, .venv): 202's proposed pairs -> gate ACCEPT med 0.0 (the documented "true case": the
  gate sees ~0 residuals when the placement is the LSQ of the same pairs; it rejects degenerate/nan sets
  and placements inconsistent with their anchors - docs/gate.md s.7, the 18/20 sample is the real check);
  2-pair model answer -> item with those pairs + 202's proposal extras (coarse/note/scale/...); no answer
  -> item with 202's proposed pairs as the starting point; no candidates -> no-picture item;
  hand-fit-only site (mound-bottom) -> nothing written; report byte-identical across two calls; suite 29
  green. The item's `evidence` comes from fit/review.candidate_evidence(PLAN, root) (200's field).
- Gotchas learned: Python binds `"a" or "b" / "c"` as `"a" or ("b"/"c")` - string/Path mixing bites in
  write_report (fixed); fit/propose.py and fitkit read THEIR checkout's ROOT (not a temp root) - tests are
  safe because the temp tree's web/data is an identical copy; fitkit.OUT is read at import time (llm_model
  uses fitkit.OUT, not a fresh env read).
- The 201 seed item alligator-effigy-mound-q4732645 (region US, 2 candidates) is committed in data/review/:
  the working run's upsert will merge into that file (same-plan entries replaced, `resolved` never
  cleared - 201's contract); bibracte (France) is never touched by 203a. Expect that file to change in
  the working-phase commit; it is NOT part of the golden.

NEXT (session 2): `tests/test_batch_us.py` per prep §3 - plain pytest, OWN function-scoped temp tree
(web/ + data/ minus data/raw, plus tests/golden), a fixture blocking socket.connect (hermetic, no ports),
run_sites with recorded_model on the fixed sample: serpent-mound-q968802 (16 cands; 1 hand-fit doc
skipped; 202 pairs as recorded answers -> auto docs), cahokia-q333661 (a 2-pair answer -> item),
mound-bottom-q14710093 (only its hand-fit doc -> nothing), one zero-candidate US site (e.g.
aberdeen-mound-q4666953 -> no-picture item). Cases: (1) per-site outcome + right format (docs: existing
format + auto + score incl. commons keys; items: 201's shape, resolved untouched); (2) both write paths
with a stub gate-free model (all-accept vs all-reject) - pin the writers; (3) golden invariance: after
the run all 39 golden paths byte-identical in the temp tree, no pre-existing platefits file rewritten;
(4) report reproducibility from SEED. No new golden file (not in Touches): box 6 asks only for
reproducibility, not a pinned sample file. Then tick boxes 1-2,6 (3,4,5 need the working run).

Then the WORKING phase (separate step, network allowed, .venv): `--working` over all 90 (AI-box tunnel
up; missing pictures/aerials fetched; fitkit sheet -> LLM). Commit docs + items + docs/batch_us.md;
re-run `sha256sum -c tests/golden/hand_fit_docs.sha256` (must all be OK: the batch adds, rewrites
none); check box 3 (every US site: auto doc OR item OR pre-existing fit) and box 5. For 203b (hand-over
to its file when it starts): import run_sites/write_report from fit.batch_us; its site list = region !=
US + the 6 region-less sites; keep the site.json["plate"]["fit"] branch of is_pre_fit (R9) - the 6
old-style hand fits have no platefits doc. SEED is shared (both reports sample from it).

Re-read: fit/batch_us.py llm_model - the working LLM prompt has never seen the model; check its answer
parsing against a real Qwen answer on the first working run and adjust the prompt (module file, mine to
change).
