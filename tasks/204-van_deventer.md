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
(2026-10-11, iteration 53 - **TOWNS recording DONE + verified; lead doc BE side DONE (uncommitted); FR/LU side of
the lead doc still to write**.)

**fit/src_van_deventer.py (all changes on disk, UNCOMMITTED - the harness saved the working tree):**
- Parse check (system python3): (66, 56) = 66 towns, 56 stageable (NL 13 + BE 21 + FR 21 + LU 1) -> **box 5 met**.
- Beaumont: full entry moved into the BELGIUM section (after Aarschot, before Oudenaarde): region="belgium",
  qid="Q95100", label="Beaumont", lon/lat 4.2383/50.2355, p625 (4.2383115, 50.2355294), place "Arrondissement of
  Thuin", wikipedia https://en.wikipedia.org/wiki/Beaumont,_Belgium, p373 "Beaumont (Hainaut)",
  file="File:Beaumont - Deventer.jpg" + long comment (Sambre bisecting the town, counts' chateau west bank,
  Charles V's grid town east; Q128282 Texas trap; the 1049x932 detail crop not staged). The old FR pending
  block is deleted. BE header comment -> 24 categories (22 to stage + 2 done), five disambiguated P373, all 22
  new entries. FR header -> 22 (21 to stage + 1 done), picks summary, no PENDING.
- file= on all 21 FR towns (every one the 1545 BNE atlas plate, or its (2) wide-sheet twin: Arras 3184, Douai
  3665, Lille 3614, Saint-Omer 3449, Valenciennes 4156; the Aire 3395 spread staged once under Aire; Hesdin
  double sheet staged once; Thérouanne 986x867 + Vieil-Hesdin 757x857 standalone plans with size caveats) +
  Le Rœulx (1545 plate, desc 'Le Rœulx') + Luxembourg City (file="File:Luxemburg 1550 65 v Deventer.jpg" +
  caption="Lutzenburg" - REQUIRED, the label 'Luxembourg' is not in the title/desc). No date= anywhere (every
  page date is 1545/1550 = the drawing's). All per-town details (sizes, reasons for every not-staged file)
  are in the TOWNS comments now - use them as the source for the lead-doc FR/LU section.
- **Live runs this session:** `.venv/bin/python fit/src_van_deventer.py --verify Beaumont` exit 0, transcript
  **/tmp/vd_verify_beaumont_iter53.txt**: label 'Beaumont', P373 'Beaumont (Hainaut)' ok, enwiki 'Beaumont,
  Belgium' matches; TRAP line as predicted: first P625 hit Q128282 'Beaumont' (Texas) 8035 km. `--check` exit
  0 (staging files still absent - `stage` runs later). The three staging jsonl NOT yet created.
- **docs/lead_van_deventer.md (one edit call applied, UNCOMMITTED):** top country lists (BE 24 incl. Beaumont,
  FR 22), BE QID method paragraph (Beaumont settled + re-verified, 22 entries), BE table (+Beaumont row), BE
  traps (+Beaumont bullet), BE per-town header/intro (24 categories: 21 staged, 1 drop, 2 done), Beaumont
  bullet (after Ath) + Le Rœulx bullet (after Lessines).

**EXACT NEXT STEP (one session, no network):**
1. Finish docs/lead_van_deventer.md - 4 remaining spots (take every oldText from sed; this file hard-wraps and
   the read tool's output proved unreliable once):
   (a) '## QID verification - France, Luxembourg': replace the 'Beaumont is the only town whose QID is still
   unverified' bullet with the settled story (Q95100 Hainaut; the 1545 plate shows the Sambre + the chateau,
   Nord has neither; region flipped; re-verify /tmp/vd_verify_beaumont_iter53.txt; the Q128282 Texas trap);
   the 'None of the QIDs verified here (the 22 non-Beaumont...)' sentence -> include Beaumont (21 FR + LU +
   moved Le Rœulx + moved Beaumont + done Bergues); the table's '23 rows: ...' line -> Beaumont moved to the
   BE table; the FR-traps 'Beaumont' bullet -> settled (trap = Q128282, 8035 km).
   (b) Replace the stub '### France, Luxembourg (QIDs verified 2026-10-11, iter 49; file= pending the --files
   run)' with '### France (22 categories: 21 staged, 1 done; checked 2026-10-11, iter 52, --files transcript
   /tmp/vd_files_fr_iter50.txt)' - one bullet per town in doc order (Aire-sur-la-Lys, Arras, Avesnes-sur-Helpe,
   Bapaume, Bavay, Bouchain, Béthune, Cambrai, Condé-sur-l'Escaut, Douai, Gravelines, Hesdin, Landrecies, Le
   Cateau-Cambrésis, Le Quesnoy, Lille, Maubeuge, Saint-Omer, Thérouanne, Valenciennes, Vieil-Hesdin, Bergues
   (done)): staged file + size + date, and every not-staged file with its reason - copy from the TOWNS
   comments; then '### Luxembourg (1 category: staged; iter 52)': the Luxembourg City bullet (2261x1878, 1550,
   desc 'Lutzenburg', hand-coloured drawing; caption route; the 3 not-staged files; region 'luxembourg' = new
   REGION_NAME value, display falls back to the raw value).
   (c) Collection section BNE bullet: 'all 23 FR towns (...Mons... as (1)/(2))' -> 'all 22 FR towns (Arras,
   Douai, Lille, Saint-Omer, Valenciennes as (1)/(2) double plates)' (Mons is BE, already in the BE list);
   '16 of the 20 BE towns (Ath, ...)' -> '18 of the 22 BE towns (the list + Le Rœulx + Beaumont; Bruges,
   Brussels, Mechelen and Aarschot not there; plus done Binche)'; the double-plate sentence -> settled (Aire
   keeps the spread, Thérouanne its own 'Terwan' row; Hesdin keeps the double sheet, Vieil-Hesdin its own
   scan; year_of takes the min, 1545).
   (d) Summary: 'running total: 56 of 60 stageable town categories staged' - NL 13/16 (3 drops), BE 21/22
   (1 drop Aarschot), FR 21/21 (no drops - not-staged files are copies/SVGs/crops/one halftone repro), LU
   1/1; 56 of the 59 town plans; box 5 met (>=50, every missing one accounted for); box 2: every QID verified
   (Beaumont settled, none pending); done towns unmentioned.
2. Append the DECISIONS.md entry: '## 2026-10-11 204 DECISION: FR/LU picks RECORDED in TOWNS (24 file= incl.
   Beaumont moved to Belgium + LU caption) - lead doc BE side done, FR/LU side next; --verify Beaumont clean
   (the Q128282 Texas trap, transcript /tmp/vd_verify_beaumont_iter53.txt); (66, 56) -> box 5 met'.
3. PITFALLS.md - file the two entries still unfiled from iter 51/52 (all the other listed pitfalls are
   already there - check first): (0) 'Agent tools and harness': the read tool's output of
   fit/src_van_deventer.py was not byte-faithful once (iter 52: showed '21 to stage + 2 done' where the file
   had '+ the 2 done') - two edit calls failed on it; sed -n/grep is the source for edit oldText of that file
   (iter 53: 28 sed-derived blocks applied clean). (1) 'pipeline/' or 'This codebase': pipeline/aw.py's UA is
   a DICT ({'User-Agent': ...}), not a string - fine into urllib Request(headers=), slicing it (UA[:60])
   raises KeyError.
4. Commit: `git add fit/src_van_deventer.py docs/lead_van_deventer.md DECISIONS.md PITFALLS.md tasks && git
   commit -m "204: TOWNS recording - 56 stageable (Beaumont settled to BE, all FR/LU file= + LU caption) - the
   hand-checked record"` (the harness already saved the uncommitted tree; this makes it a commit).
5. NEXT session (the one long run, all under .venv): `--chain` per staged town that has no chain yet (record
   the walked chains in TOWNS as "chain" - check_category only re-verifies the shape, the walk is the
   verification, PITFALLS), then `stage` (NOT --dry; writes the 3 staging jsonl), `--check` (evidence on
   every row), write tests/test_src_van_deventer.py (pattern: tests/test_src_artists.py - socket-blocking
   no_network fixture, check_staged(), subprocess `fit/evidence.py check --files <staged> --books <absent
   path>`, golden sample, negative control; box 6: year_of of every staged row in 1545-1565 - the Hesdin note
   row yields 1545 = the min), `--golden` (tests/golden/src_van_deventer_sample.json), full pytest.

**Team mode:** agent c on 203b (fit/batch_eu.py, data/db/platefits, data/review, docs/batch_eu.md,
tests/test_batch_eu.py) + 205 (fit/src_kip.py + its data/docs/tests) - untouched by me. My Touches:
fit/src_van_deventer.py, the 3 staging jsonl (created by `stage`), docs/lead_van_deventer.md,
tests/test_src_van_deventer.py, tests/golden/src_van_deventer_sample.json, plus this task file.

### OLD (driver: replace the section above; delete this marker and the old text up to just before '### Also written to PROGRESS.md')
(2026-10-11, iteration 52 - **ALL FR/LU eye checks DONE, every pick decided; TOWNS/lead-doc NOT yet
edited** - this session's TOWNS edit calls FAILED on a text mismatch (the read tool's output of fit/
src_van_deventer.py is not byte-faithful: it showed "21 to stage + 2 done" where the file has "+ the 2
done"); the file is UNCHANGED on disk and nothing is committed from this session.)

**Decisions (from the /tmp/vd_fr_thumbs/ eye check + the iter-50 --files transcript /tmp/vd_files_fr_
iter50.txt):**
- **The five (1)/(2) pairs ALL confirmed: stage the (2) wide sheet (the full sheet with the town label,
  shield, compass points + scale), NOT (1) (a single-page scan of the same drawing).** Arras (1) is one
  page of a two-page drawing (the old town cut off at the right edge); Douai/Saint-Omer/Valenciennes/
  Lille (1) are the drawing on its own page (larger scale, no label/compass). Mons (1)/(2) precedent
  holds. Staged: Arras `(2)` 3184x2614, Douai `(2)` 3665, Lille `(2)` 3614, Saint-Omer `(2)` 3449 (sheet
  label 'S. Omeri', page 34), Valenciennes `(2)` 4156 (label in cursive).
- **Hesdin/Vieil-Hesdin double sheet SETTLED - staged once under Hesdin.** `Hesdin - Deventer.jpg`
  (3408x2614, page 30): LEFT page = the big bastioned star fort labelled 'Hesdyn fort.' + blank shield
  (the 1554-1575 fortification) + a small framed inset lower-left; RIGHT page = the framed pentagon
  'Hesdyn' (the moated old town with its hill-top fort, compass Orcidens/Oriens/Meridies) = the Vieil-
  Hesdin plan. `Vieil-Hesdin - Deventer.jpg` (757x857, 1545, desc 'Vieil-Hesdin') is a standalone scan of
  exactly that right-page inset (compared pixel-for-pixel) -> its own row (the only standalone Vieil-
  Hesdin plan; size caveat). The Hesdin row keeps the French page note as-is (year_of takes the min =
  1545, in-window; no date= swap).
- **Luxembourg City SETTLED - stage `File:Luxemburg 1550 65 v Deventer.jpg`** (2261x1878, page date 1550
  = the drawing's, desc 'Lutzenburg'): the eye check confirms van Deventer's hand-coloured drawing on
  laid paper (label 'Lutzenburg' + blank shield, Dutch compass Noorde/West/Oost/Zuydt, the Alzette with
  the Bock rock and the old castle, the new bastioned fort to the west). It needs **caption="Lutzenburg"**
  in TOWNS: the label 'Luxembourg' is NOT in the title/desc (the file prints the historical spelling;
  evidence_for's caption check would otherwise fail). Not staged: `Lutzenburg.jpg` (uploaded 2005,
  'published first 1609'), `Lutzenburg 1581 Sanderus.jpg` (the 1581 Sanderus print), `Couvent Knödler
  1550.jpg` (644x468 detail crop).
- **Aire 'Plan de Deventer' (992x800, QS 1550-1565) DECIDED NOT STAGED:** a grainy halftone book
  reproduction of the same town (label 'Aire' + shield) - redundant with the BNE spread.
- Beaumont / Aire-Therouanne double plate: as settled in iter 51 (Hainaut Q95100, region -> belgium; the
  3395x2614 Aire/Therouanne spread staged once under Aire; Therouanne its own 986x867 standalone
  'Terwan' plan).
- **No date= needed on ANY new entry:** every staged file's page date IS the drawing's date (1545/1550) -
  no Gouda/Zwolle-style swap in this batch. caption= only on Luxembourg City.

**State: fit/src_van_deventer.py UNCHANGED (66 towns, 32 stageable = NL 13 + BE 19; the 3 staging jsonl
absent; docs/lead_van_deventer.md still has the '### France, Luxembourg (pending)' stub).** After the
recording step: 56 stageable (NL 13 + BE 21 + FR 21 + LU 1) -> box 5 met.

**EXACT NEXT STEP (one session; no network needed except --verify Beaumont):**
1. **TOWNS edits in fit/src_van_deventer.py. WARNING: take every oldText from `sed -n 'N,Mp'`/`grep -n`
   on the file, NOT from the `read` tool (iter-52's two edit calls both failed on read's non-faithful
   output); verify with `python3 -c "import sys; sys.path.insert(0,'fit'); import src_van_deventer as m;
   print(len(m.TOWNS), len(m.stageable()))"` after editing (expect (66, 56)).** Current line numbers:
   BE header 166-182, Le Rœulx entry 248-256, Aarschot end 306 / Oudenaarde 307, FR header 317-326, the FR
   Beaumont pending block 343-349 (delete it), LU header + entry 409-418 (TOWNS dict closes ~419). Edits:
   (a) BE header -> 24 categories (22 to stage + the 2 done), Beaumont joined iter 52 (Sambre/chateau),
       'Five items carry a disambiguated P373' (+Beaumont), file= recorded iter 46 + iter 52 (Le Rœulx +
       Beaumont, transcript /tmp/vd_files_fr_iter50.txt), 'all 22 get new catalog entries'.
   (b) Insert the full Beaumont entry after Aarschot / before Oudenaarde: region="belgium", cat "Map of
       Beaumont by Jacob van Deventer", qid="Q95100", label="Beaumont", lon=4.2383, lat=50.2355,
       p625=(4.2383115, 50.2355294), place="Arrondissement of Thuin", wikipedia=
       "https://en.wikipedia.org/wiki/Beaumont,_Belgium", p373="Beaumont (Hainaut)", file="File:Beaumont -
       Deventer.jpg" + comment (Sambre bisecting the town, counts' chateau west bank, Charles V's grid
       town east; the Q128282 Beaumont (Texas) trap ~7000 km, the recorded label/P373/enwiki confirm
       Q95100; the 1049x932 '...detail - City and Chateau de Beaumont.jpg' not staged). Comments INSIDE
       the dict parens or after the closing `),` (the PITFALLS unbalanced-braces rule).
   (c) FR header -> 22 categories (21 to stage + the 1 done); file= for the 21 recorded iter 52 from the
       transcript + the 1280 px eye check (pairs / Aire / Hesdin / size-caveat summary); drop the 'PENDING'
       and 'watch item' sentences.
   (d) Delete the FR Beaumont pending block.
   (e) Le Rœulx entry: add file="File:Le Rœulx - Deventer.jpg" (the 1545 BNE plate, desc 'Le Rœulx'); keep
       the moved-here note.
   (f) The 21 FR entries (all page date 1545, no date=): Aire-sur-la-Lys "File:Aire-sur-la-Lys - Deventer.jpg"
       (3395 spread 'Aire-sur-la-Lys & Thérouanne', staged once; left-page insets incl. 'Terwan'; the two
       SVG redraws + the 992x800 halftone repro not staged); Arras "(2)"; Avesnes-sur-Helpe; Bapaume; Bavay;
       Bouchain; Béthune (3442 spread; two SVGs not staged); Cambrai (3722); Condé-sur-l'Escaut (3529);
       Douai "(2)" (keep the existing P131 'County of Flanders' comment); Gravelines; Hesdin (comment:
       double sheet, page 30, the note as page date, staged once under Hesdin); Landrecies (1816 plate; the
       five 'Plan de Landrecies, détail ... KBR' files (1091-1805 px, QS 1550-1565, detail crops, two
       annotated) not staged); Le Cateau-Cambrésis; Le Quesnoy (3447; two SVGs not staged); Lille "(2)"
       (the 2022 png 625x452 'Lille vers 1550...' + two SVGs not staged); Maubeuge (3481); Saint-Omer "(2)"
       (label 'S. Omeri', page 34); Thérouanne "File:Thérouanne - Deventer.jpg" (986x867 standalone 'Terwan'
       plan, size caveat, the Aire spread staged under Aire); Valenciennes "(2)" (4156); Vieil-Hesdin
       (757x857 standalone scan of the double-sheet inset, size caveat).
   (g) LU: header comment gains the iter-52 file= note; Luxembourg City entry gains file="File:Luxemburg
       1550 65 v Deventer.jpg" + caption="Lutzenburg" + the eye-check/drops comment; keep the existing
       Q1842 / new-region comments.
   Then: `.venv/bin/python fit/src_van_deventer.py --verify Beaumont` (expect the TRAP line: first P625
   search hit Q128282 Beaumont (Texas) ~7000 km; label 'Beaumont', P373 'Beaumont (Hainaut)', enwiki
   'Beaumont, Belgium' confirm Q95100) and `.venv/bin/python fit/src_van_deventer.py --check` (exit 0,
   staging files still absent).
2. Lead doc docs/lead_van_deventer.md: replace '### France, Luxembourg (pending)' with per-town FR + LU
   sections (one bullet per town: staged file + size + date, and every not-staged file with its reason -
   all in the transcript and this hand-over), Beaumont into the BE section with the settlement, the QID
   table gains the Beaumont row (Q95100) and loses the pending mark, the top country lists (BE 24, FR 22),
   the Summary (running total 56 of 61 stageable categories: NL 13 + BE 21 + FR 21 + LU 1). Then commit
   TOWNS + lead doc + this hand-over.
3. NEXT session: --chain per newly staged town (24 towns, one long run; record the walked chains in the
   TOWNS entries as "chain"), `stage` (NOT --dry), `--check`, write tests/test_src_van_deventer.py
   (pattern: tests/test_src_artists.py - socket-blocking no_network fixture, check_staged(), subprocess
   `fit/evidence.py check --files ... --books <absent path>`, golden sample, negative control; box-6:
   year_of of every staged row in 1545-1565), `--golden`, full pytest.

**Pitfalls (file in PITFALLS.md when next allowed - not this session, harness context limit):** (0) the
read tool's output of fit/src_van_deventer.py was not byte-faithful ("+ 2 done" vs the file's "+ the 2
done", twice) - sed/grep is the source for edit oldText; (1) aw.py's UA is a DICT ({'User-Agent': ...}) -
passing it to urllib Request(headers=) works, slicing it (UA[:60]) raises KeyError; (2) trailing-comment-
in-unbalanced-braces rule for every TOWNS edit; (3) wbsearchentities limit=5 misses well-known short
names; (4) raw Wikimedia API calls need aw.UA or 403; (5) label searches with parentheses return EMPTY.
/tmp/vd_fr_fetch.py (thumbs/crops) and /tmp/vd_fr_thumbs/ are still on disk. Team mode: agent c on 203b +
205 - untouched by me. My Touches: fit/src_van_deventer.py, the 3 staging jsonl (created by stage),
docs/lead_van_deventer.md, tests/test_src_van_deventer.py, tests/golden/src_van_deventer_sample.json,
plus this task file.

### OLD (driver: replace the section above; delete this marker and the old text up to just before '### Also written to PROGRESS.md')
(2026-10-11, iteration 51 - **FR/LU --files batch DONE + Beaumont SETTLED as Hainaut (Q95100) + Aire/Thérouanne
double plate settled; TOWNS/lead-doc NOT yet edited**). Nothing is committed from this session: the --files
transcript and the eye-check images are in /tmp (still on disk).

**The --files batch (transcript /tmp/vd_files_fr_iter50.txt, 217 lines, exit 0; 24 towns + 4 collections):**
- The 1545 BNE atlas plate sits in every one of the 22 FR town categories + Le Rœulx's (all 1816x2614 or
  wider, page date 1545, desc = the town name) - the expected picks, confirmed.
- **Beaumont SETTLED = Hainaut (Q95100), region flips france -> belgium.** The 1545 plate
  (`File:Beaumont - Deventer.jpg`, 1816x2614, desc 'Beaumont') eye-checked: a fortified town BISECTED by a
  river (the Sambre) with a bridge, the old town + a moated square castle (the counts of Hainaut's chateau;
  the sheet's lower-left inset box = that chateau) on the west bank, Charles V's new walled grid town on the
  east bank. Beaumont (Nord) has no river and no chateau - Hainaut wins on the drawing. Fact sheet (iter-49
  transcripts, line refs /tmp/vd_verify_fr_iter49.txt:32 and /tmp/vd_lu_iter49.txt:98): label 'Beaumont',
  P625 (4.2383115, 50.2355294), P373 'Beaumont (Hainaut)', P131 'Arrondissement of Thuin', enwiki
  'Beaumont, Belgium'. The four old crops /tmp/vd_fr_thumbs/beaumont*.jpg (pre-session, 08:51-08:54) + this
  session's Beaumont_-_Deventer_{thumb,top,center}.jpg are the evidence; the previous session's
  beaumont_label_river.jpg shows the river crossing the town centre + bridge. A 1049x932 detail file
  ('...detail - City and Chateau de Beaumont.jpg', 1545) confirms the chateau; not staged (detail crop).
- **Aire/Thérouanne double plate SETTLED.** `Aire-sur-la-Lys - Deventer.jpg` (3395x2614, 1545, desc
  'Aire-sur-la-Lys & Thérouanne') = two-page spread: RIGHT page = the full Aire plan (label 'Aire.', town on
  its Lys peninsula, compass points, page no. 33); LEFT page = two framed insets: 'Terwan' (the Thérouanne
  pentagon) top-left and a second small water-bound settlement bottom-left (identity not needed for staging).
  So: stage the sheet ONCE under **Aire** (file_cat = Aire's town category; the file is in both town cats, the
  BNE cat too). **Thérouanne gets its own row**: `File:Thérouanne - Deventer.jpg` (986x867, 1545) is a full
  standalone 'Terwan' plan (pentagon, compass, bridge) - the only Thérouanne plan on Commons -> stage with the
  Ostend/Aardenburg size caveat. `File:Aire-sur-la-Lys - Plan de Deventer.jpg` (992x800, QS 1550-1565, desc
  'Plan dit de Deventer de la ville d'Aire...') - thumb not yet viewed; presumed small reproduction, not
  staged (decide when recording).
- **Hesdin/Vieil-Hesdin double plate NOT yet decided** (eye check of the crops pending): `Hesdin -
  Deventer.jpg` (3408x2614, desc 'Hesdin & Vieil-Hesdin'; page date a French note: Hesdin plan 1554-1575,
  Vieil-Hesdin 'probablement 1545') - view /tmp/vd_fr_thumbs/Hesdin_-_Deventer_{thumb,left,right,center,top}.
  `Vieil-Hesdin - Deventer.jpg` (757x857, 1545) - view its thumb; if a full plan -> own row (size caveat).
  year_of of the double sheet = 1545 (min of the years in the note - checked) so the row passes the box-6
  window; the note stays as the row date with a lead-doc explanation.
- **Luxembourg City NOT yet decided**: candidate `File:Luxemburg 1550 65 v Deventer.jpg` (2261x1878, 1550,
  desc 'Lutzenburg') - view thumb/center/top to confirm it is Deventer's drawing (a coloured plan) and not a
  later print; 'Lutzenburg' names the town (caption route works if the chain walk fails). NOT Deventer ->
  documented drops: `Lutzenburg.jpg` (1600x1200, page 2005 upload, desc 'published first 1609'),
  `Lutzenburg 1581 Sanderus.jpg` (1909x1599, 1581), `Couvent Knödler 1550.jpg` (644x468, detail of the
  franciscan convent).
- **The five (1)/(2) pairs** (Arras 3184, Douai 3665, Lille 3614, Saint-Omer 3449, Valenciennes 4156 wide =
  ~2 x the 1816 page): hypothesis (2) = the full two-page spread (stage), (1) = one page, partial (not
  staged) - the Mons (1)/(2) precedent. Thumbs for all 10 downloaded; confirm the pattern by viewing at least
  one pair's (1)+ (2) center crops (the others by thumb). The two SVG twins per town (Béthune, Le Quesnoy,
  Aire, Lille) are vector redraws (mime svg) - not staged.
- **year_of checked on every candidate date string**: all stage candidates land in 1545-1565 (Hesdin sheet
  1545; 'Aire Plan de Deventer' 1550; the 1545 pages 1545; Luxemburg 1550 1550); Lutzenburg 2005, Sanderus
  1581 - the non-Deventer drops, consistent.

**State of the table (TOWNS unchanged this session: 66 towns, 32 stageable = NL 13 + BE 19; staging files
absent on disk; check with `python3 -c "import sys; sys.path.insert(0,'fit'); import src_van_deventer as m;
print(len(m.TOWNS), len(m.stageable()))"`).** After the recording step below: 66 towns, ~55-56 stageable
(NL 13 + BE 20 + FR 21-22 + LU 0-1 + Le Rœulx), i.e. >= 50 for box 5 even before staging; Beaumont moves to
the Belgium section of the table (its entry keeps its FR-batch position? NO - move the dict entry to the
Belgium section and fix both section header comments: BE 23->24 cats (22 to stage + 2 done), FR 23->22 (21
+ 1 done)).

**EXACT NEXT STEP (one session; no long API run needed except one --verify):**
1. Finish the eye check from /tmp/vd_fr_thumbs/ (images above: Hesdin set, Vieil-Hesdin, Luxemburg 1550,
   one (1)/(2) pair's center crops + the 9 remaining pair thumbs, Aire 'Plan de Deventer').
2. TOWNS edits (one edit per town; the trailing-comment-in-unbalanced-braces rule!): file= (+ date=/caption=/
   note= where needed) on the 21 remaining FR towns + Le Rœulx + Luxembourg City; Beaumont: full record
   (region="belgium", qid="Q95100", label="Beaumont", lon/lat 4.2383/50.2355, p625 (4.2383115, 50.2355294),
   place="Arrondissement of Thuin", wikipedia="https://en.wikipedia.org/wiki/Beaumont,_Belgium",
   p373="Beaumont (Hainaut)", file=, note= the Hainaut settlement) + move the entry to the Belgium section;
   update the BE/FR section header comments (counts + this session's transcript).
3. `.venv/bin/python fit/src_van_deventer.py --verify Beaumont` (the re-verification as its own fact sheet;
   expect the TRAP line: first search hit with P625 = Q128282 Beaumont (Texas) ~7000 km away - that is the
   documented trap, the recorded label/P373/enwiki confirm Q95100).
4. Lead doc: per-town FR/LU section (replace the 'pending' stub; one bullet per town incl. every not-staged
   file with its reason), the collection section's double-plate lines updated with the eye-check result,
   the QID table gains a Beaumont row and loses none (it is already listed as pending - move it into the BE
   table with region note), the two country lists at the top (FR 23->22, BE 23->24), the Summary running
   total. Then commit TOWNS + lead doc + this hand-over.
5. NEXT session: --chain per newly staged town (24 towns, one long run), `stage` (NOT --dry), `--check`,
   write tests/test_src_van_deventer.py (pattern: tests/test_src_artists.py - socket-blocking no_network
   fixture, check_staged(), subprocess `fit/evidence.py check --files ... --books <absent path>`, golden
   sample, negative control; box-6: year_of of every staged row in 1545-1565), `--golden`, full pytest.

**Pitfalls hit/confirmed this session:** (0) `pipeline/aw.py`'s UA is a DICT ({'User-Agent': ...}), not a
string - passing it to urllib's Request(headers=) works; slicing it (UA[:60]) raises KeyError - file in
PITFALLS if not already; (1) trailing-comment-in-unbalanced-braces rule for every TOWNS edit; (2)
wbsearchentities limit=5 misses well-known short names; (3) raw Wikimedia API calls need aw.UA or 403;
(4) label searches with parentheses return EMPTY. The /tmp/vd_fr_fetch.py script (fetch thumbs + crops) is
reusable: /tmp/vd_fr_fetch.py with the FILES list edited. Team mode: agent c on 203b
(fit/batch_eu.py, data/db/platefits, data/review, docs/batch_eu.md, tests/test_batch_eu.py) - untouched.
My Touches: fit/src_van_deventer.py, the 3 staging jsonl (created by stage), docs/lead_van_deventer.md,
tests/test_src_van_deventer.py, tests/golden/src_van_deventer_sample.json, plus this task file.

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/204-van_deventer.md` (in-progress) - hand-over: (2026-10-11, iteration 50 - **FR+LU re-verify DONE (clean) and lead doc updated; all committed**). The
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and

## Next open tasks
- `tasks/215-books-llm-ports.md`
- `tasks/216-view-books-entries.md`
- `tasks/217-view-books-lists.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-11 204 DECISION: BE file batch done - 19/20 picks decided + eye-verified; Aarschot a documented drop (both files dated 1570, outside the c. 1545-1565 window)
`--files` for the 20 BE towns (transcript /tmp/vd_files_be_iter46.txt, 212 lines, exit 0) confirmed the
prediction: the 1545 BNE atlas plates sit in the town categories for 16 of the 20 (Ghent as BN 1/BN 2,
Mons as (1)/(2), Oudenaarde as Version Madrid); Bruges (7), Brussels (7), Mechelen (1) and Aarschot (2)
are not in BNE. All 9 ambiguous candidates were eye-verified from 1200 px thumbs + full-size crops
(/tmp/vd_be_thumbs/, re-download via commons.info + aw.UA; the `read` tool views images):
- **Ghent BN 1** (4919x5046, 1545) = the labelled 'Gande' sheet (city between the two rivers) - STAGED.
  **BN 2** (2834x3631, 1545) is a DIFFERENT sheet (a fortified town, no city label in the centre crop) -
  not staged, noted. Also not staged: the 1559 Donato Buoni di Pellezuoli print (a later print by another
  cartographer) and five small 2007-2012 scans/crops.
- **Mons (2)** (4393x2614, 1545) = the wide two-page sheet labelled 'Mons en Henault' (Ocidente/Oriens/
  Meridies/Septentrio) - STAGED. Mons (1) (1816x2614) is a portrait plate of the same fortified town -
  not staged, noted.
- **Brussels '(2) 01.png'** (8908x10941, circa 1555) = the KBR autograph cleanly cropped - STAGED.
  '(2).png' (9216x12288) is the same sheet WITH a TIFFEN colour-calibration strip (the ugly duplicate);
  '(2) 02' is the explicit detail; the three small Brussel 1550/1555/1560 scans (470-1233 px) and
  Molenbeek.1550.jpg (378x565, Molenbeek + the west of the 2e enceinte - the work list's 'Brussel, 1550
  (westelijk gedeelte)', partial) - all not staged.
- **Bruges 'Map of Bruges by Jacob van Deventer.jpg'** (2770x4659) - the full plan; the sheet's OWN
  caption block (bottom of the sheet, partially torn away) reads "Brugge (West Flan...) ... en omgeving
  omstreeks den jare 1550. Plattegrond in kleuren. Originade Teckening van den be-Keizerlijken..." -
  the drawing dates itself c. 1550 -> row date="circa 1550", the 2013-01-17 12:04:47 page value (an
  upload timestamp) kept as date_commons by the stage() swap. The three category detail files carry QS
  'circa 1558' for the same map - the sheet's own caption wins (recorded in the lead doc). Not staged:
  five detail crops (846x522, 1180x668 x2, 573x564, 650x832) and 'Plan Brugge ... ca.1560.jpg' (1400x1867,
  a published reproduction per C. Ruelen).
- **Mechelen** (3558x3305, page date 1550) = the KBR autograph (desc: from the atlas KBR bought in 1866)
  - STAGED; page date is the drawing date (work list 'Mechelen, 1550' agrees), no swap.
- **Ostend** (872x1255, page 'circa 1562' QS) = the full BNE atlas plate (labeled 'Oostende', the town +
  the harbour detail box) - STAGED despite the 872 px width: the only Ostend plan on Commons (the
  Aardenburg precedent, caveat in the lead doc). No swap (1562 in window).
- **Aarschot - DOCUMENTED DROP, no site, no picture:** both files ('Aarschot 1570.png', 5877x6291 - a
  genuine autograph, town labelled 'Aersfot' on the Dijle, fortress on the north bank - and its
  1278x1024 jpg copy) carry page date **1570**. Verified against the web: the nl.wikipedia article
  'Jacob van Deventer (cartograaf)' lists 'Aarschot, 1570' in its work list (the Philip II period; his
  career ran to his death in 1575, the Rutte & Vannieuwenhuyze Stedenatlas covers 1545-1575 overall).
  1570 is outside this task's c. 1545-1565 drawing window, and box 6's test checks the row date's
  year_of in 1545-1565 - a 1570 row cannot be staged honestly. The documented drop (box 5) beats a
  guessed date. (The same work list cross-confirms the other picks: Gent 1545, Doornik 1545, Den Haag
  1558, Utrecht 1565-1570, Oudenaarde minuut 1563 / netkaart 1564.)
- The 12 single-file towns (Ath, Braine-le-Comte, Chimay, Chièvres, Enghien, Halle, Kortrijk, Lessines,
  Leuze, Saint-Ghislain, Soignies, Tournai): the one 1545 BNE plate each - all staged, no swap. Leuze
... (0.8 KB more: `grep -n -A 200 -F '## 2026-10-11 204 DECISION: BE file batch done - 19/20 picks decided + eye-verified; Aarschot a documented drop (both files dated 1570, outside the c. 1545-1565 window)' DECISIONS.md`)

### 2026-10-11 204 DECISION: BE file picks RECORDED in TOWNS (19 file= + Bruges date + Leuze caption + Aarschot note); lead-doc Belgium section written; Mons/403 pitfalls filed
The iteration-46 picks (the analysis above; /tmp/vd_files_be_iter46.txt still on disk, re-read to verify every
exact title before recording) are now in TOWNS: file= on all 19 staged towns (15 of the 1545 BNE plates:
Ath, Braine-le-Comte, Chimay, Chièvres, Enghien, Ghent BN 1, Halle, Kortrijk, Lessines, Leuze, Mons (2),
Saint-Ghislain, Soignies, Tournai, Oudenaarde Version Madrid; + Ostend BNE plate circa 1562 + KBR Brussels
(2) 01 + KBR Mechelen + Bruges full plan), date="circa 1550" on Bruges (page 2013-01-17 12:04:47 is the
upload timestamp; the sheet's own caption block dates it), caption="Leuze" on Leuze (its official label
'Leuze-en-Hainaut' is not in the title/desc), note= on Aarschot (the 1570 documented drop). The Belgium
section-header comment now records the iter-46 inventory + thumb eye check. Lead doc: the pending
subsection is now '### Belgium (20 categories: 19 staged, 1 documented drop; checked 2026-10-11, --files
transcript /tmp/vd_files_be_iter46.txt)' with one bullet per town (staged file + size + date and every
not-staged file with its specific reason; Aarschot the documented drop with the nl.wikipedia work-list
cross-check), a new '### France, Luxembourg (pending)' (24 towns; the double plates as watch items), and
the Summary updated (running total 32 of 59 staged: NL 13 + BE 19). PITFALLS filed: (1) wbsearchentities
limit=5 misses well-known short names - Mons 11th in the en search, follow up at limit 20; (2) a Commons
API call with no User-Agent gets HTTP 403 - commons.get sets aw.UA, a raw script must too. Verified after
the edit: `--check` exit 0 (staging files still absent - stage runs after FR/LU), module parses clean
(the PITFALLS comment-gluing rule observed: every entry's dict closed with `),` before its comments).
NEXT: the FR batch (23 towns: --verify first - QIDs still empty in TOWNS; the BNE plates cover all 23 per
the collections section; watch the Aire+Thérouanne and Hesdin+Vieil-Hesdin double plates - stage once under
the true primary, note the second; Beaumont's region flips france->belgium if the Hainaut item wins) +
Luxembourg City (search 'Luxembourg (city)', Q1564 expected, region 'luxembourg' - a NEW region value
build_catalog does not have a display key for yet), then the one long run: --chain per staged town, stage,
--check, tests/test_src_van_deventer.py, --golden.

### 2026-10-11 204 DECISION: FR+LU QID batch - 22 FR QIDs + Luxembourg City Q1842 verified and recorded in TOWNS (Le Rœulx moved to Belgium, Beaumont pending the atlas plate); TOWNS edit uncommitted, re-verify + lead doc next
Discovered in one --verify run (/tmp/vd_verify_fr_iter49.txt, 24 towns, exit 0 - the FIRST attempt of the
session failed locally with "unknown town 'Le'": shell quoting, the Le X names were unquoted; no API calls
happened, the quoted re-run succeeded): all 23 FR fact sheets came back; the 22 non-Beaumont towns each have
a clear first-hit item (label = the town, P625 at the town, P373 = the plain town category, enwiki present)
- recorded in TOWNS with site point = P625 rounded (the BE convention; an old-town-centre offset is the watch
item once the drawings are eye-checked) and place = the modern department (Nord / Pas-de-Calais; Douai's and
Valenciennes' items also carry the historical P131 'County of Flanders' / 'County of Hainaut' - the c. 1550
context, noted in comments, the row's place stays the department). Two surprises:
- **Luxembourg City = Q1842, not the hand-over's Q1564** (Q1564 now holds 'Borgfelde', Hamburg - merged
  away). Q1842: label 'Luxembourg', P625 (6.13, 49.611389), P373 'Luxembourg City', P131 'Canton of
  Luxembourg', enwiki 'Luxembourg City'. The entry's search="Luxembourg (city)" returned EMPTY (the
  parenthesized label search - a new instance of the prep's "qualified strings return EMPTY" quirk); the
... (2.7 KB more: `grep -n -A 200 -F '## 2026-10-11 204 DECISION: BE file picks RECORDED in TOWNS (19 file= + Bruges date + Leuze caption + Aarschot note); lead-doc Belgium section written; Mons/403 pitfalls filed' DECISIONS.md`)

### 2026-10-11 204 DECISION: FR+LU re-verify clean (23 towns) + lead-doc FR/LU section written (23-row table, traps, Beaumont pending) + parentheses-search PITFALLS filed
Session started from the driver-committed TOWNS edit (6b8f85a; parse-check passed: 66 towns, 32 stageable, as
predicted). The planned re-verify run then went cleanly (23 towns = 21 FR with QIDs + Le Rœulx + Luxembourg
City; Beaumont omitted - no QID; transcript /tmp/vd_verify_fr_recheck_iter49.txt, exit 0): **every label
matches, every P373 'ok', every enwiki matches, and the first search hit with P625 is exactly the recorded QID
for all 23** (no first-hit trap in the verified set); P625→site is 0.00-0.01 km everywhere except Le Rœulx
0.91 km (the recorded item's P625 (4.1, 50.5) is rounded; the site point is the subdivision item Q21764574's
precise P625 - expected, documented). Bergues (done FR) fetched in one extra call: Q244934 label 'Bergues',
P625 2.434167, 50.968611 (→ site 0.00 km), P373 'Bergues', enwiki 'Bergues' - row added to the lead-doc
table.

Lead doc (docs/lead_van_deventer.md) updated per the hand-over: (a) Commons category counts moved with
Le Rœulx (BE 22→23 categories, FR 24→23); (b) Belgium section: Le Rœulx table row + method sentence (found
in the FR batch, moved from the prep's France list; 0.91 km explained), BE catalog count 20→21; (c) '##
France, Luxembourg (pending)' replaced by '## QID verification - France, Luxembourg (checked 2026-10-11,
iter 49; ...)': method (discovery /tmp/vd_verify_fr_iter49.txt + re-check transcripts), the three changes
from the prep's list (Le Rœulx→Belgium; Luxembourg City = Q1842 not Q1564 - that id was merged away into
'Borgfelde' Hamburg, and the 'Luxembourg (city)' search returned EMPTY, the parentheses quirk; Beaumont
pending: only Q95100 Hainaut is plausible in the en top 20, the Nord town absent, the atlas plate settles
it, region flips if Hainaut wins), the 23-row table (21 FR to stage + Luxembourg City + done Bergues) with
the re-verify distances, and '### Name-search traps - France, Luxembourg' (Le Quesnoy: exact-label twin
Q109413780 (Somme) - coordinates+enwiki decide; Lille: Belgian twin Q725235; Saint-Omer: Calvados Q844283 +
Quebec Q3463075; Thérouanne: the river Q428296; Bapaume: the 1918 ship Q19543896 + Queensland Q48807630;
Luxembourg's search chain Q32→Q1126→Q1842; Beaumont; plus the minor near-misses, notably the Cambrai
near-duplicate Q84243457 at the same coordinates); (d) the per-town subsection retitled (QIDs verified,
file= pending the --files run) keeping the double-plate watch items; (e) Summary: NL 13/16, BE 19/21
(Le Rœulx file pending), FR 0/22 (Beaumont QID pending), LU 0/1 - running total 32 of 60 stageable
categories, box 5 unchanged.

PITFALLS filed (Wikimedia section): a wbsearchentities label search containing parentheses returns EMPTY
('Luxembourg (city)' case) - search the unparenthesized label form and let the fact sheet disambiguate.

Verified: --check exit 0 (staging files still absent - stage runs after the --files picks); module parses
(66/32); this session changed no module code (the iter-49 TOWNS edit was already driver-committed).
NEXT: the FR/LU --files batch (24 towns: the 22 FR to stage incl. Beaumont + Le Rœulx + Luxembourg City),
then record file=/date=/caption= picks, then the one long run (--chain per staged town, stage, --check,
tests/test_src_van_deventer.py, --golden).

## Project-wide driver notes (newest)

### 2026-10-10 DRIVER: .venv could not be built from requirements.txt
    ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    Every package needs a pinned version and hash (AGENTS.md, Research and packages); full pip output: .agent/reports/venv.txt

### 2026-10-11 204 (agent a, iteration 51) - session ended at context limit; full detail in the task's ## Hand-over
    FR/LU --files batch DONE (transcript /tmp/vd_files_fr_iter50.txt, exit 0): the 1545 BNE atlas plate is in all
    22 FR town categories + Le Rœulx's. Eye check (images in /tmp/vd_fr_thumbs/): Beaumont SETTLED as Hainaut
    (Q95100, region flips to belgium - the plate shows the Sambre bisecting the town + the counts' chateau;
    the Nord town has neither); Aire/Thérouanne double plate settled (Aire stages the 3395x2614 spread,
    Thérouanne stages its own 986x867 'Terwan' plan). STILL PENDING the eye check: the Hesdin/Vieil-Hesdin
    double sheet + its 757x857 twin, Luxembourg City's 'Luxemburg 1550 65 v Deventer.jpg', the five (1)/(2)
    pairs, one small Aire repro. TOWNS + lead doc NOT yet edited - next session records the picks (TOWNS
    entries, `--verify Beaumont` re-check, lead doc), then the following session does --chain/stage/--check/
    tests/--golden.
