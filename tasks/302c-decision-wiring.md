Status: open
Depends on: 302b
# 302c: The decision and the wiring - the method decides, site_done's fit step calls it
Touches: fit/inkfit.py, tools/site_done.py, pipeline/plan_fit.py, tests/test_inkfit.py, tests/test_site_done.py, docs/site_flow.md, data/inkfit/

## Goal
The method decides for itself when it is not sure (parent box 3): a confidence score with a threshold
SET ON THE 302b HELD-OUT TABLE. Confident fits become automatic platefit documents (auto: true,
"fitter": "ink", the gate's score); unsure fits never reach the map - they go to the site's review
item with the reason (the best starting pairs ride along, so the human drags from a good start).
`tools/site_done.py`'s fit step calls the method on the site's uncovered candidate pictures instead of
the batch's model loop (the station that made the fabricated patterns is replaced at the source; the
line's fabrication check stays as the second line of defence). `pipeline/plan_fit.py`'s build gets the
truth-telling source line for fitter:"ink" documents (today it says "Fitted automatically by the
batch" for any auto doc).

## Acceptance criteria
- [ ] The confidence threshold is fixed on the 302b table (the rule and the chosen value written in
      docs/site_flow.md next to the table) and applied by fit/inkfit.py; an unsure result carries a
      human-readable reason string.
- [ ] site_done's fit step runs the method on uncovered candidates: confident -> new ink-fit document
      (which the existing sync path then checks and builds); unsure -> review-item candidate with the
      reason via fit/review.upsert_item (the item format of data/review/README.md, no new fields the
      page cannot ignore). Covered pictures are still never re-fitted; exit codes unchanged.
- [ ] plan_fit.build prints/stores the correct source line for fitter:"ink" documents (not "by the
      batch"); hand fits and the 20 golden documents stay byte-identical (tests/golden/hand_fit_docs.sha256
      stays green).
- [ ] tests/test_inkfit.py: end to end on ONE hand-fit site's files in the temp tree, no network - the
      site's real plate image and a committed relief seed (data/inkfit/relief/<site>.npz or a
      tests/golden seed, written by this task) drive tools/site_done.py --root; the test asserts through
      the product: the line's per-picture report, the resulting document or review item, and what the
      served page shows for that site. The model step is injectable (a recorded answer), so the test
      never touches a model server.

## Hand-over

(2026-10-12, iteration 84, agent c - FIRST session on 302c. Investigation + design only: NO code
written, suite NOT run this session. Last known suite state (302b session 3, commit 0ca3a65):
64 passed / 1 skipped / 0 failed in this branch; the driver's newest loop-start note still lists
1 failure (test_gate::test_recorded_measurement_reproduces_and_agrees) - verify which state this
branch is in with a suite run before claiming anything.)

**Read first:** the parent's Hand-over (frozen list + method contract), 302b's Hand-over and its
2 DECISIONS-archive entries (threshold guidance), and the "Measured one-shot" table in
docs/site_flow.md (~lines 224-250; section 302b starts line 129). All below was verified by
reading/running this session.

**This session's step (box 1) - do it next, in this order:**
1. fit/inkfit.py (additive ONLY - no frozen parameter, no change to any existing result field):
   - `CONF_THRESHOLD = 0.15` in/after the frozen-config block. Comment: set on the 302b table
     (docs/site_flow.md): the null-margin interval (0.1070, 0.1871] is the ONLY one that separates
     the best fit (badbury +0.1871) from the worst (calleva +0.1070, 2203.6 m); 0.15 is mid-interval
     (0.043/0.037 of room vs the rounded values). Changing it is a method change: label it,
     re-measure, never silently.
   - `decide(objective, null, confidence, gate, fabrication, reason) -> (confident, reason)`: not
     confident when reason set (existing reasons are already human-readable: "no wall ink
     extracted", "no anchor scale (the site has no size_m)", "search found no valid placement",
     "not enough wall ink (2 candidate points, need 4)", fabrication clause); when gate is None or
     verdict != fit_gate.ACCEPT ("the gate refused its own pairs (median residual %s m)"); when
     null or confidence is None ("the search-matched null did not run: no margin to decide on");
     confident only when confidence >= CONF_THRESHOLD; else the margin reason: "null margin %+.4f
     below the 0.15 confidence threshold (fit objective %.4f vs best null %.4f from the same search
     on the <scrambled template | DEM shifted half the box>)" (winner = higher of objective
     scramble/shifted; tie -> scrambled). fit_gate.ACCEPT == "accept".
   - fit(): add result keys "confident" (default False in result()) and "unsure_reason" (None).
     Every existing early return keeps confident=False. Final success return: run decide(...) with
     the ROUNDED values exactly as stored in result and pass confident=..., unsure_reason=....
     **Do NOT put the margin message into `reason`**: inkfit_heldout.measure() stores r["reason"]
     into the frozen one-shot checkpoint (data/inkfit/heldout/results.json) - re-running measure
     would then rewrite it (one-shot violation). `reason` stays None on the success path.
     Update fit()'s docstring result list with the two new keys.
2. docs/site_flow.md: a "**The confidence decision (task 302c).**" paragraph DIRECTLY AFTER the
   Measured-one-shot table: the rule (confident = pairs produced + gate accepted + fabrication
   silent + null ran + margin >= 0.15; confident -> automatic platefit document auto:true,
   fitter:"ink", gate's score; EVERY other outcome -> the site's review item with the reason,
   never to the map), the threshold 0.15 with the interval rationale, and the plain consequence:
   exactly 1 of the 21 held-out docs (badbury, 264.5 m) becomes an automatic fit, the other 20
   go to the review queue with their margins; the threshold rations the pass rate, it is NOT an
   accuracy guarantee (the null does not separate good from bad in this set).
3. Verify: (a) throwaway script: apply decide() to the 21 entries of
   data/inkfit/heldout/results.json -> exactly badbury-rings-q798831.earthworkenglan01allcgoog_
   n0132_1 confident, the rest False; spot-check reason strings (calleva margin-below, arbor-low
   negative margin, camp-d-attila no-ink); (b) `.venv/bin/python fit/inkfit_heldout.py selfcheck`
   -> 21 OK; (c) `.venv/bin/python fit/inkfit_heldout.py table` must be byte-identical to the
   committed Measured-one-shot section (frozen artifact undisturbed); (d) full suite
   `.venv/bin/python -m pytest -q` against the newest loop-start baseline; (e) optional working-
   phase smoke (network OK, ~2 min): `.venv/bin/python fit/inkfit.py badbury-rings-q798831
   earthworkenglan01allcgoog_n0132_1` -> expect margin ~0.1871, JSON now shows confident true.
4. DECISIONS entry + commit "302c: the confidence threshold (0.15) fixed on the held-out table and
   applied by inkfit (box 1) - ...".

**Box 2 (site_done _fit) - next step after box 1.** Replace the batch_us.run_sites call with a
per-uncovered-candidate loop calling inkfit.fit (import inkfit in site_done; it imports pipeline/
fit deps itself). Keep: covered-pictures rule (uncovered = rows not in pre_docs and not in the
item's candidates; no re-fit), the no-candidates/no-pre-fit no_picture item upsert, the need_fit
logic, the re-read, and exit codes 2/1/0. confident -> write the doc: path batch_us._doc_path
(root, sid, plan); content = the result's doc dict (auto True, fitter "ink", score = gate med);
write with the store convention (mkdir parents, indent=1 atomic like batch_us._save_json; never
overwrite an existing doc); print one line (wording free - only test_site_done asserts lines for
ITS scenario). not confident -> review.upsert_item(root, sid, [entry]) with the README format:
plan, title, url (row url, else books/<ia>/<file> for book rows), evidence (review.
candidate_evidence, only when present), pairs = the ink pairs (best start to drag from) or the
propose anchor pairs when the method found no placement, coarse True, why = reason or
unsure_reason, gate_score when a gate ran. No new fields beyond that (the page ignores unknown
keys, but stay minimal). CLI: --model-json FILE now feeds the INK model (recorded answers)
- define the file format {"<site>": {"<plan>": {"boxes": [[[x0,y0,x1,y1], kind], ...], "pieces":
{"<idx>": kind}}]} and a small recorded-model object (duck type: .boxes(panel), .label_pieces(
panel, pieces), .name); default (no flag) = no-model fallback (deterministic) - this REPLACES the
old "no model answer" stub behaviour. --working: keep the flag, but the live-model ink step is
FUTURE work (AI box unreachable from this VM; the 302 parent says "a future Mac run"); honest
options: (a) --working prints that the live ink model is not wired yet and runs the no-model
fallback, or (b) drop the flag. Pick (a) unless the lead's workflow says otherwise - and whatever
is chosen, the line-0 no-model message in main() changes (today: 'fit  no model given: unfitted
pictures (if any) go to the review item as "no model answer"') -> that breaks
**tests/test_site_done.py lines[0]** (asserted verbatim) and its docstring: update that ONE
assertion + docstring line in the same commit (the file is now in my Touches); stonehenge stays
green because all 13 candidates are covered there -> the fit step is not even run in that test
(verify: need_fit False, output line 3 "13 candidate picture(s): 7 fitted (doc), 6 in the review
item -> no batch run needed" must keep its exact form).

**Box 3 (plan_fit.build).** The `how` string: today keyed on doc.get("auto") alone ("Fitted
automatically by the batch ..."). Add: when doc.get("auto") and doc.get("fitter") == "ink" ->
a truth-telling line, e.g. "Fitted automatically by ink matching - the plate's own ink matched
against the site's bare-earth relief - on N matching points; one rotation and scale fits them
within X m (gate score Y m)" (similarity form; the homography form won't occur for ink docs but
handle it). Hand fits (no auto) and all non-ink auto docs stay byte-identical. Check no test pins
the batch wording (grep "Fitted automatically" tests/): test_batch_us/test_batch_eu may - if so,
their docs are non-ink, so the old text is unchanged for them; verify.

**Box 4 (tests/test_inkfit.py).** Two end-to-end tests on ONE site each, system temp tree, dead-
socket guard (copy test_site_done.GUARD pattern: socket.socket.connect etc -> AssertionError;
runpy the copied tools/site_done.py). SITES: badbury-rings-q798831 (confident, margin 0.1871 >
0.15) and calleva-atrebatum-q1027253 (unsure, margin 0.1070 < 0.15). Both are book rows of ia
earthworkenglan01allcgoog (Allcroft 1908), size [3367,5050], map_box badbury [0.107,0.278,0.857,
0.658] / calleva [0.12,0.28,0.81,0.69]; both sites size_m [1600,1600] -> 1600x1600 relief grid;
both are in web/data/sites.json (committed) and in hand_fit_sites.txt. Tree build per test:
copy tools/, fit/, pipeline/; web/data/{sites.json, plans.json, review.json} whole (committed;
propose reads the REAL checkout's catalog via its own ROOT anyway - same values); create an EMPTY
web/data/sites/<sid>/ dir (plan_fit.build only needs the dir; it creates/updates depictions.json
itself; the 19 hand-fit sites have no committed site dirs, so an empty stub is the hermetic way - none of the 6 committed site dirs would work, they are not
hand-fit sites); data/inkfit/
relief/<sid>.npz copied in (committed by me, see below); the plate at data/raw/books/
earthworkenglan01allcgoog/full/n0132.jpg (badbury) / n0360.jpg (calleva) copied from committed
golden copies (data/raw is gitignored in every checkout - the committed copies are what make
"the site's real plate image" hermetic); for badbury REMOVE its hand-fit doc from the copied
data/db/platefits store (so the picture is uncovered); run `.venv/bin/python tools/site_done.py
<sid>` in the tree (no model flag = no-model fallback; ~90-180 s per fit, measured in the
held-out run: badbury 88 s, calleva 177 s -> subprocess timeout 900). Assert through the product:
exit 0; the per-picture report lines (confident: "ink fit confident ..." then "sync ...: synced
to the map" with the new source line; unsure: "sent to the review queue (<reason>)"); the
doc file exists (badbury: auto true, fitter "ink", 10 pairs, score == gate med) or the review
item's candidate (calleva: pairs = the method's pairs, why names the margin below the 0.15
threshold, gate_score present); the served page: start `server/serve.py --port 0` (ephemeral,
conftest.py pattern - DO NOT edit conftest; write a local fixture in test_inkfit.py) against the
post-run tree and GET /data/sites/<sid>/depictions.json (badbury: a plan depiction whose source
contains the ink source line; calleva: none) and /data/review.json (calleva's item open with the
candidate; badbury's absent); the checkout itself untouched (hash pre/post, test_site_done
pattern).
**Committed seeds (write them in the box-4 session, working phase, network allowed):**
- data/inkfit/relief/{badbury-rings-q798831,calleva-atrebatum-q1027253}.npz: keys z (float64
  (h,w) = DEM metres for bbox), px_m 1.0, bbox (the 4 Mercator box edges from aw.site_bbox(site
  lon/lat, 1600, 1600) EXACTLY as inkfit.relief computes them - the loader requires bbox match
  within 1 m and shape (h,w)), and modern (bool mask) - fetch with aw.fetch_dem(bbox, 1600, 1600)
  + aw.modern_mask(bbox, 1600, 1600, 1.0) (osm_ways: 4 tries then raise; if it fails, OMIT the
  modern key and note it - but badbury's held-out run fetched overpass cleanly first try, so the
  mask matters there). BEFORE committing, run inkfit.fit on each site against the new npz and
  confirm the margin reproduces the held-out row (0.1871 / 0.1070) - if it drifts, the EA
  composite changed: record it, and the decision still holds unless a value crosses 0.15.
  np.savez_compressed (terrain compresses well; expect a few MB each - sanctioned by the task
  box, data/inkfit/ is mine). npz must NOT land under data/autofit/ (gitignored) or *.npy
  (globally gitignored) - .npz under data/inkfit/relief/ is fine (gitignore has no such rule;
  verify with git check-ignore before committing).
- Plate copies: data/inkfit/plates/earthworkenglan01allcgoog_n0132.jpg and _n0360.jpg - byte-
  copies of the VM's data/raw/books/earthworkenglan01allcgoog/full/<file>.jpg (check sizes first;
  if huge, the test still needs full fidelity - do NOT downscale; the method is deterministic on
  fixed bytes). If a file is missing from this VM's cache, fetch it via plan_fit.load_picture
  (working phase, paced) before copying.

**Pitfalls found this session (write PITFALLS entries when you hit/confirm them):**
- fit/propose.py module ROOT = its own checkout, NOT the --root passed to site_done/inkfit: in a
temp tree, seed_for reads the REAL checkout's web/data/plans.json, data/books/index.jsonl,
web/data/sites.json (module-level _CACHE). Consequence: the temp tree's copies of those files
must equal the real ones (they do - committed and unmodified by me), else the seed (and hence the
reproduction) changes silently.
- data/raw/ is gitignored in every checkout; committed test images must live in my data/inkfit/
or tests/golden/ and be copied into the temp tree by the test.
- inkfit._relief_z validates the npz (z present, shape (h,w), px_m == 1.0, bbox within 1 m) or
refetches (network) - a mismatched npz silently costs a fetch; in the dead-socket test a
refetch raises -> the test must ship a matching npz.
- The held-out run's modern-mask state: badbury's overpass call succeeded first try (no retry
lines in run.log); berkhamsted/cadbury/calleva/camp-d-attila show 504 retries (3 for calleva ->
4th attempt unlogged; relief() catches Exception -> modern None + note). For exact calleva
reproduction the stored mask may or may not have been used - the margin gap to 0.15 (0.043) is
larger than any realistic mask effect, but record what you actually find.

**Status.** All four boxes unticked. 302a and 302b are done (302b: Status done, its hand-over
lists the frozen list: data/inkfit/heldout/results.json, run.log, the Measured-one-shot section,
fit/inkfit.py's frozen parameters, tests/golden/hand_fit_docs.sha256, the 21 hand-fit docs -
none of that moves). Agent a is on 303 (also touches tools/site_done.py, pipeline/plan_fit.py,
docs/site_flow.md, tests/golden/hand_fit_docs.sha256): keep my edits to those shared files
minimal and localized (the how-string branch in build(); the _fit replacement in site_done; my
own paragraph in site_flow.md; the one assertion in test_site_done) to reduce merge friction;
I do NOT edit fit/batch_us.py (303's) or server/serve.py (303's). Re-read with fresh eyes:
fit/inkfit.py:fit (the decide insertion points), tools/site_done.py:_fit + main (the message),
plan_fit.build (the how branch), tests/test_site_done.py (line-0 + line-3 assertions),
inkfit_heldout.measure (what it stores from r).
