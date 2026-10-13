Status: done
Depends on: 306c, 306d, 306e, 306f
Touches: tests/test_fit_provenance.py

# 231: Re-point the fit_provenance year-once pin off the deleted bethlehem doc

## Goal
tests/test_fit_provenance.py::test_commons_yeared_title_drops_the_repeated_year pins
219's year-once source-line rule on a real store doc that no longer exists:
bethlehem-q2523914.c_a164ee440558d66c ("Plan de Maestricht et environs 1748, detail
Severen & Kanjel (cropped)") was one of the 3 fabricated bethlehem batch docs the 306a
audit took off the map (a858f48 / main 20277f3 - grid-round anchors fitted on maps of
Judaea for a Dutch-polder site, 2000 km away). The audit's own task (306a, done) lists
this test file in its Touches, so the re-point was meant to happen there; it did not.
Until fixed the test fails on every branch with
`FileNotFoundError: ... data/db/platefits/bethlehem-q2523914.c_a164ee440558d66c.json`
(verified on pure main 20277f3 and on agent/a's pre-merge tree, 2026-10-13).

The one pin to move: the test builds one real store doc against flat stand-in pictures
at the doc's own frame size (plan_fit.build in-process, sockets dead - the test file's
`_build_source`) and asserts the built source line verbatim. Re-point it to a
SURVIVING batch doc whose title already states a 4-digit year: after the 306c-f
orphan audits settle, search data/db/platefits/ for docs with src "commons", the
batch's own mark (auto true or by: "agent"), 4+ pairs, and a title containing the
_year4 year (the first 4-digit year 12xx-19xx, plan_fit._year4). Surviving candidates
measured 2026-10-13 include the "…, plan from Mackenzie, The Castles of England
(1897)" set (barnard/bolsover/carisbrooke/cooling/duffield/framlingham/goodrich/
herstmonceux/leicester/ludlow/oxford/raby/taunton) and york-castle-q80637.c_8dac5aacd73916b8
("York Castle in 1820"). Prefer one whose files-row year matches the title's year, so
the parenthesis the rule drops was really there before 219. Then recompute the
expected line from the doc's own fields: "{title}, Wikimedia Commons: {cite}." + the
batch's how-clause ("Fitted automatically by the batch on {n} matching points; one
rotation and scale fits them within {m} m (gate score {score} m)" - or the perspective
variant when model homography) with n = len(pairs) and m from the build on the
stand-in, and assert the repeated-year parenthesis is absent (pre-219 the line read
"{title} (c. {year}), ...").

NOT part of this task: test_line_refuses_unmarked_non_auto_doc (case b) does NOT read
the bethlehem doc - its seed is the golden doc c_022604d2be0becdc from
tests/golden/stonehenge_linecheck_docs/ (7 frozen pattern docs), and its current
failure is the shared Stonehenge 13-candidate/13-row snapshot pin (the 14th plans row
came in with the 211 pictures, main f970500) - that re-pin is task 232. The other
three case-e pins (arbor-low-q630312.earthworkenglan01allcgoog_n0597_1, bergues-
q244934.c_4bbca705be732b1c, durocortorum-q4896307.c_08d995eb23a685c2) all survive in
the store and pass - do not touch them.

## Acceptance criteria
- [x] test_commons_yeared_title_drops_the_repeated_year passes against the post-audit
      doc store (run alone, then in the full suite; no other test's pins disturbed).
- [x] The doc the pin reads exists in data/db/platefits/ at run time and was chosen
      AFTER 306c-f settle (a doc picked before the audits risks being audited off in
      turn); the expected line is recomputed from that doc's own fields (title/cite/
      pairs/score) - not copied from the old bethlehem expectation; the bethlehem docs
      are NOT resurrected (the audit's verdict stands - the anchors were fabricated).
- [x] The test docstring says which audit removed the original pin (306a) and why the
      case now lives on the new doc.

## Notes
- Depends on 306c-f (in flight): they delete more agent docs; re-run the candidate
  search when they land, and only then pick and pin.
- The candidate list above was measured on agent/a's merged tree (2026-10-13, 40
  year-titled docs total, most batch); it will shrink as the audits land.

## Lead close (2026-10-13)
Done by the lead on main (Mac commits ported): see the [lead] commit. Full suite on the Mac: 145 passed, 0 failed.
