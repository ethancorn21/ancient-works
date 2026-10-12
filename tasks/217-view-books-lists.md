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
**2026-10-12, iteration 115 (agent c) - session 3: Merian INVESTIGATION done (structure + mapping + list read);
NO code written this session (tree clean; only /tmp/merian artifacts). NEXT: transcribe HAND_FIGS entries
using the recipes below, then ocrmap/validate, then triage, then box 2.**

Environment (re-verified this session):
- LLM replicas UP: 127.0.0.1:8080 and 8081 (qwen3.8-27b vLLM); 8082/18080/18081 down (as per PITFALLS).
  triageA/triageF are therefore runnable from this machine - run them in the next session (step 4).
- hOCR is NOW cached: data/raw/books/topographiahelve00zeil/hocr_pageindex.json.gz + hocr_searchtext.txt.gz
  (ia.page_texts fetched them; data/raw is gitignored, cache is per-machine - re-call ia.page_texts if missing).
- scandata.xml (leaf metadata) and the full-res list-page image live in /tmp/merian/ on this machine:
  scandata.xml, list_full.jpg (n394 scale 1), list_c{1,2,3}{0,1}.jpg (2x column crops), n*.jpg page samples.
  Re-fetch: books_ia.get('https://archive.org/download/topographiahelve00zeil/topographiahelve00zeil_scandata.xml')
  and ia.page_image_url(ps[394], scale=1).

Book structure (the key facts):
- 436 jp2 leaves (scandata 0-based 0-435). BookReader shows 400 (n0-399); 36 leaves are absent from BR:
  25 "Delete" pages (duplicates/foldout versos) + 10 "Foldout" leaves (big engravings NOT in this item) +
  1 back color card. **The 10 missing foldouts (1-based leafNum 44, 86, 116, 168, 230, 238, 254, 346, 360, 412)
  have EMPTY hOCR - their plate content is unknown from OCR; each sits right after a wide BR leaf.**
- **65 wide BR leaves (landscape ~3300x2700) = the engraved plates**, one double-page spread each
  (perspective view on the left page, plan/map on the right; Basel n176 = leaf 197 is a 4-page spread with
  two views). Wide leaves (1-based leafNum, which equals the hOCR page index):
  21,29,39,43,51,61,67,75,81,85,91,97,101,105,109,115,123,129,133,137,141,147,151,155,159,167,181,187,
  193,197,201,205,211,215,219,225,229,237,243,249,253,265,269,275,279,283,287,293,297,301,305,317,323,
  327,337,341,345,351,359,367,375,381,389,395,401,407,411.
- **hOCR index i == 1-based leafNum** (verified: hOCR[429] = the plate list at BR n394/leafNum 429;
  hOCR[197] = "BASILEA" at BR n176; hOCR[11] = printed p7). Unlike civitates (misaligned), Merian's hOCR
  lines up - usable for titles, but still read the list page image for the list itself.
- The **book's own plate list** = "Erönung der Kupfferstich/welcher Orten ein jedes von dem Buchbinder
  inzuhefften sey" on BR n394 (leafNum 429; n395 is its upside-down duplicate). 3 columns, ~85-90 entries
  grouped by curly braces sharing one page number; footer "...102 Kupfersticken". Full transcription in the
  DECISIONS entry of this date (session 3) - it is the draft table; the next session finalizes it against
  the wide-leaf titles.
- Printed page numbers: IA pageNum verified correct on p16 (n27) and p24 (n63 = start of section "2. Bern.").
  The list's page number points to an ADJACENT text page but the side varies (Bern spread leaf 75 is AFTER
  p24, cited "24"; Zurich spreads leaves 39/43 are BEFORE p17, cited "17") - so treat the list page number
  only as a candidate window, and pin each entry to a wide leaf by the plate's own printed title.

Wide-leaf title readings from hOCR (leafNum: title) - use to match list entries:
  L21 map of German lands ("Amand...Emsden...Coruld" - list: Tafel des Teutschlands); L29 map of the
  Confederation ("cum Confinis...WAIBEN LAND" - der Endgnoffschafft); L39 = n32 ZURICH plan (legend
  A.Gross Münzer...Q.Zeughoff); L43 = n36 ZURICH view ("Tigurvm"); L51 = n42 ("Kazann"? Forsteck?); L61 =
  n52 ("Stein am Rhein, Hochen Klingen, Altea Aa, NEUNENBURG"?); L67 = n58 WINTERTHUR ("...Möburg Kyburg");
  L75 = n66 BERN plan ("St. Vincenken Münster...Das Sup...Barfüßer Closter"); L81 = n72 LENZBURG;
  L85 = n76 ("Merian" - ?); L91 = n80 (?); L97 = n86 (empty - maybe a missing-foldout twin?); L101 = n90
  (French labels "Eglise Francois, Le Chasteau, Arsenal" - ?); L105 = n94 (empty); L109 = n98 ("BIBISCUM"
  - ?); L115 = n104 glacier picture ("Abbildung des Glätschers in Gestein...Gletscher...Berner"); L123 = n120
  ("Der See...Römischer Gebaw" - 4 Waldstätter See?); L129 = n116 (empty hOCR); L133 = n128 UNTERWALDEN map
  ("Die Statt ... zu Altdorf...Sempach"); L137 = n134 SEMPACH ("SEMPACHIUM", Schlacht); L141 = n141 (?);
  L147 = n147 URI ("Staltorf...Uri...See...S.Martini"); L151 = n151 (Capuainer...Rathauß - LUCERNE plan?);
  L155 = n155 ("Rathhaus...St.Martins Pfarckirch" - LUCERNE view?); L159 = n159 ("NoBis...Eremitario" -
  Einsiedeln?); L167 = n152 UNDERWAIDIA ("Landt Ünderwalden" - the 4-Waldstätten map!); L181 = n166 (?);
  L187 = n166? no: n168 ("Glarmische" - GLARUS?); L193 = n172 (St. Alban Closter... - ?); L197 = n176
  BASILEA views (the 2-view 4-page spread); L201 = n180 ("PROSPECTVS...CATHEDRALIS...PONTIS RHEANI" =
  Brück/St.Peters view); L205 = n184 ("CAMPVS DIVI PETRI...FEATZ IN BASEL" = St. Peters Platz); L211 = n190
  ("Münchenstein"); L215 = n194 ("Pierre..." = Pierre-Perthuis); L219 = n198 ("WALLENBURG"); L225 = n204
  (empty); L229 = n208 ("SIND SEES" - Romanshorn?); L237 = n214 ("Freiburg Üechtlandt...FRYBURCH");
  L243 = n218 (empty); L249 = n224 SCHAFFHAUSEN view ("...im weflen fcht. Anno 1644"); L253 = n228
  SCHAFFHAUSEN map ("Descriptio Catarractarum Rhieni...Statt Schaffhausen"); L265 = n236 APPENZELL;
  L269 = n240 (Appenzell map legend "Ufer, Sarnen Stift...Verena Limat fluu"); L275 = n246 (? "Vorstatt,
  Closter Sion, das Schloß"); L279 = n250 COINS ("Abrif der Silberen...Heidnifchen Gefchirzen und Münzen...");
  L283 = n254 ("Forum Trapezum, Zurzach...Kylsberg"); L287 = n258 (?); L293 = n264 (Forte S.Catharina... -
  BIEL?); L297 = n268 ("Dieffenb...Okethor, Sigellthurn" - ?); L301 = n272 ("Pfeffers"? "Templum Purockrale");
  L305 = n276 ("Capuciner...Schukenhauß...das Schloß" - ?); L317 = n288 ("NOBIL...MvLhusen PATRON...St.
  Sterbans" - MÜLLHAUSEN); L323 = n294 ("St.Johans Closter...Rathauß...Der Biezer See" - BIEL view?);
  L327 = n298 ("Rathhauss...Spital" - BIEL plan?); L337 = n308 (empty); L341 = n312 ("S.Gervais...La Porte
  dela Monoye...Le lac Leman" - NEUCHATEL, French); L345 = n316 ("Wnser Frawen Kirch...Vestung...Fürstliche
  Schloß" - ?); L351 = n320 ("EOCOMVYIT...Turn...Vnser Frawen Kirch...Vestung" - RAPPERSWIL?); L359 = n328
  ("WEYERHAUS"); L367 = n334 (empty); L375 = n342 (garbled); L381 = n348 ("Ober Lmbs in ober Rhezia...Chur"
  - GRISONS map); L389 = n356 ("HaubKirc...Peters Kirch...Rathhaus" - CHUR plan?); L395 = n362 ("Alte
  Pfarre...Burgerhäus...auf der Fluoß" - PLÜRS?); L401 = n368 ("St.Sigismond...Ablage" - ?); L407 = n374
  ("Sanien Thor...Kleine Thor...Gundis Thor...Hundsturn...S.Theodori" - SITTEN?); L411 = n378 ("Turbential,
  Weylen, Tofs Fluss...BRAITEN LANDEIBERG" - Breitenlandenberg).

NEXT STEPS (in order):
1. Finalize the table (see DECISIONS session-3 draft): read the /tmp/merian/list_c* crops for exact names +
  page numbers (OCR is too garbled to trust); where a wide-leaf hOCR title disagrees, the plate's own title
  wins. For each of the 65 wide leaves: assign list entry(ies) by (a) list page window, (b) title match,
  (c) image spot-checks where >1 candidate (images: ia.page_image_url(ps[n], scale=4) - /tmp/merian has
  n16? no: samples n3,n4,n5,n6,n7,n8,n12,n13,n20,n21,n26,n27,n32,n36,n38,n63,n66,n176,n393,n394,n395,n396).
  The 10 missing-foldout plates have no leaf n: transcribe them with fig = "" (empty) - parse_hand_figures
  must be extended to allow fig=None (hand-over 2 already anticipated this: "keep the .json dump contract:
  {"plates": null, "figures": [...]}, indent=0, ensure_ascii=False, key order fig,title,page,kind,kind_by");
  in validate they count as nopage, and list_pages/index skip n=None - verify those branches handle it
  (list_pages: `n = f["fig"] if ia_id in HAND_FIGS ...` then `if n is not None` - already safe; validate:
  `if n is None: nopage += 1` - already safe; parse: change int(fig) to None when empty).
2. Kinds (record the judgement in DECISIONS): perspective town/canton view = o (a drawing, GOAL pt 5);
  bird's-eye town plan/map ("im Grund") = s (213's precedent: civitates town plans are s); regional maps
  (Tafel des Teutschlands, Endgnossenschaft, 4-Waldstätter-See) and the coins sheet = u (excluded: not town
  views; HAND_FIGS u = "excluded from the drawings"). kind_by = hand. Titles: the book's own printed title
  (e.g. "Tigurvm. Zürich.", "BASILEA"), with the list's name in brackets where it differs.
3. `books.py ocrmap merian_helvete00zeil` -> data/books/lists/topographiahelve00zeil.json[.map.json]
  (new files; Touches: data/books/lists/ already covered). Verify: the other 18 list files byte-identical
  (md5 baseline: re-run ocrmap no-args and compare against git show HEAD of each); civitates files still
  byte-identical to 213's. `books.py validate` no-args: merian entry must come out None (stage A empty)
  and all 8 plan books byte-identical. Commit module change + list file (+ .map.json if populated - with no
  triage, lp={} so .map.json = []; still commit it for consistency with civitates's committed .map.json).
4. Triage (LLM up): `books.py fetch merian_helvete00zeil` (triage images), then `triageA`, then `triageF`
  (400 pages at ~qwen 27b: civitates 292 took a while - budget time; run_stage is resumable). Then
  `books.py index` + `validate` no-args: expect one row per list entry on a wide leaf (a spread carrying a
  view+plan pair yields 2 rows for the same leaf_n; ~65 leaves, more rows), view true for kind o /
  false for kind s; found_by list_view/list as in civitates, plus stage-A-flagged extras; ALL other
  books' rows byte-identical to HEAD; then RESTORE index.jsonl + validation.json (git checkout) per the
  207/216 precedent (this task commits neither). Tick box 2, set Status: done, note 211's merge will
  rebuild.

Re-read: pipeline/books_lists.py:parse_hand_figures - extend for fig="" -> None; verify list_pages/
validate_book/cmd_index handle n=None for HAND_FIGS books (validate already does; list_pages checks
`n is not None`; cmd_index iterates lp only - confirm no other path dereferences f["fig"]).

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
