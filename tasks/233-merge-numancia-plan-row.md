Status: open
Depends on: 212
Touches: tests/test_merge.py, web/data/plans.json

# 233: The merged Numancia picture back in the plan list (machine-dependent exclusion)

## Goal
tests/test_merge.py::test_plan_list_refresh_is_pure_growth asserts that 210's merged
Numancia picture reached the plan list: a row with sites ["numancia"] and book
"Wikimedia Commons" (its 206 Shotwick twin passes). It has failed on main since
f970500 with "no Wikimedia Commons plan row for the merged picture of numancia".

Root cause (measured on agent/a's merged tree, 2026-10-13): the exclusion is
MACHINE-DEPENDENT, not a data loss. tools/export_plans.py's commons_rows() includes a
picture only when a local copy exists at data/raw/commons/<site>/<sha16(title)>.jpg -
and data/raw is gitignored, so every machine carries its own copies. (The books
branch is machine-dependent the same way: an index row is skipped without its
full_local page image.) The numancia row itself never changed: the files.jsonl row
(by fit/src_numancia.py, url archive.org/details/memoriasdelareal009real, title
"Plano de las excavaciones hechas en el sitio de Numancia (Lám. IV, fig. 5, Saavedra
1879; …)") and its classified row (p_plan 1.0, by hand) are byte-identical from
ef84a05 through f970500 to HEAD; its local copy data/raw/commons/numancia/
0fa271e2444f7bfc.jpg sits in this VM's shared store (210 staged it), while the lead's
Mac - where f970500's re-export ran - lacked it, so the re-export dropped the row.
Measured: running export_plans on this machine reproduces 953d9ab's 1168-row
plans.json BYTE-FOR-BYTE, numancia row included (it is a COMMONS row: book
"Wikimedia Commons", id c_0fa271e2444f7bfc = sha16 of the title; the books index and
memoriasdelareal009real's page images are not involved - an earlier note guessed
"book = the ia id", which was wrong). Conversely, the 307 rows the lead's 1474-row
file carries (the 211 pictures, the Civitates/Merian full pages) have no local
copies on this machine yet, so a naive re-export HERE would drop them instead.

## The work (after 212 lands)
1. 212's live run fetches a local copy for every kept files row that lacks one (its
   fetch phase: thumb first, else the full-file url via commons.info's 1280 px
   imageinfo; paced 1/s, resumable, skips rows that already have a copy) and then
   regenerates plans.json - so on this machine the numancia row AND the 307 Mac rows
   come back in that re-export, and the test should pass unchanged. Verify: run the
   test, and diff the re-exported key set against the committed 1474 - every
   pre-existing (id, sites[0]) key must survive (the test's own "pure growth"
   assertion checks this; a row lost to a failed fetch is a data finding to record,
   not something to patch around - see the 212 hand-over's live-run note).
2. Only if the test still fails on the numancia row (that one fetch failed): fetch the
   1879 plate (leaf 507, Lám. IV, of IA item memoriasdelareal009real - the files row's
   own url names the item; pipeline/books_ia.py page images or the item's full page)
   and save it as data/raw/commons/numancia/0fa271e2444f7bfc.jpg, re-run
   tools/export_plans.py, commit the plans.json delta. The row then comes back exactly
   as ef84a05's (same name/cite) - the test needs no re-pinning.
3. Record the machine-dependence so a future re-export's row deltas read as
   environment, not data loss: the test's docstring (a plans.json row exists only on
   machines that hold the picture's local copy - f970500's Mac port dropped numancia
   this way, and a re-export elsewhere can only grow what its own store holds) and
   the PITFALLS.md entry on export_plans (added by 212's investigation; extend it if
   anything new is found).

## Acceptance criteria
- [ ] test_plan_list_refresh_is_pure_growth passes (both the shotwick and the numancia
      half) against the post-212 plans.json, alone and in the full suite.
- [ ] Every (id, sites[0]) key of the committed pre-212 plans.json (1474) is present
      in the re-exported file: no silent loss of the 211/Civitates rows on this
      machine.
- [ ] The machine-dependence is recorded (docstring and PITFALLS), so the next
      re-export's row deltas are explainable at a glance.

## Notes
- Depends on 212: it alone writes web/data/plans.json now (this task must not race
  its fetch/re-export); run strictly after it.
- If step 1 finds the test already green, this task shrinks to verification + the
  recording of step 3: that is still worth its own commit.
