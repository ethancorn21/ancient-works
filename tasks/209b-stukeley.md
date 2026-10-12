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

(2026-10-13, iteration 149, agent a - session 3. READ-ONLY: re-verified the whole
settled design against the current code; nothing written, working tree clean, no test
run this session (last measured suite state: 104 passed, 1 skipped, 0 failed,
iterations 146/147 - re-baseline when you start). The session-2 hand-over carries the
full verified row values and is preserved in git: `git show
62a0ae6:tasks/209b-stukeley.md`. NEXT SESSION = THE BUILD of the Commons leg, per the
order at the bottom of this section.)

**What session 3 established (all read-only, all re-verified against current code):**
1. The 4 "PITFALLS to file" from session 2 are ALL ALREADY IN PITFALLS.md - no filings
   needed: line 217 (HathiTrust/Google Books refuse this VM), line 591 (upload.wikimedia.
   org rate-limits raw FILE downloads separately from the API - it even cites 209b's own
   /tmp/agent-a-209b/dl2.py), line 762 (fit/src_*.py CLI sys.path insert), line 951 (the
   3-point in-process wrap; it ends by noting a book that IS on IA (209b's Stukeley)
   needs no wrap: register() only adds the BOOKS entry). Session-2 step 1 is DONE.
2. `.gitignore` has `data/raw/` - so data/raw/books/<ia>/{bookreader.json,metadata.json}
   are LOCAL CACHE ONLY, not in the repo. The session-2 --status test plan assumed the
   cached bookreader.json is available in a fresh checkout: it is NOT. FIX: the test
   must fabricate a tiny stand-in cache by `monkeypatch.setattr(books_ia, "RAW",
   str(tmp_path / "books"))` + writing `<tmp>/books/<IA>/bookreader.json` in the shape
   books_ia.pages() reads: `{"data": {"brOptions": {"data": [[{page}, ...]]}}}` where
   each page is `{"leafNum": k+1, "width": w, "height": h, "uri": ""}` (pages() flattens
   the spreads and assigns n itself). Assert the printed leaf count; monkeypatch
   books.llm_up to False (the no_network socket fixture guards the rest).
3. `data/books/lists/` and `data/books/triage/` ARE git-tracked (other books'
   .json/.map.json and A-F jsonl are committed) - the per-book artifacts the IA-leg
   sessions write WILL be committed; only the raw page images stay out (gitignored).
4. books_lists imports numpy + PIL at module top (venv-only) - it stays a lazy import
   inside functions; the module top stays stdlib-only (the kip/hoare/mackenzie idiom).
5. Design refinements superseding the session-2 wording where they conflict:
   a. STAGED rows are 8-tuples (title, sid, named, want, label, kind, w, h) so stage()
      asserts the live (w,h) against the table and fails loud on a replaced file.
   b. The canonical guard is TITLE-only (stronger than Kip's (site,title)): any title
      already in data/commons/files.jsonl fails loud - this is what rejects the two
      Petrie 1880 titles (files.jsonl rows 713/714) whatever site a rogue row names.
   c. Test isolation: register() mutates books.BOOKS (a module dict) - the test must
      use `monkeypatch.setitem(books.BOOKS, src.KEY, ...)` so teardown removes the key
      (hoare's test does a bare assignment and leaks; do NOT copy that). Same for
      books_lists.PLATES when testing the STUKLEY_PLATES injection path.
   d. The test's fake-meta table uses the session-2 live values verbatim (Houghton:
      date '1743', desc starts 'Illustration labeled "A Scenographic view of the Druid
      temple of Abury...'; Dessin: date '1722', desc 'Stonehenge Dessin Stukeley 1722.';
      kitscoty: date '' desc '' -> the only row taking the Kip/Mackenzie date override
      date='1722', date_commons=''). commons.info() is the only live call in stage()
      (one batched 3-title metadata call, paced - safe per PITFALLS 591; file BYTES are
      never fetched).
   e. Cite: metadata.json has title/date/creator ALL None, so CITE stays hand-written
      'William Stukeley, Stonehenge, a Temple Restor'd to the British Druids, London
      1740'; confirm the exact printed title from the hOCR title page when --list runs
      (IA leg session) and correct CITE if it differs.

**Build order (one session - the Commons leg; run everything under .venv/bin/python):**
1. Re-baseline the suite (`.venv/bin/python -m pytest`, ~3 min) - background it while
   you write the module.
2. Write fit/src_wiltshire_stukeley.py = the session-2 design (git show
   62a0ae6:tasks/209b-stukeley.md, section "The settled design") with refinements 5a-d:
   header doc with usage; ROOT + sys.path.insert(<root>/pipeline) at top; KEY=
   "stukeley_templerestored1740", IA="bim_eighteenth-century_stonehenge-a-temple-rest_
   stukeley-william_1740", REGION="Europe", YEAR=1740, hand-written CITE/WHY; FILES_B/
   CLASSIFIED_B = data/commons/{files,classified}_wiltshire_b.jsonl (currently ABSENT -
   staging creates them); FILES_CANONICAL = data/commons/files.jsonl; SITES constants
   (avebury-q661855: Q661855 'Avebury' -1.854167,51.428611; stonehenge-q39671: Q39671
   'Stonehenge' -1.826111,51.178889; kit-s-coty-house-q4222497: Q4222497 "Kit's Coty
   House" 0.50261,51.32 - all in data/catalog/sites.jsonl, cross-checked against the
   catalog at stage time, drift fails loud); STUKLEY_PLATES = None + TODO comment
   (the --list session fills it; when set, register() also injects
   books_lists.PLATES[IA] = STUKLEY_PLATES in-process - 217 owns books_lists.py, the
   in-process injection is the civitates/217 pattern cmd_ocrmap's comment points to);
   register() = BOOKS entry ONLY, no wrap (the book really is on IA); --fetch ->
   books.cmd_fetch([KEY]) unmodified; --status offline (leaf count + triage progress
   from the cached bookreader.json, llm_up ports); --triage A|F|B -> books.
   cmd_triage_{a,f,b}([KEY]) unmodified; --list = if STUKLEY_PLATES is None:
   books_ia.page_texts(IA) (downloads + caches the ~165 KB hOCR pair) and print the
   first ~20 leaves' text for transcription; if set: register() then
   books_lists.cmd_ocrmap([KEY]) -> writes ONLY per-book lists/<ia>.json +
   lists/<ia>.map.json (map [] until stage A exists - cmd_ocrmap already guards);
   --stage [--dry] the 3 Commons rows (live re-verify per 5d; the 8-tuple guards);
   --check offline (join: every row names a catalog/web site, (site,title) unique, no
   canonical-title clash, classified 1:1) + evidence.check(FILES_B, data/books/
   .no-books) expecting 3 PASS exit 0; --golden -> tests/golden/
   src_wiltshire_stukeley_sample.json = all 3 file rows + classified, Kip's _norm
   (checked='0000-00-00', date_commons='0000-00-00'), sort_keys, indent 1.
   STAGED (live-verified values from session 2):
     1. ("File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg",
        "avebury-q661855", "Abury", "1743", "Avebury, scenographic view by William
        Stukeley, 1743 (TAB. VIII of the 1743 second edition of Abury, a temple of
        the British druids)", "plan", 2269, 1362)
     2. ("File:Stonehenge Dessin Stukeley 1722 03547.jpg", "stonehenge-q39671",
        "Stonehenge", "1722", "Stonehenge, inward view by William Stukeley, 1722
        (Itinerarium Curiosum)", "view", 4620, 2430)
     3. ("File:Stukelykitscoty.jpg", "kit-s-coty-house-q4222497", "Kitscoty", "1722",
        "Kit's Coty House, pen drawing by William Stukeley, 1722 (Itinerarium,
        style-attributed - Commons has no date)", "view", 1020, 320)
   The kitscoty 1722 attribution nuance belongs in docs/lead_wiltshire.md (already
   there), not on the row beyond date=1722.
3. Run --stage (live, ONE paced batched metadata call) -> creates the two staging
   files with 3 rows each; then --check (must print 3 PASS, no 'join:' lines, exit 0)
   and --golden.
4. Write tests/test_src_wiltshire_stukeley.py (no_network socket-blocking fixture as
   in tests/test_src_kip.py; NO LLM calls): (a) stage() on a TEMP tree (monkeypatch
   FILES_B/CLASSIFIED_B to tmp paths; monkeypatch commons.info to the fake-meta table
   of 5d): both files written, second run idempotent no-op, kitscoty row date='1722' +
   date_commons='' while the other two have no date_commons key, evidence.check passes
   offline on all 3; (b) a Petrie-title row (e.g. "File:47 of 'Stonehenge- plans,
   descriptions and theories' (11135894643).jpg" - in the real canonical files.jsonl)
   in a monkeypatched STAGED raises SystemExit naming the canonical clash; (c) --check
   against the REAL committed staging files (read-only): 3 rows, all sites existing,
   "evidence: 3 rows, 3 pass, 0 fail, 0 no-tie"; (d) golden() to a temp path == the
   committed sample (after _norm); (e) register(): BOOKS entry present with the exact
   dict, books_ia.pages is UNMODIFIED (no wrap - the key difference from hoare's
   test), books_lists.PLATES untouched while STUKLEY_PLATES is None (setitem per 5c);
   (f) --status offline per fact 2 (fabricated cache, llm_up monkeypatched False).
5. Run the full suite (.venv/bin/python -m pytest); must be green (any red unrelated
   to 209b's files: verify it fails without your changes too, record in DECISIONS,
   leave it - the driver re-checks on merge).
6. docs/lead_wiltshire.md Stukeley section: add one line - "the module is built
   (iteration 149); the 3 Commons rows are staged in data/commons/
   files_wiltshire_b.jsonl and pass fit/evidence.py 3/3 (golden: tests/golden/
   src_wiltshire_stukeley_sample.json)"; keep the Stage-A/B recall line PENDING (IA
   leg). Commit (one commit for module+staging+golden+tests+doc is fine; message:
   "209b: Commons leg built - 3 Stukeley rows staged, checked 3/3, golden + tests").

**Next session after that (the IA book leg; needs live LLM replicas - books.LLM_URLS
ports 8080,8081,8082,18080,18081):** --fetch (166 triage pages, resumable - foreground
with a generous timeout or nohup; fetch_triage is idempotent), --triage A, --list
(read the front leaves, transcribe the printed plate list into STUKLEY_PLATES in the
module - format `plate|sub|title|page|kind` like books_lists PLATES; commit), re-run
--list (writes lists/<ia>.json + .map.json), --triage F/B on the flagged pages, then
stage the IA-book rows into the SAME files_wiltshire_b (evidence = the book's printed
list entry naming the place; date 1740; sites: stonehenge-q39671 for the Stonehenge
plan + Avenue plan; the Wiltshire map - check what it shows: if it maps a whole
region, record it in the lead doc instead of staging it), record the Stage-A/B
recall in the lead doc, extend --check/--golden/tests for the book rows, re-run the
suite.

**Do not:** write the shared data/books/index.jsonl / validation.json (211 rebuilds
them); re-stage the two Petrie files (canonical, files.jsonl rows 713/714) or any
hand fit (Allcroft Avebury fig. 187, Allcroft Windmill Hill fig. 186 in
data/db/platefits/); edit pipeline/ or other tasks' files; git merge/rebase/reset/
stash/branch-switch; run tests with bare python3. If the human later delivers
*A survey of Wilts* (1740), it is added to THIS task as a second local-copy book
(the 209a wrap pattern).
