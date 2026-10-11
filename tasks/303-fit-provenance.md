Status: in-progress
# 303: Every fit says who placed it - no agent fit passes as a hand fit
Depends on: none
Touches: data/db/platefits/, pipeline/plan_fit.py, tools/site_done.py, tests/test_fit_provenance.py, docs/site_flow.md, fit/batch_us.py, tests/golden/hand_fit_docs.sha256, tests/golden/src_mackenzie_sample.json, server/serve.py, web/data/sites.json

## Goal
The line's fabrication check (301) looks only at documents marked `"auto": true`; a document without the mark is
treated as the owner's hand fit and goes straight to the map. 206 wrote
data/db/platefits/shotwick-castle-q7502621.c_e6e5490609414bb9.json with 4 pairs placed by an agent session
(round page pixels: 405,25 / 827,570 / 620,835 ...) and no mark. The owner's hand fits are listed in
tests/golden/hand_fit_docs.sha256 (20), plus Maiden Castle's DPLA plan placed on the Mac page 2026-10-11 (main cd104ca).

## Acceptance criteria
- [ ] Every platefit document carries who placed it: `"by": "hand"` (the page's save, the owner) or `"by": "agent"`
      (anything a script or a session wrote). The page's save path (server/serve.py -> plan_fit) writes "hand"; every
      agent/script path writes "agent". Existing documents: the 21 hand fits get "hand"; every other one gets "agent".
- [ ] The line treats a document without "by": "hand" as automatic: the fabrication check and everything else that
      applies to automatic fits applies to it. Shotwick's 206 fit goes through that check, and the result (map or
      review queue, with the reason) is recorded in docs/site_flow.md.
- [ ] tests/test_fit_provenance.py: every document in data/db/platefits/ has "by"; the hand ones match the golden list
      plus Maiden Castle; a document without "by" is refused by the line.

## Notes
- Do not change the pairs of any hand fit, and do not touch fit/inkfit.py or the 302 tasks (agent c's job).

## Hand-over

(iteration 93, agent a - MIGRATION DONE, code steps pending)

**Done this session (committed):**
- Every one of the 116 existing platefit docs now carries `"by"`: the 21 hand fits
  (the 20 of the pre-migration golden + maiden-castle-q1232816.c_c20ff6b1f16d173d) get
  `"hand"`, all other 95 (the 94 auto + shotwick's 206 agent doc) get `"agent"`.
  Pairs/`auto`/everything else untouched (verified: only the `"by"` key was added, indent=1, no
  trailing newline, key order preserved).
- `fit/batch_us.py`: `write_doc` stamps `"by": "agent"` on every batch doc it writes (batch_eu
  imports this writer, so both batches are covered); `write_golden` now keys the golden on
  `by == "hand"` (was: not auto). Regenerated golden = 40 lines: the 21 hand docs + the 19
  hand-fit site.json files; shotwick (agent) is OUT of it. `sha256sum -c` = 40/40 OK.
- `tests/golden/src_mackenzie_sample.json` (206's, added to my Touches): pins the shotwick doc
  byte-for-byte, so the migration changed it by one line ("by"); regenerated with the module's
  own `--golden` flag, the mechanism its docstring names for an intended change.
- Full suite green after the migration (64 passed, 1 skipped): the batch tests only require the
  golden files to stay byte-identical (they don't regenerate/compare the set), gate_heldout
  derives over the `auto` set, which the migration does not touch.

**Still to do (the acceptance boxes), next sessions, in this order:**
1. `pipeline/plan_fit.py`: add `who_placed(doc)` ("hand" / "agent" when `by` is valid; else
   `"agent"` only when `"auto"` is true - auto is the batch's own mark, so an unmarked auto doc
   is still an agent fit and must not read as hand; else None). `build()` refuses a doc whose
   who is None (SystemExit, no build) and picks the public source-line wording from who instead
   of `doc.get("auto")` (hand -> "Placed by hand...", agent -> "Fitted automatically...").
   `main()` must refuse (print, skip, never build, never delete) a doc whose who is None, and
   stamp `by: agent` into the file of an unmarked AUTO doc it syncs (self-healing migration for
   batch docs written before the merge - see DECISIONS 2026-10-11 iter 93 for why).
2. `server/serve.py` (in Touches): PUT /api/db/platefits/<doc> stamps `"by": "hand"`
   (overwrite: the page's save is the owner's word on every pair in the doc). Other collections
   untouched (test_document_store_roundtrip uses a scratch collection and stays green).
3. `tools/site_done.py` `_sync`: who = plan_fit.who_placed. who == "hand": build, no fabrication
   check (the owner's fit). who == "agent" (incl. unmarked auto): the existing fabrication
   check; a pattern doc is upserted + deleted as today, a clean agent doc is built (and an
   unmarked auto doc is stamped by:agent in the file first - own site only, keeps
   test_site_done's "only that site's files" invariant). who is None (unmarked NON-auto - the
   shotwick class): REFUSED: not built, doc NOT deleted (it may be a good hand fit that lost its
   mark), a review candidate upserted with the reason "no provenance: the doc has no 'by' field
   (page saves write hand; agent paths write agent)", reported as refused.
4. `tests/test_fit_provenance.py` (hermetic, no network, no fixed ports - copy-one-site-tree
   pattern of tests/test_site_done.py with the socket-dead GUARD and a temp dir):
   a. repo invariant: every doc in data/db/platefits/ has a trustworthy provenance: by in
      {hand, agent} (an unmarked doc must at least carry auto: true - the batch's own mark);
      the hand set == the golden's platefits entries (21, the golden's 20 + maiden-castle
      c20ff6b1) and sha256sum -c over the whole golden passes.
   b. the line refuses an unmarked NON-auto doc end-to-end: temp copy of one built site, a
      synthetic unmarked doc (never built, no download because refusal precedes the build),
      run the copied line (no model needed, sockets dead): exit 0, doc still present, no plan
      overlay in depictions.json, review item gained the candidate with the no-provenance why,
      second run byte-stable (item file unchanged).
   c. an unmarked AUTO doc is treated as agent (fabrication check applies): seed a copy of one
      of the 7 golden stonehenge pattern docs (tests/golden/stonehenge_linecheck_docs/, no by
      field, auto: true) into the temp store -> the line sends it to the item and deletes it
      (same as today's behaviour, just without trusting an absent by).
   d. the page save path writes hand: serve.py against a temp tree (port 0, as test_serve does
      with its `served` fixture) - PUT a platefit doc without by -> GET shows by: hand.
5. Live run + docs/site_flow.md: `.venv/bin/python tools/site_done.py shotwick-castle-q7502621`
   in THIS checkout (network ok live; the doc is src:commons, so load_picture may download the
   big jpg once - it paces itself). Expected: who=agent, fabrication_pattern returns None
   (checked: lattice u-gaps 375/215/207 max/med 1.81, v-gaps 545/120/145 max/med 3.76, 1D none,
   grid-round 4/8=50% < 90%), so it syncs to the map with the auto wording; web/data/sites.json
   drawings 0->1 (in Touches). Record the outcome + reason + nearest margins in
   docs/site_flow.md (box 2).

**Hazards:**
- Agent c (203b, in parallel) has a branch with the OLD 39-line golden and may merge EU batch
  docs that predate this migration (auto, no by). After both merge to main: (i) the golden is
  only ever changed by me, so main takes my 40 lines; c's tests check their checkout's golden
  against their docs - consistent; (ii) c's auto docs reach main unmarked -> who_placed treats
  unmarked-auto as agent (never refused, never hand), and the next line/plan_fit sync stamps
  them by:agent (self-heal). My test a. above must therefore accept unmarked-auto docs but not
  unmarked non-auto ones. Do NOT "fix" unmarked auto docs by hand in the store: let the code
  stamp them.
- 207a/b/c (agent c) will write Roman fits through LLM/batch paths: their docs go through
  batch_us.write_doc (by:agent) or the page (by:hand) - no action for me; if c ever writes a
  doc file directly, the convention is by:agent.
- tests/golden/hand_fit_docs.sha256: I own it now (in my Touches); 203a is done and 203b doesn't
  touch it, so no parallel writer. The golden's byte content changes exactly once, in this task.
- Re-read after step 3: tools/site_done.py:_sync - confirm the refusal check precedes any
  plan_fit.build call (a build attempt on an unmarked doc would raise SystemExit from build()
  and count as a sync FAILURE, not a refusal - the report would lie).
