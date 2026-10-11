Status: in-progress
# 204: Van Deventer - the remaining town plans (c. 1550s)
Depends on: 200
Touches: fit/src_van_deventer.py, data/catalog/extras_van_deventer.jsonl, data/commons/files_van_deventer.jsonl, data/commons/classified_van_deventer.jsonl, docs/lead_van_deventer.md, tests/test_src_van_deventer.py

## Goal
GOAL.md point 4: Jacob van Deventer's town plans, drawn c. 1545-1565 for Charles V and Philip
II. The Commons category "Maps by Jacob van Deventer" holds about 70 town categories; six are
already hand-tied in pipeline/sources.py (including the hand-fitted Bergues), leaving ~64 towns
not on the map yet. For each: verify the Wikidata item by hand (a name search alone gives the
wrong place - the Barnard Castle trap), tie the picture with machine-checkable evidence (200),
and stage the catalog entry and the picture rows in this task's own staging files. 211
consolidates the staging into the canonical files and builds the sites.

## Acceptance criteria
- [ ] Verified before use (docs/lead_van_deventer.md): the Commons category exists and its
      town list is recorded; every staged picture is a Van Deventer plan (the drawing's date
      c. 1545-1565 is recorded on the row - where Commons only has an upload date, the known
      drawing date is used and noted); unusable files (photos, modern reprints, too small) are
      listed with the reason, not staged.
- [ ] The hand-checked file -> QID table lives in fit/src_van_deventer.py (the sources.py
      pattern): every QID verified against its label and coordinates, with the town-centre
      lon/lat recorded on the row, not just the municipality point (Gouda misses by up to
      800 m). Towns whose QID cannot be verified are listed in docs/lead_van_deventer.md with
      the reason.
- [ ] Staged rows: extras_van_deventer.jsonl (one entry per new town: id, name, place,
      lon/lat of the old town, region, kind "town", QID, wikipedia) and
      files_van_deventer.jsonl (one row per staged picture, in the files.jsonl shape, with the
      200 evidence field - P373 category / P180 / caption+coords - and a classified row "plan"
      by hand). fit/evidence.py check passes offline on every staged row.
- [ ] No duplicate sites: a town whose QID is already in the catalog gets its picture row for
      that existing site id, no new catalog entry.
- [ ] At least 50 of the ~64 towns are staged, or docs/lead_van_deventer.md accounts for each
      missing one with a verified reason (a documented drop beats a guessed row).
- [ ] Test (no network): the staged files join (every file row names a staged or existing
      site; every new catalog entry has at least one picture) and the evidence check passes;
      a golden sample of rows.

## Notes
- The six already hand-tied towns are NOT re-staged here (their rows exist in the canonical
  files via sources.py); this task is the remaining ~64.
- If the work grows past a few sessions: split into subtasks 204a-... by country
  (Netherlands / Belgium / France / Germany + other), ~16 towns each, same shape of boxes per
  subtask (each with its own extras_/files_/classified_ staging files suffixed by the
  subtask, e.g. files_van_deventer_a.jsonl, and its own docs/lead_van_deventer_a.md); record
  the town list per subtask in this parent's hand-over. 211 consolidates whatever staging
  files exist.

## Hand-over
(2026-10-11, iteration 45 - BE QID batch verified + recorded in TOWNS + lead-doc BE sections written; the
module and doc edits are in the working tree UNCOMMITTED - commit them with your first edit. The task file
itself was renamed this iteration: it is tasks/204-van_deventer.md (underscore; a 0-byte duplicate
204-van-deventer.md existed and was merged into this one, then deleted - git shows it as a rename/deletion,
no content lost). Next: the BE --files inventory.)

**Done this session (verified by running):**
1. Task-file fix the driver demanded: consolidated the empty tasks/204-van_deventer.md with the real content
   from tasks/204-van-deventer.md (hyphen); first line now `Status: in-progress`.
2. BE discovery: `.venv/bin/python fit/src_van_deventer.py --verify <the 20 BE towns>` (transcript
   /tmp/vd_verify_be_iter45.txt, 110 lines; /tmp may be wiped). All 19 without a recorded QID resolved from
   the printed candidates; **Mons was NOT in its 5-candidate search** (planetary 'mons' + 4 French communes
   outrank it; the city is 11th in the en results, 4th in fr) - found by a follow-up search at limit 20:
   **Q83407**, label 'Mons', P625 (3.9525, 50.454722), P373 'Mons (Hainaut)', P131 'County of Hainaut',
   enwiki 'Mons, Belgium' (snippet scripts /tmp/vd_mons_iter45.py, /tmp/vd_mons2_iter45.py).
3. TOWNS (fit/src_van_deventer.py): all 20 BE rows now carry qid/label/lon/lat/p625/place/wikipedia/p373
   (site point = P625 rounded to 4 dp - the hand check found no old-town-centre offset). Four P373s are
   disambiguated: Brussels 'Brussels (municipality)', Halle 'Halle (Belgium)', Mons 'Mons (Hainaut)', Leuze
   'Leuze-en-Hainaut' (Leuze's item label IS 'Leuze-en-Hainaut'). Ghent = Q1296 (the prep's verified one,
   re-confirmed).
4. Re-verification of the 20 (transcript /tmp/vd_verify_be_recheck_iter45.txt): **all labels match (no LABEL
   CHECK), all P373 'ok', all P625 within 0.01 km of the table point, enwiki all match**. One nuance:
   Saint-Ghislain Q668950 has NO en label on Wikidata (the re-check prints an empty label - the search API's
   label and the enwiki article confirm the item; not a mismatch, documented in the lead doc).
   Traps measured: Bruges first hit Q327025 759 km (Bruges, Gironde); Leuze first hit Q326134 92 km
   (Leuze, Aisne); Mons first hit Q1108786 780 km (Mons, Var); Mechelen's 3rd candidate is the Dutch
   Mechelen Q100020 (no first-hit trap). The other 16: first hit = the recorded item.
5. Box 4 for the BE batch: offline known_sites() check (12575 sites) - **none of the 20 BE QIDs in the
   catalog**: all 20 get new catalog entries (no existing-site reuse, no done-QID clash).
6. docs/lead_van_deventer.md: new '## QID verification - Belgium' section (method, the 20-row table with
   measured distances, the Mons follow-up, the disambiguated-P373 note, the Saint-Ghislain label gap) +
   '### Name-search traps - Belgium' (Mons/Leuze/Bruges/Mechelen); the old combined pending section became
   '## France, Luxembourg (pending)' (24 towns: FR 23 + LU 1; Beaumont's country, Luxembourg City region,
   and the prep-candidate discard notes carried over - Brussels now resolved in BE).

**Tests:** last run 33/33 green (iteration 44; the TOWNS edit compiles and both --verify runs above imported
it fine, but `pytest -q` and `--check` have NOT been re-run since the TOWNS edit - do that first).

**Next step - the BE file batch** (previous hand-over step 2, unchanged):
1. `cd` + sanity first: `.venv/bin/python -m pytest -q` (expect 33/33) and `.venv/bin/python
   fit/src_van_deventer.py --check` (expect exit 0: staging jsonl still absent -> joins empty, 0 evidence
   rows) - the TOWNS edit is data-only, both must pass. Then commit the iteration-45 work:
   `git add -A && git commit -m "204: BE QID table verified + recorded; lead-doc BE sections"` (task file,
   module, doc, DECISIONS, PITFALLS all in the tree).
2. `.venv/bin/python fit/src_van_deventer.py --files <the 20 BE towns>` (~2-4 min, 429-paced; transcript to
   /tmp/vd_files_be_iterNN.txt): picks expected = the BNE atlas 1545 plates for 16 of the 20 (Ath,
   Braine-le-Comte, Chimay, Chièvres, Enghien, Ghent, Halle, Kortrijk, Lessines, Leuze, Mons, Ostend,
   Oudenaarde, Saint-Ghislain, Soignies, Tournai); **Bruges, Brussels, Mechelen and Aarschot are NOT in the
   BNE** - their picks must come from their own town categories (the "Maps of ..." cats hold 7/7/7/2 files
   per the old prep). Record picks in TOWNS (file=, +date= where the page date is not the drawing's), write
   the lead-doc 'Per town' BE bullets (staged vs not-staged per file, sizes + dates from the transcript),
   update the pending 'Per town' section to '### Belgium', commit.
3. Then FR (23 towns; BNE plates cover all of them; watch the double plates: 'Aire-sur-la-Lys - Deventer.jpg'
   = Aire+Thérouanne, 'Hesdin - Deventer.jpg' = Hesdin+Vieil-Hesdin - stage once under the true primary town,
   note the second; Beaumont's region flips france->belgium if the Hainaut item wins) + Luxembourg City
   (search 'Luxembourg (city)', Q1564 expected, region 'luxembourg' - new region value, noted in the lead
   doc). Then the one long run: `--chain <town>` per staged town (depth cap 6; paste the printed JSON into
   TOWNS['chain']; towns whose picked file sits in a collection cat need filecat = that cat), `stage` (NOT
   dry), `--check`, write tests/test_src_van_deventer.py (pattern tests/test_src_artists.py: socket-blocking
   fixture, check_staged, subprocess `fit/evidence.py check --files ... --books <absent>`, golden sample via
   --golden, negative control; box-6 date rule: year_of of the row date in 1545-1565), `--golden`.

**Transcripts** (/tmp may be wiped - re-run): /tmp/vd_verify_be_iter45.txt (discovery, 20 towns),
/tmp/vd_verify_be_recheck_iter45.txt (re-verification), /tmp/vd_mons*_iter45.py (the Mons follow-up
snippets, reusable). The NL-era ones (vd_files_nl_iter43, vd_verify_iter41, vd_stage_dry_iter44,
vd_list_iter44) are gone if /tmp was cleaned.

**Pitfalls:** NOT yet filed (cut off by the context limit - file it with the next commit): a PITFALLS entry
under 'Wikimedia APIs (Commons, Wikidata)': wbsearchentities' limit=5 truncation hides well-known short
names - Mons (Belgium) Q83407 ranks 11th in the en search (the planetary term 'mons' and ten French
communes outrank it; it is 4th in the fr search) - when the town's item is not among the five, follow up
with a higher limit (20 worked). The keep()/swap-order entry (pipeline/commons.py)
and the trailing-comment-joins-lines entry still apply (the TOWNS comments this session are all inside-
parenthesis, per that rule). Team mode: agent c on 203a (fit/batch_us.py, data/db/platefits, data/review,
docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256, tasks/802-*, tasks/803-*) -
untouched; agent c also on 802 (tools/gate_heldout.py, tests/test_gate.py) - untouched; my Touches:
fit/src_van_deventer.py, the 3 staging jsonl, docs/lead_van_deventer.md, tests/test_src_van_deventer.py,
plus the task file rename.
