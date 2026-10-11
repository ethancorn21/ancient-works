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
Session 4a (2026-10-11, iteration 37). Two things happened:

1. LEAD'S DISK FIX - DONE + COMMITTED (eea8852). tests/test_batch_us.py: the `tree` fixture now
   HARD-LINKS web/ + data/ into tmp (os.link, symlink fallback cross-device; data/raw stays a symlink
   to the shared store) and copies only files the batch rewrites in place (only candidate:
   docs/batch_us.md; write_doc/upsert_item are atomic new-inode writers, so linked originals are safe).
   Added tmp_path_retention_policy="failed" (successful runs' temp trees no longer retained). Verified:
   5 tests 15.4 s -> 4.9 s; 3 consecutive runs add ~0 disk; full suite 34/34 in .venv (44 s).
   (Background: this checkout's data/raw is a SYMLINK to /home/agent/projects/ancient-works/data/raw,
   1.9 G shared images; du -sh data/raw shows 0 - check file validity via the target, e.g. PIL.open.)

2. WORKING PHASE - IN PROGRESS. Tunnel UP: qwen3.8-27b on 127.0.0.1:8080/:8081 (vLLM), :8082 (llama.cpp);
   run with AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions (llm.py reads that env var; default
   18080 is wrong here; and llm.ask's default url= arg binds at def time - env var, not reassignment).
   All 58 working candidates' images are LOCAL (37 book pages + 21 commons thumbs); 18 candidate sites,
   all with relief.jpg (no fetches needed). The full run command:
   `AW_LLM_URL=http://127.0.0.1:8081/v1/chat/completions .venv/bin/python fit/batch_us.py --working`

   PILOT RESULT (15 real Qwen calls; scripts /tmp/pilot_llm.py, /tmp/pilot_llm2.py still on disk):
   parsing works, but the CURRENT prompt makes the model FABRICATE regular patterns (identity maps,
   1:1 grid lines, diagonal ladders, corners-to-corners) that are internally perfect (gate med 0.0)
   and PASS the frozen gate - docs/gate.md section 7's "consistent global error" as a systematic
   model failure. Left as is, the auto docs would be garbage. An improved-prompt A/B (metre coverage,
   labelled ranges, seed scale window, anti-pattern + honesty clauses, stated scale + feature names)
   routed 4/5 fabrications to review items (correctly); one small commons picture still 1:1-passes.
   Root cause also visible in the sheets themselves: map_box-less book rows = FULL TEXT PAGES with the
   figure ~15% of the panel, gridded in PIL's tiny default font, downscaled to 1600 px - illegible.

   batch_us.py ON DISK IS UNCHANGED (my rewrite edit failed on exact-match; the composed text is not
   saved). RE-IMPLEMENT in fit/batch_us.py (my file), replacing llm_model and adding helpers:
   - _sheet(site,row,box): fitkit.plan_image(row).crop(box) + fitkit.ground/ground_view, 900-px panels;
     own grid: DejaVuSans-Bold 22 px (path /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf, exists)
     labels at BOTH ends of every line; step = first of (100,200,500,1000) with step*scale >= 90 sheet px;
     plan blue (0,0,200) / ground red (200,0,0); save fitkit.OUT/fit_<sid>_<pid>.jpg; return
     (path, ground_size, ground_m) where ground_m = corners' Mercator x-span (aw.to_merc).
   - _model_prompt: "left panel crop ... labels run x0-x2 across, y1-y3 down (WxH px crop; covers
     ~(box_w*scale) x (box_h*scale) m when the proposal has scale_m_px)"; right panel "0-gw across,
     0-gh down (covers ~G x G m)"; seed hint "proposed starting placement ... %s m/px and rotation
     %s deg (coarse=%s); a true match should be within about 50%% of that scale"; "Match 4 to 8
     features that are the SAME real feature on both sides: wall or rampart corners, gate gaps,
     bastion or mound tips, road junctions, church footprints, river crossings, field edges"; "every
     coordinate must lie inside its panel's labelled range above"; "Do NOT pick grid-line
     intersections, evenly spaced points or points along a straight line: real features have irregular
     spacing ... at least three of your points must not lie on one straight line"; "If you cannot
     confidently identify 4 ... answer with only the pairs you truly see (even 0 or 1) - never pad a
     list with guessed or evenly spaced points"; JSON: {"scale_m_px": <estimate>, "features":
     [short name per pair], "pairs": [[u_plan,v_plan,u_ground,v_ground], ...]}; pass to llm.ask_json
     with images=[sheet].
   - _parse_answer: drop pairs with (u,v) outside [box] or ground px outside [0,gsz]; collect feature
     names; return (pairs, feats).
   - model(): after parse, if len(pairs)>=3 and ans has numeric scale_m_px>0: implied = abs(a)*k from
     plan_fit.similarity(pairs[:min(8,len)]); if max(implied/stated, stated/implied) > 2.0 -> note
     "stated scale %.3f disagrees with its own points (%.3f m/px): not trusted" and trim pairs (and
     feats) to 3 => the <4 branch routes it to the item. Note = "features: ..." + any mismatch note;
     empty pairs -> note "the model recorded no usable pairs". Keep the existing exception handling
     (sheet build / call failures -> note, never raise).
   Tests are UNAFFECTED (recorded answers bypass llm_model) - keep 5/5 + full suite green.

   Then: re-run the A/B pilot (tee raw answers to a file; I can also READ the sheet jpgs with the read
   tool and eyeball pairs - use that to judge any auto-passing answer); then the full --working run
   (58 candidates, ~10-40 min, long timeout); then verify in THIS checkout: `sha256sum -c
   tests/golden/hand_fit_docs.sha256` (all 39 OK - box 4), report's "error (no outcome)" bucket empty
   and counts sum to 90 (box 3); tick 3/4/5; commit (llm_model change + docs + items + docs/batch_us.md;
   the alligator-effigy-mound item merges via upsert and will change - not in the golden). EXPECT a LOW
   auto-doc rate (most sites end as review items carrying the model's pairs - box 3 is satisfied by
   design: a fit OR a ready item; the human's drag is the authority, the 18/20 sample is the backstop).
   Do NOT weaken the gate or the tests to raise the auto rate.

State of this checkout: boxes 1, 2, 6 ticked; 3, 4, 5 pending the working run. data/db/platefits/ still
exactly the 20 pre-batch docs; data/review/ has the alligator + bibracte items. For 203b (later):
import run_sites/write_report; site list = region != "US" plus the 6 region-less sites (keep the
site.json["plate"]["fit"] branch of is_pre_fit, R9); report docs/batch_eu.md; shared SEED 20261010.
