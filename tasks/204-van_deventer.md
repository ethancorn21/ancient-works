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
(2026-10-11, iteration 46 - BE `--files` inventory DONE and every BE pick decided + eye-verified;
**no TOWNS/doc edits written yet** - the picks are fully analyzed below, the next agent just records them.
Working tree is clean (the driver committed iteration-45's work as 4d6dbf2). Tests: 38/38 green and
`--check` exit 0, both run this session BEFORE any edit (the suite grew from 33 via merged 802/803 tests).
Next step: write the 21 BE TOWNS edits below, the lead-doc BE section, the Mons PITFALLS entry, DECISIONS,
then `pytest -q` + `--check` + commit.)

**Done this session (verified by running):**
1. Sanity: `pytest -q` 38/38 (43 s); `fit/src_van_deventer.py --check` exit 0 (0 rows - staging still
   absent). Confirmed the BE QID table + lead-doc BE sections are committed in main (4d6dbf2).
2. BE inventory: `.venv/bin/python fit/src_van_deventer.py --files Ath Braine-le-Comte Bruges Brussels
   Chimay Chièvres Enghien Ghent Halle Kortrijk Lessines Leuze Mechelen Mons Ostend Saint-Ghislain
   Soignies Tournai Aarschot Oudenaarde > /tmp/vd_files_be_iter46.txt` (212 lines, exit 0, ~2 min):
   the 1545 BNE atlas plates in the town cats for Ath, Braine-le-Comte, Chimay, Chièvres, Enghien, Ghent
   (BN 1 + BN 2), Halle, Kortrijk, Lessines, Leuze, Mons ((1)+(2)), Ostend (png, ca.1562), Saint-Ghislain,
   Soignies, Tournai, Oudenaarde (Version Madrid); **not in BNE**: Bruges (7 files), Brussels (7), Mechelen
   (1), Aarschot (2) - exactly as the hand-over predicted.
3. Eye check of all 9 ambiguous candidates: downloaded 1200 px thumbs + full-size crops to
   /tmp/vd_be_thumbs/ (may be wiped; re-run snippet was inline - `commons.info` + `aw.UA` download; the
   `read` tool views images fine). Verified: Ghent BN 1 = the labelled 'Gande' sheet; BN 2 = a DIFFERENT
   unlabelled sheet (centre-cropped, no city label); Mons (2) = wide two-page sheet labelled 'Mons en
   Henault', (1) = portrait plate of the same fortified town; Brussels '(2) 01.png' (8908x10941) = the KBR
   autograph cleanly cropped, '(2).png' (9216x12288) = same sheet WITH a TIFFEN calibration strip, '(2) 02'
   = its detail; Bruges full map (2770x4659) has a caption block at the sheet's bottom reading
   "Brugge (West Flan...) ... en omgeving omstreeks den jare 1550. Plattegrond in kleuren. Originade
   Teckening..." - the sheet dates ITSELF c. 1550 (full-size crop /tmp/vd_be_thumbs/bruges_caption.png);
   Mechelen (3558x3305) = KBR autograph (desc: from the atlas KBR bought in 1866); Ostend (872x1255) =
   full BNE plate; Aarschot (5877x6291) = a genuine autograph (town labelled 'Aersfot' on the Dijle) but
   dated 1570.
4. **Aarschot = documented DROP (the one BE drop):** both files are dated 1570 (page dates; the jpg copy
   1278x1024 too). Cross-checked on the web: the nl.wikipedia article 'Jacob van Deventer (cartograaf)'
   work list says "Aarschot, 1570" (Philip II period, after the c. 1545-1565 window; its bibliography's
   Rutte & Vannieuwenhuyze Stedenatlas spans 1545-1575 overall, but this task's window is 1545-1565 and box
   6 checks row dates in that window, so a 1570 row cannot be staged). Documented drop, no site, no picture.
   The same work list cross-confirms the other picks' dates: Gent 1545, Mechelen 1550, Doornik 1545,
   Brussel 1550 (westelijk gedeelte = the Molenbeek.1550.jpg partial, dropped), Den Haag 1558, Utrecht
   1565-1570, Oudenaarde minuut 1563 / netkaart 1564.

**The 20 BE picks (record these in TOWNS next session - file/ are exact Commons titles):**
- BNE 1545 plates (page date 1545 = drawing date, NO date= swap needed): Ath `File:Ath - Deventer.jpg`
  (3438x2614); Braine-le-Comte `File:Braine-le-Comte - Deventer.jpg`; Chimay `File:Chimay - Deventer.jpg`;
  Chièvres `File:Chièvres - Deventer.jpg`; Enghien `File:Enghien - Deventer.jpg`; Ghent
  `File:Ghent by Jacob Van Deventer, BN 1.jpg` (4919x5046, the 'Gande' sheet - BN 2 not staged: different
  unlabelled sheet; also not staged: the 1559 Donato Buoni print and five small 2007-2012 scans); Halle
  `File:Halle - Deventer.jpg` (desc is the French 'Hal'); Kortrijk `File:Kortrijk, map by Jacob van
  Deventer.JPG`; Lessines `File:Lessines - Deventer.jpg`; Leuze `File:Leuze - Deventer.jpg` +
  **caption="Leuze"** (label 'Leuze-en-Hainaut' is not in the title/desc - without caption= the caption
  route would fail); Mons `File:Mons (2) - Deventer.jpg` (4393x2614, the labelled two-pager - (1) is a
  portrait plate of the same fortified town); Saint-Ghislain `File:Saint-Ghislain - Deventer.jpg`;
  Soignies `File:Soignies - Deventer.jpg` (the two 2011 'd'apres'/tiny copies not staged); Tournai
  `File:Tournai - Deventer.jpg`; Oudenaarde `File:Oudenaarde, map by Jacob van Deventer, Version Madrid.JPG`
  (3368x2614, page 1545 - keep the page date; the work list dates the netkaart 1564, note it; the detail +
  DI-676 + Version Brussels copies not staged).
- Ostend `File:Oostende map Jacob van Deventer.png` (872x1255, page 'circa 1562' = drawing date, no swap):
  the ONLY Ostend plan and a full BNE plate - staged against the <~1000 px width heuristic (Aardenburg
  case), caveat in the lead doc.
- Mechelen `File:Mechelen, Belgium, Deventer, 1550.png` (3558x3305, page 1550, KBR autograph).
- Brussels `File:Brussels map by Jacob van Deventer, Atlas des villes des Pays-Bas, 73 places levées, ca.
  1555 (2) 01.png` (8908x10941, page 'circa 1555' = drawing date, no swap): the KBR autograph cleanly
  cropped. NOT staged: (2).png (same sheet + TIFFEN strip), (2) 02 (detail), Brussel 1550 v Deventer¹.JPG
  (470x561), Brussel 1555 Deventer.jpg (600x752), Brussel 1560 v Deventer.jpg (1233x1479, the 'minuut'),
  Molenbeek.1550.jpg (378x565, Molenbeek + west of the 2e enceinte - partial, the work list's 'Brussel
  1550 (westelijk gedeelte)').
- Bruges `File:Map of Bruges by Jacob van Deventer.jpg` (2770x4659) + **date="circa 1550"** (the sheet's own
  caption block 'omstreeks den jare 1550'; the page date 2013-01-17 12:04:47 is an upload timestamp -> the
  stage() swap keeps it as date_commons). The three category detail files carry QS 'circa 1558' - the
  sheet's own caption wins (note this in the lead doc). NOT staged: the 5 detail crops (846x522, 1180x668
  x2, 573x564, 650x832) and `Plan Brugge Jacob van Deventer ca.1560.jpg` (1400x1867, published reproduction
  per C. Ruelen).
- Aarschot: **note= drop** (no file=): text above (1570, both files, work list, window).

**Exact next step (one session):**
1. fit/src_van_deventer.py: extend the Belgium section-header comment (line ~166) to say the picks were
   recorded 2026-10-11 (iter 46) from the --files inventory + thumb eye check; add `file=` to the 19 staged
   entries + `date="circa 1550"` (Bruges) + `caption="Leuze"` + `note=` (Aarschot), per the pick list
   above. **Watch the PITFALLS rule: a trailing comment after `)` inside the unbalanced `{...}` display
   glues the next line onto the logical line - put comments INSIDE the dict parentheses or after the
   closing `),`, and keep every entry's comma.** Verify: `.venv/bin/python fit/src_van_deventer.py --check`
   (parses the module, exit 0) and `pytest -q` (expect 38/38).
2. docs/lead_van_deventer.md: replace '### Belgium, France, Luxembourg (pending)' (line ~252) with
   '### Belgium (20 categories: 19 staged, 1 documented drop; checked 2026-10-11, `--files` transcript
   /tmp/vd_files_be_iter46.txt - re-run: .venv/bin/python fit/src_van_deventer.py --files <towns>)' + one
   bullet per town (staged file with size/date + every not-staged file named with its specific reason,
   using the pick list above) + '### France, Luxembourg (pending)' (24 towns; the old pending text
   '44 towns left' moves there, corrected to 24). Update the '## Summary' paragraph (line ~281): BE 19 of
   20 staged, 1 documented drop (Aarschot); running total 32 of 59 stageable (NL 13 + BE 19); FR 23 + LU 1
   pending. Note in the Aarschot bullet the nl.wikipedia source (article 'Jacob van Deventer
   (cartograaf)', work list 'Aarschot, 1570') and the Rutte & Vannieuwenhuyze Stedenatlas (1545-1575) for
   the window context.
3. PITFALLS.md, under '### Wikimedia APIs (Commons, Wikidata)': file the deferred Mons entry -
   wbsearchentities limit=5 truncation hides well-known short names: Mons (Belgium) Q83407 ranks 11th in
   the en search (the planetary term 'mons' + French communes Var/Hérault/Charente/Gard outrank it; 4th in
   the fr search) - when the item is not among the five, follow up at limit 20. Where: _search_candidates
   in fit/src_van_deventer.py + the Wikidata wbsearchentities API. Symptom: the town's item simply absent
   from the 5 candidates. (Also a small fact worth the same entry or a new one: a Commons API call with no
   User-Agent gets HTTP 403 - commons.get sets aw.UA; a raw urllib script must too.)
4. DECISIONS.md entry: 'BE file batch done - 19/20 picks recorded (16 BNE plates + KBR Brussels/Mechelen +
   caption-dated Bruges + BNE Ostend); Aarschot documented drop (1570, outside the c. 1545-1565 window -
   both files + the nl.wikipedia work list agree)'.
5. Commit: `git add -A && git commit -m "204: BE file picks recorded + lead-doc Belgium section; Aarschot
documented drop (1570, out of window)"`.
6. Then FR (23 towns; `--verify` the 23 first - QIDs still empty in TOWNS; BNE plates cover all; watch the
   double plates 'Aire-sur-la-Lys - Deventer.jpg' (Aire+Thérouanne) and 'Hesdin - Deventer.jpg' (Hesdin+
   Vieil-Hesdin): stage once under the true primary, note the second; Beaumont's region flips
   france->belgium if the Hainaut item wins) + Luxembourg City (search 'Luxembourg (city)', Q1564 expected,
   region 'luxembourg' - new region value). Then the one long run: `--chain <town>` per staged town (paste
   the printed JSON into TOWNS['chain']; towns whose picked file sits in a collection cat need
   filecat = that cat - check per town), `stage` (NOT dry), `--check`, write tests/test_src_van_deventer.py
   (pattern tests/test_src_artists.py: socket-blocking fixture, check_staged, subprocess
   `fit/evidence.py check --files ... --books <absent>`, golden sample via `--golden`, negative control;
   box-6 date rule: year_of of the row date in 1545-1565), `--golden`.

**Transcripts** (/tmp may be wiped - re-run): /tmp/vd_files_be_iter46.txt (this session's BE inventory,
212 lines); /tmp/vd_be_thumbs/ (the 11 thumb PNGs/JPGs + bruges_caption.png + ghent_bn2_center.jpg -
re-download with commons.info + aw.UA if needed); /tmp/vd_be_thumbs_iter46.py (the download snippet -
reusable). Iteration-45 transcripts (vd_verify_be*, vd_mons*) are gone if /tmp was cleaned - the lead-doc
'QID verification - Belgium' section carries all the results.

**Pitfalls:** the Mons limit-5 entry is STILL not filed (do it in step 3). The trailing-comment-joins-
lines entry (PITFALLS line ~112) applies to every TOWNS edit - comments inside the parentheses or after
the `),` only. The keep()/swap-order entry (pipeline/commons.py) is why Bruges gets date= (the 2013
upload timestamp would fail keep() otherwise). Team mode: agent c on 203a (fit/batch_us.py, data/db/
platefits, data/review, docs/batch_us.md, tests/test_batch_us.py, tests/golden/hand_fit_docs.sha256,
tasks/802-*, tasks/803-*) - untouched; agent c also on 802 (tools/gate_heldout.py, tests/test_gate.py) -
untouched. My Touches: fit/src_van_deventer.py, the 3 staging jsonl, docs/lead_van_deventer.md,
tests/test_src_van_deventer.py, plus this task file.
