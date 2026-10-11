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

(iteration 94, agent a - migration + step 1 done; steps 2-5 pending)

**Done so far (all committed on this branch):**
- Migration (iter 93, 1f562ca): all 116 existing platefit docs carry `by` (21 hand = 20 golden +
  maiden-castle c20ff6b1; 95 agent incl. shotwick's 206 doc); `fit/batch_us.py` `write_doc` stamps
  `by: agent` (batch_eu shares it); golden re-keyed on `by == "hand"` (40 lines: 21 docs + 19
  site.json, shotwick out); `tests/golden/src_mackenzie_sample.json` re-baselined via its own
  `--golden` flag; `auto` untouched everywhere (gate_heldout derivation unaffected).
- Step 1 (iter 94, 7352da3) `pipeline/plan_fit.py`: `who_placed(doc)` -> "hand" | "agent" | None
  (by is authoritative; unmarked is agent only with the batch's own `auto` mark - an unmarked auto
  doc must never read as hand; anything else unplaced). `build()` raises the provenance
  SystemExit (NO_PROVENANCE constant) before any build work. Its public source line now keys on
  who: hand -> existing "Placed by hand..."; auto-with-score -> existing batch+gate strings
  (byte-identical for every doc class in the store - verified: no doc hits the new branches);
  agent-without-gate (the shotwick class) -> "Fitted automatically on N matching points; ...".
  `main()`: unplaced doc -> print refusal, skip (no build, no delete); unmarked auto -> stamp
  `by: agent` into the file (key last, aw.save_json indent=1/no-trailing-newline, migration's
  shape) before the is_done check; then build as today. Verified hermetically (temp-tree root):
  refuse/stamp/skip/marked-untouched, truth table 8/8.
- Data fix (iter 94, 2f863ba) `web/data/sites.json`: 9 drawing counts 0->1 for sites whose fit
  overlay already existed on disk but whose count was never refreshed (same orphan class as
  shotwick's). Produced by the line's own `set_drawings` during a verification sweep I ran
  bare by accident (no root arg - plan_fit has no root guard; PITFALLS entry added). The rebuilt
  webps/depictions were byte-identical to HEAD, so this file is the only real diff.

**Suite at loop end: 64 passed, 1 skipped, 0 failed** (the driver's loop-start test_gate red does
not reproduce here - 1dcbc06/218 fixed it on main, synced in 923f786).

**Still to do, in this order:**
2. `server/serve.py` (in Touches): the PUT /api/db/platefits/<doc> handler (the `api()` PUT/DELETE
   branch, ~line 196) stamps `data["by"] = "hand"` (OVERWRITE: the page's save is the owner's word
   on every pair in the doc) when `parts[2] == "platefits"`, before the existing
   `json.dump(data, f, indent=1)` write - the write already preserves key order, so a doc without
   by gets it last (the migration's shape); a doc with a stale/other by gets it replaced in place.
   Other collections keep the raw bytes (test_document_store_roundtrip uses a scratch collection
   and must stay green). No GET change needed (it returns the file's JSON as-is).
3. `tools/site_done.py` `_sync`: who = plan_fit.who_placed(doc) BEFORE anything else per doc:
   - who == "hand": build, NO fabrication check (the owner's fit - the check exists to police the
     batch model, never a human's drag).
   - who == "agent" (incl. unmarked auto): the existing flow; if the file lacks a trustworthy by
     first stamp by:agent into the doc file (batch_us._doc_path / _save_json convention - OWN SITE
     ONLY, keeps test_site_done's "only that site's files" invariant); pattern doc -> upsert +
     delete as today; clean -> build (plan_fit.build itself now double-guards provenance).
   - who is None (unmarked non-auto - the shotwick class): REFUSED - not built, doc NOT deleted,
     review.upsert_item a candidate {plan, title, url, pairs, why: plan_fit.NO_PROVENANCE},
     reported like a send (a `sent`-style dict or its own bucket; the per-picture summary must say
     refused with that reason). Reuse _pattern_entry's shape; its why-prefix "line check: " is
     fabrication-specific - use NO_PROVENANCE verbatim for this one.
   Re-read after step 3 (from iter 93): _sync - confirm the refusal check precedes any
   plan_fit.build call (a build attempt on an unmarked doc would raise SystemExit from build()
   and count as a sync FAILURE, not a refusal - the report would lie).
4. `tests/test_fit_provenance.py` (hermetic, ephemeral port only, no fixed ports, writes only to
   the system temp dir):
   a. repo invariant: every doc in data/db/platefits/ has a trustworthy provenance - by in
      {hand, agent} (an unmarked doc must at least carry auto: true); the hand set == the golden's
      21 platefit entries and `sha256sum -c tests/golden/hand_fit_docs.sha256` passes.
   b. the line refuses an unmarked NON-auto doc end-to-end: temp copy of one built site (the
      test_site_done.py copy-one-site-tree pattern, sockets dead with its GUARD, no model, no
      download because refusal precedes the build): run the copied line -> exit 0, doc still
      present, no plan overlay in depictions.json, review item gained the candidate whose why is
      exactly plan_fit.NO_PROVENANCE, second run byte-stable.
   c. an unmarked AUTO doc is treated as agent: seed one of tests/golden/stonehenge_linecheck_docs/
      (7 files, auto:true, no by) into the temp store -> the line sends it to the item and deletes
      it (today's behaviour, just without trusting an absent by); if it were clean it would be
      built and the file stamped by:agent.
   d. the page save writes hand: serve.py against a temp tree, port 0 (conftest `served` fixture or
      its own server - see hazard below): PUT /api/db/platefits/<x> without by -> GET shows
      by: hand, and a second PUT that carries a stale by is overwritten to hand.
5. Live run (network OK here): `.venv/bin/python tools/site_done.py shotwick-castle-q7502621` in
   THIS checkout. Expected: who=agent; fabrication_pattern None (iter-93 measurement: lattice
   u-gaps max/med 1.81, v-gaps 3.76, 1D none, grid-round 50% < 90%); doc is src:commons so
   load_picture downloads the big jpg once (paced); it syncs to the map with the new
   "Fitted automatically on 4 matching points..." wording; web/data/sites.json drawings 0->1
   (in Touches). Record outcome + reason + nearest margins in docs/site_flow.md (box 2) and tick
   the boxes. Re-run the full suite afterwards.

**Hazards:**
- The serve worker (after_write) runs plan_fit.main([]) in a DAEMON THREAD on the server's OWN
  tree after any platefits write. In a test tree (conftest copies data/db wholesale, no data/raw)
  that sweep: refuses/stamps fast, but every not-current doc it reaches fails at load_picture -
  book docs FileNotFoundError (fast), commons docs network (the machine HAS network; 76 of the
  116 docs are not-current, see the PITFALLS entry - a mid-sweep non-SystemExit aborts the rest
  of that wake, so expect a partial, slow background sweep). For test d: assert only the
  SYNCHRONOUS PUT/GET effects (the stamp happens in the request handler, before the wake), and
  if you reuse the `served` fixture, do NOT add waits that depend on the background sweep;
  teardown kills the server. Never call plan_fit.main()/the CLI without a temp root in any
  verification (PITFALLS: it sweeps the real checkout and mutates sites.json).
- Agent c (203b) may merge EU batch docs that predate the migration (auto, no by) into main.
  My code treats unmarked-auto as agent (never refused, never hand) and the next line/plan_fit
  sync stamps them by:agent (self-heal) - so my test a must accept unmarked-auto docs but not
  unmarked non-auto ones. Do NOT hand-edit unmarked auto docs in the store.
- 207a/b/c (agent c) will write Roman fits through batch_us.write_doc (by:agent) or the page
  (by:hand) - no action needed from me; if c ever writes a doc file directly, the convention is
  by:agent (say so in a DECISIONS note if you see otherwise).
- tests/golden/hand_fit_docs.sha256: I own it (in my Touches); its byte content changes exactly
  once, in this task (done, iter 93). web/data/sites.json: I own it (in my Touches); 2f863ba
  already refreshed 9 stale counts - step 5's live run adds shotwick's 0->1.
