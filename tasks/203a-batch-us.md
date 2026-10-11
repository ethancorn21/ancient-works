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
- [x] fit/batch_us.py runs the loop for a set of US sites: for each site, every candidate picture
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
- [x] Test (no network, port 0, no model-server call): the loop run on a fixed sample of US sites
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
Session 4b (2026-10-11, iteration 37). Step done: the session-4a-specified `llm_model` rewrite is
RE-IMPLEMENTED and committed in fit/batch_us.py (4a's composed text was lost when its edit call
failed; implemented from the 4a spec, verified):
- `_font`/`_step`/`_grid`: DejaVuSans-Bold 22 px (/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,
  exists on this VM), a label at BOTH ends of every grid line, step = first of (100,200,500,1000)
  with step*scale >= 90 sheet px.
- `_sheet(site,row,box)`: fitkit.plan_image crop + fitkit.ground/ground_view, 900-px panels, plan
  blue (0,0,200) / ground red (200,0,0), saved fitkit.OUT/fit_<sid>_<pid>.jpg; returns
  (path, ground (W,H), Mercator x-span m of the site corners).
- `_model_prompt`: both panels' labelled coordinate ranges + metre coverage, the 202 seed scale
  window ("within about 50%"), anti-fabrication clauses (no grid intersections / even spacing /
  >=3 collinear; never pad a short list), JSON {"scale_m_px", "features", "pairs"}.
- `_parse_answer`: drops pairs whose (u,v) leaves the crop box or whose ground px leaves the
  ground image; feature names kept index-aligned with the surviving pairs.
- `llm_model` closure: stated-scale cross-check - with >=3 parsed pairs and a numeric stated
  scale_m_px > 0, implied = |a|*k from plan_fit.similarity(pairs[:min(8,len)]); ratio > 2.0 ->
  note "...: not trusted" + trim to 3 pairs -> run_sites' <4 branch routes it to the review item.
  Sheet-build / call failures -> note, never raised (unchanged).
Verified: import ok; the sheet eyeballed with the read tool (poverty-point, the full-text-page
root case: bold labels legible at both ends, the mound is clear in the ground panel - far better
than 4a's tiny-bitmap-font sheet); _parse_answer drops the out-of-range points in a synthetic
answer (3 of 5 kept, feature indices follow the survivors); tests unaffected by design (recorded
answers bypass llm_model): tests/test_batch_us.py 5/5 (4.9 s), full suite 34/34 in .venv (42 s).
PITFALLS filed this session: llm.ask's default url= binds at def time (set $AW_LLM_URL or pass
url=; reassigning llm.URL does nothing); this Qwen fabricates identity/corner/diagonal/1:1
patterns that pass a consistency-only gate (docs/gate.md section 7) - the batch's prompt/parse/
cross-check is the counterweight, the gate stays frozen.

TUNNEL: was UP in session 4a (qwen3.8-27b on 127.0.0.1:8080 AND :8081 two vLLM instances, :8082
llama.cpp; harness env LLM_URL=http://127.0.0.1:8081). Re-verify at the start of the next
session before any pilot (a tiny llm.ask or curl to 127.0.0.1:8081). Run everything with
AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions (llm.py's default 18080 is wrong here).

NEXT (session 4c), in order:
1. A/B pilot on the same 5 candidates of 4a: /tmp/pilot_llm.py still calls b.llm_model (now the
   NEW one) and wraps llm.ask to print raw answers - update it to TEE the raw answers to a file
   (/tmp/llm_raw_4c.txt) and print the gate verdict per pick; /tmp/pilot_llm2.py's inline prompt
   copy is superseded (delete or ignore). Picks: tremper-mound-and-works-q7838197 /
   c_75950f29c23bf033; pyramid-mound-q7263260 / ancientmonuments00squi_n0134_1;
   poverty-point-q964745 / annualreportofbu1218901891smit_n0138_1; serpent-mound-q968802 /
   annualreportofbu1218901891smit_n0636_1; cahokia-q333661 / c_8c44bb427b76aa7a.
   Accept when the known fabrications (4a: identity, corner-to-corner, diagonal ladder, 1:1)
   route to items; any REMAINING auto-passing answer must be eyeballed against its sheet jpg
   (read tool) and plausibly match the same real features.
2. If the pilot is acceptable: full run
   `AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions .venv/bin/python fit/batch_us.py --working`
   (58 new candidates over 18 sites; ~10-40 min; give it a long timeout and confirm it finishes;
   all 58 images are local - 37 book pages + 21 commons thumbs, data/raw is the shared symlink;
   all 18 sites have relief.jpg so no aerial fetch; sheets land in /tmp).
3. Verify in THIS checkout: `sha256sum -c tests/golden/hand_fit_docs.sha256` (all 39 OK -> box 4);
   report's "error (no outcome)" bucket empty and the counts sum to 90 (box 3).
4. Tick boxes 3, 4, 5; commit (docs + items + docs/batch_us.md - the llm_model change already went
   in 4b's commit; the alligator-effigy-mound item is MERGED by the upsert, its file changes in
   this commit and is NOT in the golden).

EXPECT a LOW auto-doc rate (most of the 18 candidate sites end as review items carrying the
model's pairs - box 3 is satisfied by design: a fit OR a ready item; the human's drag is the
authority, the report's 18/20 sample is the backstop). Do NOT weaken the gate or the tests to
raise the auto rate.

State of this checkout: boxes 1, 2, 6 ticked; 3, 4, 5 pending the working run. data/db/platefits/
still exactly the 20 pre-batch docs; data/review/ has the alligator + bibracte items. For 203b
(later): import run_sites/write_report; site list = region != "US" plus the 6 region-less sites
(keep the site.json["plate"]["fit"] branch of is_pre_fit, R9); report docs/batch_eu.md; shared
SEED 20261010.
