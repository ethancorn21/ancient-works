Status: in-progress
# 207a: Horsley, Britannia Romana (1732)
Depends on: 200
Touches: fit/src_roman_horsley.py, data/books/triage/, data/books/lists/, data/raw/books/britanniaromanao00hors/

## Goal
Subtask of 207 (the parent's Hand-over has the full mechanics): index John Horsley's
*Britannia Romana* (1732) with the existing book machinery and stage its site-plan rows tied
to Roman sites. Chosen IA copy: `britanniaromanao00hors` (Google Books scan, 936 leaves,
median 2237x3861 px, hOCR page text + djvu.txt present). Alternatives (only if specific pages
of the Google copy are unreadable): `bim_eighteenth-century_britannia-romana-or-the_horsley-john_1732`
(British Museum, 831 leaves, median 7984x13809 px) and the `..._0` copy (827 leaves,
8328x14257 px) - much larger images.
Note: this book's ~121 engraved plates are mostly Roman inscriptions and sculptures (list
kind "o"); its true site plans are the few maps (kind "s"). Stage the site plans; the
inscription plates are indexed in the list mapping (each names the site where the stone was
found) but are not staged as picture rows.

## Acceptance criteria
- [x] The book is fetched from the Internet Archive (data/raw/books/britanniaromanao00hors/)
      and triaged with the existing machinery, per-book artifacts only
      (triage/britanniaromanao00hors.*.jsonl, lists/britanniaromanao00hors.json,
      lists/britanniaromanao00hors.map.json); the shared data/books/index.jsonl and
      validation.json are NOT written by this subtask.
      (done 212-220: fetch 936, A 936/0err, B 17/0err, lists the 22-entry version)
- The remaining boxes were MOVED to the split parts (2026-10-14, iteration 221, driver
  instruction: this task kept what is already built and committed; the parts depend on this
  task, then on each other in order 807 -> 808 -> 809; together they cover these boxes):
  - the list transcription/mapped to leaves + the stage-A/B recall recorded in the Horsley
    section of docs/lead_roman.md -> tasks/807 (the list corrected to 24 entries: the 219
    version's 22 + n0114/n0185, proven genuine site plans at 220)
  - the staged rows (files_roman/classified_roman/extras_roman, rows tagged with this book,
    200 evidence field, 1732) -> tasks/808
  - the fit/evidence.py check passing offline on every staged row + at least 90% of the
    verified site-plan pages staged, or each missing one accounted for in the lead doc ->
    808 + 809
  - the no-network test (the staged files join, the evidence check passes, a golden sample
    of rows) -> tasks/809

## Notes
- The LLM replicas serve on 127.0.0.1:8080-8082 (model qwen3.8-27b); since 215 re-pointed
  pipeline/books.py's LLM_PORTS to 8080,8081,8082,18080,18081, no in-process LLM_URLS patch is
  needed. (Superseded for the remaining work: every leg left for this book is offline - the
  triage stages that needed the replicas are done; the parts 807/808/809 use no LLM.)
- The catalog already holds the major British Roman forts with QIDs (305 roman_fort rows:
  206 England, 54 Wales, 22 Netherlands, 17 France, plus 6 no-QID extras: vindolanda and the
  four Antonine Wall camps, aventicum). (Now carried per site in 808's Notes.)
- The LLM triage of 936 pages was the long pole: run it as a resumable background job (the
  stage jsonl is append-only and skips done pages; see the "long background data jobs"
  PITFALLS entry). (Done: A 936/0err, B 17/0err - no long pole remains.)

## Hand-over
(2026-10-14, iteration 221, agent c - SPLIT per the driver: agent a had nothing to build for
25 minutes and other open tasks (230) waited on this one, so the unbuilt work became three
top-level tasks in the free 800-range: 807 (the list correction to 24 entries + the lead-doc
section; Depends on: this task), 808 (the --stage: 17 staged rows + the new extras sites;
Depends on: 807), 809 (the --check + golden + no-network test; Depends on: 808). Each
carries its own Goal/Acceptance and the operational details that lived in this hand-over (the
two-entry transcription, the validate_book one-liner, the catalog check, the image notes) in
its Notes section. This task keeps what is already built and committed (below) and is DONE:
box 1 ticked, boxes 2-5 moved into the parts. Task 230's Depends on line was updated the same
session (807/808 added; 207c removed per 230's own dropped-subtask note). No tests run this
session - a task-file-only change, no code touched; last suite state below.)

**Built and committed (the parts build on this - all in this branch's git history):**
- data/raw/books/britanniaromanao00hors/ - fetched: 936 triage-size jpgs + the bookreader/hOCR/
  djvu cache (gitignored raw).
- data/books/triage/britanniaromanao00hors.A.jsonl - 936/936 rows, 0 errors (703 text_only /
  151 other_illustration / 80 plate_site_plan / 2 unparsed).
- data/books/triage/britanniaromanao00hors.B.jsonl - 17 rows, 0 errors (2026-10-14, replicas
  8080/8081, 18 s): B re-read all 17 as plans with the printed titles + site_names (the source
  of truth for the staging rows' titles; B's schema has no kind field - verdict = non-empty
  plans[]).
- fit/src_roman_horsley.py - the 219 version: CITE (title page n0014 + the BM-volume note
  from n0015), the 22-entry HORSEY_FIGS (15 s wall maps + N.11 o + 6 country-map o + 2
  Ptolemy-fold-out o), register() (in-process BOOKS + HAND_FIGS injection), --fetch /
  --status / --triage A|F|B / --list. --stage/--check/--golden are documented in the
  docstring but not built yet (808/809 build them).
- data/books/lists/britanniaromanao00hors.json ({"plates": null, "figures": [22 entries]}) +
  .map.json (22 entries; site_plan=true on the 15 wall-map leaves) - the 22-entry version;
  807 regenerates 24/17.
- PIVOT (220, the reason the list grows 22 -> 24): n0114 (P.44, the Ardoch + Innerpeffery
  legionary camps) and n0185 (P.113, the five secondary stations GLANNIBANTA/ALIONE/
  BREMETEN RACUM/OLENACUM/VIROSIDUM) - which 219 dismissed as stage-A false positives
  ("parametric hallucinations") - are GENUINE site-plan plates (verified on the full-size
  images + the book's text pp.43-44/113); a whole-book hOCR sweep (every page <700 chars
  listed, plan-vocabulary scan of every page) found no further kind-s leaves - the 24-entry
  list (17 s / 7 o) is complete. Stage A against the 22-entry list: recall 1.0/1.0,
  precision 0.882, flagged_not_in_list [114, 185] (those two genuine plates). The verbatim
  transcription of the two table entries is in 807's Notes.
- docs/lead_roman.md: only the intro + the Roy section (207c, dropped) exist; the Horsley
  section is 807's (it goes before the Roy section; Maclauchlan's lands between them when
  207b starts its section).
- The staging files (data/commons/files_roman.jsonl, classified_roman.jsonl,
  data/catalog/extras_roman.jsonl) do not exist on this branch yet - 808 (or 207b, whichever
  stages first) creates them; both books append tagged rows to the same files and the
  driver serializes them by file overlap.
- Catalog (220 check; sites.jsonl 12603 rows + extras.jsonl 193, keyed by "name"): none of
  the seven P.113/Ardoch/Innerpeffery sites exists - all new no-QID extras rows (808); the
  Antonine camps bar-hill-fort/inchtuthil/raedykes/rough-castle-fort already exist in
  extras.jsonl (reuse, don't re-create).
- Suite at the split: 1 failed / 156 passed / 1 skipped (389 s; .venv/bin/python -m pytest
  tests/ --ignore=tests/test_gate.py -p no:cacheprovider); the lone red = agent a's 307d
  placement test (known pre-existing: seed check + /tiles/relief 404, PITFALLS).
- If a 807/808/809 session needs context its Notes lack: the DECISIONS entries "207a 215"
  (no-list discovery + front-matter map + corner marks), "207a 218" (country-map reads +
  machinery re-verification) and "207a 221" (this split, incl. the 220 pivot fact 220 never
  journaled), and the git history of this file (the 216/219/220 hand-overs, superseded
  here).
