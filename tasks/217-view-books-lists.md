Status: in-progress
# 217: Book machinery - town-view lists and the view-as-drawing index for Civitates/Merian
Depends on: 216
Touches: pipeline/books_lists.py, data/books/lists/

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
- [ ] The index emits one row per indexed town-view plate for the view books, and the row records that
      it is a VIEW (not a plan) - a field 211's merge and the page can branch on (the plan books' rows
      are unaffected in shape).
- [x] `books.py validate` over the existing plan books gives the same results as before the change
      (their metrics must not drift - a view plate is not a site plan for their recall/precision).

## Hand-over
**2026-10-12, iteration 122 (agent c) - session 8: STEP A LANDED, committed (3ab444f).**
HAND_FIGS['topographiahelve00zeil'] = the session-7-verified 80-row table (11 s / 8 u / 61 o; 14 leafless rows
fig '' = plate has no leaf in the item); parse_hand_figures maps fig '' -> None; `books.py ocrmap
merian_helvete00zeil` regenerates data/books/lists/topographiahelve00zeil.json as the table's dump (raw UTF-8,
key order fig,title,page,kind,kind_by) + .map.json = [] (stage A empty). Byte-verified: the 18 other list files
md5-identical (s7 baseline /tmp/merian/lists_md5_before_s7.txt AND git HEAD), civitates .json still 0881ec0c,
validate no-args per-entry == HEAD (only delta = civitates' "figures" block, the session-2 numbers the 207/216
precedent deliberately left uncommitted), shared files restored, suite 101 passed / 1 skipped.
BOX 2 STAYS OPEN: merian's index rows only exist once the volume is triaged (step B below). NEXT: step B.

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
