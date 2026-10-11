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
(2026-10-11, iteration 43 - NL file inventory DONE: town_files() now covers the 4 collections + town-subcats at
depth 1; 13 of 16 NL picks recorded in TOWNS (file + date); next: lead-doc NL + collection sections, then BE QIDs.)

**UNCOMMITTED in the working tree (the harness saved these; commit them with your lead-doc edits):**
`fit/src_van_deventer.py` (my only touched file this session): (1) `town_files()` extended - after the towns it
prints the 4 COLLECTIONS (same line format; a collection file that also sits in an inventoried town cat gets the
`[also in: ...]` tag; the atlas at depth 1) and it inventories each town cat's own subcategories at depth 1
(tagged `[sub: ...]`, prefix stripped when the subcat extends the town cat name); (2) the 13 staged NL TOWNS rows
carry `file=` (+ `date=` where the page date is not the drawing's: Rotterdam "circa 1560"; Sluis and Valkenburg
"circa 1545-1565"); (3) the 3 NL drops carry `note=` (Groningen (province) note enriched with its file facts;
Leeuwarden and Middelburg new notes). Module docstring usage line updated. Everything else as of iteration 42.

**Verified this session (run, not reasoned):** `--list` passed AGAIN (70 = 66 + 4; fourth re-run on 2026-10-11).
`--files <16 NL towns>` ran clean under .venv: transcript `/tmp/vd_files_nl_iter43.txt` (217 lines; if gone,
re-run the command, ~2 min at 429 pacing). Live probes: the BNE atlas category holds only 1 root file
(`Deventer-Dionantum.jpg` 6144x6144, 1550-1565) + 1 subcat (`Map of Landrecies by Jacob van Deventer (Atlas des
villes des Pays-Bas ...)` with 5 KBR detail scans) - and that same subcat ALSO hangs under the plain Landrecies
town cat (why the depth-1 town-subcat inventory was added). The 16 NL town cats have no other subcats. `stage
--dry` and `--check` were NOT yet run this session (see next step 1).

**evidence.py semantics re-read (801 merged in main; check is OFFLINE from stored fields only):**
`check_caption`: `norm(named_place)` substring of `norm(title+desc)`, then stored `place_lon/lat` vs
`site_lon/lat` distance must reproduce stored `dist_m` within 1000 m and be <= 50 km - NO live re-resolution
(`resolve_places` is record-side only), so `evidence_for` (stored resolution = the verified site point,
dist_m 0.0) passes for any file that names the town. `check_category`: `row["cat"] == site_cat`, `via[-1] ==
cat`, `file_cat not in via`. 801 added kinds `part_mention`/`sheet_mention` (and book checks) - my rows use
only `category`/`caption_coords`. `check(files, books, catalog=EXTRAS)` is how `--check` runs it (NO_BOOKS =
absent path, skipped).

**The NL picks (13 staged) and drops (3) - detail goes into the lead doc (next step 2):**
Staged: Aardenburg `Aardenburg 1560.jpg` (500x500 - STAGED despite the <~1000px heuristic: it is the only
Aardenburg plan on Commons, a full plan, circa 1560; caveat goes in the lead doc), Alkmaar `Kaart van Alkmaar
en Oudorp door Jacob van Deventer 01.jpg` (5019x4971, 1550-1570; the BNE plate/1900-RAA/1920/RCE copies not
staged), Amsterdam `Kaart van Amsterdam c1550 (City Map) Jacob van Deventer.jpg` (4283x5229, 1550-1570),
Enkhuizen `... Enkhuizen 1558-1560.jpg` (2514x2387; the detail twin not), Goes `Goes 1572 Bijkrt v Deventer.jpg`
(1412x1784, page date 1560 - the ONLY Goes row inside the c. 1545-1565 window; the netkaart 4276x3341 is dated
1572/1575 = a later revision, and also in the BNE cat; 1988 RCE not), Groningen `... Groningen volledig.jpg`
(6568x5088, 1563-1567, netkaart+carton; the 1282 ca-1565 scan and the carton crop not), Haarlem `Kaart van de
stad Haarlem ... NL-HlmNHA 1100 KNA006000046.JPG` (2359x2272, 1565, Haarlem municipal collection; the two
identical 3306x8152 no-desc uploads, the "Kopie" and the "volgens de oude teekening" repro and the undated
1213x1332 and the gracht crop not), Reimerswaal `Reimerswaal 1560 Minuut v Deventer.jpg` (3501x2541, 1560,
original; bijkaart/netkaart/circa-1560/1545-BNE-plate copies not), Rotterdam `Map of Rotterdam around 1560s by
Jacob van Deventer.jpg` (2953x2033; page date is an upload timestamp, desc dates the drawing 1558-1563 -> TOWNS
date "circa 1560", date_commons keeps the page value; the uitsnede/photo/1918-book-crop/1911-scan not), Sluis
`... Zeist en Sint Anna ter Muiden - Sluis - 20201361 - RCE.jpg` (2900x2137, 1980 RCE album reproduction = the
only full-plan candidate, the Zwolle done-row precedent; TOWNS date "circa 1545-1565" the known window,
date_commons 1980), The Hague `1558, Den Haag. Jacob van Deventer.jpg` (4413x4705, 1558; same file = the
autograph in the NA cat), Utrecht `Utrecht.jpg` (2164x2155, 1565-1570; the 1955/1955-glasplaat/1982 RCE
repros and the Buiten-Wittevrouwen 1000x557 not), Valkenburg `... te Zeist - Valkenburg - 20237999 - RCE.jpg`
(2878x2102, 1980 RCE album reproduction, only full-plan candidate, also in the RCE cat; TOWNS date "circa
1545-1565"; the nine detail/small files not). DROPS: Groningen (province) (province map; its 2 files are crops
of the Friesland gewestkaart), Leeuwarden (only file 593x636 is a 1975 redrawn model after Deventer, not the
plan), Middelburg (only file 2412x3233 is a 1942 RCE detail crop of the stadhuis). **R5 found:** the Sluis cat
holds `227 Damme.jpg` (2684x2606, 1545, Damme's netkaart, also in the BNE cat) - a Damme plan misfiled in the
Sluis cat; Damme is a done town (its canonical row uses its own file) -> note only, never stage.

**Next steps (exact):**
1. Sanity: `.venv/bin/python fit/src_van_deventer.py stage --dry` (live c.info for the 13 titles, ~1-2 calls:
   exercises keep() + evidence_for on every pick; must print "staged: 13 new sites, 13 new pictures" + no
   raise), then `--check` (staging files still absent: joins empty, evidence over 0 rows, exit 0), then the
   `.venv/bin/python -m pytest -q` suite (was 33/33 green at iteration 42; my change is TOWNS data + town_files
   only - expect still green). Then COMMIT everything (module + the lead doc below): "204: NL file picks in
   TOWNS + town_files collection/depth-1 inventory - ...".
2. Lead doc (still at iteration 42 state - the (pending) sections need the NL material from this session):
   (a) category section: "(two more live runs on 2026-10-11)" -> four re-runs (latest after the town_files
   extension); (b) replace "Per town: staged picture or documented drop (pending)" with the NL section per the
   picks/drops/R5 above (one bullet per town: staged file (title, size, date on the row) or drop reason; the
   not-staged candidates named briefly); (c) replace "The collection categories (pending)" with the four found:
   BNE 61 = the "Planos de ciudades de los Países Bajos" atlas plates (Part II/III; most page-date 1545 = the
   Charles V campaign; covers the 23 FR + 17 of the 20 BE towns incl. Halle as "Hal"; double-plates: Aire-sur-la-
   Lys+Thérouanne, Hesdin+Vieil-Hesdin (French desc, odd date field) - matters for the FR batch; plus Amsterdam
   vol3-map35 1560-61, Alkmaar, Reimerswaal Manuscrito 13, Ghent BN 1/2, Goes 1572, Oostende c.1562, IJlst
   c.1575, Nieuwpoort+Dunkerque and Hontscoten+Veurne "16th C" two-town sheets, Woudrichem/Gorinchem, Appingedam
   - the non-60 places stay out of scope), NA 2 = The Hague autograph (the staged file) + Schoonhoven/Nieuwpoort
   two-town sheet (out of scope), RCE 69 = the Zeist album reproductions 1955-1981 (supplied the Sluis and
   Valkenburg staged rows; Middelburg detail-only; the rest are non-60 NL towns or the done Venlo/Zwolle),
   Atlas = Deventer-Dionantum root (out of scope) + the one Landrecies subcat with its 5 KBR detail scans (1091-
   1805 px, 1550-1565; the subcat double-parents under the atlas AND the plain Landrecies town cat - for the FR
   batch). (d) Summary section: add the NL subtotal (13/16 staged, 3 documented drops) but keep it (pending) until
   all 60 are in.
3. Then the BE batch per the previous hand-over step 3: `.venv/bin/python fit/src_van_deventer.py --verify <20 BE
towns>` (discovery mode: search candidates; record qid/label/lon/lat/p625/place/wikipedia/p373 per town; Ghent
Q1296 is already verified in prep - record it; Beaumont's region flips to belgium if the Hainaut item wins; the
BNE 1545 plates are the expected BE file picks - check them in the BE --files run). Then FR (23; watch the
Aire+Thérouanne and Hesdin+Vieil-Hesdin double-plates - one file, two towns: stage once, note the second), then
Luxembourg City (search "Luxembourg (city)", Q1564 expected, region luxembourg - no REGION_NAME key, fallback
noted). Each batch: --verify, then --files (the picks), then lead-doc batch section, commit.
4. Then the one long run (hand-over step 4 from iteration 42, unchanged): `--chain <town>` per staged town (depth
cap 6; paste the printed JSON via list into TOWNS["chain"]; for towns whose picked file sits in a collection
cat, record `filecat` = that cat - cat_chain starts from filecat), then `stage` (not dry), `--check`, write
`tests/test_src_van_deventer.py` (pattern tests/test_src_artists.py: socket-blocking fixture, check_staged,
subprocess `fit/evidence.py check --files ... --books <absent>`, golden sample via --golden, negative control;
box-6 date rule: year_of of the row date must land in 1545-1565 - note "circa 1545-1565" parses to 1545,
"circa 1560" to 1560) and `--golden`. If a batch overruns the budget, split per the task Notes (204a NL/204b
BE/204c FR/204d LU) with per-subtask staging files; note the NL picks are then ALREADY in the parent's TOWNS.

**Tests:** suite last ran 33/33 green (iteration 42, before this session's module change). No test of mine yet
(tests/test_src_van_deventer.py not created; the 3 staging jsonl files don't exist yet - created by stage()).

**Pitfalls:** no new entries filed this session; the existing ones (trailing-comment-joins-lines, dict.update
2-tuples, Wikimedia 429 + Retry-After via commons.get, check_category shape-only) all still apply - the TOWNS
edits this session used comment lines INSIDE dict(...) calls (legal, but the trailing-comment trap from iter 41
is why each comment starts on its own line). Team mode: agent c on 203a (fit/batch_us.py, data/db/platefits,
data/review, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256, tasks/802-*,
tasks/803-*) - untouched; my Touches: fit/src_van_deventer.py, the 3 staging jsonl, docs/lead_van_deventer.md,
tests/test_src_van_deventer.py.
