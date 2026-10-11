Status: in-progress
# 200: Evidence — every picture tied to its place, machine-checkable
Depends on: none
Touches: fit/evidence.py, data/commons/files.jsonl, data/commons/classified.jsonl, data/books/index.jsonl, pipeline/books_match.py, tests/test_evidence.py, tests/evidence_sample/, tests/golden/evidence_check.txt

## Goal
GOAL.md point 3: every picture row records evidence a program can check that ties the picture to the site
it depicts: the file is in the Commons category of the site's Wikidata item (P373), or its structured data
says it depicts (P180) that item, or its title or caption names the place and the coordinates agree. Why:
the Rijksmuseum's "Gezicht op Hampton Court" is Hampton Court in Herefordshire (its caption says so), not
the palace; a name search alone gives the town for Barnard Castle and the village for Richard's Castle.

## Acceptance criteria
- [ ] `fit/evidence.py` records, in the `"evidence"` field of each picture row (data/commons/files.jsonl and
      the book index rows in data/books/index.jsonl that reach the plan list), which kind of tie holds —
      category (P373) / depicts (P180) / caption+coords / hand-tied QID — plus the specifics that proved it
      (the category page, the property value, the place named, the distance to the site) and a checked date.
- [x] `evidence.py check` re-verifies every row offline from the stored fields only and lists failures; it
      runs clean on the committed rows.
- [ ] It fails closed: a row whose caption names a place that resolves to a different location (the Hampton
      Court trap) does not get a passing field; a row with no tie at all is reported, not silently kept.
- [x] Test (no network): a fixed in-repo sample of rows with known-good and known-bad ties; golden output of
      the check over that sample.

## Notes
- The rows of `pipeline/sources.py` are hand-checked QIDs: their evidence kind is "hand-tied QID" (record the
  source name); verify each against the source's table, don't re-fetch.
- Wikidata/Commons metadata is fetched live in the working phase and stored in the row; `check` reads stored
  fields only (tests never fetch).
- Extend rows, never move or delete them; keep every existing field byte-identical.

## Hand-over

**Where I am (2026-10-10, iteration 12).** Offline record done and committed; check is clean; boxes 2 and 4
are ticked. Box 1 and box 3 remain: they need `record --live` for the 1343 commons rows that still have no
evidence field. Committed this session: `06847a2` (evidence recorded on the 38 hand-tied + 890 book rows;
1452/1490 files.jsonl lines byte-identical, every changed line parses with "evidence" last, verified by script),
`187fd66` (books_match refactor: extracted `row_inputs`, `score_candidate`, `site_toks`, `name_lookup_keys` -
behavior-neutral, `matches.jsonl` hash 30f099b1… + stdout summary byte-identical before/after, file left
untouched in the tree), `5f5a707` (set_field fix + check rewrite + record test).

Two real bugs were found and fixed this session (details in DECISIONS, both have PITFALLS entries -
PITFALLS edits are UNCOMMITTED, the harness saved them):
1. `set_field` dropped the line terminator -> `record` would have glued jsonl rows into one line on its first
   real run. Caught before damage. Now: terminator preserved; guarded by
   `tests/test_evidence.py::test_record_appends_evidence_without_touching_existing_bytes` (record CLI on a tmp
   fixture: line count/terminators, untouched rows byte-identical, recorded rows keep every original byte as a
   prefix, evidence is the only and last new key). Re-running `record` is idempotent (0 recorded: rows skip on
   rec == "evidence/1").
2. `check_book_caption` re-stated the matcher's rules more strictly than the matcher itself (full-name
   substring test vs the matcher's distinctive-token / exact-phrase ties; place recompute without the
   BOOK_SCOPE default state) -> 52 of 135 legitimate book matches FAILed. Now it calls the matcher's own
   extracted functions and requires the one-pair evaluation to reproduce the stored record (place dict
equality, score round(…,2) equality, empty why, thresholds, HAND). Only the runner-up margin stays stored
   (catalog is not monotone; a full re-run would fail on data growth).

**Test state at last run:** `.venv/bin/python -m pytest tests/ -q` = 12/12 PASS (11 old + the new record test).
`fit/evidence.py check` on the real files: exit 0, `evidence: 2271 rows, 173 pass, 0 fail, 2098 no-tie` (173 =
38 hand_tied + 135 book caption_coords; 2098 = 755 book none + 1343 commons "no evidence recorded"). The
sample golden (`tests/golden/evidence_check.txt`) is unchanged and passes - the sample verdicts are identical
under the new check.

**Current hypothesis:** the remaining 1343 commons rows will record fine through the category / site-claim /
caption routes; the only unverified live route is `fetch_file_item` (P180 from the file page). If it cannot
find the item QID, those rows simply fall through to caption/none - the design is fail-closed, so the risk is
coverage, not correctness.

**Exact next steps (this is the last session needed, ~1):**
1. FIRST probe `fetch_file_item` (unverified, see 5f5a707-era note): the wbmi JSON with P180/P6216 statements
   is present in a Commons file page's HTML, but no item-QID pattern (`ItemPage/(Q\d+)`, `"wikibaseItem"`,
   `"globalItem"`) matched yet. Do 1-2 requests only (shared IP with other agents' checkouts; bursts 429 -
   commons.get is paced at 1 s/request). If the item id truly is not in the HTML, drop the P180 route from
   `record_live_row` (rows fall through to caption/none) and note it in DECISIONS.
2. `.venv/bin/python fit/evidence.py record --live` (resumable - rerun after interruptions; it skips the 1381
   rows already recorded). Expect 30-60 min: per row ~ categories (50/batch) + site claims (50/batch) +
   subcats (per site cat, cached across rows) + 1 HTML GET + place resolutions (wbsearchentities + P625).
   Verify after: line count unchanged, every line parses, all 1381 titled rows now carry evidence (box 1).
3. `fit/evidence.py check` on the real files must exit 0. Any FAIL is now a real finding (stored fields don't
   support the tie) - inspect it against the stored evidence before deciding; never loosen check to get clean
   (AGENTS.md stuck rule). Box 3 confirmation on real data: the Hampton Court trap row (Kip plate -195, if
   present) and any other caption-conflict rows must be NONE-with-conflict, never PASS; no-tie rows are
   printed (the fail-closed case is already pinned by the sample golden).
4. `.venv/bin/python -m pytest tests/ -q` must stay 12/12 (test_data joins the same jsonl files - a changed row
   shape would surface there).
5. Tick box 1 (every picture row has evidence with the specifics + checked date) and box 3, set
   `Status: done`, commit. Commit the uncommitted PITFALLS.md additions in that final commit.

**Notes:** the driver's "`.venv could not be built`" note describes MAIN (tasks/800, another agent's task -
do not touch requirements.* from here); this branch's requirements.txt is pinned+hashed and .venv works
(12/12 ran in it). Task 001 stays blocked on the human's box-2 ruling - not mine to touch. The matcher's full
output is non-monotone in catalog growth: never add a persistent golden over `matches.jsonl` (tasks 204-211
grow the inputs); use one-off before/after byte comparisons for matcher refactors (PITFALLS entry).
