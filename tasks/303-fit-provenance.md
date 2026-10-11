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

(iteration 96, agent a - steps 1-3 done; step 4 (tests) and step 5 (shotwick live run + site_flow.md) pending)

**Done and committed on this branch (all verified, suite 64 passed / 1 skipped / 0 failed at loop end):**
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
  `_provenance_entry` candidate (shape of _pattern_entry but why = plan_fit.NO_PROVENANCE verbatim - no
  'line check:' framing, no gate-score sentence), own "refused" report bucket, NOT a sync failure
  (exit 0); (2) who agent with by absent (unmarked auto) -> `_stamp_agent` writes by:agent into the doc
  file first (batch_us._doc_path/_save_json, key appended last, indent=1 no trailing newline; own site
  only; no print of its own); (3) who != hand -> fabrication check as before (pattern: upsert
  _pattern_entry + unlink) then is_done/build (plan_fit.build's guard is the double protection);
  (4) who hand -> straight to is_done/build, check skipped. Refusal precedes EVERYTHING (check and
  build) - that is the adversarial guarantee (an unmarked PATTERN doc is refused, not sent).

**Still to do, in this order:**
4. `tests/test_fit_provenance.py` (hermetic; ephemeral ports only; writes only to the system temp dir).
   The test_site_done.py shapes are the model (copy-one-tree + GUARD subprocess; in-process module
   load for entry-shape checks). Cases:
   a. repo invariant: every doc in data/db/platefits/ has by in {hand, agent}; an unmarked doc must
      at least carry auto: true (accept unmarked-auto - agent c's 203b may merge pre-migration EU
      docs; never unmarked non-auto); the hand set == the golden's 21 platefit entries;
      `sha256sum -c tests/golden/hand_fit_docs.sha256` passes.
   b. the line refuses an unmarked NON-auto doc end-to-end (copy-one-built-site tree, sockets dead via
      the GUARD, no model - refusal precedes the build so no download): exit 0; doc still present and
      byte-identical (no stamp); no plan_* overlay in the site dir; the site's review item gained the
      candidate whose why is EXACTLY plan_fit.NO_PROVENANCE (rebuild it with the module's own
      _provenance_entry, like test_site_done does for _pattern_entry); SECOND the 201-contract
      outcome: export recorded resolved: {doc: <site>.<plan>, at: <doc's at>} into the item file
      (write-once) and the item LEFT web/data/review.json's open list (the page never shows it -
      PITFALLS entry); second run byte-stable, identical lines (refusal idempotent). Worked example:
      the iter-96 DECISIONS entry (Stonehenge tree, seed = a golden doc with its auto mark stripped;
      the item's lead candidate is a book row, so the item file keeps its name).
   c. an unmarked AUTO doc is treated as agent - never hand, never refused: (i) seeding one of
      tests/golden/stonehenge_linecheck_docs/ (auto:true, no by) sends it to the item and deletes it -
      test_site_done_line already pins exactly this, a light re-assert suffices; (ii) network-free
      proof of the rest: an unmarked-auto doc WITH a current overlay (fake site dir + depictions.json
      entry fit:{at, doc} matching the doc's at and <site>.<plan>) -> "skipped" AND the file stamped
      by:agent (key last, indent=1 bytes); second pass no re-stamp. Coords must dodge
      fabrication_pattern: irregular one-decimal values, nothing within 0.5 px of a multiple of 10, no
      3 sharing a coordinate, no near-arithmetic gaps (the iter-96 script used u 13.4/27.9/88.2/121.7,
      v 22.6/55.1/60.8/134.3). The hand exemption, network-free: the SAME doc marked by:hand ->
      "skipped" (a pattern doc with a current overlay returns "skipped" ONLY if the check did not
      fire), while marked agent -> "sent" + deleted.
   d. the page save writes hand: serve.py against a temp tree, --port 0, NO pipeline/ copied (worker
      dies on import - no sweep, no network): PUT /api/db/platefits/<x> without by -> GET shows
      by:hand (key last, indent=1, no trailing newline); a second PUT carrying a stale by ->
      overwritten to hand in place; a PUT to another collection -> bytes raw.
   Re-read after step 4: `_sync_doc` in tools/site_done.py - fresh-eyes confirm the refusal check
   precedes the fabrication check and the build (a build attempt on an unmarked doc would raise
   SystemExit from build() and report as FAILED, not refused - the report would lie).
5. Live run (network OK on this machine): `.venv/bin/python tools/site_done.py shotwick-castle-q7502621`
   in THIS checkout. Expected: who=agent (by: agent, no auto, no score) -> no stamp (by present);
   fabrication_pattern None (iter-93 measurement: lattice u max/med 1.81, v 3.76; 1D none; grid-round
   50% < 90%); src:commons -> load_picture downloads the big jpg once (paced); synced to the map with
   the new "Fitted automatically on 4 matching points..." source line; web/data/sites.json drawings
   0 -> 1 (in Touches - commit it). Record the outcome (map, with that reason and the nearest
   margins) in docs/site_flow.md (acceptance box 2), tick the boxes, re-run the full suite.

**Hazards:**
- Never call plan_fit.main()/its CLI bare (no root guard) - it sweeps the real checkout and mutates
  web/data/sites.json (PITFALLS). Always a temp root or --root <temp tree>.
- The serve worker's after_write runs plan_fit.main() on the server's OWN tree after any platefits
  write: in a test tree without data/raw, not-current docs fail mid-sweep (one non-SystemExit aborts
  the rest of that wake; 76 of the 116 docs are not-current here). In tests assert only synchronous
  request effects; if a full data/db is in the tree, expect a slow partial background sweep.
- data/raw is a SHARED symlinked store (PITFALLS) - never compare per-site web/data/sites/* bytes
  from a live run against a fixed baseline; the temp-tree pattern (copy, not symlink) is safe.
- Agent c (203b) may merge pre-migration EU docs (auto, no by) into main; the code self-heals them
  (stamp by:agent at the next sync) - test a must accept unmarked-auto. Do NOT hand-edit unmarked
  auto docs in the store. 207's Roman fits arrive via batch_us.write_doc (by:agent) or the page
  (by:hand) - no action needed; if c writes a doc file directly, the convention is by:agent.
- Candidate follow-up (a human decision, not built by me): a REFUSED doc auto-resolves its review
  item per 201's derived-resolution contract (doc exists -> resolved -> the page hides the item), so
  a refused candidate is only findable in the item file, not the Review tab. 303 conforms (fit/review.py
  not in my Touches); if the human wants refused candidates page-visible, that is a 201 contract
  change -> new top-level task (lowest free number 200-499, Depends on: 303, Touches: fit/review.py +
  a test). The real 303 case (shotwick) is by:agent -> map, so nothing live is affected today.
