Status: dropped
Depends on: 230
Touches: tests/test_matchfit_station.py, tests/fixtures/matchfit_station/

# 243: Re-record the 302f matcher-station fixtures after 230's index rebuild drifted the input hashes

## Dropped (2026-10-14, iteration 216, agent a)

Absorbed into 230 itself. The driver rejected 230's done-claim (a423d19) naming this
task's two tests as new failures - but they failed because of 230's own index rebuild,
so a separate task with "Depends on: 230" was a deadlock (the driver cannot accept 230
while 243's tests are red, and 243 cannot run until 230 is accepted). 230 added the two
paths to its own Touches line and re-recorded the fixtures itself (record.py against the
live ELoFTR, 2026-10-14 23:15Z): index_row re-stamped 4c7be2d0 -> 003d1d77, replay
validated, test_matchfit_station 2/2 green on 230's branch. Nothing left for this task.

## Goal
230's book-index rebuild (37edbfb, the 211 consolidation re-run) re-stamped
evidence.checked on all 1,112 index rows (2026-10-12 -> 2026-10-14). The 302f
fixtures (tests/fixtures/matchfit_station/records.json, records_unsure.json) pin
sha256 hashes of their 9 inputs in the header (`header.input_hashes`: hand_doc,
plan_image, site_dir, sites_entry, plans_row, index_row, catalog_row, site_json,
data_review), and tests/test_matchfit_station.py::_drift recomputes them against
the live repo on every run, failing both tests with "rerun record.py" on any
mismatch. The only drifted input is `index_row`: the pinned row
earthworkenglan01allcgoog_n0132_1 hashes 4c7be2d0... in the fixture (== the row at
37edbfb^; the fixture itself was re-recorded 2026-10-14 06:04Z by task 238,
8af2d91, against the pre-230-rebuild index) vs 003d1d77... now, and the ONLY field
that changed is `evidence` (the checked stamp). The 15 matcher request bodies per
fixture are unchanged (same plan crop / ground / window), so the re-record should
replay the same candidates - it re-stamps the 9 input hashes, re-records the live
responses and re-validates the replay against the frozen held-out checkpoint
(data/matchfit/heldout/results.json).

Working phase (live ELoFTR required): confirm the matcher is up (curl
127.0.0.1:8091 - the model servers run on this VM's own cards, see the PITFALLS
"Model servers (this VM's own cards)" entries), then run
`.venv/bin/python tests/fixtures/matchfit_station/record.py` and commit the two
refreshed fixtures.

## Acceptance criteria
- [ ] Both tests in tests/test_matchfit_station.py pass (_drift no longer fires:
      the fixture header's index_row hash equals the current row's hash).
- [ ] The refreshed headers show recorded_at after 230's rebuild (2026-10-14), and
      the response key SET (sha256 of each request body, 15 per fixture) is
      unchanged from before the re-record - the requests are byte-identical, so
      only the header moves (response values may have moved slightly if the GPU
      drifted; record.py's replay + heldout checks validate that).
- [ ] No change to the test file's logic or to record.py itself (record.py
      regenerates the fixtures, it is not edited for this).
