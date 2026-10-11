Status: open
# 208: The German Limes - fort plans from the old reports
Depends on: 200
Touches: fit/src_limes.py, data/catalog/extras_limes.jsonl, data/commons/files_limes.jsonl, data/commons/classified_limes.jsonl, docs/lead_limes.md, tests/test_src_limes.py

## Goal
GOAL.md point 4, the least certain of the seven leads: fort plans from the German Limes
reports (ORL and its successors; the forts of the Upper and Lower Germanic Limes are a
natural growth area - many are not in the catalog yet). Verify first whether free,
machine-readable fort plans exist (old government reports are public domain, but the scans
must actually be available: a library site, an archive, Internet Archive, or Commons). If
yes: stage the plans tied to their forts. If no: document exactly what was searched and
drop the lead - the other six leads stand on their own (PLAN.md assumption 7).

## Acceptance criteria
- [ ] docs/lead_limes.md records the verification either way: what sources were checked
      (names, URLs, dates), what is free and machine-readable, and the decision (proceed /
      drop). A dropped lead ends this task with `Status: dropped`, the documentation
      committed, and no staging files.
- [ ] If proceeding: staged rows - files_limes.jsonl for every staged fort plan (with the
      200 evidence field: the report's list/caption names the fort; coordinates from the
      report cross-checked where possible) and extras_limes.jsonl for forts not in the
      catalog (QID from Wikidata where it exists, kind "roman fort", lon/lat from the
      report); a classified row by hand per picture; the plan's date recorded on the row
      (the 150-year rule: fort plans of structures are exempt, recorded anyway).
- [ ] At least 10 fort plans staged from at least 2 sources, or the documentation accounts
      for every missing one with a reason (a verified drop beats a guessed row).
- [ ] fit/evidence.py check passes offline on every staged row; test (no network): the
      staged files join and the evidence check passes, with a golden sample. If the lead
      was dropped, the test asserts the documentation exists and the staging files are
      absent or empty.

## Notes
- If the reports turn out to be Internet Archive books indexable with pipeline/books.py,
  work in per-book files only (triage/<ia>.*, lists/<book>.json) and add those exact paths
  to this task's Touches line before writing them - never the shared index.jsonl or
  validation.json (211 rebuilds both).
- The forts' QIDs are patchy on Wikidata: name+coordinates from the report is an acceptable
  tie when no QID exists, recorded as such on the row (the evidence kind says so).

## Hand-over
