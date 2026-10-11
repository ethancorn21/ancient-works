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
