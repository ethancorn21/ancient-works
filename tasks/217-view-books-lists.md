Status: done
# 217: Book machinery - town-view lists and the view-as-drawing index for Civitates/Merian
Depends on: 216
Touches: pipeline/books_lists.py, pipeline/books.py, data/books/lists/

## Goal
GOAL.md point 5 (2026-10-10): artists' aerial and bird's-eye views count as drawings as much as
surveys. The machinery does not let them through: stage A types a perspective view
`other_illustration`, the list taxonomy's kind "o" means "other (views, sections alone, ...)", and
`cmd_index` emits an index row only for kind "s" (site plan) - so a book of town views (Civitates,
Merian) validates and triages but indexes to nothing. Add the per-book list transcriptions to
`books_lists` and the taxonomy/index change that carries a town-view plate through as a drawing.

Source material: task 213's hand transcription `data/books/lists/civitatesorbiste00brau.json` (its town
plates with inscriptions and printed pages - the single source of truth; lift it, do not re-transcribe
it by hand a second time) and `data/books/triage/civitatesorbiste00brau.F.jsonl` (per-figure captions).
Merian's `topographiahelve00zeil` list: transcribe from the book's own contents pages (its OCR is
cached in `data/raw/books/<ia>/`) once the civitates path works.

## Acceptance criteria
- [x] `books_lists` carries the civitates_liber2 town list; `books.py ocrmap civitates_liber2`
      regenerates `data/books/lists/civitatesorbiste00brau.json`[`.map.json`] from it (the file content
      stays 213's; the module mirrors it - one place for the knowledge, the file is the dump).
- [x] The index emits one row per indexed town-view plate for the view books, and the row records that
      it is a VIEW (not a plan) - a field 211's merge and the page can branch on (the plan books' rows
      are unaffected in shape).
- [x] `books.py validate` over the existing plan books gives the same results as before the change
      (their metrics must not drift - a view plate is not a site plan for their recall/precision).

## Hand-over
**2026-10-12, iteration 124 (agent c) - session 9: STEP B COMPLETE IN CODE; box 2 ticked, Status: done. Only PITFALLS entries + final commit left.**

STATE (working tree, uncommitted - the harness keeps these; do not re-run anything):
- pipeline/books.py: BLANK_INK_BOOKS = {"topographiahelve00zeil": 0.01} + site_pages_model uses it (per-book
  ink floor; global BLANK_INK 0.005 untouched - plan books unaffected).
- pipeline/books_lists.py: 2 table rows corrected (s7's leafless call was wrong for both):
  `|S. Luciensteig|85|o` -> `350|S. Luzissteig in Vünken sambt Alter Demolierten vnd Neuen Schantzen|85|o`,
  `|Werdenstein und S. Urbani|90|o` -> `384|WERDENSTEIN. Kloster S. Urban|90|o` (titles = the plates' own printed
  titles, read by stage A and corroborated by the cached hOCR; both kind o).
- data/books/lists/topographiahelve00zeil.json (new md5 1f49058c) + .map.json (57 mapped leaves; site_plan leaves
  still [32,66,124,134,172,218,268,288,298,308]).
- data/books/index.jsonl + data/books/validation.json: RESTORED to 6fff103 (the pre-task baseline; 211 owns them -
  207/216/211 precedent; `git checkout 6fff103 --` was used because HEAD=354b38c no longer is the baseline).
- data/books/triage/topographiahelve00zeil.A.jsonl (400/400) + .F.jsonl (108): committed by the driver in 354b38c;
  clean, don't touch.
- Task file: Touches gained pipeline/books.py. Box 2 ticked and Status: done in this session (everything
  below was verified this session; no re-run needed).

VERIFIED THIS SESSION (suite 101 passed / 1 skipped after all changes; 184 s):
- Iter 123 (cut off) had run fetch+triageA+triageF+no-args index/validate; the driver committed the dirty tree as
  354b38c (shared files included - against s8's restore plan; no memory written). A fresh no-args rebuild of that
  state is BYTE-IDENTICAL to 354b38c's files => faithful artifacts, not tampering.
- Diff vs 6fff103 baseline: 890 plan-book rows byte-identical IN ORDER; 118 civitates rows (107 new + 11
  model-flagged rows reshaped by 217's machinery - the intended delta, s2-verified); 8 plan validation entries
  byte-identical; civitates entry + only the s2-verified "figures" block (listed 121, site 7, recall 0.429,
  precision 0.273 - matches s2); new merian entry.
- AFTER the fix (the state 211's rebuild will reproduce): index 1068 = 890 + 118 + 60. Merian = 60 rows on 57
  leaves, ALL list-derived (title_source "book's figure list, hand-transcribed", zero null titles): view true 50 /
  false 10; found_by list_view 45 / list 6 / list+qwen 6 / list_view+qwen 3; page_type other_illustration 58 /
  plate_site_plan 2 (n308, n350 - stage A's type kept, the view field disambiguates). NO stage-A-only rows.
- Merian validate entry: pages 400, triaged_A 400, flagged_stageA 66, F 108, flagged 8; figures: listed 80,
  parsed_with_page_on_a_leaf 68, site 11, unsure 8, other 61, gt_site_pages 10, recall_pages 0.5, recall_pm1 0.5,
  precision_strict 0.625, precision_lenient 0.625, flagged_on_other_only_pages [246,350,384],
  flagged_not_in_list [], missed_pages [32,66,134,218,298], stage_A_only {recall 0.1, precision 0.015, 66}.

WHY THE TWO FIXES (evidence for the DECISIONS entry):
- n350/n384 are REAL plates (ink 0.2025/0.3551; genuine plate leaves in this book all >= 0.1834): hOCR leaf 383
  garbles exactly stage A's read of the S. Luzissteig title; hOCR leaf 419 carries the "MONASTERIU S.URBANI" legend.
  s7's "no plate leaf between n348 and n356" missed n350; Werdenstein's window check likewise missed n384.
- The 4 dropped junk rows (n121 0.0054, n153 0.0073, n205 0.0097, n231 0.0073) are faint show-throughs: hOCR is
  garbage on all four; n153 carried a cross-book invented title ("Plan of the Mound at the Fork of the Road, near
  the Village of" + "PLATE XXV" - a 19th-c American idiom in a 1654 Swiss book; "PLATE XXV" read on n121 too).
- s8's predictions corrected: list rows 58/55 not 66/63 (the 8 u rows are excluded from index rows by design),
  gt_site_pages 10 not 11 (n55 leafless), stage-A-only actually [121,153,205,231,350,384] not the speculative
  {76,176,264,320,342} (those extras are typed other_illustration, F says no plan -> no rows, as designed).

NEXT (next agent, small): 1) Two PITFALLS entries (session 9 was at the context limit and could not edit
PITFALLS.md): under "This codebase / pipeline/books.py, pipeline/books_ia.py (the book machinery)" - a book's
fold-out show-through can be darker than global BLANK_INK (0.005, tuned on Thomas <=0.004); Qwen types such
pages plate_site_plan and invents cross-book titles; the per-book floor is BLANK_INK_BOOKS (books.py); check
the ink gap before trusting faint pages. Under "Agent tools and harness" - the driver's "[driver] uncommitted
work after iteration N" safety-net commit commits an interrupted session's dirty SHARED files; the next session
must re-derive the planned state and restore from the correct baseline commit (`git checkout <baseline> --
<file>`; plain `git checkout --` restores the driver's commit, not the baseline). 2) Final commit of the
uncommitted code: `git add -A && git commit -m "217: step B done - merian triage verified (rebuild
byte-identical), table corrections n350/n384 (s7's leafless call wrong, hOCR+stage-A prove the plates exist),
per-book ink floor 0.01 drops 4 Qwen-misread show-throughs, 60 hand-list view rows on 57 leaves, shared files
restored to 6fff103 for 211"`. 3) Stop. No code changes beyond what is in the tree; no re-runs needed.

STATE OF THE WORK (all committed; the module is the one source of knowledge):
- pipeline/books_lists.py: the second HAND_FIGS key. 80 rows in list order col1->col2->col3; a double-page (or
  4-page, n176) spread = 1 row; a leaf with two entries = 2 rows, o before s (n72 = Lenzburg+Brugg + Habsburg;
  n124 = Sempach o + Sursee s; n134 = Altorff o + Flüelen s). fig = 0-based n of the wide leaf (67 wide leaves
  exist; n76/n264/n342/n320 are wide leaves deliberately NOT in the table - extras / second views).
- The 14 fig-'' rows (validate counts them "nopage"; list_pages/index skip them): Elgaw+Murrz 16, Eglisaw-group
  20, Willisaw+Wedeschwyl 23, Thron 26, Engelberg 41, Nünkirchen 55 (s - the fo230 plan leaf is BR-hidden),
  Lowerk+Wellenk 60, Pfeffers 63, Plürs 83, S. Luciensteig 85, Bispach 88, Chastillard+Blonay 90,
  Sandeck+Mauwister 90, Werdenstein+S. Urbani 90.
- NOT in the table -> surface as stage-A-only index rows (view=True, found_by ["qwen"], title from stage A) at
  triage IF stage A types them plate_site_plan: n76 Oron, n264 LVGANO+BELLINZONA, n342 FLURSIUM (the 3 extras),
  plus n320 (Neuenburg's 2nd view) and n176's 2nd view. n143 is a TEXT page (not a figure).
- data/books/lists/topographiahelve00zeil.json[.map.json] committed; ocrmap rewrites both (.map.json populates
  from list_pages once stage A exists).

STEP B (the only remaining work - triage, then rebuild; next session):
1. LLM replicas: 127.0.0.1:8080/8081 (qwen3.8-27b); 8082 is down while the 5060 Ti image matchers hold it
   (PITFALLS). Check: curl -s 127.0.0.1:8080/v1/models.
2. `.venv/bin/python pipeline/books.py fetch merian_helvete00zeil` - 400 triage images (1400 px) into
   data/raw/books/topographiahelve00zeil/triage/ (resumable; network-heavy, long timeout).
3. `.venv/bin/python pipeline/books.py triageA merian_helvete00zeil`, then `triageF merian_helvete00zeil` -
   run_stage is resumable (re-run to continue). USE THE BOOK KEY (an ia id dies with KeyError - PITFALLS).
   Budget: 400 pages at qwen 27b (civitates' 292 took a while) - let it run across sessions if needed.
4. Then NO-ARGS: `.venv/bin/python pipeline/books.py index` and `validate` (shared files; this task commits
   NEITHER - restore both with `git checkout --` after verification, 207/216/211 precedent).
   Expected merian INDEX rows: 66 rows on 63 leaves (the 66 table rows WITH fig; per_entry doubles n72/n124/
   n134 to 2 rows each; view = True for kind o / False for kind s - n124/n134 give one True + one False;
   title from the hand table, title_source "book's figure list, hand-transcribed", fig == leaf_n; found_by
   "list_view" for o-only leaves, "list" for s-only, "list" ALSO for the mixed n124/n134 (the elif in
   cmd_index gives s precedence), + "qwen" where the model flagged the leaf too) + the stage-A-only rows above.
   Expected merian VALIDATE entry (it appears once stage A exists): pages 400, triaged_A 400, figures {listed
   80, expected null, parsed_with_page_on_a_leaf 66, site 11, unsure 8, other 61, gt_site_pages 11, ...} -
   recall/precision are whatever the model's flags give; do not force numbers. civitates entry = session-2's
   verified figures (PITFALLS); the 8 plan books byte-identical to HEAD.
   VERIFY: diff the rebuilt index.jsonl + validation.json against `git show HEAD:<file>` per row/entry (never
   a /tmp copy - PITFALLS); everything except the merian rows/entry (and civitates' uncommitted "figures"
   block) must match; then `git checkout -- data/books/index.jsonl data/books/validation.json`.
5. Tick box 2; Status: done. (211's merge rebuilds index/validation for the page; the `view` field is 211's
   row contract, verified on civitates rows in session 2.)
- Stuck rule: if fetch/triage fails repeatedly (LLM down, IA 404s), log each attempt in DECISIONS; ask_human
  on the 3rd, set blocked.

Re-read: none (the parse change is verified: civitates' dump stays byte-identical; the merian table parses to
80 entries, 14 with fig=None, as designed). If a table row is ever questioned, the per-row evidence (image
titles, list crops, 5 s7 list corrections) is in the DECISIONS s7 entry; the git history of this task file
keeps the older hand-overs with the verbatim 81-line plate-list transcription (s4), the 67 wide-leaf
(n, leafNum) pairs and the hOCR-alignment facts (hOCR index i == 1-based leafNum, aligned unlike civitates).
Full-res re-fetch of ANY of the 436 leaves (incl. the 10 BR-hidden foldouts):
`books_ia.get('https://archive.org/download/topographiahelve00zeil/page/n<1-based leafNum>.jpg')` (PITFALLS).
