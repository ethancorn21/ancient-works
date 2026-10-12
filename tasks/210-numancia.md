Status: done
# 210: Numancia - the excavation plans of the 1860s
Depends on: 200
Touches: fit/src_numancia.py, data/catalog/extras_numancia.jsonl, data/commons/files_numancia.jsonl, data/commons/classified_numancia.jsonl, data/raw/commons/numancia/, docs/lead_numancia.md, tests/test_src_numancia.py, tests/golden/

## Goal
GOAL.md point 4: Numancia (the Roman city in Spain, already a built site on the map) gets
its excavation plans of the 1860s. The lead is unverified: find where the plans live (the
1860s-70s excavation reports - the excavations ran under Juan de Dios Villanueva - a book
on Internet Archive, a Spanish archive, or Commons), check that it is old enough, free and
machine-readable, and stage the rows tied to the site. If no free machine-readable copy
exists, document the search and drop the lead.

## Acceptance criteria
- [x] The source of the 1860s plans is verified and recorded in docs/lead_numancia.md
      (where it is, its date, its freedom/license, how the pages are machine-readable) - or
      the lead is dropped, the file says exactly what was searched (sources, dates,
      paywalls, format problems) and why nothing qualified, and this task ends
      `Status: dropped`.
- [x] If verified: staged rows - files_numancia.jsonl for every staged plan tied to the
      existing Numancia site (the identification is part of the verification: the plans
      must depict Numancia, and the row records the specific check) with the 200 evidence
      field and a classified row by hand ("plan"); the plan's date (1860s) recorded on the
      row. extras_numancia.jsonl only if the reports show other sites not in the catalog
      yet.
- [x] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample of rows. If
      the lead was dropped, the test asserts the documentation exists and the staging
      files are absent or empty.

## Notes
- Numancia's excavation plans are the rare case where the drawing is younger than 150
  years would be (1860s = just about old enough) - the age is recorded on the row either
  way; plans of the structure are exempt from the 150-year rule (PLAN.md assumption 4).
- The site is already built with (or without) a drawing: this task adds candidate
  pictures, it does not fit them - the batch/cover loop does.

## Hand-over
(iteration 131, agent c - session 6: **TASK DONE**. The one row is staged, checked and golden-pinned; the lead doc records the final state. If the driver reopens this task, everything below re-verifies in seconds.)

**State.** All three boxes ticked, Status: done. Committed: fit/src_numancia.py (session 5, 431 lines), data/commons/files_numancia.jsonl (the one row: site numancia, Q623407, caption_coords evidence, dist_m 26.1, place_label "Numantia", checked 2026-10-12), data/commons/classified_numancia.jsonl (p_plan 1.0 by hand), tests/test_src_numancia.py (4 tests), tests/golden/src_numancia_sample.json + src_numancia_evidence.txt, docs/lead_numancia.md §7 (the final record: the verbatim staged rows, the no-thumb decision, the --render recipe, the sweep, the tests). extras_numancia.jsonl intentionally ABSENT (no new sites).

**Verification recipe (all offline, seconds):**
- `.venv/bin/python fit/src_numancia.py --check` -> rc 0, no "join:" lines, `PASS   caption_coords       numancia|Plano de las excavaciones hechas en el sitio de Numancia (Lám. IV, fig. 5, Saavedra 1879; excavations of 1853/1855)`, `evidence: 1 rows, 1 pass, 0 fail, 0 no-tie`.
- `.venv/bin/python -m pytest -q tests/test_src_numancia.py` -> 4 passed (socket-blocked fixture; CLI-vs-golden via sys.executable; the Mons negative control fails on the "(the trap), not a tie" clause - 1079 km, computed not hard-coded; golden sample equality).
- Full suite at done-claim: 123 passed, 1 skipped, 0 failed (the driver's four loop-start failures had been fixed on main by other merges before this session).
- Live re-verify of the source (network, working phase): `.venv/bin/python fit/src_numancia.py --sweep` (item up, 766 leaves, file sizes, no license field, the index line, the %PDF range GET, the local render when present).

**The one worktree-local artifact:** data/raw/commons/numancia/0fa271e2444f7bfc.jpg (gitignored shared store; 6713x2709, 1157133 bytes, sha256 c8415ffb94c6bfa50aea92335efef9e0babab8be615f7a44df2b55bfc9931415) - re-derive in any worktree that needs the picture with `.venv/bin/python fit/src_numancia.py --render` (byte-reproducible; task 211's operator runs it before the page or fit tool opens the row - the row is simply absent from plans.json in image-less worktrees, by design). The tests never require the file.

**CLI note:** the staging command is `stage` (no dashes) per the module docstring; `--stage` hits the usage error (session-5/6 hand-overs wrote it dashed - don't "fix" one side without the other).

**For 211 (consolidation):** the two staging files are the complete contribution of this lead; the caption evidence route never consults the catalog, so the check verdict is stable after the rows move into the canonical files; the row's no-thumb + data/raw-gitignored design is recorded in docs/lead_numancia.md §7 and in PITFALLS (the new Internet Archive subsection: per-module --render + hermetic tests).
