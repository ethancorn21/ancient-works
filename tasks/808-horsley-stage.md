Status: done
Depends on: 807
Touches: fit/src_roman_horsley.py, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl, docs/lead_roman.md

# 808: Horsley - stage the 17 site-plan rows into the shared roman staging files

## Goal
Build the module's --stage leg (documented in fit/src_roman_horsley.py's docstring but not yet
implemented): append the book's 17 verified site-plan rows - one per kind-s leaf of 807's
corrected 24-entry list (the 15 wall maps, n0114, n0185) - to the parent's shared roman
staging files (data/commons/files_roman.jsonl + classified_roman.jsonl; new sites in
data/catalog/extras_roman.jsonl), every row tagged with britanniaromanao00hors, each with the
200 evidence field and the book's date 1732. Append-only and idempotent (the 204/205
pattern); --dry previews; fully offline (no LLM, no network). The staging plan to execute is
the Horsley section 807 wrote in docs/lead_roman.md.

## Acceptance criteria
- [x] --stage and --dry in fit/src_roman_horsley.py: append-only, idempotent (a second run
      changes no file byte-wise), offline, writes ONLY data/commons/files_roman.jsonl,
      data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl (creating each if
      absent; never touching other rows, other books' tagged rows, or any file outside those
      three).
- [x] files_roman.jsonl gains exactly 17 rows tagged with this book (one per kind-s leaf:
      n236-254 even, n278-286 even, n114, n185), row shape per data/commons/files.jsonl
      (site/qid/title/year/wd_plan/cat/url/thumb/w/h/mime/date/desc/evidence): the 15 wall
      maps tied to their principal named fort per the 216 design (multi-fort maps tie to the
      most-named/planned fort, the others recorded in desc) on the 216-verified catalog QID
      sites where one exists (castrum-segedunum-q637958 SEGEDUNVM, pons-aelius-q7227963
      PONSAELIVM, rudchester-roman-fort-associated-civil-s-q17669775 VINDOBALA,
      haltonchesters-roman-fort-settlement-and-q17648018 HANNAVVM, aesica-q4688554 the Aesica
      plan on N.7, birdoswald-roman-fort-and-the-section-of-q17650767 BORCOVACEVS) and to
      existing-or-new extras otherwise; url/thumb = the IA full page image
      https://archive.org/download/britanniaromanao00hors/page/nNNNN.jpg (the STABLE url, not
      the redirect target); n0114 ONE row tied to the new Ardoch "roman site" extras row
      (the Innerpeffery camp recorded on the row's desc); n0185 ONE row tied to the principal
      of the five P.113 forts' new "roman fort" extras row (the other four forts' names on
      desc; the choice recorded in desc + a DECISIONS entry); every row: year 1732 and the
      200 evidence field (rec "evidence/1", kind caption_coords, checked <date>,
      named_place = the plate's printed list entry, place_qid/place_label, place_lon/
      place_lat, site_lon/site_lat, dist_m - fit/evidence.py's check_caption verifies this
      OFFLINE from the stored fields: the named place appears in norm(title+desc) and the
      stored distance reproduces within 1 km and is <= 50 km).
- [x] classified_roman.jsonl gains 17 rows classifying those (site, title) as "plan" (by
      hand).
- [x] extras_roman.jsonl gains the new no-QID site rows the staged rows need, row shape per
      data/catalog/extras.jsonl's no-QID rows (id/name/place/lon/lat/region/kind/
      location_check{...}/source): region LOWERCASE and per-site (england for the P.113
      forts and the Hadrian's-wall forts, scotland for Ardoch and the Antonine-wall forts -
      the parent's mechanics; the old extras.jsonl capitalized regions are 211's to
      normalize), kind "roman fort" or "roman site" (207a's spec, a space), lon/lat from a
      cross-check (Wikipedia/Wikidata) recorded in location_check, no QID (220's catalog
      check: none of the seven P.113/Ardoch/Innerpeffery sites exists; the Antonine forts
      already in extras.jsonl - bar-hill-fort, inchtuthil, raedykes, rough-castle-fort - are
      REUSED, not re-created). Check how 809's join counts "every new site has its plans"
      BEFORE deciding whether all five P.113 forts get their own row (the 220 note) or only
      the principal one.
- [x] All 17 verified site-plan leaves staged (100%, which meets 207a's moved 90% box with
      nothing missing); if any row must be dropped, the reason is recorded in a DECISIONS
      entry and appended to the Horsley section of docs/lead_roman.md (this task may touch
      that section for the accounting only - 807 wrote it, 808 runs after it).

## Notes (operational facts carried from the 207a split, 2026-10-14 iteration 221)

**Read fit/evidence.py IN FULL first** (it was only skimmed at 220): check_caption (~line
190), check_book (~265), check_book_caption (~290) - book rows re-derive books_match's
one-pair rule from the row's printed text + the current catalog row at the stored score;
only the runner-up margin stays stored. The 200 evidence contract (task 200) is what
809's --check enforces.

**Row content sources:** the staged titles/desc come from stage B's jsonl
(data/books/triage/britanniaromanao00hors.B.jsonl: 17 rows, printed titles + site_names per
page - n0114 "Innerpeffery camp." + "Ardoch camp.", n0185 the five Roman names, the wall maps
their segment fort names) and from the corrected 24-entry list (807) for the printed list
entry that is the evidence's named place. The 216 wall-map -> fort design and QID mapping is
in the DECISIONS entries 207a 216/219 (search for "castrum-segedunum"); the wall-map extras
that are NOT in the catalog (to check before creating rows: Condercum, Cilurni/Chesters,
Procolitia, Magna, Petriana, Congavata, Tunnocelum, and the Antonine forts Balmuildie,
Kirkintilloch, Falkirk-end where not already in extras.jsonl) are named in the 219
hand-over, in the git history of tasks/207a-horsley.md.

**The staging files do not exist yet on this branch** (207c's hand-over notes the *_roman.
jsonl files are created by the first book to stage; 207b may create them in parallel for the
Maclauchlan book - the same-file rule keeps 808 and 207b serial, and both books' appends are
tagged rows in the same files, so re-run --stage after any merge to stay idempotent).

**New site coordinates (cross-check, record in location_check):** Ardoch (Perthshire, near
the River Allan confluence; the P.44 plate's Ruchel/Ruchill + Knoch rivers place it), and the
P.113 five: Lanchester (Northumberland, the Cariseaux/Lanchester station), Whitley Castle
(Carlisle, the best-preserved of the five), Old Penrith (Bremenetracum, near Penrith), Old
Carlisle (Olenacum, north of the modern town), Elenborough (near Penrith, the station
"now Elenborough" per the plate). Wikipedia/Wikidata for the lon/lat cross-check; the
location_check note should say the coordinates were cross-checked against the book's map +
the web source.

**No LLM in this task and in 809's** (the replicas 8080-8082 are only needed by triage
stages, all already run). url/thumb: store the stable /download/ URL; the image is served
from archive.org on demand (remember the 302: -L for any manual download, but the ROW stores
the stable URL).

**Suite baseline at the split:** 1 failed / 156 passed / 1 skipped (the lone red = agent a's
307d placement test, known pre-existing). No test imports this module until 809; re-baseline
on the final run.

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: same owner lift as 807
- DECISIONS 2026-10-14 207. Runs after 807.)
## Hand-over
(2026-10-14, iteration 152, agent c - DATA RUN SESSION, TASK DONE: all 5 boxes ticked, Status: done.
The 147-151 hand-over blocks were replaced by this note; their lasting facts live in the
DECISIONS entries (808 147/148/150/152) and the module itself, which is now self-documenting
(docstring + STAGE_ROWS/NEW_SITES comments + the staged rows' descs).)

**What landed (3 commits this session):**
1. (the driver committed 84db6df before the session) fit/src_roman_horsley.py: the full
   --stage/--dry leg - STAGE_ROWS (17 leaves, leaf order 114, 185, 236-254 even, 278-286 even)
   + NEW_SITES (8 no-QID rows) + _page_sizes + stage(dry) + __main__ wiring. --check/--golden
   still raise "not built yet (809)".
2. 9adaf16 the three data files: files_roman.jsonl 1->18 rows, classified_roman.jsonl 1->18,
   extras_roman.jsonl 1->9 (17/17/8 appended by this book; 207b's row 1 byte-identical,
   sha256-verified).
3. 61ff60b + 5cc71d6: docs/lead_roman.md Horsley section gains the "**Staged (808,
   2026-10-14 ...)**" accounting paragraph (between Staging and Deferred), the DECISIONS
   entry for the run, and the PITFALLS entry (mid-suite edits break integrity tests).

**Verification (all this session):** --dry AND --stage under the socket-block wrapper
(urllib.request/ssl + socket.connect/create_connection/getaddrinfo all raise) - 42 rows, ZERO
network errors; a second --stage appended nothing (git diff vs HEAD identical after both runs
= idempotent); git diff --stat shows ONLY the three *_roman.jsonl files; evidence.check over
the 17 rows (temp file, books path absent, catalog = data/catalog/sites.jsonl): "17 rows, 17
pass, 0 fail, 0 no-tie", exit 0 - the caption_coords contract (named_place = the row's title,
place_* = site_* = the tied site's own coords, dist_m 0.0) verifies OFFLINE from stored
fields. Full suite on the STABLE tree (commit everything before starting it - see PITFALLS):
169 passed / 1 skipped / 0 failed (2026-10-14; the earlier 1/159/1 baseline is stale - agent
a's 212 work on main fixed the old 307d placement red and the suite grew to 170).

**For 809 (the --check/--golden legs):** the join spec (148 item 3, restated): (a) every
staged file row names an existing catalog site or a staged extras_roman site; (b) every NEW
extras row has >=1 staged plan row; (c) (site,title) unique; (d) classified 1:1 with file
rows; (e) a staged id already in the canonical files must be byte-identical (merge norm:
json.dumps sort_keys, ensure_ascii=False); (f) a staged QID held by another existing site =
collision (all 8 new rows are qid null - safe). 207b's check_staged()/golden()/_norm in
fit/src_roman_maclauchlan.py (~lines 345-465) are the pattern. This book's rows filter by
by == "fit/src_roman_horsley.py" (files) / source (extras). The only existing test reading
the shared roman files is tests/test_src_roman_maclauchlan.py - it monkeypatches its own
module's file paths to temp files and filters the real files by by/source == its own module,
so it stays green against any book's rows. No test imports fit/src_roman_horsley.py yet.
Note the maclauchlan book (207b) is still "in progress" in the lead; if 207c (Roy) stages
into the same files later, re-run --stage after any merge (idempotent).
