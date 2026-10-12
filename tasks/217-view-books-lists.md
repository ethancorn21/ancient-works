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
**2026-10-12, iteration 119 (agent c) - session 5: MERGED main (conflicts: 221 + place pngs, keep main's; committed 5edeebb; suite 101 passed / 1 skipped). Identification MAJORLY ADVANCED: found session-4's LLM results file /tmp/merian/llm_ids.json (40 vision readings of the ambiguous leaves - not mentioned in the old hand-over); scandata says 67 foldout leaves (one after EACH wide leaf; only the known 10 missing from BR, the other 57 are IN BR with n's); full printed-page map extracted. IDENTIFICATION TABLE ~90% SETTLED below. NEXT: (a) classify the 57 in-BR foldouts from per-page hOCR text (a foldout CAN be an independent plate - fo230 = the Neunkirchen plan = the missing Nünkirchen 55 entry - so check each for titles of entries I mark 'none'); (b) re-run /tmp/merian/identify.py (resumable; its 3 errored jobs n66/n110/n166 have their chk/ files now); (c) image-check the 'pending' rows from /tmp/merian/d2/ (49 downscaled imgs, max 1200px); (d) record final table + kind decisions in DECISIONS; then old steps 2-4 (HAND_FIGS + parse ''->None + ocrmap/validate/commit, triage, box 2).**

MERGE (this session): main merged into agent/c, committed 5edeebb. Conflicts resolved keeping main's side for: tasks/221-review-stats-test.md (main's complete task file; my branch had only a 'Status: open' stub from the driver-sweep of an empty file) and docs/site_flow/place_{before,after}.png (main's 307c screenshots that docs/site_flow.md:549-551 references; my branch's were stray driver-swept files, before was 0 bytes). Suite after merge: 101 passed / 1 skipped (green). NOTE: npm test is dead (no package.json on main); test command = .venv/bin/python -m pytest (pytest.ini now in repo: tmp retention 1/failed only).

IDENTIFICATION TABLE (session 5; sources: hOCR = /tmp/merian/wide_hocr.txt, LLM = /tmp/merian/llm_ids.json (qwen3.8-27b, 127.0.0.1:8080/8081), IMG = my reads: fo44=dup text p19 'Beschreibung der Eydnosschafft', fo86=Burgdorff view = larger duplicate of n86. 'none' = no leaf in BR -> fig ''; kinds: o view, s plan, u excluded; '?' = decide after image).
COL1 (list col1, 23 lines): 1 Tafel des Teutschlands 10 -> n16 [u] hOCR; 2 der Endgnoschaffte 15 -> n24 [u]; 3 Elgaw+Murrz 16 -> none; 4 Zürieh im Grund 17 -> n32 [s]; 5 [Zürich] im Prospect 17 -> n36 [o]; 6 Forsteck 19 -> n42 [o] (s4 img); 7 Eglisaw+Grüningen+Griffensee+Regensperg 20 -> none; 8 Stein am Rhein 21 -> n52 [o]; 9 Winterhur+Undelfingen+Kyburg 22 -> n58 [o]; 10 Willisaw+Wedeschwyl 23 -> none; 11 Bern 24 -> n66 [s?] (d_n0066 pending; LLM errored s4, re-run); 12 Thron [Thun] 26 -> none; 13 Araw+Arberg+Arburg 27 -> n80 [o] LLM (3 views grid); 14 Lenzburg+Bruck 27 -> n72 [o?/s?] hOCR 'LENTZBURGV' (no chk img; fetch if needed); 15 Habsburg 27 -> none; 16 Burgdorff 28 -> n86 [o] LLM (fo86 = larger dup, no n, unlisted); 17 Lausanne 29 (list prints '79') -> n90 [o] hOCR (isle labels); 18 Thun 31 -> n94 [o] LLM 'THUNA'; 19 Beven 31 -> n98 [o?] hOCR 'BIBISCUM' (d_n0098 pending); 20 Gletscher 32 -> n104 [u? DECIDE: I lean u - landscape, not a town view or plan; record in DECISIONS] hOCR 'Abbildung des Gletschers'; 21 Murten+Nevis+Wisslisburg 34 -> n110 [s?] hOCR 'AVENTICUM...Romijcher gebawen' (d_n0110 pending; LLM errored s4, re-run); 22 Lucern 36 -> n116 [o] LLM 'LVCERN' (fo116 = larger dup, no n); 23 Der 4. Waldstätten See 36 -> n120 [u] LLM 'Abbildung der 4. Waldstätten See' regional map.
COL2 (30 lines): 24 Sempach+Sursee 37 -> n124 [o?] hOCR 'SEMPACHIUM...Schlacht' (d_n0124 pending); 25 Münster 37 -> n128 [o] LLM 'Ragus et Ecclesia Collegiata MUNSTER in Argovia'; 26 Altorff 38 -> n134 [s?] hOCR legend (d_n0134 pending); 27 Schwyz 39 -> n138 [o] LLM 'SVITIA, Schwentz'; 28 [Schwyz] im Prospect 39 -> n142 [o] LLM 'Prospect des Haubt Closters Schwytz'; 29 Einsiedlen 39 -> n146 [o?] hOCR 'NOBILIS EREMITARIO' (d_n0146 pending); 30 Unterwalden 41 -> n152 [u] LLM 'Das Landt Unterwalden' regional map; 31 Engelberg 41 -> none (s4's 'n160=Engelberg' was WRONG: LLM read n160 as 'TVGIVM. Zug.'); 32 Zug 43 -> n160 [o] LLM 'TVGIVM. Zug'; 33 Glaris 44 -> n166 [o?] hOCR 'Glermisch' (d_n0166 pending; LLM errored s4, re-run); 34 Basel im Grund 46 -> n172 [s] hOCR (Basel legend: S. Alban, Papyr mühlen, Teutschhaus, St. Peter...); 35 [Basel] im Prospect 46 (2. Kupffer) -> n176 [o] (4-page spread = 2 views; 2 rows? decide at impl) hOCR 'BASILEA' (fo198 IN BR - check if it is a 3rd/dup plate in step a); 36 Die Brück 47 -> n180 [o] hOCR 'PROSPECTVS CATHEDRALIS...PONTIS RHEANI'; 37 S. Peters Planz 47 -> n184 [o] hOCR 'CAMPVS DIVI PETRI...FEATZ IN BASEL'; 38 Münchenstein 48 -> n190 [o] hOCR; 39 Lichtstall 49 -> n194 [o] LLM 'Viechtstall' (hOCR 'PIERRE' was garbage); 40 Wallenburg 49 -> n198 [o] hOCR 'WALLENBURG'; 41 Pierre-pertuisse 50 -> n204 [o] LLM 'PIERRE PERTUISE' (landscape pass view; kind = same decision as Gletscher? I lean o here - it is a named place view in the list; record); 42 Romamostier 50 -> n208 [o] LLM 'Romamostier' (hOCR 'SIND SEES' was garbage; the s4 'Romamostier in col2!' reconciliation: n208 IS col2's); 43 Freÿburg 52 -> n214 [o] hOCR 'FRYBURCH' (d_n0214 pending); 44 Solothurn 53 -> n218 [s] LLM 'SOLOTURVM' bird's-eye plan; 45 Schaffhausen 54 -> n224 [o] hOCR; 46 Fall des Rheins 55 -> n228 [u? DECIDE with Gletscher] LLM 'Eigentliche Bildnüß des Großen Wasserbruchs oder Falls des Rheins im Lauffen' landscape; 47 Nünkirchen 55 -> fo230 [s] LLM 'Zünkirk' bird's-eye plan = the NUN-KIRCHEN plate but NOT in BR -> fig '' (validate nopage); 48 Appenzell+Herisaw 56 -> n236 [o?/s?] hOCR 'APPENZELL' (d_n0236 pending; n240 is NOT its map - see 52); 49 Baden 57 -> n240 [o] LLM 'Baden im Argov' (Große/Kleine Bäder legend); 50 Elingenaw+Leuggern+Wettingen+Mittlere Aare 58 -> n246 [o] LLM (4 views: Klingnaw, Leuggern, Fall des Rheins, Monast. Wettingen); 51 Heidnische Münzen vnd Silbergeschirr 58 -> n250 [u] hOCR 'Monetarum'; 52 Zurzach 58 -> n254 [s?/o?] hOCR 'FORVM TRAPEZUM, Zurzach, Kyffenberg' + lettered legend (d_n0254 pending; LLM errored s4, re-run; fo254 = larger Zurzach dup, no n).
COL3 (28 lines): 53 Bremgarten 59 -> n258 [o] LLM 'BRENGGARTEN'; 54 Lowerk+Wellenk 60 -> none; 55 Dissenhoven 60 -> n268 [o?] hOCR 'Dieffenhofert...Okethor, Sigellthurn' (d_n0268 pending); 56 Frauenfeldt+Mellingen 60 -> n272 [o] LLM (2 stacked views); 57 Rapperswyl 61 -> n276 [o] LLM 'RAP PERSWYL' (NOT Pfeffers - hOCR 'PFEBERG' garbage); 58 Pfeffers 63 (2 Kupfer, hw '2 Ansichten') -> none (2 rows? 1 row? decide; no leaf anywhere); 59 Müllhausen 65 -> n288 [o?] hOCR 'MvLHus PATRON' (d_n0288 pending); 60 Biel 66 -> n294 [o] + n298 [s] (ONE list line, TWO leaves: view + plan pair; d_n0294/d_n0298 pending); 61 S. Gallen 67 -> none; 62 Genff im Grund 70 -> n308 [s] LLM 'GENEVE. GENEVA' bird's-eye plan (hOCR was empty); 63 [Genf] im Prospect 71 -> n312 [o] LLM 'GENEUE. Genff'; 64 Neuenburg 72 (hw '2 Ansichten'+'2K') -> n316 [o] LLM 'NEOCOMVM. Steinenburg am See' + n320 [o] LLM 'Neuenburg Am See. Neocomum ad Lacum' (2 rows, one list line); 65 Weylerhauß+Eastelen+Etiszweyl 77 -> n328 [o?] hOCR 'WEYERHAUS' (d_n0328 pending); 66 Chur 79 -> n334 [o] LLM 'Chur. CURIA RHETIA' (hOCR empty); 67 Plürs 83 -> n362 [o?] hOCR 'Alte Pfarre...auf der Fluoß...Rbodanus' (d_n0362 pending); 68 Ursprung des Rheins 84 -> n348 [u? DECIDE with Gletscher/Falls] LLM 'Fontes Rheni anterioris et Posterioris' landscape (hOCR 'Ober Lmbs...Chur' was the legend); 69 S. Luciensteig 85 -> n368 [o?] hOCR French 'St. Sigismond...Ablage...La Cure de Laveg' - title does NOT say Luciensteig (d_n0368 pending; if image says otherwise, re-check my col3 transcription of 85); 70 Leugg 87 -> n356 [o] LLM 'Leug'; 71 Brieg+Naters 88 -> none; 72 Bisp/ oder Bispach 88 -> none; 73 S. Mauritij 89 -> none (S. Mauritius castle over Sion?); 74 Sitten 90 -> n374 [o] hOCR 'Sanien Thor...Hundsturn...S. Theodori' (d_n0374 pending); 75 Breiten Landenberg 90 -> n378 [o] hOCR 'BRAITEN LANDEIBERG' (d_n0378 pending); 76 Chastillard+Blonay 90 -> none; 77 Sandeck+Mauwister 90 -> none; 78 Werdenstein+S. Urbani 90 -> none.
EXTRAS (plate, no list entry -> stage-A rows like civitates' unlisted views; kind o): n76 (85) Oron [o] (s4 img); n264 (293) LVGANO+BELLINZONA [o] (LLM, 2 stacked views -> 1 or 2 rows?); n342 (375) FLURSIUM. TERRA MOTU OBRUTVM [o] (LLM: before/after earthquake views).
FOLDOUTS (1-based leafNum; all 67 = wide leaf L +1): IN BR (have n; check content in step a): 22,30,40,52,62,68,76,82,92,98,102,106,110,124,130,134,138,142,148,152,156,160,182,188,194,198,202,206,212,216,220,226,244,250,266,270,276,280,284,288,294,298,302,306,318,324,328,338,342,352,368,376,382,390,396,402,408. KNOWN: fo230 = Neunkirchen plan (independent plate!). NOT IN BR (no n -> fig '' if a list entry): 44 (dup text p19 - read), 86 (Burgdorff larger dup - read), 116 (LVCERN larger dup - LLM), 168 (dup text 'Beschreibung der Eydgnoschafft' - LLM), 230 (Neunkirchen plan - LLM), 238 (blank - LLM), 254 (Zurzach larger dup - LLM), 346 (blank - LLM), 360 (blank + small emblem - LLM), 412 (black w/ color chart, 3744x5616 portrait - LLM).
STRUCTURE FACTS (re-verified s5): scandata leafNum is 0-BASED; 1-based = +1. 67 wide leaves (n,1-based): (16,21),(24,29),(32,39),(36,43),(42,51),(52,61),(58,67),(66,75),(72,81),(76,85),(80,91),(86,97),(90,101),(94,105),(98,109),(104,115),(110,123),(116,129),(120,133),(124,137),(128,141),(134,147),(138,151),(142,155),(146,159),(152,167),(160,181),(166,187),(172,193),(176,197),(180,201),(184,205),(190,211),(194,215),(198,219),(204,225),(208,229),(214,237),(218,243),(224,249),(228,253),(236,265),(240,269),(246,275),(250,279),(254,283),(258,287),(264,293),(268,297),(272,301),(276,305),(288,317),(294,323),(298,327),(308,337),(312,341),(316,345),(320,351),(328,359),(334,367),(342,375),(348,381),(356,389),(362,395),(368,401),(374,407),(378,411). Printed-page windows (1-based leaf): p10=19, p15=32, p16=35, p17=48, p18=49, p19=54, p20=55, p21=64, p22=65, p23=72, p24=73, p25=78, p26=79, p27=94, p28=95, p29=104, p31=112, p32=113, p33=118/120, p34=121, p35=126, p36=127, p37=144, p38=145, p39=160/162, p40=165, p41=178, p42=179, p43=182/184, p44=185/188, p45=191, p46=192/206, p47=208, p48=220, p49=222/223, p50=224, p51=234/235, p52=244/247, p53=246/248, p54=259/260, p55=263, p56=270, p57=272/273, p58=274/290, p59=291, p60=306, p61=308, p63=314/315, p64=320/321, p65=330, p66=335, p67=336, p72=354, p73=357, p76=364, p77=365, p78=370, p79=373, p82=378, p83=379, p84=386, p85=387, p87=392/393, p88=394/404, p89=405, p90=406. List page citations are UNRELIABLE (several entries sit far from their cited window) - title match wins.
ARTIFACTS (this machine): /tmp/merian/ has scandata.xml, wide_hocr.txt (67 lines), llm_ids.json (40 LLM results), identify.py (RESUMABLE: skips done keys; JOBS = 40 ambiguous leaves incl. fo's; re-run for the 3 errored), corr.py/pairs.py (foldout-dup correlation; pair_*.jpg fetched), d2/ (49 images max 1200px: all chk n-images + all 10 foldouts - use these for reads), chk/ (54 scale-3 originals), foldout_*.jpg (10 full-res), list_c*.{jpg} crops, n*.jpg page samples. Re-fetch if /tmp wiped: books_ia.get(f'https://archive.org/download/topographiahelve00zeil/page/n{NNNN}.jpg') for missing wide leaves (NNNN = 1-based leafNum works for foldouts; for BR leaves use ia.page_image_url(p, scale=3) - the chk naming nNNNN used the 1-based leafNum, NOT the BR n!); scandata via books_ia.get('.../topographiahelve00zeil_scandata.xml'); hOCR texts via ia.page_texts (caches into data/raw/books/<ia>/).
KIND DECISIONS PENDING (record in DECISIONS when settled): Gletscher n104 (I lean u - not a town view/plan), Rhine Falls n228 (I lean u - landscape, not a town), Rhine source n348 (lean u), Pierre-Perthuis n204 (lean o - named place view in the list); coins n250 = u; regional maps n16/n24/n120/n152 = u; Neunkirchen fo230 = s but fig '' (plan on a missing leaf).

NEXT STEPS (s6, in order):
1. Extract per-page text for all 436 pages: data/raw/books/topographiahelve00zeil/hocr_searchtext.txt.gz (360KB stream) + hocr_pageindex.json.gz (436 entries [a,b,c,d] - figure out which fields are start/end byte offsets; VALIDATE against /tmp/merian/wide_hocr.txt for 2-3 known wide leaves first). Classify the 57 in-BR foldout leaves: blank / text-dup / larger dup of its wide partner / independent plate (any independent plate titles matching my 'none' entries - Elgg 16, Eglisau 20, Willisau 23, Thun 26, Habsburg 27, Engelberg 41, Lowerk 60, Pfeffers 63, St. Gallen 67, Brig 88, Bispach 88, S. Mauritij 89, Chastillard 90, Sandeck 90, Werdenstein 90 - get its n and add rows).
2. Re-run /tmp/merian/identify.py (3 pending: n66, n110, n166; their chk files exist now) - LLM replicas 127.0.0.1:8080/8081 up per PITFALLS.
3. Image-check the 'pending' rows via d2/ reads (small batches, update this table after each batch): n0066, n0098, n0110, n0124, n0134, n0146, n0166, n0214, n0236, n0254, n0268, n0288, n0294, n0298, n0328, n0362, n0368, n0374, n0378 (+ fetch d2 for n0072 from chk/n0072? - NOT in chk yet: page_image_url scale 3). Resolve kinds o/s for each; confirm n368's title vs list's 'S. Luciensteig' (re-check col3 line 85 in list_c3* crops if mismatched).
4. Finalize: write the complete table as the HAND_FIGS['topographiahelve00zeil'] pipe table into pipeline/books_lists.py (fig|title|page|kind|kind_by; fig = 0-based BR n for leaves with one; fig '' for foldout-only/missing; titles = the plate's own printed title, list name in brackets where it differs; kind_by hand; 2-row entries: Biel n294+n298, Neuenburg n316+n320, Basel-im-Prospect n176 (1 or 2 rows - decide: civitates precedent = 1 row per leaf in HAND_FIGS unless the list has separate lines; here the list has ONE line for the pair -> use 2 rows only if both kinds differ (Biel: o+s -> 2 rows); extras Oron/Lugano/Flurschm = NOT in HAND_FIGS (they are stage-A rows, like civitates)). Extend parse_hand_figures: fig '' -> None (one-line change; civitates table has no '' figs so byte-identical - verify).
5. books.py ocrmap topographiahelve00zeil -> data/books/lists/topographiahelve00zeil.json[.map.json]; verify all 19 other list files byte-identical (md5 vs git show HEAD); validate no-args: merian entry None (no stage A yet) + 8 plan books byte-identical; commit module + new files (NOT index.jsonl/validation.json - restore if touched).
6. Triage: books.py fetch, triageA, triageF (run_stage resumable); then index + validate no-args: one row per leaf-carrying list entry (view true for o / false for s) + extras; all other books byte-identical; restore shared files; tick box 2; Status: done.

Re-read: pipeline/books_lists.py:parse_hand_figures - the fig=''->None change must keep civitates' table parsing byte-identical (civitates has no '' figs; int(fig) path untouched for non-empty).

Working tree: clean (merge committed; no code written this session). Last suite: 101 passed / 1 skipped (post-merge, this session).

(Previous sessions' details below this marker are SUPERSEDED where they conflict with the above - keep for the civitates side, which is done: boxes 1+3 ticked.)
---
**OLD (s4, kept for civitates context): 2026-10-12, iteration 116 (agent c) - session 4: Merian plate-list TRANSCRIPTION finalized from the 2x crops
(all 3 columns read, exact names + page numbers); MAJOR FINDING: the 10 'missing' foldout leaves EXIST in the
IA item as full-res JPGs (session 3's 'not in this item' was wrong). No code written yet. Tree clean.
NEXT: finish leaf identification (batch 2 of images), write HAND_FIGS['topographiahelve00zeil'] + the
parse_hand_figures fig=''->None extension, ocrmap/validate/commit; then triage; then box 2.**

Environment (re-verified this session):
- LLM replicas UP: 8080/8081 (8082/18080/18081 down, per PITFALLS). /tmp/merian intact: scandata.xml,
  list_full.jpg, list_c{1,2,3}{0,1}.jpg (2x crops), list_c12-14/c32/c33/list_lower (my extra crops),
  page samples n*.jpg, **foldout_0044/0086/0116/0168/0230/0238/0254/0346/0360/0412.jpg (full-res, NEW this
  session)**, chk/n%04d_s3.jpg = scale-3 images of all 51 ambiguous wide leaves (n 42..378, fetched this
  session; re-fetch: ia.page_image_url(p, scale=3), books_ia.get returns BYTES).
- **The 10 foldout leaves are downloadable**: `https://archive.org/download/topographiahelve00zeil/page/nNNNN.jpg`
  for NNNN in 44,86,116,168,230,238,254,346,360,412 (all JPEG-verified this session). They are absent from
  ia.pages() (BR hides them) so they have NO n and can get NO index row - but their titles are readable,
  which pins which list entries they hold. NOTE: foldout 44 is a DUPLICATE TEXT PAGE (p19 'Beschreibung der
  Endgnoschafft'), NOT a plate; foldout 86 = the BURGDORFF view (double-page plate). Sizes: 86/116/254
  landscape (plates), 44/168/230/238/346/360/412 portrait (412 is 3744x5616 - possibly a double-page spread;
  check which are text duplicates vs plates before trusting them).

Plate-list transcription (FINAL, from 2x crops of n394; 75 lines / 81 plates; page = printed number; names as
printed - modern spelling in [] where I'm confident):
- col1: Tafel des Teutschlands 10; der Endgnoschaffte 15; Elgaw [Elgg]+Murrz [Murr] }16; Z\u00fcrich im Grund 17;
  [Z\u00fcrich] im Prospect 17; Forsteck 19; Eglisaw [Eglisau]+Gr\u00fcningen+Griffensee+Regensperg [Regensberg] }20;
  Stein am Rhein 21; Winterhur [Winterthur]+Undelfingen [Andelfingen]+Kyburg }22; Willisaw [Willisau]+Wedeschwyl
  }23; Bern 24; Thron [Thun] 26; Araw [Aarau]+Arberg+Arburg [Aarberg] }27; Lenzburg+Bruck [Brugg] }27; Habsburg
  27; Burgdorff [Burgdorf] 28; Lausanne 79; Thun 31; Beven [B\u00e9ven] 31; Gletscher 32; Murten+Nevis+Wisslisburg
  }34; Lucern 36; Der 4. Waldst\u00e4tten See [4-Waldst\u00e4tter-See map] 36.
- col2: Sempach+Sursee [Z\u00fcrichsee] }37; M\u00fcnster 37; Altorff [Altdorf, Uri] 38; Schwyz 39; [Schwyz] im
  Prospect 39; Einsiedlen 39; Underwalden [Unterwalden] 41; Engelberg 41; Zug 43; Glaris 44; Basel im Grund 46;
  [Basel] im Prospect 2. Kupffer 46; Die Br\u00fcck daselbst 47; S. Peters Planz [Platz] daselbst 47; M\u00fcnchenstein
  48; Lichtstall 49; Wallenburg 49; Pierre-pertuisse [Pierre-Perthuis] 50; Romamostier [Romainm\u00f4tier = the
  AVENTICUM/Avenches plate] 50; Fre\u00efburg in \u00dcechtland [Fribourg] 52; Solothurn 53; Schaffhausen 54; Fall des
  Rheins im Laufsen [Rheinfall] 55; N\u00fcnkirchen [Neunkirchen] 55; Appenzell+Herisaw [Herisau] }56; Baden im
  Aergow 57; Elingenaw [Klingnau]+Leuggeren [Leuggern]+Wettingen+Der Mittleren Lau\u00dfen [Mittlere Aare] }58;
  Heidnische M\u00fcnzen vund Silbergeschirr 58; Zurzach 58.
- col3: Bremgarten 59; Lowerk+Wellenk }60; Dissenhoven [Dissenhofen] 60; Frauenfeldt [Frauenfeld]+Mellingen
  }60; Rapperswyl [Rapperswil] 61; Pfeffers 2. Kupffer 63 (handwritten '2 Ansichten'); M\u00fcllhausen [M\u00fcllhausen]
  65; Biel 66; S. Gallen 67; Genff [Genf] im Grund 70; [Genf] im Prospect 71; Neuenburg 72 (handwritten
  '2 Ansichten'+'2K'); Weylerhau\u00df [Weyerhau\u00df/WEYERHAUS]+Eastelen [Castelen?]+Etiszweyl [?] }77; Chur 79; Pl\u00fcrs
  [Fl\u00fclen] 83; Ursprung des Rheins 84; S. Luciensteig 85; Leugg [?] 87; Brieg [?]+Naters }88; Bisp/ oder Bispach
  88; S. Mauritij [St. Maurice] 89; Sitten [Sion] 90; Breiten Landenberg [Breitenlandenberg] 90; Chastillard
  [Ch\u00e2tillens?]+Blonay }90; Sandeck+Mauwister [?] }90; Werdenstein+S. Urbani [St. Ursanne] }90.
- Footer: handwritten '3 Karten un. 102 Ansichten' (3 maps + 102 views); printed footer '102 Kupfersticken'
  (session 3). My count is 81 plates (23+30+29) - the gap vs 102 = plates hidden in list lines I may have
  merged (the '2 Kupffer' lines = 2 each); NOT an acceptance criterion, do not chase it.

Leaf structure (verified this session, ia.pages):
- 400 BR leaves, n = 0-based index; 67 WIDE leaves (landscape) = the engraved spreads (session 3 said 65 -
  miscount, corrected). Wide (n, leafNum): (16,21),(24,29),(32,39),(36,43),(42,51),(52,61),(58,67),(66,75),
  (72,81),(76,85),(80,91),(86,97),(90,101),(94,105),(98,109),(104,115),(110,123),(116,129),(120,133),
  (124,137),(128,141),(134,147),(138,151),(142,155),(146,159),(152,167),(160,181),(166,187),(172,193),
  (176,197) 4-page,(180,201),(184,205),(190,211),(194,215),(198,219),(204,225),(208,229),(214,237),(218,243),
  (224,249),(228,253),(236,265),(240,269),(246,275),(250,279),(254,283),(258,287),(264,293),(268,297),
  (272,301),(276,305),(288,317),(294,323),(298,327),(308,337),(312,341),(316,345),(320,351),(328,359),
  (334,367),(342,375),(348,381),(356,389),(362,395),(368,401),(374,407),(378,411).
- 36 leaves absent from BR (12-15, 32,33, 44,45, 86,87, 116,117, 162,163,168,169, 170-173, 230,231, 238,239,
  254,255, 260,261, 346,347, 360,361, 412,413, 435,436); the 10 FOLDOUTS = 44,86,116,168,230,238,254,346,360,412
  (each right after a wide leaf); rest = Delete duplicates. hOCR index i == 1-based leafNum (aligned, unlike
civitates). /tmp/merian/wide_hocr.txt = all 67 wide-leaf hOCR dumps.
- scandata pageNumData (78 assertions) is sparser but consistent with ia.pages pageNum; key: p16=leaf34,
  p17=leaf47, p19=leaf53, p20=leaf54, p21=leaf63, p22=leaf64, p23=leaf71, p24=leaf72 (start '2. Bern.'),
  p25=leaf77, p26=leaf78, p27=leaf93, p28=leaf94, p29=leaf103, p31=leaf111, p32=leaf112, p33=leaf117/119,
  p34=leaf120, p35=leaf125, p36=leaf126, p37=leaf143, p38=leaf144, p39=leaf159/161, p40=leaf164, p41=leaf177.

Identifications SETTLED so far (image-verified unless noted):
- n16 = Tafel des Teutschlands [u] (map of German lands); n24 = der Endgnoschaffte [u] (map of the
  Confederation, 'WAIBEN LAND'); n32 = Z\u00fcrich im Grund [s] (plan, legend A.Gro\u00df M\u00fcnzer..Z.Nemmarckt);
  n36 = Z\u00fcrich im Prospect [o] ('Tigurvm'); **n42 = Forsteck [o] (image read this session: 'Forsteck.
  FORSTECK.' hill-castle view; hOCR 'Kazann' was garbage)**; n52 = Stein am Rhein [o] (Hochen Klingen,
  Neunenberg); n58 = Winterhur+Undelfingen+Kyburg [o] (3 entries, 1 leaf); n66 = Bern [s?] (plan legend -
  CHECK IMAGE: is there a view half too? single list entry either way); n72 = Lenzburg+Bruck [o?/s? - check];
  **n76 = Oron [o] (image read this session: 'ORON.' view with castle + hunting scene; Oron is NOT in the
  printed list - an EXTRA view; decide kind o with kind_by 'hand/A' and how the index rows it - probably
  stage-A-flagged extra like civitates's unlisted views)**; foldout 86 = Burgdorff [o] (view, confirmed
  image; but foldout has no n -> no index row, list entry fig=None, validate counts nopage); n90 = Lausanne
  [o] (hOCR French labels: Eglise Francois/Isle, Le Chasteau, Arsenal, Roche - Lausanne's isle; the list's
  odd 'Lausanne 79' sits in the Bern section); n104 = Gletscher (glacier panorama - KIND DECISION NEEDED:
  I lean o 'a view/drawing in its own right', but it is not a town view; record in DECISIONS); n110 =
  Murten+Nevis+Wisslisburg [s?] ('AVENTICUM...Romijcher gebawen von der Statt Auentico' - Roman ruins plan;
  note the book's Murten=Aventicum plate, NOT Avenches; list name 'Romamostier' p50 belongs to a DIFFERENT
  later leaf - see below); n120 = ? (castle legend 'zu Altdorf...Sempach' - candidate P23 4-Waldst\u00e4tter See
  map [u]); n152 = ? ('UNDERWAIDIA...Die vier Walls...' - also a 4-Waldst\u00e4tter candidate [u] - DECIDE which of
  n120/n152 is the map vs which is a town, by image).
- NOT YET IDENTIFIED (images in /tmp/merian/chk/, read next session): n80 (91), n86 (97, empty hOCR),
  n94 (105, empty), n98 (109 'BIBISCUM'), n116 (129, empty), n124 (137 Sempach - confirm), n128 (141
  'Stecken und Astifft' = M\u00fcnster? confirm), n134 (147 Altorff/Uri), n138 (151 Lucerne-ish legend?), n142
  (155 Leodegars/M\u00fcnze legend?), n146 (159 Einsiedeln - confirm 'Nobilis Eremitario'), n152 (167), n160
  (181 'Oswalch...Frawen Closter'), n166 (187 'Glermisch' = Glaris?), n172 (193 'S. Alban Closter' = Basel
  suburb? = Basel im Grund [s]?), n176 (197 4-page = Basel im Prospect 2 Kupfer [o x2]), n180 (201 'PROSPECTVS
  CATHEDRALIS...PONTIS RHEANI' = Br\u00fcck [o]), n184 (205 'CAMPVS DIVI PETRI...FEATZ IN BASEL' = S. Peters Platz
  [o]), n190 (211 M\u00fcnchenstein [o]), n194 (215 Pierre-Perthuis [o]), n198 (219 Wallenburg [o]), n204 (225
  empty - ?), n208 (229 'SIND SEES' = Romanshorn? but list has no Romanshorn - 'Romamostier' 50 is in col2!
  RECONCILE), n214 (237 Freiburg [o]), n218 (243 empty - Solothurn?), n224 (249 Schaffhausen view [o]), n228
  (253 Schaffhausen map 'Descriptio Catarractarum Rhieni' [s?/u?]), n236 (265 Appenzell [o]), n240 (269
  Appenzell map legend [u?/s?]), n246 (275 'Vorstatt, Closter Sion, das Schlo\u00df' + 'Der mittere Laufsen oder
  Fall des Rheins' = Rheinfall [o] - the map-ish one?), n250 (279 coins sheet [u]), n254 (283 'Forvm
  Trapezum, Zurzach' = Zurzach [s]), n258 (287 'Capuciner Closter...das Schloss' = ?), n264 (293 'Forte
  S. Catharina...Lago de Lugano' = ? Lugano-ish map?), n268 (297 'Dieffenhofert...Okethor, Sigellthurn' =
  Dissenhoven [o?/s?]), n272 (301 'Pfeffers...Templum Purockrale' = Pfeffers [o x2 - 2 Kupfer, one leaf? or
  two?]), n276 (305 'Capuciner...Schukenhau\u00df...das Schloss' = ?), n288 (317 'MvLhusen...St. Sterbans' =
  M\u00fcllhausen [o]), n294 (323 'St. Iohans Closter...Der Bieter See' = Biel [o?/s?]), n298 (327 'Blatz thor...
  Das Rahthaufe' = Biel [s?/o? - the pair with n294]), n308 (337 empty - S. Gallen?), n312 (341 'S. Gervais...
  Le lac Leman' = Genff [o?/s? - French, Lake Geneva]), n316 (345 'Unser Frawen Kirch...Vestung...Port
  Salanchon' = ? Neuenburg-ish), n320 (351 'EOCOMVYIT...Vnser Frawen Kirch...Hundes Turn' = ?), n328 (359
  WEYERHAUS [o]), n334 (367 empty - ?), n342 (375 garbled - ?), n348 (381 'Ober Lmbs...Chur' = Chur [s?/u?]),
  n356 (389 'HaubKirc...Peters Kirch...Rathhaus' = Chur plan [s?/o?] or a second Chur?), n362 (395 'Alte
  Pfarre...Burgerh\u00e4us...auf der Fluo\u00df...Rbodanus' = Pl\u00fcrs [o]), n368 (401 'St. Sigismond...Ablage' French =
  S. Luciensteig? [o?/u?]), n374 (407 'Sanien Thor...Hundsturn...S. Theodori' = Sitten/Sion [o]), n378 (411
  'BRAITEN LANDEIBERG' = Breiten Landenberg [o]); foldouts 116,168,230,238,254,346,360,412 (read images:
  which are plates vs text duplicates - 412 is 3744x5616).
- Unmatched list entries (find their leaf): Habsburg 27, Thun 26, Araw-group 27, Thun 31, Beven 31, Altorff
  38, Schwyz 39, [Schwyz] im Prospect 39, Unterwalden 41, Engelberg 41, Zug 43, Glaris 44, Basel im Grund 46,
  Die Br\u00fcck 47, S. Peters Planz 47, M\u00fcnchenstein 48, Lichtstall 49, Wallenburg 49, Pierre-pertuisse 50,
  Romamostier 50, Freÿburg 52, Solothurn 53, Schaffhausen 54, Fall des Rheins 55, N\u00fcnkirchen 55, Appenzell
  56, Baden 57, Elingenaw-group 58, M\u00fcnzen 58, Zurzach 58, Bremgarten 59, Lowerk+Wellenk 60, Dissenhoven 60,
  Frauenfeldt+Mellingen 60, Rapperswyl 61, Pfeffers 63, M\u00fcllhausen 65, Biel 66, S. Gallen 67, Genff 70/71,
  Neuenburg 72 (x2), Weylerhau\u00df/Eastelen/Etiszweyl 77, Chur 79, Pl\u00fcrs 83, Ursprung des Rheins 84,
  S. Luciensteig 85, Leugg 87, Brieg+Naters 88, Bispach 88, S. Mauritij 89, Sitten 90, Breiten Landenberg 90,
  Chastillard+Blonay 90, Sandeck+Mauwister 90, Werdenstein+S. Urbani 90, Elgaw+Murrz 16 (its leaf = ? -
  foldout 44 is a text dup, so Elgg+Murr's plate is either missing entirely or on a wide leaf I mis-ID'd;
  CHECK: no wide leaf between n24 (29) and n32 (39) -> Elgg+Murr may have no plate leaf in this item at all
  -> transcribe with fig='' like the foldouts).

NEXT STEPS (in order):
1. Finish identification: read /tmp/merian/chk/n%04d_s3.jpg for the NOT-YET-IDENTIFIED set above + the 8
   unread foldouts (/tmp/merian/foldout_NNNN.jpg; downscale before reading if too big - .venv/bin/python +
   PIL). Where hOCR title + list order + printed-page window (pN = leaf above; a plate between pN-1 and pN
   is cited N, side varies) leave >1 candidate, the image title wins. Record every kind judgement (o =
   perspective view incl. a canton/town view; s = bird's-eye 'im Grund' plan/map of a town; u = excluded:
   regional maps Teutschlands/Endgnoschaffte/4-Waldst\u00e4tter-See/Lugano-ish/coins; glacier = decide o vs u and
   record in DECISIONS) in the DECISIONS entry for this date.
2. Implement in pipeline/books_lists.py: HAND_FIGS['topographiahelve00zeil'] = pipe table fig|title|page|
   kind|kind_by (fig = the 0-based n of the wide leaf, from the (n, leafNum) list above; page = the printed
   list number as a string; foldout-only plates and any leafless entries = fig '' ; parse_hand_figures:
   change int(fig) to None when fig == '' (one-line change; list_pages/validate already None-safe - verify
   cmd_index: it only iterates lp, and lp skips n=None, so no deref). The .json dump contract stays
   {"plates": null, "figures": [...]}, indent=0, ensure_ascii=False (HAND_FIGS books), key order
   fig,title,page,kind,kind_by. Titles: the book's own printed title as on the plate (e.g. 'Forsteck.
   FORSTECK.' -> 'Forsteck'), list name in brackets where it differs.
3. `books.py ocrmap merian_helvete00zeil` -> data/books/lists/topographiahelve00zeil.json[.map.json] (new
   files; .map.json = [] until triaged since lp={} when stage_a is empty - still commit it, civitates
   precedent). Verify: all 18 OTHER list files byte-identical (md5 vs git show HEAD of each), civitates
   .json still md5-identical to 213's. `books.py validate` no-args: merian entry = None (no stage A yet),
   all 8 plan-book entries byte-identical to HEAD. Commit module + list files (NOT index.jsonl/
   validation.json - restore to HEAD state if touched).
4. Triage (LLM up): `books.py fetch merian_helvete00zeil`, then `triageA`, then `triageF` (400 leaves;
   run_stage is resumable - start it, let it run across sessions if needed). Then `books.py index` +
   `validate` no-args: expect one row per list entry that has a leaf (view true for kind o / false for kind
   s; Oron-type extras appear as stage-A rows); ALL other books' rows byte-identical to HEAD; then RESTORE
   index.jsonl + validation.json (git checkout) per the 207/216 precedent (this task commits neither). Tick
   box 2, set Status: done, note 211's merge will rebuild.

Re-read: pipeline/books_lists.py:parse_hand_figures - the fig=''->None change must keep civitates' table
parsing byte-identical (civitates has no '' figs; int(fig) path untouched for non-empty).

Working tree this session: clean (no code written; all artifacts under /tmp/merian/).

Verified this session:
- Wide-leaf count is 67 (not 65 as session 3 said) - the hand-over list above is the corrected one.
- hOCR of all 67 wide leaves extracted to /tmp/merian/wide_hocr.txt (index i == 1-based leafNum, aligned).
- Foldout JPGs download (10/10); 44 = text dup (p19), 86 = Burgdorff plate; rest unexamined.
- Last full-suite run (session 2, still valid - tree unchanged since): 100 passed / 1 skipped.

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

### Also written to PROGRESS.md (moved here by the driver)

# PROGRESS (generated by the driver before every session)

Hand-over notes live in each task's `## Hand-over` section at the end of its task file: write yours in your
task file (for a subtask, read its parent's too).

## Tasks in flight
- `tasks/203-batch-fit.md` (split)
- `tasks/207c-roy.md` (blocked)
- `tasks/207-roman-books.md` (split) - hand-over: (2026-10-11, iteration 63 - SPLIT into 207a/207b/207c; this is the plan for the remaining
- `tasks/211-merge-build.md` (open) - hand-over: **From 213 (2026-10-11, iteration 39, parent done-claim):** the *_artists* staging files exist and
- `tasks/217-view-books-lists.md` (in-progress) - hand-over: **2026-10-12, iteration 115 (agent c) - session 3: Merian INVESTIGATION done (structure + mapping + list read);
- `tasks/302-autofit-real.md` (split) - hand-over: (2026-10-11, iteration 74, agent c - FIRST session on this task; investigation only, no code written. Split into 302a-302d; next step is 302a.)
- `tasks/302c-decision-wiring.md` (open) - hand-over: (2026-10-12, iteration 84, agent c - FIRST session on 302c. Investigation + design only: NO code
- `tasks/304-survey-fit.md` (in-progress) - hand-over: (2026-10-12, iteration 91, agent c - session 7. The lead directed: freeze the stub as it is
- `tasks/307b-on-map.md` (split) - hand-over: (2026-10-12, iteration 116, agent a - 307ba's five boxes are all done and committed, but
- `tasks/307-fit-tool-rework.md` (split) - hand-over: (2026-10-12, iteration 107, agent a - SPLIT into 307a/307b/307c/307d; investigation only,

## Next open tasks
- `tasks/207a-horsley.md`
- `tasks/207b-maclauchlan.md`
- `tasks/219-source-line-year.md`

## Your task's journal

Its newest `DECISIONS.md` entries, the driver's notes on it included (a rejected done claim says why here). Search `DECISIONS.md` and `DECISIONS-archive.md` for other tasks' reasoning.

### 2026-10-12 217 DECISION: civitates view-book design settled - HAND_FIGS per-leaf table in the module (the file is its dump), index gets a `view` row field for kind-o plates; shared index.jsonl/validation.json restored, not committed (207/216 precedent); no BOOK_SCOPE for the view books
Session 1 on 217: investigation only, no code (full plan is in the task's Hand-over). Decisions made, each with
its evidence:
1. **The module mirrors 213's hand list, the file stays the dump.** `HAND_FIGS["civitatesorbiste00brau"]` will
   hold the 121-line pipe table (fig|title|page|kind|kind_by) transcribed verbatim from
   data/books/lists/civitatesorbiste00brau.json (pre-generated at /tmp/hand_figs_table.txt); `parse_hand_figures`
   + `figure_list` (OCR-parsed or hand) feed cmd_ocrmap/validate_book/list_pages. `fig` = the leaf's own n, so
   hand books need no page-number mapping (pagenum_map/map_plates untouched).
2. **Byte format is an invariant, not a detail.** The civitates .json is a dump with `indent=0,
   ensure_ascii=False` (raw Æ - verified: dumps(parsed, indent=0, ensure_ascii=False) == file, and NOT equal
   with the default); four of the other eight books' files contain `\uXXXX` escapes (default writer). So
   cmd_ocrmap dumps `ensure_ascii=(ia_id not in HAND_FIGS)` for both .json and .map.json; all other bytes
   (indent=0, key order fig,title,page,kind,kind_by) reproduce 213's file and 216's eight byte-identical files.
3. **The `view` field is the row contract for 211 and the page.** cmd_index adds `"view"` to rows of
   HAND_FIGS books only (true = kind-o town view, false = kind-s plan, true = model-flagged leaf not in the
   list); placed right after "page_type" via a `**{}` spread so plan-book rows get NO new key and stay
   byte-identical (box 2's "shape unaffected"). found_by gains the tag "list_view" (mirrors "list"). The page's
   plans.json already has a `view` column (bool, set from Clef for Commons bird's-eye pictures) - the index
   field is the book-row feed for it; 211's merge/export maps it (their lane, noted in the hand-over).
   civitates hOCR is misaligned (213 pitfall) -> index takes T={} for hand books and never calls page_texts.
4. **Expected outputs (to verify next session):** ocrmap civitates_liber2 -> .json md5-identical to 213's,
   .map.json [] -> 118 leaves (7 site_plan + 111 view; 213a left populating it to 217 - that change is the
   machinery extension, committed under data/books/lists/). index (no args) -> 118 new civitates rows (111
   view:true + 7 view:false; 890 plan-book rows byte-identical; baseline run saved: /tmp/idx_committed,
   /tmp/idx_baseline_run.log - note the committed file was built in an older BOOKS row order, so diff per row
   id, not per line). validate -> 8 plan-book entries byte-identical (box 3), civitates entry gains "figures"
   (listed 121; recall_pages 0.286 = 2/7 of the hand plans {90,237} of the 11 model-flagged; stage_A_only 3).
5. **Shared files restored, not committed** (after verification: git checkout -- index.jsonl validation.json):
   the 207->216 precedent keeps them for 211's rebuild; 216's note to 217 ("run no-args at the 211/217 rebuild
   stage") I read as a warning against subset runs, and the 211 hand-over already treats "zero civitates rows
   until the rebuild" as expected. The `view` contract above is what 211 branches on.
6. **No BOOK_SCOPE entry for civitates_liber2:** the volume includes American towns (fig 261 MEXICO, 262
   CUSCO), so any region filter would be wrong; a missing scope means "no filter" (.get default) - recorded so
   the next agent does not "fix" it.

### 2026-10-12 217 DECISION: civitates machinery landed - HAND_FIGS mirrors 213's per-leaf list (the file is its dump; ensure_ascii=False for hand books only), list_pages/validate/index branch on HAND_FIGS, index rows gain a `view` field on hand-book rows only; boxes 1 and 3 ticked, box 2 waits on the Merian list
Session 2 (iteration 114) implemented session 1's design as written and verified all of it (the task's hand-over
has the full numbers):
- ocrmap civitates_liber2: the .json comes out md5-identical to 213's committed file (0881ec0c...); .map.json
  [] -> 118 leaves (7 site_plan) - committed (data/books/lists/ is in Touches). No-args ocrmap: the other 17
  list files byte-identical (md5-checked against session 1's baseline).
- index no-args: 1008 rows. The 890 plan-book rows byte-identical IN ORDER to the HEAD baseline (session 1's
  unmodified-code run, committed by the driver). 118 civitates rows: view true 111 / false 7; found_by
  list_view 103 / list_view+qwen 8 / list 4 (n58,85,98,109) / list+qwen 3 (n90,237,238); page_type
  other_illustration 117 / plate_site_plan 1 (n238); title_source "book's figure list, hand-transcribed" on all;
  fig == leaf_n; captions_ocr empty (T={} bypasses the misaligned hOCR). The `view` key is absent from every
  plan-book row - the row-shape contract for 211 and the page.
- validate no-args: the 8 plan-book entries byte-identical to HEAD (box 3); the civitates entry gains the
  "figures" section (listed 121; site 7 / unsure 3 / other 111; gt_site_pages 7; flagged 11).
- Full suite 100 passed / 1 skipped.
CORRECTION to session 1's predicted numbers: recall_pages is 3/7 = 0.429 (not 0.286) and precision_strict is
3/11 = 0.273 (not 0.18) - leaf 238 (Jerusalem, kind s in the hand list) is ALSO stage A's plate_site_plan, so
it is in both gt_site and flagged; session 1's arithmetic counted it once. The actuals are self-consistent and
verified; recorded in PITFALLS so nobody "fixes" the code toward the stale prediction.
Boxes: 1 and 3 ticked (verified). Box 2 ("for the view books", plural) stays open: the machinery is proven on
civitates, but the goal's Merian helvete list is not transcribed yet - that is the remaining step (fetch/cache
the hOCR, find the contents pages, transcribe into HAND_FIGS, triage the volume, then its rows appear and the
box ticks). The other four view books stay out of scope.
Note for future baseline work: /tmp/idx_committed (session 1's copy) is STALE - it predates 216's BOOKS order
and the current row shape (it even carries the `evidence` key the current cmd_index does not emit, a 200-era
post-hoc field). Diff rebuilds against `git show HEAD:<file>` or a fresh unmodified-code run, never a saved
/tmp copy (PITFALLS).

### 2026-10-12 217 DECISION: Merian helvete investigation (session 3) - book structure mapped; the plate list is the book's own "Erönung der Kupfferstich" (BR n394); hOCR index == 1-based leafNum (aligned, unlike civitates); 65 wide BR leaves are the engraved spreads; 10 big-plate foldouts are absent from the item; the list's page number points to an adjacent text page with varying side, so it is a window not a rule
Session 3 on 217: investigation only, no code (working tree clean; artifacts in /tmp/merian on this
machine: scandata.xml, list_full.jpg = n394 full-res, list_c{1,2,3}{0,1}.jpg 2x column crops, page-image
samples). Findings, each verified:
1. **LLM replicas are up** (127.0.0.1:8080/8081, qwen3.8-27b; 8082 down per the 5060 Ti image matchers):
   `books.py fetch/triageA/triageF merian_helvete00zeil` are runnable from this machine - triage is the
   step after the transcription, not a blocker.
2. **hOCR fetched and aligned.** hOCR page index i == 1-based leafNum == BR leafNum field (verified at
   i=429 the plate list at n394, i=197 "BASILEA" at n176, i=11 printed p7). So - unlike civitates -
   hOCR titles can be trusted for this book's leaves. 436 hOCR pages; BR shows 400.
3. **Structure:** 436 leaves all imaged; BR omits 36: 25 Delete (duplicates/foldout versos) + 10 Foldout
... (4.2 KB more: `grep -n -A 200 -F '## 2026-10-12 217 DECISION: civitates machinery landed - HAND_FIGS mirrors 213's per-leaf list (the file is its dump; ensure_ascii=False for hand books only), list_pages/validate/index branch on HAND_FIGS, index rows gain a `view` field on hand-book rows only; boxes 1 and 3 ticked, box 2 waits on the Merian list' DECISIONS.md`)

## Project-wide driver notes (newest)

### 2026-10-11 DRIVER: test suite failing at loop start (1 tests)
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_gate.py:36: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    1 failed, 59 passed in 63.50s (0:01:03)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (4 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees
    tests/test_serve.py::test_platefits_docs_match_sites
    FAILED tests/test_batch_eu.py::test_union_full_coverage_live - AssertionError...
    FAILED tests/test_gate.py::test_recorded_measurement_reproduces_and_agrees - ...
    FAILED tests/test_serve.py::test_platefits_docs_match_sites - AssertionError:...
    4 failed, 60 passed in 64.37s (0:01:04)
    (full test output: .agent/reports/last-test-output.txt)

### 2026-10-11 DRIVER: test suite failing at loop start (3 tests)
    tests/test_batch_eu.py::test_union_check
    tests/test_batch_eu.py::test_union_full_coverage_live
    tests/test_serve.py::test_platefits_docs_match_sites

### 2026-10-12 HAND-OVER NOTE (agent c, 217, iteration 116): session cut at context limit.
    217 status: Merian plate-list transcription FINAL (full table in tasks/217-view-books-lists.md
    hand-over); the 10 foldout leaves exist in the IA item as JPGs (foldout 86 = Burgdorff plate);
    51 wide-leaf images fetched to /tmp/merian/chk/; identified so far: n42=Forsteck, n76=Oron.
    NEXT: finish leaf identification (batch 2, image set in hand-over), write
    HAND_FIGS['topographiahelve00zeil'] + parse_hand_figures fig=''->None, ocrmap/validate/commit,
    then triage, then box 2. No code written this session; tree clean; last suite run 100 passed /
    1 skipped (session 2, still valid). Details: DECISIONS.md (session-4 entry) + task hand-over.
