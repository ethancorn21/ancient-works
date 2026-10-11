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
- [ ] Test (no network): a fixed in-repo sample of rows with known-good and known-bad ties; golden output of
      the check over that sample.

## Notes
- The rows of `pipeline/sources.py` are hand-checked QIDs: their evidence kind is "hand-tied QID" (record the
  source name); verify each against the source's table, don't re-fetch.
- Wikidata/Commons metadata is fetched live in the working phase and stored in the row; `check` reads stored
  fields only (tests never fetch).
- Extend rows, never move or delete them; keep every existing field byte-identical.

## Hand-over

**Where I am (2026-10-10, iteration 10).** `fit/evidence.py` is WRITTEN (uncommitted, harness-saved): the whole
task's core - `check` (offline re-verification, one line per row: PASS/FAIL/NONE, exit 1 iff FAIL) and
`record` (appends an `"evidence"` field to a row's end, existing bytes untouched; offline: 38 hand-tied
sources rows + all book rows via the matcher; `--live`: paced Commons/Wikidata fetch for the remaining
~1343 commons rows - categories, site claims, file items, place resolutions). `tests/evidence_sample/`
is BUILT (uncommitted): `files.jsonl` = 11 rows (2 real rows pulled verbatim from data/commons/files.jsonl:
Old Sarum "An Exact Plan" = category via subcat "Old Sarum in art"; the real Kip Hampton Court row =
hand_tied; rest synthetic) and `index.jsonl` = 4 book rows (Fort Hill matched; Serpent Mound + Banwell
Cross hand-rejected via books_match.HAND; Paint Creek ambiguous). NOT yet done: `tests/test_evidence.py`,
`tests/golden/evidence_check.txt`, running anything, `record` on the real files.

**Expected golden (verify each line matches before committing the golden; the Hampton Court conflict distance
is computed by the code, expect ~194 km):**
```
PASS   category        old-sarum-q782719|File:An Exact Plan and Section of Old Sarum.jpg
PASS   category        old-sarum-q782719|File:Old Sarum cathedral ruins plan 1850.jpg
PASS   depicts         old-sarum-q782719|File:Old Sarum cathedral plan, hand-coloured 1860.jpg
PASS   depicts         old-sarum-q782719|File:Old Sarum plan from the 1755 survey.jpg
PASS   caption_coords  caister-castle-q5017844|File:Plan of Caister Castle, drawn from the tower.jpg
NONE   none            hampton-court-herefordshire-q1443802|File:Gezicht op Hampton Court RP-P-1905-195.jpg  conflict: caption 'Hampton Court' resolves to Q571484, <~194> km from the site
PASS   hand_tied       hampton-court-herefordshire-q1443802|File:Gezicht op Hampton Court, RP-P-1905-194.jpg
NONE   -               old-sarum-q782719|File:Antiquarian sketch of an English castle.jpg  no evidence recorded
FAIL   category        old-sarum-q782719|File:Broken evidence chain.jpg  site category 'Old Sarum West' differs from the row's 'Old Sarum'
FAIL   depicts         old-sarum-q782719|File:Depicts the wrong item.jpg  depicts Q9999999, not the site's Q782719
FAIL   caption_coords  caister-castle-q5017844|File:Caister Castle with a wrong distance.jpg  stored distance 200000.0 m does not reproduce (0 m)
PASS   caption_coords  ancientmonuments00squi_n0068_1
NONE   none            ArcheologicalAtlasOfOhio_n0176_1  hand-rejected: different effigy: Warren County serpent, not Adams County Serpent Mound
NONE   none            earthworkenglan01allcgoog_n0576_1  hand-rejected: the cross earthwork, not the hillfort Banwell Camp
NONE   none            ancientmonuments00squi_n0054_1  ambiguous: half or less of the site's name is in the title
evidence: 15 rows, 6 pass, 3 fail, 6 no-tie
```
(returncode 1; the golden file must be exactly this, generated by running the check, not retyped.)

**Exact next steps:**
1. Write `tests/test_evidence.py`: one test, subprocess
   `[sys.executable, "fit/evidence.py", "check", "--files", "tests/evidence_sample/files.jsonl", "--books",
   "tests/evidence_sample/index.jsonl"]` with cwd=ROOT; assert stderr == "", returncode == 1,
   stdout == tests/golden/evidence_check.txt. (No server fixture needed; .venv python has numpy/scipy/PIL.
   The module imports books_match->books->PIL and sources->aw->numpy at import time - fine under .venv.)
2. Run that check command by hand FIRST; verify every line against the expected golden above (the conflict
   km value will be computed - just confirm it is > 50); then generate the golden from the actual stdout.
3. `.venv/bin/python -m pytest tests/test_evidence.py -x`.
4. Run `.venv/bin/python fit/evidence.py record` (no --live): records the 38 sources rows (hand_tied) and
   all 890 book rows (135 matched -> caption_coords, rest none) into the REAL data/commons/files.jsonl and
   data/books/index.jsonl. Then verify byte-identity of all pre-existing fields (json round-trip probe I used:
   every line must equal json.dumps(json.loads(line), ensure_ascii=False)+"\n" both before and after, and the
   old line must be a byte-prefix... actually just confirm each changed line's parsed dict differs from the
   original only by the added "evidence" key) and run `check` on the real files: expect 0 FAIL, exit 0
   (many NONE - that is the intended report, see DECISIONS).
5. NEXT session: `record --live` for the remaining commons rows. FIRST verify `fetch_file_item` - my HTML
   probe showed the Commons file page embeds a wbmi JSON with P6216/P180 statements but I never confirmed
   where the file item's own QID appears in that HTML (patterns tried: ItemPage/(Q\d+), "wikibaseItem",
   "globalItem" - none matched). If no pattern works, probe the page source for the item id; if it truly is
   not there, drop the P180 route (rows fall through to caption/none) and note it. PACE: this machine shares
   its IP with other agents hitting Wikimedia; bursts get 429 (I hit two). Use commons.get (1 s pace) and
   keep interactive probes to 1-2 requests at 2-3 s apart.

**Design settled (details in DECISIONS.md):** check = "clean" means zero FAIL; no-tie rows are printed as
NONE (reported, never silent - box 3) and do not fail the exit code. Book rows: record runs the matcher once
and stores the decision; check re-verifies the stored record against the row's printed text, the current
catalog row and the HAND table - it deliberately does NOT re-run the matcher over the whole (growing)
catalog, which is not monotone.
