Status: done
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
- [x] `fit/evidence.py` records, in the `"evidence"` field of each picture row (data/commons/files.jsonl and
      the book index rows in data/books/index.jsonl that reach the plan list), which kind of tie holds —
      category (P373) / depicts (P180) / caption+coords / hand-tied QID — plus the specifics that proved it
      (the category page, the property value, the place named, the distance to the site) and a checked date.
- [x] `evidence.py check` re-verifies every row offline from the stored fields only and lists failures; it
      runs clean on the committed rows.
- [x] It fails closed: a row whose caption names a place that resolves to a different location (the Hampton
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

**Status: DONE (2026-10-10, iteration 13).** All four acceptance boxes ticked; `Status: done`.

**State of the data.** Every picture row carries an `"evidence"` field (rec `evidence/1`, kind, specifics, a
`checked` date): commons 1381/1381 (825 category, 164 caption_coords, 38 hand_tied, 354 none - 74 of those are
stored conflicts, the rest genuinely have no place named in the caption); books 890/890 (135 caption_coords +
none-with-reason, from the earlier session). `fit/evidence.py check` on the real files: exit 0, 2271 rows,
1162 pass / 0 fail / 1109 no-tie (the NONE lines are printed, e.g. `conflict: caption 'Bethlehem' resolves to
Q5776, 2396 km from the site`). `check` makes no network calls. Tests: 12/12, incl. the sample golden (unchanged
this session) and the record byte-preservation test.

**What this session did (commits below).** (1) The P180 live route was broken and was replaced: the old code
scraped the file page's HTML for a global item QID (never present - old files have only a *local* MediaInfo
entity, `wbEntityId: M<page id>`) and its P180|P6216 regex attributed P6216 *license* values (Q19652 "public
domain") as depictions (PITFALLS entries). New: `fetch_page_ids` (query prop=info, 50/batch) +
`fetch_file_entities` (Commons `wbgetentities ids=M<pid> props=statements`, 50/batch; chases a page's normalized
global item via the WD service; P180 only). `check_depicts` now accepts P180 (file item, Q or M) and P3311/P18
(site item); P6216 is out. (2) `record --live` is now batched (categories/claims/page-ids/entities 50/call,
place resolutions batched claims fetch, subcats cached per site category) with a chunked flush every 25 rows so
an interrupted run keeps progress; the full 1338-row run finished in one session with no 429s, and rerunning is
idempotent (rows skip on rec == "evidence/1").

**Verified before the done claim.** 1490 lines in files.jsonl (unchanged count); 1343 lines changed vs HEAD, each
keeps its HEAD version byte-for-byte with `"evidence"` the only and last key added, all terminators intact;
147 lines (38 already recorded + 109 sentinels) untouched; books index.jsonl byte-identical to HEAD; every
evidence dict has rec + checked; every conflict row is kind=none (asserted).

**Facts worth knowing if this is ever reopened.**
- The `depicts` kind has **0 hits in this corpus** - that is a measured fact, not a pipeline bug: no site item
  lists any of these files in P3311/P18 (files that do are in the category too and take the category kind first),
  and none of the files' items depicts the site's item. The route stays implemented and is pinned by the sample
  golden (one PASS, one FAIL P180 row).
- The 280 no-tie rows without a conflict (most are OS-sheet maps whose captions name the sheet town, not the
  site) are the coverage gap the acceptance wording allows ("reported, not silently kept"). A follow-up for
  improving their coverage (token-level name matching, a sheet-index route) is **tasks/801** (Depends on: 200,
  Touches: fit/evidence.py).
- The live run is resumable: rerun `fit/evidence.py record --live`; it skips recorded rows. Batch prefetch means
  a partial run's later chunks re-fetch only the unrecorded tail's facts.

**Re-read** (only if this task reopens): `fit/evidence.py:fetch_file_entities` - the `statements` vs `claims`
key difference between the local wiki and the WD service, and the `normalized.item` chase.

Commits: this session's work on top of `73508fe` (driver) - see `git log -- tasks/200-evidence.md`.

