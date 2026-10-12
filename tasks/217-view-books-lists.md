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
**2026-10-12, iteration 114 (agent c) - session 2: the civitates machinery is implemented and verified (boxes 1
and 3 ticked). REMAINING: the Merian helvete list + that volume's triage, then box 2 and Status: done.**

Working tree now: this session committed pipeline/books_lists.py (HAND_FIGS mirrors 213's per-leaf table;
figure_list/list_pages/validate/index branch on HAND_FIGS; the `view` row field; the byte-format invariant:
ensure_ascii=False for hand books only) and data/books/lists/civitatesorbiste00brau.map.json ([] -> 118 leaves,
7 with site_plan; entries carry the hand figure plus type "figure"). The shared rebuild files (index.jsonl,
validation.json) were RESTORED to their committed state (git checkout) - they stay 211's rebuild; this task
commits neither. data/books/lists/civitatesorbiste00brau.json is untouched (byte-identical to 213's).

Verified this session (all re-run; DECISIONS entry of the same date):
- `books.py ocrmap civitates_liber2`: .json md5-identical to 213's committed file (0881ec0c...); .map.json
  populated: 118 leaves (7 site_plan).
- `books.py ocrmap` no-args: the other 17 list files byte-identical (md5 vs /tmp/lists_md5_before.txt).
- `books.py index` no-args: 1008 rows; the 890 plan-book rows byte-identical IN ORDER to the HEAD baseline
  (session 1's unmodified-code no-args run; diff against `git show HEAD:data/books/index.jsonl`, NOT
  /tmp/idx_committed - that copy is stale, see PITFALLS). The 118 civitates rows: view true 111 / false 7;
  found_by ('list_view',) 103 / ('list_view','qwen') 8 / ('list',) 4 (n58,85,98,109) / ('list','qwen') 3
  (n90,237,238); page_type other_illustration 117 / plate_site_plan 1 (n238); title_source "book's figure list,
  hand-transcribed" on all 118; fig == leaf_n; page_printed None; captions_ocr [] (the hOCR misalignment is
  bypassed: T={} for hand books). The `view` key exists on civitates rows only (plan-book rows have no key).
- `books.py validate` no-args: the 8 plan-book entries byte-identical to HEAD (box 3). The civitates "figures"
  section is FINAL: listed 121 / expected null / parsed_with_page_on_a_leaf 121 / site 7 / unsure 3 / other 111 /
  gt_site_pages 7 / recall_pages 0.429 / recall_pages_pm1 0.429 / flagged_nonplate_pages 11 / precision_strict
  0.273 / precision_lenient 0.273 / flagged_on_other_only_pages [30,62,65,66,93,105,186,229] /
  flagged_not_in_list [] / missed_pages [58,85,98,109] / stage_A_only {recall 0.143, precision_strict 0.333,
  precision_lenient 1.0, flagged 3}. (recall 0.429 = 3/7: hit {90,237,238} - session 1's 0.286/0.18 prediction
  missed n238, which is both a hand plan and an A-flagged leaf; the new numbers are correct, PITFALLS records it.)
- Full suite: 100 passed / 1 skipped.

NEXT STEP (box 2, the goal's Merian part) - transcribe topographiahelve00zeil's list from the book's own
contents pages, then add the volume to HAND_FIGS:
1. Its hOCR is NOT cached yet (only bookreader.json + metadata.json in data/raw/books/topographiahelve00zeil/;
   the goal's "its OCR is cached" is false): call ia.page_texts("topographiahelve00zeil") once - it lazy-caches
   hocr_pageindex.json.gz + hocr_searchtext.txt.gz into data/raw/books/<ia>/ (committed? they live under RAW -
   check .gitignore; raw data is gitignored, the cache is per-machine).
2. Find the contents pages in page_texts (read a few pages' OCR until the town index appears), then transcribe
   per leaf like civitates. Decide the fig convention from what the page actually says: a sequential
   one-plate-per-leaf list -> fig = the leaf's n (the current parse_hand_figures shape); a printed index with
   page numbers -> map through pagenum_map (extend figure_list/parse_hand_figures if needed, keeping the .json
   dump contract: {"plates": null, "figures": [...]}, indent=0, ensure_ascii=False, key order fig,title,page,
   kind,kind_by). kind: o = town view (a drawing), s = plan, u = excluded; kind_by hand.
3. `books.py ocrmap merian_helvete00zeil` -> its .json becomes the dump; commit the module change + the list
   file. `books.py validate` then gives it a "figures" section (stage A empty -> validate_book returns None
   until triaged, which is fine).
4. Index rows appear only once the volume is triaged: `books.py triageA merian_helvete00zeil` (needs the local
   LLM replica answering on 127.0.0.1:8080-8082, PITFALLS; run_stage exits cleanly if none) and `triageF` for
   the view plates; fetch the triage images first (`books.py fetch merian_helvete00zeil`). After triage:
   no-args index + validate, check the view:true rows, re-verify every other book byte-identical, restore the
   shared files, tick box 2, set Status: done. No BOOK_SCOPE entry needed (missing scope = no filter, like
   civitates). The other four untriaged view books (civitates liber1/4/5, merian panb665) stay out of 217's
   scope - the goal names civitates + Merian helvete only.

Re-read: none (the module changes are small and every observable output was byte-verified this session).
