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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/204-van-deventer.md` (in-progress) - hand-over: (2026-10-11, iteration 42 - lead doc written: category census + NL QID section + NL traps; next: close the
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and

## Next open tasks
- `tasks/215-books-llm-ports.md`
- `tasks/216-view-books-entries.md`
- `tasks/217-view-books-lists.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 204 DECISION: built fit/src_van_deventer.py in full (module-first) and verified the NL batch of QIDs
    Chose module-first (skeleton with all functions + the 66-town table, then per-country QID batches) over
    running the whole live inventory in one session: the session budget cannot hold ~300 paced API calls, and
    the module is the vehicle for every later step (verify/files/chain/stage/check). The 70-subcategory list
    (prep's 2026-10-10 constant) re-verified live today. The 16 NL towns hand-verified (search candidates
    checked against label + P625 + P373 + enwiki; every city item's P373 is its own town category): Aardenburg
    Q955, Alkmaar Q972, Amsterdam Q727, Enkhuizen Q9918, Goes Q81220, Groningen Q749, Groningen (province)
    Q752 (drop: province map, not a town), Haarlem Q9920, Leeuwarden Q25390, Middelburg Q52101, Reimerswaal
    Q2590944 (city, not the municipality Q10078 - they share P373 'Reimerswaal'), Rotterdam Q34370, Sluis
    Q10080 (NL city, not Q2289934 Sluis-in-Mol), The Hague Q36600, Utrecht Q803, Valkenburg Q100076 (the old
    town item, P373 'Valkenburg, Limburg'; Q9771 is the modern town; no enwiki on Q100076 -> no wikipedia
    field, sources.py's own rule). Site points: old-town centres hand-recorded in TOWNS (lon/lat), the
    p625 municipality point recorded beside each; per-town distances go to the lead doc (computed, not
    eyeballed). Next: re-verify the recorded table, lead doc (category + NL sections), the --files NL
    inventory, then the BE batch (incl. recording Ghent Q1296 and settling Beaumont's BE-vs-FR region - the
    TOWNS 'france' guess for Beaumont flips if the verified item is Hainaut).

### 2026-10-11 204 DECISION: region values lowercase in the staged catalog rows (deventer-lead convention)
    The six done deventer rows use lowercase netherlands/belgium/france and build_catalog.place_of/make_site
    look REGION_NAME up by str(region).lower(), so lowercase is the convention this lead continues (213's
    display-case "Italy" was the exception made while waiting for 214). Luxembourg City is the one new value
    "luxembourg": REGION_NAME has no key for it, so the site display falls back to the raw lowercase string
    (works; noted in the lead doc; a REGION_NAME key would be a small follow-on task, not mine).

### 2026-10-11 204 DECISION: re-verification of the recorded QID table is clean (22 towns) - 3 name-search traps documented, 4 module bugs fixed
    Ran `--verify` with no args (every recorded town: the 16 NL + the 6 done) - 28 s, no 429 stalls, exit 0.
    All 16 NL: labels match (no LABEL CHECK), every P625 within 0.74 km of the recorded old-town point
    (maxes: Haarlem 0.74, Amsterdam 0.68, Leeuwarden 0.65, Rotterdam 0.63, Sluis 0.59, Goes 0.49 km - the
    Gouda-800 m class of offset, now computed not eyeballed), P373 matches the table string exactly in all
    16 (every category-route target confirmed), enwiki matches (Valkenburg's old-town item Q100076 has none,
    as recorded). The 6 done towns re-confirm the plain-town-category P373 pattern. Three name-search traps
    (first hit with P625; all within 50 km, so no auto-flag, and the caption route stores the verified site
    point, so the exposure is documentary only): 'Sluis' resolves FIRST to Q2065987 - a distinct item
    ('place with town rights and privileges' / 'cadastral populated place in the Netherlands' / 'fortified
    town', no enwiki, P625 (3.3883, 51.3089) 8 km SW of the town, P373 'Sluis (city)' vs Q10080's 'Sluis';
    noted on the TOWNS row) - 'Reimerswaal' to the municipality Q10078 (the city Q2590944 is recorded, ~9 km);
    'Valkenburg' to the modern town Q9771 (the old town Q100076 is recorded, 0.19 km - same spot). Box 4: only
    the six done QIDs are in the catalog (12575 known sites checked); no other NL QID collides, so no
    reuse-of-existing-site case yet (the BE/FR/LU batches must re-check per town - stage() already handles it).
    Module fixes in the same commit (fresh-eyes read of the iteration-40 build): (a) verify_qids crashed with
    KeyError on the 6 done towns (their TOWNS rows carry no label/lon/lat/p373) - no-args now includes them
    degraded (no distances, P373 "(none recorded)") and an unknown town name fails loud; (b) cat_chain
    returned a " -> "-joined string INCLUDING the file category, but evidence_for records t["chain"] as the
    via and check_category requires via[-1] == site_cat and file_cat not in via - it now returns and prints
    the via list as JSON (paste into TOWNS) and walks with ciclimit 500 (a parent list over 50 would have
    silently lost the chain); (c) check_staged's per-row town lookup called _site_row over ALL TOWNS entries
    -> KeyError on the done towns - now a precomputed sid->town map (slug id and, when the QID is already
    cataloged, the existing site id) over fully recorded towns only; (d) golden()'s pick loop indexed a
    site-id-keyed dict with town names (never matched) - now a town -> staged-row map. Suite 33/33 green.
    Transcript: /tmp/vd_verify_iter41.txt (re-run: .venv/bin/python fit/src_van_deventer.py --verify, ~30 s).

### 2026-10-11 204 DECISION: wrote docs/lead_van_deventer.md (category census + NL QID section + NL traps); fixed two stale TOWNS count comments
The lead doc now holds the verified material (the pending sections stay marked pending): (1) the category
section - name/URL, 70 = 66 town + 4 collections, the --list assertion, all 66 town categories listed by
country with the 6 done marked (NL 19 / BE 22 / FR 24 / LU 1), the 4 collection names incl. the BNE atlas;
(2) the NL QID table - 16 rows (QID/label/P625/site-point/P625->site distance/enwiki; distances taken from the
iter-41 transcript /tmp/vd_verify_iter41.txt, all <= 0.74 km, labels/P373 clean, the 3 done NL re-confirmed);
(3) the three NL name-search traps with measured distances: Sluis first hits Q2065987 (9.0 km SW, P373
'Sluis (city)', no enwiki) vs recorded Q10080; Reimerswaal first hits the municipality Q10078 (9.1 km, shares
the P373 with the city so P373 cannot separate them) vs recorded city Q2590944; Valkenburg first hits the
modern Q9771 (0.14 km, same spot) vs recorded old town Q100076 (no enwiki -> no wikipedia field). Pending
sections carry: the BE/FR/LU QID batches (Ghent Q1296 already verified in prep - record with the BE batch;
... (1.1 KB more: `grep -n -A 200 -F '## 2026-10-11 204 DECISION: re-verification of the recorded QID table is clean (22 towns) - 3 name-search traps documented, 4 module bugs fixed' DECISIONS.md`)

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

### 2026-10-11 204 (agent a, iteration 43) HAND-OVER: NL file inventory done - 13/16 picks in TOWNS
    town_files() extended (the 4 collections + town subcats at depth 1; the atlas keeps its per-place plates
    inside the towns' categories - Landrecies's 5 KBR detail scans) and the 13 staged NL TOWNS rows carry file=
    (+ date= for Rotterdam/Sluis/Valkenburg); 3 NL drops documented (Groningen province, Leeuwarden, Middelburg).
    These module changes are UNCOMMITTED (harness-saved). Lead doc's Per-town and collection-categories sections
    are still (pending). Next: sanity `stage --dry` + `--check` + pytest (last 33/33), commit module + lead doc,
    then the BE QID batch, FR, LU, then the one long --chain run + stage + test + golden. Full detail:
    tasks/204-van-deventer.md and the DECISIONS entry above.
