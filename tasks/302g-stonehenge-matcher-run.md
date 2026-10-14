Status: open
Depends on: none
# 302g: Stonehenge on the matcher-first line - the run, the browser check, the plain statement
Touches: docs/site_flow.md, docs/site_flow/, data/review/, data/db/platefits/, web/data/sites.json, web/data/review.json, web/data/sites/stonehenge/

## Goal
Parent box 5: "Run on Stonehenge: whatever it puts on the map, checked in a browser
against the real stones (screenshot in docs/site_flow/); say plainly if it places
nothing". This is the method-agnostic box-5 run with the current matcher-first line
(site_done._fit: the pretrained matcher first on every undocumented picture, the vision
batch the second pass, the fabrication and spread guards fencing both) - explicitly NOT
a revival of the dropped 302c/302d ink work.

State at iteration 208 (verified): stonehenge-q39671 = 0 drawings, 1 overlay
(web/data/sites.json); 14 candidates in
data/review/stonehenge-q39671.earthworkenglan01allcgoog_n0582_1.json (7 "line check:
fabricated...", 4 "median residual > 45 m", 2 feature-based, 1 "no model answer"); no
matcher document anywhere. The only Stonehenge screenshot (docs/site_flow/stonehenge.png,
2026-10-11) predates the matcher. The matcher's only Stonehenge record so far: a near-miss
and a 0.26-fraction RoMa on the earthworks, below the 0.4 bar (docs/matchfit.md
sections 7-8) - so the a-priori expectation is "places nothing", which the box explicitly
accepts; the point is to run the real line, check the result in a browser against the
sarsens, and record it plainly.

Environment (iteration 208): ELoFTR answers at 127.0.0.1:8091 (RTX 5060 Ti); RoMa at
:8092 is refused, so the run degrades to ELoFTR only (matchfit.run use_roma=False) -
record that. The batch's fit model (the Mac-side Qwen per 302's first session; the 8080
vLLM is the approved Clef-flash classifier, not the batch's fit model) is not reachable
from this VM, so uncovered candidates come back with the batch's "no model answer" - a
recorded environment fact, not a defect of this task.

## Acceptance criteria
- [x] The live run of `tools/site_done.py stonehenge-q39671` (this checkout, the live
      ELoFTR): full stdout+stderr saved and committed as a NEW file under docs/site_flow/
      (e.g. stonehenge-matcher-<date>.log), with the run date and matcher availability
      (ELoFTR up, RoMa down) stated in the record. -> docs/site_flow/stonehenge-matcher-2026-10-14.log
      (run 2026-10-14 02:06-02:10 CDT, exit 0, wall 3m08s; ELoFTR up on 127.0.0.1:8091, RoMa down
      on :8092 -> ELoFTR-only run; the header states both probes verbatim).
- [x] The run's effect on all 14 candidates stated per candidate in the record (what the
      matcher did for each picture, what the batch did, which documents were written or
      deleted and why); the pre-run snapshot of the current 14 entries is recorded in the
      same section. -> the log's per-candidate section (all 14: ELoFTR unsure/empty, batch not
      run, no docs written or deleted, item entries byte-identical) + the 14 pre-run entries
      verbatim in the log's pre-run snapshot section.
- [ ] Whatever the line puts on the map is checked in a browser against the real sarsens
      with the 301/306 pattern (tools/shot.mjs: headless Chrome 155,
      NODE_PATH=/home/agent/tools/shot/node_modules, the tree served by
      server/serve.py --port 0): the stonehenge map page, the overlay's stone positions
      against the known circle/avenue layout, an [eval] measurement of the overlay's
      extent, and a screenshot committed as a NEW file under docs/site_flow/. If the line
      placed nothing: the current map page is screenshotted anyway and the record says
      plainly "the method placed nothing on Stonehenge" with the per-candidate reasons -
      that is a passing answer to this box.
- [ ] A new section in docs/site_flow.md APPENDED at the end of the file (do not edit any
      other section - agent a's 307d work also writes there and both must merge cleanly):
      run date, matcher availability, what was placed (or not), the screenshot name, the
      plain statement.
- [x] The golden files and the 21 hand-fit documents byte-unchanged; no new reds against
      the newest driver loop-start note. web/data/review.json is a generated whole-queue
      publish: if it conflicts at merge time with other tasks' exports, regenerate it
      with fit/review.py export rather than hand-merging. -> all golden lines verify (41/41 OK
      before AND after the run and the suite: the golden now carries 22 platefit docs - Fort Ancient
      joined the hand-fit golden in lead commit c72706b - plus 19 site.json; the box's "21" is the
      pre-merge count) and the full suite is green: 168 passed / 1 skipped / 0 failed (525 s), vs
      the newest driver note's 1 failed (307bb's placement test - now green on this tree) /
      159 passed / 1 skipped of 161; the suite has since grown to 169 tests.

## Hand-over

(2026-10-14, iteration 128, agent c - live-run session. Boxes 1, 2, 5 ticked; remaining =
boxes 3-4: the browser check (screenshot) and the section APPENDED to docs/site_flow.md. About
one session's work.)

**Done and committed this session:**
- The live run of the current matcher-first line: `.venv/bin/python tools/site_done.py
  stonehenge-q39671` (real checkout, no --root, no --working/--model-json), 2026-10-14 02:06-02:10
  CDT, exit 0, wall 3m08s. ELoFTR UP (127.0.0.1:8091/health: zju-community/matchanything_eloftr on
  the RTX 5060 Ti); RoMa DOWN (127.0.0.1:8092 refused) -> ELoFTR-only run (matchfit.run
  use_roma=False; no picture got the RoMa second pass). Grounds matched: relief.jpg (site-box
  corners), six-inch-1st.webp and os1inch.webp (own corners) - no imagery.jpg for this site - each
  in 5 centred windows: 15 /match calls per picture, 210 total.
- RESULT: the line placed nothing. 0 of 14 pictures became documents: ELoFTR "the matcher found
  nothing consistent" on 3 (the earthworks, Early Man Fig 143, Fig 145a) and "not sure: 3-7
  consistent points (need 10)" on the other 11 (best per picture: six-inch-1st x1.0 for most;
  relief x1.0/x0.7 for three; rotations -125..+31 deg). No documents written, none deleted. The
  vision batch never ran (all 14 already had review-item entries, so nothing was uncovered) - the
  task's "no model answer" environment fact therefore did not apply to this run; the item's one
  such entry (c_61b86efb4511e099) is pre-existing from the 301-era batch.
- Recorded in docs/site_flow/stonehenge-matcher-2026-10-14.log (boxes 1+2): header (run date,
  both /health probes verbatim, the RoMa-down degradation, the batch fact), the pre-run snapshot
  (sites.json entry, 0 docs in the store, the site dir, and the 14 candidate entries VERBATIM),
  the per-candidate effect section (matcher verdict / batch / docs / item state for each of the
  14, with the pre-run why quoted), the post-run verification, the plain statement, then the full
  stdout+stderr verbatim.
- Verified by diff: the item file, the site's depictions.json, the site dir (no new overlay), the
  sites.json entry (drawings 0, overlays 1, score 1.1, oldest 1842) and all 14 candidate entries
  are byte-identical before/after; the ONLY file the run changed is web/data/review.json, whose
  diff is the top-level "at" timestamp (the whole-queue re-publish: 456 open of 480 item files;
  the 24 excluded all carry a resolving doc, counted via review.resolved_doc) (box 5, the
  regenerate-at-merge clause stands for the driver).
- Suite (full, `.venv/bin/python -m pytest tests/ -p no:cacheprovider`): 168 passed / 1 skipped /
  0 failed (525 s) -> no new reds vs the newest driver loop-start note (that note's lone red,
  307bb's test_placement_gestures_and_save_in_the_browser, is GREEN on this tree; the suite also
  grew 161 -> 169 tests since the note) (box 5). Golden: 41/41 OK before and after the run and the
  suite, the file itself untouched.

**Next session (boxes 3-4, in order):**
1. Serve THIS checkout (the full web/data/sites build is here - the 306d worktree pitfall does not
   apply to the live checkout): `.venv/bin/python server/serve.py --port 0`, parse the base URL it
   prints, kill it after the shot. The page is a hash-routed SPA: the stonehenge page is
   `<base>/#stonehenge-q39671` (web/index.html start(): `S.byId[id]` -> select).
2. The shot: `NODE_PATH=/home/agent/tools/shot/node_modules POSTWAIT=300 node tools/shot.mjs
   <base>/#stonehenge-q39671 docs/site_flow/stonehenge-matcher-2026-10-14.png 8000 1200 800 "<js>"`
   (tools/shot.mjs usage line: <url> <out.png> [waitMs=4000] [w=1200] [h=800] [js]; the [js] probe
   is an EXPRESSION - write it as an `(async () => {...})()` IIFE, as tests/test_review.py's
   PROBE_LIST does: poll S.ready && S.sites.length, read the page's own state; the [eval] line is
   JSON). The 301/306 pattern: check what the map shows for the site (expect ONLY the 1842 OS
   six-inch sheet inside the site box lon -1.833276..-1.818946, lat 51.174397..51.183380 - the
   c.1900 one-inch is hidden by MIN_AGE_YEARS - and no plan overlay), its stone positions against
   the real sarsens (circle + avenue around the site point -1.826111, 51.178889; the sheet's
   corners are in web/data/sites/stonehenge-q39671/depictions.json), and an [eval] measurement of
   the overlay's extent. Commit the screenshot as the NEW file named above (box 3). If the line
   placed nothing (it did): the record says plainly "the method placed nothing on Stonehenge" -
   that is the passing answer.
3. APPEND one section to the very END of docs/site_flow.md (append-only: agent a's 307d writes
   there too - touch no other section): run date, matcher availability (ELoFTR up / RoMa down),
   what was placed (nothing; per-candidate reasons, pointing at the log for the 14-entry detail),
   the screenshot name, the log name, the plain statement (box 4).
4. Commit EXPLICIT paths only. Gotcha: every full-suite run regenerates agent a's
   docs/site_flow/307d_*.png (they show modified in this working tree with different bytes each
   run) - they are 307d's files: never commit them from my branch.

**Re-read:** tools/shot.mjs (the usage line and the [eval]/[after] mechanics - and that the page's
`S` state is a bare name, not on window); tests/test_review.py queue()/_shot/_probe (the served-
ephemeral-port + IIFE-probe idiom and the 404-count gotcha); web/index.html start() (hash routing)
and how overlays render (S.dep/applyDep, ~line 1530: the texture load order imagery->relief/block)
for the extent probe; the current END of docs/site_flow.md (agent a's 307d section may have
landed - append after whatever is last).
