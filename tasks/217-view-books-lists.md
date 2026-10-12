Status: open
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
- [ ] `books_lists` carries the civitates_liber2 town list; `books.py ocrmap civitates_liber2`
      regenerates `data/books/lists/civitatesorbiste00brau.json`[`.map.json`] from it (the file content
      stays 213's; the module mirrors it - one place for the knowledge, the file is the dump).
- [ ] The index emits one row per indexed town-view plate for the view books, and the row records that
      it is a VIEW (not a plan) - a field 211's merge and the page can branch on (the plan books' rows
      are unaffected in shape).
- [ ] `books.py validate` over the existing plan books gives the same results as before the change
      (their metrics must not drift - a view plate is not a site plan for their recall/precision).

## Hand-over
**2026-10-12, iteration 113 (agent c) - session 1: investigation complete, NO code written yet. All design
questions settled below; next session implements + verifies, then Merian is the follow-on step.**

Working-tree state right now (from the baseline runs): `data/books/index.jsonl` and `data/books/validation.json`
are DIRTY (rebuilt with the CURRENT code, pre-edit). They are baseline artifacts, NOT deliverables: next session
starts with `git checkout -- data/books/index.jsonl data/books/validation.json`. Saved copies:
- /tmp/idx_committed (committed index.jsonl, 890 rows, no civitates; built in an older BOOKS row order - the file
  starts allcroft_1908 while BOOKS starts squier_davis_1848, so a no-args rebuild reorders the lines; compare
  per-row, not per-line) and /tmp/val_committed (8 plan-book entries, no civitates).
- /tmp/idx_baseline_run.log (baseline no-args index: 901 rows = the 890 plan-book rows + 11 civitates rows from
  the OLD mechanism: the 10 F-flagged pages + n238; found_by [qwen], no view field) and /tmp/val_baseline_run.log
  (baseline validate: civitates_liber2 entry appended with NO "figures" section - parse_figures returned []).
- /tmp/hand_figs_table.txt - the 121-line pipe table (fig|title|page|kind|kind_by) generated VERBATIM from
  data/books/lists/civitatesorbiste00brau.json; paste it into HAND_FIGS (no title contains `|` or `"`).

Verified facts (all on this machine, .venv; see the DECISIONS entry of the same date):
- The committed civitates list file is a byte dump: `json.dumps(parsed, indent=0, ensure_ascii=False)` == file
  (raw UTF-8, one `Æ`); the other 8 books' list/map files contain `\u` escapes (4 of them) and are identical
  under the current default-ascii writer - so the ocrmap writer must dump ensure_ascii=False ONLY for
  HAND_FIGS books and keep the default for the rest (byte-identity of 216's 8 books is an invariant).
- 121 list entries: `fig` = the leaf's own n (0-based; equals the stage-A row n - fig 4 title == A n=4 caption,
  etc.). Kinds: 111 o / 7 s (n58 Paris, 85 Bruges, 90 Ghent, 98 Antwerp, 109 Amsterdam, 237/238 Jerusalem; all
  kind_by hand) / 3 u (187,199 = faded BLANK fold-out versos, ink 0.0005/0.0008 < BLANK_INK; 197 = Milan arms,
  "excluded from drawings" per 213). The 121 fig set == EXACTLY A's 118 other_illustration + 3 plate_site_plan
  (187/199/238) leaves. Only fig 193/194 carry a printed page ("2"/"3", the Vienna fold-out's own numbering).
- site_pages_model("civitatesorbiste00brau") = 11 pages: [30,62,65,66,90,93,105,186,229,237,238] (F flagged 10
  "plan" pages - of which only 90/237 are real plans, the other 8 are views F misread - plus n238 from A's
  plate_site_plan; 187/199 dropped by the ink filter). Of the 7 real plans, A typed only 238 as
  plate_site_plan; the other 6 are A other_illustration.
- civitates bookreader.json pages have NO pageNum key -> row page_printed = None. No stage B file. hOCR
  (page_texts) is MISALIGNED for this book (213 pitfall) - index code must not use it for civitates rows.
- Merian: data/raw/books/topographiahelve00zeil/ has ONLY bookreader.json + metadata.json - NO hOCR, no triage
  (the goal's "OCR is cached" is not true for the text; the next Merian step must fetch page_texts/djvu and
  fetch+triage the book first; only the two 213-verified civitates+Merian helvete lists are in 217's scope,
  the other four untriaged view books stay out).

DECIDED DESIGN (implement all in pipeline/books_lists.py; nothing else):
1. After the KIND_OVERRIDES block add: `HAND_FIGS = {"civitatesorbiste00brau": """<the 121 lines from
   /tmp/hand_figs_table.txt>"""}` with a comment (per-leaf hand transcription of the view book's own plates;
   data file is its dump; kind o = town view = a drawing, s = bird's-eye plan, u = excluded; kind_by hand|A);
   `parse_hand_figures(ia_id)` (splits `|`, page "" -> None, dict key order fig,title,page,kind,kind_by - that
   order is what makes the dump byte-identical); `figure_list(ia_id)` = `parse_figures(ia_id) or
   parse_hand_figures(ia_id)`. Extend the module docstring's 2nd paragraph to mention the per-leaf transcriptions.
2. `list_pages`: for ia in HAND_FIGS map by n = f["fig"] (skip pagenum_map) and include kind in "so" (view
   books) instead of "su"; plan books byte-unchanged.
3. `cmd_ocrmap`: `figs = figure_list(ia_id)`; keep the 216 guard but fix its comment (now no source =
   PLATES/FIG_LISTS/HAND_FIGS all absent - mills etc.); both json.dump calls get
   `ensure_ascii=(ia_id not in HAND_FIGS)` (civitates .json must come out byte-identical to 213's; its
   .map.json goes [] -> 118 leaves {n, site_plan, entries} - that change is 217's machinery extension, 213a
   left it to 217; commit it, data/books/lists/ is in Touches); print "list site pages" -> "list leaves"
   (no test asserts the text - grep'd).
4. `validate_book`: `figs = figure_list(ia_id)`; for hand books n = f["fig"] (pmap = {}); "expected":
   FIG_COUNT.get(ia_id). Expected civitates numbers to check in the output: listed 121, site 7, other 111,
   unsure 3, gt_site_pages 7, recall_pages 0.286 (2/7 = 90,237), recall_pages_pm1 higher (adjacent leaves),
   precision_strict 0.18 (2/11), stage_A_only flagged 3 (187,199,238) recall 0.143 / precision 0.333.
5. `cmd_index`: `view_book = ia_id in HAND_FIGS`; `T = {}` for hand books (bypass ia.page_texts entirely -
   misalignment pitfall - the existing try/except stays for the others); marking loop adds "list_view" for
   leaves whose entries are kind o (after the existing "list" for s, before the list_unsure elif); `fig_es`
   gains `or (view_book and e["kind"] == "o")`; title_source for a hand figure entry = "book's figure list,
   hand-transcribed" (keep the OCR string for parsed lists, plates string for plates); row dict gains
   `**({"view": (entry["kind"] == "o") if entry else True} if view_book else {})` placed right after
   "page_type" - NO key at all for plan books (that is what keeps their rows byte-identical).
   Expected result: 118 new civitates rows (111 view:true + 7 view:false; found_by [list_view] or
   [list_view, qwen] for the 10 F-flagged views / [list] or [list, qwen] for the 7 plans; page_type
   "other_illustration" for 117, "plate_site_plan" for 238; fig = n).
VERIFICATION RECIPE (next session): edit, then (a) `books.py ocrmap civitates_liber2` -> .json must be
md5-identical to the committed file, .map.json populated; (b) `books.py ocrmap` (no args) -> all other
lists/ files md5-identical (baseline: /tmp/lists_md5_before.txt); (c) `books.py index` (no args) -> diff per
row (id -> exact line) against /tmp/idx_baseline_run's output: the 890 plan-book rows byte-identical, 118
new civitates rows as above; (d) `books.py validate` -> the 8 plan-book entries byte-identical to
/tmp/val_baseline_run's output (box 3), civitates entry gains the "figures" section with the numbers above;
(e) `pytest tests/ -q` full suite (last full run: 100 passed / 1 skipped - 309's fix in; no books-specific
test reads the list files directly, test_data only joins plans.json ids into index.jsonl); then
`git checkout -- data/books/index.jsonl data/books/validation.json` (207/216 precedent: the shared files are
211's rebuild - 216's note names "the 211/217 rebuild stage" for a NO-ARGS index run; I chose restore-not-commit
for consistency with 207/216; the DECISIONS entry records the row contract (the `view` field) for 211).
Commit: pipeline/books_lists.py + data/books/lists/civitatesorbiste00brau.map.json only. Then tick boxes
1-3. NEXT STEP AFTER THAT: the goal's Merian part (transcribe topographiahelve00zeil's list from its own
contents pages: first `books.py fetch merian_helvete00zeil` to cache hOCR, find the contents pages in
page_texts, transcribe per-leaf like civitates - the book's OCR may be clean (the misalignment pitfall was
civitates-specific); the book also needs triageA before any index rows will appear, but the LIST itself can
be added now; it is a separate step for a later session). BOOK_SCOPE decision: NO entry for civitates_liber2
(its towns include the Americas - MEXICO fig 261, CUSCO fig 262 - so any region scope would be wrong; a
missing scope just means no filter, .get default).
