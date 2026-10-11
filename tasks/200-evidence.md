Status: in-progress
# 200: Evidence — every picture tied to its place, machine-checkable
Depends on: none
Touches: fit/evidence.py, data/commons/files.jsonl, data/commons/classified.jsonl, data/books/index.jsonl, tests/test_evidence.py, tests/evidence_sample/, tests/golden/evidence_check.txt

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
- [ ] `evidence.py check` re-verifies every row offline from the stored fields only and lists failures; it
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

**Where I am (2026-10-10, iteration 11).** Test + golden are committed and green (box 4 ticked):
`tests/test_evidence.py` (subprocess `fit/evidence.py check` over `tests/evidence_sample/`, byte-compares stdout
against `tests/golden/evidence_check.txt`, asserts stderr empty + exit 1) passes; full suite 11/11.
The golden pins 15 rows: 7 PASS (Old Sarum x4: category-via-subcat, category direct, depicts P180, depicts
P3311/wd_plan; Caister caption+coords 0 m; Kip Hampton hand_tied), 5 NONE (the Hampton Court trap - caption
'Hampton Court' resolves to Q571484, 187 km > 50 km tolerance, stored none+conflict, fail-closed; one row with
no evidence at all; two hand-rejected book rows; one ambiguous Paint Creek row), 3 FAIL (broken category chain,
depicts the wrong item, stored distance does not reproduce).

One fix this session: `check_book_caption` passed the raw site name to `books_match.name_keys`, which strips
suffixes only from already-normalized (lowercase) names - the Fort Hill row FAILed "does not name" and is now
re-verified end to end. Check normalizes first (the matcher's own convention); PITFALLS entry added.

**Exact next steps (offline record on the real files):**
1. `.venv/bin/python fit/evidence.py record` (no --live): appends `"evidence"` to the 38 sources rows
   (hand_tied, verified against the repo tables) and to all book rows (matcher once: matched ->
   caption_coords, else none). It is resumable (skips rows with evidence.rec == "evidence/1").
2. Verify the write: snapshot the original files first (cp to /tmp). After: every unchanged line byte-identical;
   every changed line parses to a dict differing from the original only by the added "evidence" key (files are
   pure ASCII, so the json round-trip in set_field is byte-safe - verified iteration 10).
3. `.venv/bin/python fit/evidence.py check` on the real files: expect exit 0 (0 FAIL; the remaining ~1343
   commons rows print NONE "no evidence recorded" - the intended report until --live), then
   `.venv/bin/python -m pytest tests/ -q` must stay 11/11 (test_data joins the same jsonl files - the new key
   must not break anything).
4. Tick box 1 (fields recorded with specifics + checked date) and box 2 (check runs clean on the committed rows)
   once steps 2-3 pass.
5. NEXT session: `record --live` for the remaining ~1343 commons rows. FIRST verify `fetch_file_item`: the
   wbmi JSON with P180/P6216 statements is in the file page HTML, but no item-QID pattern matched yet
   (ItemPage/(Q\d+), "wikibaseItem", "globalItem"). Probe the page source once (1-2 requests, 2-3 s apart - this
   machine shares its IP with other agents and bursts 429); if the item id truly is not in the HTML, drop the
   P180 route (rows fall through to caption/none) and note it. Pacing: commons.get at 1 s pace.
6. After the live record: run `check` on the real files again (failures, if any, need fixing before done), then
   tick box 3 (the Hampton Court trap row must be NONE-with-conflict, never a pass; no-tie rows reported).
   Then Status: done.

**Driver notes from PROGRESS (absorbed 2026-10-10):** the .venv build failure in main is tasks/800 (open,
another agent); this branch's requirements.txt is the pinned+hashed one and .venv builds (verified this
session: 11/11 ran in it). Task 001 stays blocked on the human's box-2 ruling - not mine to touch.
