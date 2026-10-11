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

(iteration 97, agent a - steps 1-4 done; step 5 (shotwick live run + site_flow.md) pending)

**Done and committed on this branch (all verified, suite 68 passed / 1 skipped / 0 failed at loop end):**
- Migration (iter 93, 1f562ca): all 116 platefit docs carry `by` (21 hand = 20 golden + maiden-castle
  c20ff6b1; 95 agent incl. shotwick's 206 doc); `fit/batch_us.py` write_doc stamps `by: agent`
  (batch_eu shares it); golden re-keyed on `by == "hand"` (40 lines: 21 docs + 19 site.json, shotwick
  out); `tests/golden/src_mackenzie_sample.json` re-baselined via its own --golden; `auto` untouched
  everywhere (gate_heldout derivation unaffected).
- Step 1 (iter 94, 7352da3) `pipeline/plan_fit.py`: `who_placed(doc)` -> "hand" | "agent" | None (by
  authoritative; unmarked is agent ONLY with the batch's own auto mark; anything else unplaced).
  `build()` raises the NO_PROVENANCE SystemExit before any build work; public source line keys on who
  (hand -> "Placed by hand..."; auto-with-score -> the existing batch+gate strings, byte-identical for
  every stored class; agent-without-gate -> "Fitted automatically on N matching points...").
  `main()`: unplaced -> refuse (no build, no delete); unmarked auto -> stamp by:agent into the file
  (self-heal). Data fix 2f863ba: web/data/sites.json 9 stale drawing counts refreshed by the line's own
  set_drawings (orphan class, no depictions changed).
- Step 2 (iter 95, 5f728aa) `server/serve.py`: PUT /api/db/platefits/<doc> stamps by:hand (overwrite;
  both page save paths go through it); other collections byte-identical; module docstring records it.
- Step 3 (iter 96, 77f0cc0 + 1cf8a24) `tools/site_done.py`: the line acts by who_placed, decided FIRST
  in `_sync_doc`: (1) who None (unmarked non-auto) -> REFUSED: no build, no delete, upsert a
  `_provenance_entry` candidate (why = plan_fit.NO_PROVENANCE verbatim), own "refused" report bucket,
  NOT a sync failure (exit 0); (2) who agent with by absent (unmarked auto) -> `_stamp_agent` writes
  by:agent into the doc file first; (3) who != hand -> fabrication check as before (pattern: upsert
  _pattern_entry + unlink) then is_done/build (plan_fit.build's guard is the double protection);
  (4) who hand -> straight to is_done/build, check skipped. Refusal precedes EVERYTHING.
- Step 4 (iter 97, THIS session) `tests/test_fit_provenance.py` (4 tests, all hermetic, ephemeral
  ports, system temp dir only): (a) repo store - every doc has by in {hand, agent} or at least the
  batch's own auto mark (never unmarked non-auto; unmarked-auto tolerated: 203b may merge
  pre-migration EU docs, the self-heal stamps them), hand set == the golden's 21 platefit entries,
  `sha256sum -c tests/golden/hand_fit_docs.sha256` passes (the 20 golden + Maiden Castle byte-frozen);
  (b) end-to-end refusal (copied Stonehenge tree + GUARD, no model - refusal precedes the build so no
  download): seed = golden doc c_022604d2be0becdc with its auto mark stripped (its pairs ARE the 1D
  ladder pattern, so the test proves refusal precedes the check); asserts exit 0, exact stdout
  (13 lines incl. the refused line with NO_PROVENANCE verbatim and the 12 item-candidate lines with
  the 201-contract resolved suffix), doc kept byte-identical (no stamp), no plan_* built, item at its
  own path with resolved {doc, at} write-once, refused candidate == _provenance_entry rebuilt
  in-process, item LEFT web/data/review.json's open list, one-site-only invariants, second run
  byte-stable with identical lines (refusal idempotent); (c) in-process unmarked-auto = agent (no
  network): the golden pattern doc sent+deleted with the check's reason; a non-pattern doc (coords
  13.4/27.9/88.2/121.7 x 22.6/55.1/60.8/134.3 - all three clauses dodged, verified in the test) with
  a current overlay -> "skipped" AND the file stamped by:agent (key last, indent=1, no trailing
  newline), second pass no re-stamp; hand exemption: the SAME pattern doc with a current overlay,
  by:hand -> "skipped" (a pattern doc skips only if the check did not fire - it polices the batch
  model, never a human's drag), by:agent -> "sent" + deleted; (d) the real server (serve.py --port 0
  against a temp tree with no pipeline/ - the fit worker dies on import, so no sweep, no network;
  the file-set assertion proves it): PUT platefits without by -> by:hand key last; stale by:agent
  overwritten in place (position kept); another collection's bytes raw.

**Still to do (step 5):** the live run (network OK on this machine): `.venv/bin/python
 tools/site_done.py shotwick-castle-q7502621` in THIS checkout. Expected: who=agent (by: agent, no
 auto, no score) -> no stamp (by present); fabrication_pattern None (iter-93 measurement: lattice
 u max/med 1.81, v 3.76; 1D none; grid-round 50% < 90%); src:commons -> load_picture downloads the
 big jpg once (paced); synced to the map with the new "Fitted automatically on 4 matching points..."
 source line; web/data/sites.json drawings 0 -> 1 (in Touches - commit it). Record the outcome
 (map, with that reason and the nearest margins) in docs/site_flow.md (acceptance box 2), tick the
 boxes, re-run the full suite.

**Hazards:**
- Never call plan_fit.main()/its CLI bare (no root guard) - it sweeps the real checkout and mutates
  web/data/sites.json (PITFALLS). Always a temp root or --root <temp tree>.
- The serve worker's after_write runs plan_fit.main() on the server's OWN tree after any platefits
  write: in a test tree without data/raw, not-current docs fail mid-sweep (one non-SystemExit aborts
  the rest of that wake; 76 of the 116 docs are not-current here). In tests assert only synchronous
  request effects; if a full data/db is in the tree, expect a slow partial background sweep. (The
  303 test d's tree has no pipeline/ at all, so the worker dies on import - no sweep, no network.)
- data/raw is a SHARED symlinked store (PITFALLS) - never compare per-site web/data/sites/* bytes
  from a live run against a fixed baseline; the temp-tree pattern (copy, not symlink) is safe.
- Agent c (203b) may merge pre-migration EU docs (auto, no by) into main; the code self-heals them
  (stamp by:agent at the next sync) - test a must accept unmarked-auto. Do NOT hand-edit unmarked
  auto docs in the store. 207's Roman fits arrive via batch_us.write_doc (by:agent) or the page
  (by:hand) - no action needed; if c writes a doc file directly, the convention is by:agent.
- The step-4 tests pin the repo's 21-hand set and the stonehenge 13-candidate item (lead = the book
  row earthworkenglan01allcgoog_n0582_1, which is why the refusal's upsert keeps the item file's
  name). If a human adds a hand fit or a batch changes that item, the tests fail by design -
  extend them on purpose (the golden is re-keyed the way iter 93 did it).
- Candidate follow-up (a human decision, not built by me): a REFUSED doc auto-resolves its review
  item per 201's derived-resolution contract (doc exists -> resolved -> the page hides the item), so
  a refused candidate is only findable in the item file, not the Review tab. 303 conforms (fit/review.py
  not in my Touches); if the human wants refused candidates page-visible, that is a 201 contract
  change -> new top-level task (lowest free number 200-499, Depends on: 303, Touches: fit/review.py +
  a test). The real 303 case (shotwick) is by:agent -> map, so nothing live is affected today.
