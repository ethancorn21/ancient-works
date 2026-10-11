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
(2026-10-11, iteration 47 - **BE file picks RECORDED and everything about BE is done**: 19 `file=` entries
+ Bruges `date="circa 1550"` + Leuze `caption="Leuze"` + Aarschot `note=` drop, all in TOWNS; lead-doc
Belgium section written; Mons limit-5 + 403/User-Agent pitfalls filed; DECISIONS appended. Working tree
clean after this session's commit. Tests 38/38 green, `--check` exit 0, both run this session AFTER the
edit. NEXT SESSION: the FR batch (23 towns), then Luxembourg City, then the one long run
(--chain, stage, test, golden).)

**State of the table now (re-verify with a one-liner importing the module if in doubt):**
- TOWNS has 70 towns: NL 19 (13 staged + 3 drops + 3 done), BE 22 (19 staged + 1 drop Aarschot + 2 done),
  FR 24 (23 to verify + Bergues done), LU 1 (to verify). `stageable()` = 32 (NL 13 + BE 19) - checked by
  importing the module this session (with-file=19 BE, note-only Aarschot, date-swap Bruges, caption Leuze).
- Staging files (extras_/files_/classified_van_deventer.jsonl) DO NOT EXIST yet: `stage` runs only after
  FR + LU are recorded (one long run, see below). `--check` is green with 0 rows until then.
- All BE QIDs verified (iter 45; the re-check transcripts are gone but the full results are in the lead-doc
  'QID verification - Belgium' section). No BE QID is in the built catalog (12575-site check of 2026-10-11)
  - all 20 get new catalog entries. FR QIDs are still EMPTY in TOWNS; LU QID empty.

**Exact next step (one session - the FR batch):**
1. `.venv/bin/python fit/src_van_deventer.py --verify Aire-sur-la-Lys Arras Avesnes-sur-Helpe Bapaume Bavay
   Beaumont Bouchain Béthune Cambrai Condé-sur-l'Escaut Douai Gravelines Hesdin Landrecies Le
   Cateau-Cambrésis Le Quesnoy Le Rœulx Lille Maubeuge Saint-Omer Thérouanne Valenciennes Vieil-Hesdin >
   /tmp/vd_verify_fr.txt` (23 towns; discovery mode prints the 5-candidate fact sheets; watch the Mons-class
   truncation - a town absent from its 5 candidates needs a limit-20 follow-up, PITFALLS). Record qid/label/
   lon/lat/p625/place/wikipedia/p373 per town into TOWNS (site point = the old-town centre the plan is
   centred on; BE used the P625 rounded because no offset showed - judge per town, Gouda-style offsets are
   the class to watch). **Beaumont's region flips france->belgium if the Hainaut item wins** (the lead doc's
   pending section says so). Then a re-verify run (listing the 23) and record the per-town P625->site
   distances in the lead-doc table.
2. `.venv/bin/python fit/src_van_deventer.py --files <the 23 FR towns>` > /tmp/vd_files_fr.txt: the 1545 BNE
   atlas plates cover ALL 23 (collections section of the lead doc). They sit in the town categories as
   `<Town> - Deventer.jpg`, EXCEPT the two double plates (one file, two towns - stage ONCE under the true
   primary, note the second): `Aire-sur-la-Lys - Deventer.jpg` (3395x2614) is "Aire-sur-la-Lys &
   Thérouanne"; `Hesdin - Deventer.jpg` (3408x2614) is "Hesdin & Vieil-Hesdin" (French desc, odd date field:
   Hesdin 1554-1575, Vieil-Hesdin "probablement 1545"). Eye-check the two thumbnails (commons.info + aw.UA
   download, then the `read` tool views images - the iter-46 pattern, /tmp/vd_be_thumbs/ may be wiped) to
   pick the primary (the town whose old town the sheet is centred on); the second town gets its own row
   ONLY if a full plan of its own exists (else a documented note - decide from the evidence and record the
   reasoning; do not guess). Also (1)/(2) pairs exist (Arras, Douai, Lille, Saint-Omer, Valenciennes): same
   plate in two crops/sizes - pick the better one (the BE Mons (2) pattern: the labelled wide sheet).
   Page date 1545 = the drawing's date (no date= swap) unless a file's page date is an upload timestamp
   (then date= the known drawing date - the Bruges pattern, stage() keeps the page value as date_commons).
3. **Luxembourg City**: `--verify Luxembourg City` (the entry has `search="Luxembourg (city)"`), expect
   Q1564; record the facts. Its category is `Maps of Luxembourg City Jacob van Deventer` (no "by" - the one
   irregular title); get its file from the --files run (probably the Luxembourg National Library / KBR
   scan). region='luxembourg' is a NEW value build_catalog's REGION_NAME has no key for (display falls back
   to the raw value - acceptable, flagged in the lead doc). Q1564 is almost certainly not in the built
   catalog, but stage() reuses an existing site id automatically if it is (box 4).
4. Lead doc: write a '## QID verification - France, Luxembourg' section (same shape as the BE one: method,
   24-row table, traps - Beaumont's) and replace the '### France, Luxembourg (pending)' subsection under
   'Per town' with '### France (...)' + '### Luxembourg (...)' per-town bullets (copy the BE bullet
   format: staged file + size + date, every not-staged file named with its specific reason, drops with the
   full reasoning), and update the Summary (running total of staged; box 5 needs >= 50 of 60 or every
   missing one accounted for).
5. Commit: `204: FR+LU QID table recorded + file picks + lead-doc sections`.

**Then the one long run (following sessions):** for every staged town (NL 13 + BE 19 + FR + LU): `.venv/bin/
python fit/src_van_deventer.py --chain <town>` and paste the printed via list into `chain=` in TOWNS (the
category evidence route; via[-1] must be the town's p373). Towns whose picked file sits in a collection
category (not the town's own) need `cat` = that collection cat for the walk - check per town from the
--files transcript ([also in: ...] tags). A town whose chain walk fails goes to the caption route
(caption= in TOWNS) if the file names the town, else a documented drop. Then `stage` (NOT --dry; expect
"staged: 32+ new sites, 32+ new pictures" + the build list), `--check` (every staged row passes
evidence), write tests/test_src_van_deventer.py (pattern: tests/test_src_artists.py - a socket-blocking
no_network fixture, check_staged over the staged files, subprocess `fit/evidence.py check --files ...
--books <absent>`, a golden sample via --golden, a negative control; box-6 date rule: year_of of every
staged row's date in 1545-1565), then `--golden` to write tests/golden/src_van_deventer_sample.json.
Tests must not bind fixed network ports or write outside the project + temp dir (team mode). NOTE: `stage`
needs network (commons.info on every staged title) - run it live under .venv, never in a test.

**Pitfalls (all in PITFALLS.md):** (1) the trailing-comment-in-unbalanced-braces rule for EVERY TOWNS edit
- comments only INSIDE the dict parens or AFTER the closing `),` (a comment after `)` with a dropped comma
silently glues the next key onto the logical line; the SyntaxError lands lines below). (2) wbsearchentities
limit=5 misses well-known short names - follow up at limit 20 (filed this session). (3) raw Wikimedia API
calls need the aw.UA User-Agent or they 403 (filed this session). (4) the keep()/swap-order fact in the
pipeline/commons.py section: stage() swaps the known drawing date BEFORE keep() (the sources.py pattern) -
a post-1925 reproduction of a c. 1550 drawing passes judged on the drawing's year; a page date that is an
upload timestamp (the Bruges 2013 case) MUST be swapped or keep() drops it. Team mode: agent c on 203a
(fit/batch_us.py, data/db/platefits, data/review, docs/batch_us.md, tests/test_batch_us.py,
tests/golden/hand_fit_docs.sha256, tasks/802-*, tasks/803-*) and 802 (tools/gate_heldout.py,
tests/test_gate.py) - untouched. My Touches: fit/src_van_deventer.py, the 3 staging jsonl (created by
stage), docs/lead_van_deventer.md, tests/test_src_van_deventer.py,
tests/golden/src_van_deventer_sample.json, plus this task file. /tmp transcripts from iter 46
(vd_files_be_iter46.txt, vd_be_thumbs/) may be wiped; the lead doc carries all BE results.
