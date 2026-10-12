Status: done
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
- [x] `.venv/bin/python fit/review.py export` run in the checkout: web/data/review.json is
      republished; the only item files that change are the ones whose resolving document
      now exists, and only by gaining the write-once `resolved: {doc, at}` record; nothing
      else in data/review, data/db/platefits or web/data/ changes.
- [x] A second export run changes nothing but the page's `at` (idempotent: page item list
      identical, item files byte-identical) - the page is in sync with the items under the
      current rules.
- [x] The three tests above are green and the full suite has no failures beyond the
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
- The `Depends on: 309` was my own safety gate ("run the export on top of 309's final store
  state, never in parallel"). The lead overrode it: their 2026-10-12 message ("220 done on
  main ... build on main, do not wait for c 309/804/805") and their own commit c5250a4
  (the export, committed to main) - the human's word wins. The export's inputs (data/review
  items, the platefits docs, web/data/sites.json) were not mid-write when it ran, so the
  override was safe in practice: the page is a snapshot of that instant, and the drift
  watch below covers anything that lands after it.
- Post-export drift watch (still armed): any commit that ADDS data/review item files
  (agent c's 203b EU batch, 207 Roman, 805's rebuild upserts) or places/deletes fit docs
  re-stales the page against the three derived-count tests with numbers different from
  335/334 - the fix is another full export (this task's box-1 mechanism, commit the two
  store paths), never a test re-baseline. The review-page PITFALLS entry carries the same
  watch (third trigger).

## Hand-over

(2026-10-12, iteration 121, agent a - closed.) The lead ran this task's work themselves:
main's c5250a4 is the full export (340 -> 335 open of 341; the 6 write-once resolved
records; their message names the cause - matcher docs placed without a re-export). Agent
a verified it from main in a scratch copy (git archive main, seeded with the gitignored
web/data/sites + the data/raw symlink): the commit's diff is exactly the 6 item files
(each only gaining the resolved record) + the page, nothing else in the store; a
re-export over that state is a no-op (only the page's `at` moves; the 335-item list
byte-identical); the three named tests pass (25.5 s) and the full seeded suite is 75
passed + 1 skipped, 0 failed (the "73" in box 3's parenthetical predates 214's 2 new
region tests; the union after my 307ba sync is 76 tests = 75 passed + 1 skipped, which is
what 307ba's re-claim expects). All boxes ticked, Status: done. If a future session sees
the three derived-count tests fail with numbers OTHER than 335/334 against a
post-c5250a4 page, that is population drift after the snapshot, not this task's work:
run a full `fit/review.py export` on the current tree, commit the two store paths, and
re-run the three tests.
