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

(2026-10-12, iteration 146, agent a - FIRST session. Re-baseline + full Commons visual
verification DONE; all memory files written; the module is NOT yet built. Next session:
file 4 PITFALLS entries, then build fit/src_wiltshire_stukeley.py.)

**State.**
- Suite last ran (this session, before any edits): **104 passed, 1 skipped, 0 failed**
  (182 s, `.venv/bin/python -m pytest`). The stale failures in the driver's 2026-10-11
  notes (test_gate/test_batch_eu/test_serve) are gone. No code has been written yet, so
  the baseline stands.
- **docs/lead_wiltshire.md**: the Stukeley section is WRITTEN (edited this session,
  uncommitted - the harness holds it): the full Commons verification table (266 category+
  subcat files scanned), the 3 rows to stage, the Oxford-model exclusion, the Petrie note
  (unblocks 209c), the 1743-vs-1740 Avebury-edition fact, and the pending Stage-A/B recall
  line.
- **DECISIONS.md**: two 209b entries appended this session (the Commons verification +
  staging decisions; the Petrie 1880 finding).
- **tasks/209c-petrie.md**: new `## Hand-over` written (the Petrie finding; both Flickr
  files = 1880 Pl. I/II and ALREADY canonical in files.jsonl rows 713/714 with
caption_coords + the BL Georeferencer desc; fallback (a) satisfied; if the human declines
  the 002 download, 209c must NOT re-stage them - the canonical rows are the Commons leg).
- **tasks/209-wiltshire.md** (parent): the Stukeley bullet in Per-book facts updated in
  place with the verification outcome.
- **PITFALLS.md: NOT yet edited** (I had just mapped the section structure when the limit
  hit). File these 4, one entry each, in this order:
  1. under `## This machine and its environment` (section ends ~line 216, before
     `## Libraries and frameworks`): the 209a-drafted fact (a) - *HathiTrust and Google
     Books refuse this VM - books not on IA need a human download (the 207c pattern)*
     (full text is in 209a's Hand-over, item under "PITFALLS entries drafted").
  2. under `### fit/` (section ~lines 582-747): drafted fact (b) - *a fit/src_*.py CLI
     that lazily imports pipeline modules needs its own sys.path insert at module top -
     tests hide it* (full text in 209a's Hand-over). When building the Stukeley module
     this session's next step, DO the sys.path insert at module top (copy from
     fit/src_mackenzie.py).
  3. under `### pipeline/books.py, pipeline/books_ia.py (the book machinery)` (~901-931):
     drafted fact (c) - *a human-downloaded book (not on IA) runs the UNMODIFIED machinery
     through a 3-point in-process wrap* (full text in 209a's Hand-over). Note for 209b:
     NOT needed here - the Stukeley book really is on IA.
  4. under `### Wikimedia APIs (Commons, Wikidata)` (~470-581, next to the existing
     API-429 entry): NEW from this session - *upload.wikimedia.org rate-limits raw FILE
     downloads separately from the API: 3 back-to-back full-file fetches 429'd on the 4th*
     (Where: any bulk Commons file download; Symptom: urllib HTTPError 429 "Too many
     requests (f061ab2)" after ~3 consecutive downloads even though the API calls were
     paced; Why: the CDN, not the API, owns the file-download limit; do: space downloads
     ~30+ s apart with backoff, as /tmp/agent-a-209b/dl2.py did).

**The Commons findings (verified, from the lead-doc table - re-read it):**
- STAGE 3 rows into data/commons/files_wiltshire_b.jsonl + classified_wiltshire_b.jsonl
  (all kind-verified by eye this session):
  1. `File:Houghton Arc 855.214 - Stukely, the Druid temple of Abury.jpg` (2269x1362) =
     Stukeley TAB. VIII p.14, the 1743 2nd-edition Avebury "Scenographic view... as in its
     original" -> **avebury-q661855** (coords -1.854167, 51.428611), kind **plan**
     (p_plan 1.0), date **1743** (the copy the scan comes from; first ed. 1740),
     evidence **caption_coords** named "Abury" (title+description spelling;
     `books_match.norm('Abury') in norm(title+' '+desc)` verified True in-process),
     place = Avebury's own coords, dist_m 0.0.
  2. `File:Stonehenge Dessin Stukeley 1722 03547.jpg` (4620x2430) = the 1722 Itinerarium
     "An inward view of Stonehenge Aug. 1722 from the north" -> **stonehenge-q39671**
     (-1.826111, 51.178889), kind **view** (p_birdseye 1.0), date 1722 (Commons metadata
     agrees), caption_coords named "Stonehenge" (title), dist 0.
  3. `File:Stukelykitscoty.jpg` (1020x320) = Stukeley's pen drawing of the Uffington scene
     ("The upper Kitts Cate house" barrow, "The Grave", Fedderham place) ->
     **kit-s-coty-house-q4222497** (0.50261, 51.32), kind **view**, date **1722**
     (STYLE attribution to his 1722 Itinerarium drawing set - Commons has NO date; record
     the attribution on the row's evidence-reason or the lead doc), caption_coords named
     "Kitscoty" (the filename's mangled spelling; `norm('Kitscoty')` = 'kitscoty' is a
     substring of norm('Stukelykitscoty.jpg') - verified True in-process), dist 0.
  - Row shape: mirror files_kip.jsonl exactly (site, qid, title, year, wd_plan false,
    cat null, name, by='fit/src_wiltshire_stukeley.py', url, thumb, w, h, mime, date,
    desc, artist, license, page, evidence); classified row {site, title, p_plan,
    p_birdseye, p_photo, by:'hand'}.
  - **commons.keep() trap for row 3**: no date in metadata AND no plan-word in the title
    -> keep() drops it. Use the Kip override: pass date=1722 (date_commons = the metadata
    value) to year_of/keep in stage() (the pattern is in fit/src_kip.py stage(), ~line
    560: `if want and c.year_of(title, m2) != ...: m2 = dict(m2, date=want,
    date_commons=m.get('date'))`).
- NOT staged (recorded in lead doc): `File:Stonehenge Stukley Oxford 03543.jpg` (a view of
  Stukeley's conjectural RESTORED model, Whistock's Oxford print; the Commons 1722 date is
  wrong for the print); the two Petrie Flickr files (already canonical); everything else
  in the category (too small, portraits, book pages, 1996 photo, non-catalog sites).

**The IA book leg (next session's main work):** ia=
bim_eighteenth-century_stonehenge-a-temple-rest_stukeley-william_1740 (*Stonehenge, a
Temple Restor'd to the British Druids*, 1740, BMB scan). metadata.json is already cached
in data/raw/books/<ia>/ (fetch it further if the session needs it). BookReader list =
**166 leaves** (n0-n165, leafNum == n, ~8657x13266) - verified this session. hOCR
(14.7 MB) + hocr_searchtext + hocr_pageindex + DjVuTXT + scandata all downloadable via
the standard pipeline/books_ia.py helpers. **No 209a-style local-copy wrap is needed** -
the book really is on IA, so books.cmd_fetch (IIIF re-encode to the triage slot),
books.run_stage (A/F/B) and books_lists run UNMODIFIED. The plates (Stukeley's numbered
Stonehenge plan, the Avenue plan, the Wiltshire map) tie to stonehenge-q39671. The book's
printed list of plates is transcribed from the hOCR searchtext (the books_lists PLATES
pattern) -> per-book lists/<id>.json + .map.json only.

**Exact next step (in order):**
1. File the 4 PITFALLS entries above (one edit each, exact placement given).
2. Build `fit/src_wiltshire_stukeley.py` (mirror fit/src_kip.py for the Commons leg;
   mirror fit/src_wiltshire_hoare.py's CLI shape for --fetch/--status/--triage, but the
   book leg delegates straight to books.cmd_fetch/books.run_stage - NO wrap; sys.path
   insert for pipeline/ at module top per PITFALLS (b)); register
   `books.BOOKS["stukeley_templerestored1740"]` (ia = the bim_... id, region Europe,
   year 1740, cite/why).
3. `--list`: transcribe the printed plate list from the hOCR searchtext (download it
   first: books_ia.page_texts needs hocr_pageindex + hocr_searchtext - ~165 KB total).
4. `--triage A` as a resumable nohup background job (check LLM ports 8080/8081/8082 first;
   8080/8081 were up last session) - 166 pages, short book, a few minutes to ~30.
5. `--triage F`/`B` on the plan leaves; `--stage` (the IA book rows: evidence = the
   book's printed list entry names the place - the 200 evidence field per row, date 1740;
   plus the 3 Commons rows above) -> files_wiltshire_b.jsonl + classified_wiltshire_b.jsonl;
   `--check` (offline join + fit/evidence.py over the files); `--golden`
   (tests/golden/src_wiltshire_stukeley_sample.json - a sample covering one evidence
   flavour per row type: the caption_coords Commons rows + a book-list row).
6. tests/test_src_wiltshire_stukeley.py (hermetic, the no_network socket-blocking fixture
   as in tests/test_src_kip.py; no LLM; monkeypatch the book DIR for fetch-path tests;
   staging/check tests offline against the real data files read-only or a temp tree).
7. Record the Stage-A/B recall numbers in the Stukeley section of docs/lead_wiltshire.md
   (its last line) and run the full suite.

**Do not:** write the shared data/books/index.jsonl / validation.json (211 rebuilds);
re-stage the two Petrie files (canonical) or any hand fit (Allcroft Avebury fig. 187,
Allcroft Windmill Hill fig. 186 in data/db/platefits/); edit pipeline/ or other tasks'
files; git merge/rebase/reset/stash/branch-switch; run tests with bare python3 (use
`.venv/bin/python -m pytest`). If the human later delivers *A survey of Wilts* (1740), it
is added to THIS task as a second local-copy book (the 209a wrap pattern).
