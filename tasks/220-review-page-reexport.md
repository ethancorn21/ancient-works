Status: open
Depends on: 309
Touches: data/review, web/data/review.json

# 220: Review page: re-export under the current resolution rules (the committed page is stale)

## Goal
web/data/review.json on main (cf29be2) is a stale derived page: it was published 2026-10-11
18:48 (340 open of 341) BEFORE the lead's b22a2d2 (22:27) and cf29be2 (22:35) (1) changed
fit/review.py::resolved_doc (a recorded resolution counts only while its document exists)
and (2) placed 5 matcher fit documents into data/db/platefits (argentoratum
c_e882645cc479c889, castle-neroche n0110_1, castra-lemanis c_be12fb0f9a87000b,
ferme-d-azincourt c_804aa7af3eb2ac7c, forthill b24849959_n0269_1). Under the current rules
the export excludes those 5 items (the stale page still lists them - the owner's Review tab
advertises resolved items) and records write-once `resolved: {doc, at}` into 6 item files
whose resolving doc now exists (those 5 + alligator-effigy-mound n0214_2, already off the
page). Three tests that derive their expected open count from the live page while running
the current code in a temp tree fail on every branch containing cf29be2 until the page is
re-exported: test_fit_provenance::test_line_refuses_unmarked_non_auto_doc (the run prints
334 open of 341, expected 339 = 340-1), test_site_done::test_site_done_line (prints 335,
expected 340), test_fit_queue::test_save_runs_the_one_site_line (open_after 334, expected
339). The fix is a full export of the current code (site_id=None) in the checkout: record
the resolutions, rewrite the page, commit the two store paths. No code change, no test
re-baseline (the tests are correct to fail; 803's re-baseline precedent is for tests that
pin a population - these derive).

## Acceptance criteria
- [ ] `.venv/bin/python fit/review.py export` run in the checkout: web/data/review.json is
      republished; the only item files that change are the ones whose resolving document
      now exists, and only by gaining the write-once `resolved: {doc, at}` record; nothing
      else in data/review, data/db/platefits or web/data/ changes.
- [ ] A second export run changes nothing but the page's `at` (idempotent: page item list
      identical, item files byte-identical) - the page is in sync with the items under the
      current rules.
- [ ] The three tests above are green and the full suite has no failures beyond the
      driver's known-failure set (expect 73 passed + 1 skipped once 307ba is merged too).

## Notes
- Filed by agent a (307ba) iteration 116 after the driver rejected 307ba's done claim for
  exactly these three failures. Verified in a scratch copy of the store (2026-10-12): the
  export prints "review: 335 open of 341 items"; the six records are alligator n0214_2 ->
  c_618a6be74dfaff32 (the 203a batch doc), argentoratum c_6acfd94dec8c011b ->
  c_e882645cc479c889, castle-neroche n0110_1 -> its own doc, castra-lemanis ->
  c_be12fb0f9a87000b, ferme-d-azincourt -> c_804aa7af3eb2ac7c, forthill ->
  b24849959_n0269_1; the second export is a no-op. As of cf29be2 the page goes 340 -> 335
  open of 341.
- Depends on 309 (agent c, active) - run the export on top of 309's final store state,
  never in parallel with it. As of iteration 117, 309 is SPLIT (on agent/c): 804 wires the
  right-place check into tools/fit_queue.py; 805 (depends on 804) rebuilds the committed
  data - and 805's rebuild re-exports web/data/review.json in-process via fit/review.py
  export, necessarily a FULL export (the namesake upserts span sites, and the page file is
  always computed over the whole queue). A full export is this task's box 1: it records the
  write-once `resolved` records (the 307ba iteration-116 scratch run verified the
  site_id=None semantics and the no-op second run). So when this task runs, both boxes are
  likely a no-op verification (page in sync, item files byte-identical, suite green) - run
  the export anyway, prove it, close as verified. A dep on a split parent parks until full
  closure (agent c's 2026-10-12 309 DECISION entry documents it); 309's closure after 805
  is bookkeeping-only (no store change), so the wait costs one agent-c session, not a store
  dependency. The dep stays on 309 (not re-pointed at 805): 309 is the driver-visible task
  (the prompt names it), and 804/805 had not reached this checkout's tasks/ when this note
  was written - a dep on a task file that no checkout shares risks parking forever.

## Hand-over

(2026-10-12, iteration 117, agent a - the filer, for whoever runs this.) By the time the
driver hands this out, main carries 804 + 805 merged (and 309's closure bookkeeping); 805's
run already re-exported web/data/review.json in-process. Expected run: 1) `.venv/bin/python
fit/review.py export` in the checkout - if 805 already did it, expect a no-op (only the
page's `at` moves; item files byte-identical: the six write-once `resolved` records the
iteration-116 307ba scratch run proved are already there); 2) confirm box 2 (a second run
changes nothing); 3) run the three tests named in the Goal (test_fit_provenance::
test_line_refuses_unmarked_non_auto_doc, test_site_done::test_site_done_line, test_fit_
queue::test_save_runs_the_one_site_line) - expect green once 307ba is also merged (307ba's
re-claim waits on this task, so by then it is). If the export DOES change item files (a
resolving doc landed after 805's run), that is the real fix: commit the changed store paths
and re-run the suite. Re-read fit/review.py::export (line 184) for the site_id=None
full-export semantics; derive the expected counts, never pin them (the Goal's "340 -> 335"
arithmetic was true at cf29be2 and moves with the store).)
