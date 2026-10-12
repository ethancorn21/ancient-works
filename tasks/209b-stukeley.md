Status: in-progress
# 209b: Stukeley (1740s) - the Temple Restor'd scan on IA + his Commons plates
Depends on: 200
Touches: fit/src_wiltshire_stukeley.py, data/books/triage/, data/books/lists/, data/commons/files_wiltshire_b.jsonl, data/commons/classified_wiltshire_b.jsonl, docs/lead_wiltshire.md, tests/test_src_wiltshire_stukeley.py, tests/golden/src_wiltshire_stukeley_sample.json

## Goal
Subtask of 209 (the parent's Hand-over has the full mechanics - read it): get Stukeley's
drawings of the Wiltshire sites onto the map. Two legs, both from sources reachable from this
VM: (1) the complete British Museum scan of *Stonehenge, a Temple Restor'd to the British
Druids* (1740), ia=`bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740`
(BookReader pages + hOCR verified 2026-10-13), indexed with the standard book machinery -
its plates (Stukeley's numbered Stonehenge plan, the Avenue plan, the Wiltshire map) tie to
stonehenge-q39671; (2) the Commons-hosted Stukeley plates (the 205-Kip pattern, no book
machinery) - first the 1740 Avebury plan `File:Houghton Arc 855.214 - Stukely, the Druid
temple of Abury.jpg` (2269x1362, visually verify first - it has no description metadata),
then every other fit-sized (>= 1000 px) Stukeley plate in `Category:William Stukeley` that
shows a catalog site. If the human also delivers *A survey of Wilts* (1740, the true
Wiltshire volume - see the open ask_human in 209a/209c), it is added here as a second
local-copy book.

## Acceptance criteria
- [ ] The BMB 1740 scan is fetched from IA (data/raw/books/bim_eighteenth-century_stonehenge-
      a-temple-rest_stukeley-william_1740/) and triaged with the existing machinery, per-book
      artifacts only (triage/<ia>.*.jsonl, lists/<ia>.json, lists/<ia>.map.json); the shared
      data/books/index.jsonl and validation.json are NOT written.
- [ ] The book's printed plate list is transcribed (the books_lists PLATES pattern, from the
      hOCR; the book is short - check the leaf count from scandata first) and mapped to
      leaves; the stage-A/B recall against that list is recorded in the Stukeley section of
      docs/lead_wiltshire.md (instead of the shared validation.json).
- [ ] Staged rows (appended to the shared-per-suffix staging files, rows tagged with this
      book): files_wiltshire_b.jsonl for every verified site-plan plate - the IA book's
      Stonehenge/Avenue plans (site stonehenge-q39671) and the Commons plates (the 1740
      Avebury plan -> avebury-q661855; the 1722 Stonehenge drawing and any other fit-sized
      verified Stukeley plate -> its site) - each with the 200 evidence field (the book's
      printed list entry for the IA rows; for the Commons rows the hand verification or the
      caption names the place - the specific check recorded on the row) and a classified row
      by hand ("plan"); the work's date (1740/1722) is recorded on the row.
- [ ] The existing hand fits are NOT re-staged or re-fitted (the Allcroft fig. 187 Avebury
      fit in data/db/platefits/avebury-q661855.earthworkenglan01allcgoog_n0581_1.json, the
      Allcroft Windmill Hill fit): new rows only.
- [ ] fit/evidence.py check passes offline on every staged row. At least 90% of the verified
      site-plan pages/plates are staged, or each missing one is accounted for in
      docs/lead_wiltshire.md.
- [ ] Test (no network): the staged files join (every row names an existing or staged site)
      and the evidence check passes; a golden sample of rows
      (tests/golden/src_wiltshire_stukeley_sample.json).

## Notes
- First session: re-baseline the test suite, then VISUALLY verify the Commons candidates by
  downloading them (Commons API `url` field) and looking at them: the Houghton Avebury plan
  (expect Stukeley's 1740 plan of the circle with numbered stones and the Longstones),
  `File:Stonehenge Dessin Stukeley 1722 03547.jpg` (4620x2430, expect the 1722 Itinerarium
  drawing), `File:Stonehenge Stukley Oxford 03543.jpg` (3606x2976, source unverified -
  identify it), and the two unlabeled Flickr files
  `File:47 of 'Stonehenge- plans, descriptions and theories' (11135894643).jpg`
  (2245x2852) / `File:49 of '...' (11133409654).jpg` (4641x2874) - if either is the Petrie
  1880 plan, that finding unblocks 209c (tell the 209c agent / the driver) and the file is
  NOT staged here. Everything else in Category:William Stukeley is <1000 px (too small) or
  not a site drawing (the Clarendon palace ruins 1723 is Roman/medieval - check whether it is
  a catalog site before any staging).
- The Commons leg needs no LLM; only the IA book leg uses the triage stages (ports per the
  parent's mechanics; the book is short, so no long background job expected).
- LLM calls never run in tests (the no_network socket-blocking fixture as in
  tests/test_src_kip.py).

## Hand-over

(2026-10-13, iteration 147, agent a - session 2. Investigation only: the 3 Commons rows
are LIVE-VERIFIED down to the last metadata field (exact values below), the module design
is settled, NOTHING is written yet (no PITFALLS entries, no module, no tests, no staging
files). Context limit hit right after the live-metadata check. Next session: file the 4
PITFALLS entries, then build fit/src_wiltshire_stukeley.py exactly as designed below.)

**What this session did (all read-only + one paced live read):**
- Re-read all memory files; the driver committed iteration 146's work (702ee04), so the
  working tree is CLEAN - docs/lead_wiltshire.md (full Stukeley section incl. the
  verification table), DECISIONS entries and 209c's hand-over are all in git now.
- Read the whole relevant code: pipeline/books.py (BOOKS, cmd_fetch, run_stage,
  triage_path, llm_up), pipeline/books_ia.py (cached/get/pages/page_texts/full_url),
  pipeline/books_lists.py (PLATES, parse_plates, map_plates, cmd_ocrmap, list_pages),
  pipeline/commons.py (year_of, keep, info, NO/PLANWORD), fit/evidence.py (check,
  check_caption, check_book), fit/src_kip.py (the Commons-leg pattern: INVENTORY/STAGED/
  evidence_for/stage/check/golden), fit/src_wiltshire_hoare.py (CLI shape, register wrap,
  sys.path insert), fit/src_mackenzie.py (the date-override idiom),
  tests/test_src_wiltshire_hoare.py (the no_network fixture + monkeypatch DIR pattern).
- **Live-verified the 3 Commons rows** (`.venv/bin/python`, commons.info, paced - all
  values below are current): every check the staging decision needs passed in-process:
  1. `File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg`: 2269x1362
     jpeg; date='1743' (the METADATA date is already the plate's year - NO override
     needed, no date_commons); artist='William Stukeley (author)'; license='Public
     domain'; desc starts 'Illustration labeled "A Scenographic view of the Druid
     temple of Abury in north Wiltshire as in its original". From Abury, a temple of
     the British druids, and some others described (London: 1743)...'; year_of=1743,
     keep=True; norm('Abury') in norm(title+desc)=True.
  2. `File:Stonehenge Dessin Stukeley 1722 03547.jpg`: 4620x2430 jpeg; date='1722';
     artist='G.Garitan'; license='CC BY-SA 3.0'; desc='Stonehenge Dessin Stukeley 1722.';
     year_of=1722, keep=True; norm('Stonehenge') in norm(title)=True.
  3. `File:Stukelykitscoty.jpg`: 1020x320 jpeg; date='' desc='' artist='';
     license='Public domain'; year_of=None, **keep=False** (the trap: no date and no
     plan-word in the title) -> the Kip/Mackenzie override applies: want='1722' makes
     stage() set date='1722', date_commons='' (verified: year_of(title,{date:'1722'})=
     1722 and keep() then True; norm('Kitscoty')='kitscoty' is a substring of
     norm('Stukelykitscoty.jpg')=True). Its thumburl is the ORIGINAL url (unscaled).
  - All three: `page` = the commons.wikimedia.org File: page; `url`/`thumb` are the
    upload/ thumb.wikimedia.org URLs (utm params included in the returned values -
    stored as returned, as Kip does).
- **Catalog sites confirmed** in data/catalog/sites.jsonl: stonehenge-q39671
  (Q39671 'Stonehenge' -1.826111,51.178889), avebury-q661855 (Q661855 'Avebury'
  -1.854167,51.428611), kit-s-coty-house-q4222497 (Q4222497 'Kit's Coty House'
  0.50261,51.32, aliases incl. 'Kitts Coty House'). All three exist -> NO extras file
  needed, NO new site rows; the join check is 'every row names an existing catalog
  site'.
- **Book facts:** data/raw/books/<ia>/ has only bookreader.json (166 leaves) +
  metadata.json cached; metadata.json has title/date/creator ALL None (write CITE by
  hand: 'William Stukeley, Stonehenge, a Temple Restor'd to the British Druids,
  London 1740' - confirm the exact printed title from the hOCR title page when --list
  runs). hocr_pageindex.json.gz = 1953 B, hocr_searchtext.txt.gz = 163953 B (the ~165 KB
  --list download), _djvu.txt 404 KB, _hocr.html 14.7 MB, scandata + page_numbers.json
  present. /home/agent has 13 GB free (the triage tree is ~166 x ~400 KB, no pressure).

**The settled design for fit/src_wiltshire_stukeley.py (write it this next session):**
- Header doc (usage, per the hoare/kip style). Module top: `sys.path.insert(0,
  os.path.join(ROOT, "pipeline"))` (PITFALLS b). stdlib-only at top; books/books_ia/
  books_lists/commons import lazily inside functions (the venv-only pattern).
- Constants: KEY="stukeley_templerestored1740", IA="bim_eighteenth-century_stonehenge-
  a-temple-rest_stukeley-william_1740", REGION="Europe", YEAR=1740, CITE, WHY; FILES_B =
  data/commons/files_wiltshire_b.jsonl, CLASSIFIED_B = data/commons/classified_
  wiltshire_b.jsonl (both currently ABSENT - staging creates them), FILES_CANONICAL,
  SITES_JSONL, NO_BOOKS = data/books/.no-books, LISTS dir = data/books/lists/
- `register()`: just `books.BOOKS[KEY] = dict(ia=IA, region=REGION, year=YEAR, cite=
  CITE, why=WHY)` - **NO wrap** (the book really is on IA; contrast hoare). Idempotent.
  If STUKLEY_PLATES (module constant, the transcribed list text, None until the --list
  session) is set, also `books_lists.PLATES[IA] = STUKLEY_PLATES` in-process (I cannot
  edit pipeline/books_lists.py - 217 owns it; the in-process injection is the civitates/
  217 pattern cmd_ocrmap's comment points to).
- `--fetch` -> `books.cmd_fetch([KEY])` (unmodified: IIIF re-encode to
  ia.RAW/IA/triage/, resumable); `--status` -> offline: leaf count + first/last sizes
  from the cached bookreader.json, triage progress (count existing triage files),
  LLM ports via books.llm_up (it catches every exception -> returns False under the
  no_network fixture, so it is test-safe); `--triage A|F|B` -> books.cmd_triage_{a,f,b}
  ([KEY]) unmodified.
- `--list`: if STUKLEY_PLATES is None: `books_ia.page_texts(IA)` (downloads the ~165 KB
  pair) and print the first ~20 leaves' text so the next agent transcribes the printed
  plate list; if set: register() then `books_lists.cmd_ocrmap([KEY])` -> writes ONLY
  lists/<ia>.json + lists/<ia>.map.json (per-book; map stays [] until stage A runs -
  cmd_ocrmap already guards `if stage_a(ia_id) else {}`).
- `--stage [--dry]`: the Commons leg NOW (3 rows from a STAGED table exactly like
  Kip's: (title, site, named, want, name_label, kind)); the IA-book rows come in a LATER
  session once lists/<ia>.map.json + stage B exist (their evidence = the book's printed
  list entry naming the place; keep the table slot for them, e.g. a BOOK_PLATES list
  keyed by plate). stage(): live re-verify (c.info: url present, w/h match the table,
  named still a norm-substring of live title+desc; a title Commons no longer holds ->
  fail loud), the Kip date-override (only kitscoty triggers it: year_of None != 1722),
  `c.keep(title, m2)` must pass else fail loud, idempotent on (site,title) against both
  FILES_B and CLASSIFIED_B, NEVER accept a title already in canonical files.jsonl (the
  two Petrie titles must be rejected loudly - the 209c guard). Rows mirror files_kip.
  jsonl: {site, qid, title, year: c.year_of(title, m2), wd_plan: False, cat: None,
  name: <label>, by: 'fit/src_wiltshire_stukeley.py', **m2, evidence: evidence_for(...)};
  classified {site, title, p_plan, p_birdseye, p_photo, by: 'hand'} - row 1 kind plan
  (1.0,0,0), rows 2-3 kind view (0,1.0,0).
- evidence_for(named, site): {"rec":"evidence/1","kind":"caption_coords","checked":
  now(), "named_place": named, "place_qid": site qid, "place_label": site name,
  "place_lon/lat": the site's OWN catalog point, "site_lon/lat": same, "dist_m": 0.0}
  (Kip's shape; check_caption re-verifies offline: named a norm-substring of title+desc,
  dist reproduces, d<=50 km - all 3 verified True in-process this session).
  Site table: {"avebury-q661855": (Q661855,'Avebury',-1.854167,51.428611),
  "stonehenge-q39671": (Q39671,'Stonehenge',-1.826111,51.178889),
  "kit-s-coty-house-q4222497": (Q4222497,"Kit's Coty House",0.50261,51.32)} - take the
  values from the catalog at stage time where the join allows, but the handover's
  verified constants are the fallback for the evidence dict (Kip hard-codes its sites;
  check_staged re-reads the catalog so drift fails loud).
- `--check` (offline): join = every FILES_B row names an EXISTING site (sites.jsonl or
  web/data/sites.json - Kip's known_sites() pattern), (site,title) unique, not in
  canonical files.jsonl (esp. the two Petrie titles), classified 1:1; then
  `evidence.check(FILES_B, NO_BOOKS)` -> all 3 must PASS (no FAIL, exit code 0).
- `--golden`: tests/golden/src_wiltshire_stukeley_sample.json = all 3 staged rows +
  classified, Kip's _norm (checked='0000-00-00', date_commons='0000-00-00'), sort_keys,
  indent 1. One file covers all three flavours: named 'Abury' (desc-spelling),
  'Stonehenge' (title), 'Kitscoty' (mangled title, date-override row).
- STAGED table values (from the live check above):
  1. ("File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg",
     "avebury-q661855", "Abury", "1743", "Avebury, scenographic view by William
     Stukeley, 1743 (TAB. VIII of the 1743 second edition of Abury, a temple of the
     British druids)", plan)
  2. ("File:Stonehenge Dessin Stukeley 1722 03547.jpg", "stonehenge-q39671",
     "Stonehenge", "1722", "Stonehenge, inward view by William Stukeley, 1722
     (Itinerarium Curiosum)", view)
  3. ("File:Stukelykitscoty.jpg", "kit-s-coty-house-q4222497", "Kitscoty", "1722",
     "Kit's Coty House, pen drawing by William Stukeley, 1722 (Itinerarium, style-
     attributed - Commons has no date)", view)
  The 1722 attribution nuance on row 3 is recorded in docs/lead_wiltshire.md (it is
  already there), not on the row beyond date=1722.

**Exact next step (in order):**
1. File the 4 PITFALLS entries (text unchanged from the previous hand-over, restated in
   the driver-committed version above in git - see the superseded section via
   `git show ee87b17:tasks/209b-stukeley.md` if it has been trimmed: (a) HathiTrust/Google
   Books refuse this VM -> under '## This machine and its environment'; (b) fit/src_*.py
   sys.path insert -> under '### fit/'; (c) 209a's 3-point in-process wrap -> under
   '### pipeline/books.py, pipeline/books_ia.py (the book machinery)'; (d) NEW: upload.
   wikimedia.org rate-limits raw FILE downloads separately from the API - 3 back-to-back
   full-file fetches 429'd on the 4th (urllib HTTPError 429 'Too many requests
   (f061ab2)' despite paced API calls; space downloads ~30+ s apart with backoff) ->
   under '### Wikimedia APIs (Commons, Wikidata)'.
2. Write fit/src_wiltshire_stukeley.py per the design above (the STAGED table with the
   three rows; STUKLEY_PLATES = None placeholder with a TODO comment pointing at the
   --list session).
3. Run `--stage` (live, paced: 3 files of metadata) -> creates files_wiltshire_b.jsonl +
   classified_wiltshire_b.jsonl with the 3 rows; then `--check` (must print 3 PASS,
   exit 0) and `--golden`.
4. Write tests/test_src_wiltshire_stukeley.py (hermetic; read
   tests/test_src_kip.py first for the staging/golden test shape + the no_network
   socket-blocking fixture; no LLM calls): (a) stage() on a TEMP tree (monkeypatch
   FILES_B/CLASSIFIED_B + a fake commons.info/meta: writes both files, idempotent
   second run, the kitscoty row carries date='1722' + date_commons='' while the other
   two have no date_commons, every row's evidence passes evidence.check offline, a
   Petrie-title row is rejected loudly); (b) the join+evidence check against the REAL
   committed files (read-only) - 3 rows, all sites existing, 3 PASS; (c) golden
   determinism: golden() to a temp path == the committed sample (after _norm);
   (d) register() puts the BOOKS entry (no wrap: assert books_ia.pages is UNMODIFIED -
   a key difference from hoare's test); (e) --status runs offline under no_network
   (llm_up returns False gracefully, leaf count from the cached bookreader.json).
5. Run the full suite (`.venv/bin/python -m pytest`): baseline was **104 passed, 1
   skipped, 0 failed** (iteration 146; re-baseline the moment you start if the driver
   notes anything newer) - must stay green with your new tests added.
6. Update docs/lead_wiltshire.md's Stukeley section: 'the module is built (iteration
   148...), the 3 Commons rows staged + checked (evidence 3/3 PASS), golden written';
   keep the recall line pending.
7. THEN (next session, needs the LLM replicas): `--fetch` (166 triage pages, resumable;
   run in a foreground with a generous timeout or nohup - fetch_triage is idempotent),
   `--triage A` (check ports 8080/8081/8082 first; 8080/8081 were up on 2026-10-12),
   `--list` (read the front leaves, transcribe the printed plate list into
   STUKLEY_PLATES in the module, commit), re-run `--list` (writes lists/<ia>.json +
   .map.json), `--triage F/B` on the flagged pages, then the IA-book rows into the same
   files_wiltshire_b (evidence = the printed list entry; date 1740; sites:
   stonehenge-q39671 for the Stonehenge plan + Avenue plan; the Wiltshire map - check
   what it shows; if it maps a whole region, see whether it is stageable like a map or
   gets recorded in the lead doc instead), record the Stage-A/B recall in the lead
   doc, extend --check/--golden/tests for the book rows, re-run the suite.

**Do not:** write the shared data/books/index.jsonl / validation.json (211 rebuilds);
re-stage the two Petrie files (canonical, files.jsonl rows 713/714) or any hand fit
(Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186 in data/db/platefits/);
edit pipeline/ or other tasks' files; git merge/rebase/reset/stash/branch-switch;
run tests with bare python3. If the human later delivers *A survey of Wilts* (1740), it
is added to THIS task as a second local-copy book (the 209a wrap pattern).
