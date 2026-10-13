Status: in-progress
# 306e: Look at the orphan agent fits, UK part 2 (o-y) - 17 docs, 13 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306e.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 17
UK platefit documents with `by: agent` (sites o-y) that are ORPHANS - in the store, but no
overlay built on the site and not referenced by any review item, so a visitor sees them not at
all. Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the doc's stored
pairs placed. The verdict records where the doc stands today (invisible) and whether the
placement is good enough to keep.

## Acceptance criteria
- [ ] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
      open, the doc's pairs placed in the fit tool over the aerial; plus a shot over the LiDAR
      relief where the site has one), taken with `tools/shot.mjs` against `server/serve.py
      --port 0` on this checkout (recipe in the parent's Hand-over; GET only, ephemeral port).
- [ ] One line per doc appended to the "## The agent fits, looked at (task 306)" section of
      `docs/site_flow.md`: what the drawing's lines sit on (the real banks, walls, ditches,
      streets) and the verdict (keeps its document / deleted - and it is an orphan today,
      invisible on the page).
- [ ] A fit whose drawn works visibly miss the real ones is dealt with the 303 way: the picture
      is upserted into the site's review item with the reason (`fit/review.py upsert_item`
      pattern), the document is deleted, and the site's review page file is re-exported scoped
      to the site (never another site's item file). The site stays covered for the union check
      (an open item counts). A fit that sits right keeps its document, and its line says so.
- [ ] No `by: hand` document is touched; no new test failures against the driver's newest
      loop-start note (suite green in this checkout 2026-10-12: 123 passed, 1 skipped,
      test_gate pre-existing red).

## Docs (17, 13 sites)
- offa-s-dyke-q1127343.c_1cca85e7b4b5a89e - OS 1902 Nantcribba 02
- okehampton-castle-q1419982.c_0edd7f87db67ff20 - Plan of Okehampton Castle
- old-sarum-q782719.c_041083ec68b532f8 - Ancient Plan of Old Sarum
- old-sarum-q782719.c_ff62c9585a92b375 - Plan & elevations of Old Sarum (DPLA)
- oxford-castle-q2600886.c_ba6b308580428184 - Oxford Castle, plan from Mackenzie, The Castles of England (1897)
- pilsbury-castle-q7194511.c_7ff765c177ca7bae - Pilsbury Castle plan
- pontefract-castle-q1949590.c_3213330a52fe6018 - The history of the ancient borough of Pontefract (14739695456)
- pontefract-castle-q1949590.c_d135fb32326df430 - The history of the ancient borough of Pontefract (14762763065)
- portus-adurni-q762664.c_42bedb90fffce1d4 - Portchester Castle, derived from the Penny Cyclopaedia (1836) v6 p 354
- portus-adurni-q762664.c_4912bb54aa79f3ea - Burg von Portchester, Penny Cyclopaedia 1836 p 354
- raby-castle-q4583646.c_fe1d6c7f0ba858cb - Raby Castle, plan from Mackenzie, The Castles of England (1897)
- richborough-roman-fort-q1309736.c_edad7da41d234534 - Richborough Castle, derived from the Penny Cyclopaedia (1836) v6 p 353
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 - Penny Magazine 1836: plan of the druidical temple at Stanton Drew
- taunton-castle-q7688781.c_05cb4a02bd58e82e - Taunton Castle, plan from Mackenzie, The Castles of England (1897)
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 - WINDMILL SITES, LEWES DOWN (Allcroft 1908)
- york-castle-q80637.c_8dac5aacd73916b8 - York Castle in 1820
- york-castle-q80637.c_a7db545536f13e24 - Plan of Center, Broome County 1855 (Gifford Wenig)


## Hand-over
(2026-10-13, iteration 196, agent c - **EXECUTED taunton-castle c_05cb4a02bd58e82e the
303 way: NEW item created (lead = this plan; the site had none), doc deleted, scoped
export (346,359)->(347,360), 14th of 17 lines written, suite = baseline 154/1/1.**
**NEXT session: judge the LAST 2 sites (3 docs): windmill-hill n0558_2 (APPEND to its
existing item) and york-castle x2 (append; c_a7db is the toponymic-collision class).**)

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed** (last run: 196, 309 s). The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Expect exactly that in every run; any other failure = my new red.

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181);
okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED
(183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED (190);
portus-adurni c_4912bb54aa79f3ea DELETED (191); raby-castle c_fe1d6c7f0ba858cb DELETED
(192); richborough-roman-fort c_edad7da41d234534 DELETED (193); stanton-drew
c_59a5c636a9e00703 DELETED (194); taunton-castle c_05cb4a02bd58e82e DELETED (judged 195,
EXECUTED 196). **3 docs (2 sites) remain after taunton:**
windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2, york-castle x2.

**What 196 did (executed taunton the 303 way; the 195 hand-over's NEXT STEP 1-7, steps
1-6 done, step 7 = next session):**
1. Preconditions re-checked LIVE: fr._find_item = (None, None) (no item);
   fr.candidate_evidence = the hand_tied row (files.jsonl line 1457, kind hand_tied,
   source 'pipeline/sources.py mackenzie'); fr._sha16('File:Plan of Taunton Castle
   (1897).jpg') == plan. Export baseline (346, 359) confirmed by counting 359 item
   files on disk + 346 open page entries.
2. Script /tmp/aw306e_texec.py (pattern /tmp/aw306e_stexec.py, both still alive):
   entry = {plan, title, url = doc["url"] = media/commons/taunton-castle-q7688781/
   05cb4a02bd58e82e.jpg (REPO-RELATIVE - consistent with all 8 previously created 306e
   items; the 195 'use the row's url verbatim' note is loose, the page must serve the
   image so the local path is the right url), pairs (the doc's 4), coarse False,
   evidence (the row's), label '1897', cite+ref (the doc's), size [1280,1461],
   place_reason '306e audit 2026-10-13: ... Wrong place, right kind. Document
   deleted.'}. fr.upsert_item (returns an ABSOLUTE path) CREATED
   data/review/taunton-castle-q7688781.c_05cb4a02bd58e82e.json (lead = this plan, sole
   candidate); os.remove the doc; fr.export(fr.ROOT, site) -> (347, 360) exactly as
   predicted (a NEW open item adds one to both counts).
3. Verified: item = [c_05cb4a02bd58e82e], resolved None, no_picture_found None; page
   entry under name 'Taunton Castle' (sites.json). git status = exactly 3 files (D
   doc, M web/data/review.json, ?? item) - no other site's item touched.
4. 14th of 17 lines written into the 306e block of docs/site_flow.md (after the
   stanton-drew line, before '## The site markers become arrowheads (task 308,
   2026-10-13)'), same shape as the raby/oxford/portus lines.
5. Suite: 154/1/1 = baseline.

**NEXT STEP (session 197) - the LAST 2 sites (3 docs), then the task is DONE:**
1. **windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2** (Allcroft 1908,
   'WINDMILL SITES, LEWES DOWN'; model None - the page's default plan model fits it;
   6 stored pairs, url None = a BOOKS doc, so its row is data/books/index.jsonl by id
   n0558_2, not files.jsonl). The site's item already holds [n0557_1, n0558_1]
   (data/review/windmill-hill-q4348373.earthworkenglan01allcgoog_n0557_1.json, lead
   n0557_1, open, no_picture_found None): if DELETED, APPEND the entry to THAT item
   (lead/file name stay), do NOT create a second item. Judged on the committed shots
   (docs/site_flow/agent_fits/windmill-hill-..._n0558_2.png + _relief.png) + the LAYERS
   composite recipe below.
2. **york-castle-q80637 c_8dac5aacd73916b8** ('York Castle in 1820' watercolour, score
   31.7) + **c_a7db545536f13e24** ('Plan of Center, Broome County 1855' (Gifford Wenig)
   = Center is a TOWN in Broome County, NEW YORK - toponymic-collision class, almost
   certainly DELETED wrong place). Existing item (c_81ecab4a9284f156 + 4 more, open)
   -> append. Check each doc's files.jsonl row for evidence before upserting (assert
   candidate_evidence non-None).
3. After all 17 lines are in: TICK box 2; box 3 is complete when the york/windmill
   verdicts are executed; then tick box 3 (box 4 already holds: no `by: hand` doc
   touched). Set the task `Status: done` (all 4 boxes).
4. Full suite each session (expect 154/1/1 = baseline).

**The 303 way (summary; full recipe in the 189-196 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the source row title
WITH its 'File:' prefix for commons / as-is for books; fr._sha16(title) asserted ==
plan), url (for a commons doc: doc["url"] = media/commons/<site>/<plan-without-c_>.jpg
repo-relative, the pattern of all 306e items; for a books doc: check what the existing
book-doc items use), pairs (the doc's own), coarse False, evidence (fr.candidate_
evidence(plan) - returns None if the row is missing/unevidenced; assert non-None;
kind category OR hand_tied), label, cite, ref, size, place_reason '306e audit
2026-10-13: ... Document deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new
plans APPEND, the lead/file name stay (an item with this plan already present gets
the entry replaced in place); a site with no item gets CREATED (lead = the one
candidate); then os.remove the doc; then fr.export(fr.ROOT, site) (scoped; keeps
other branches' re-stamps - see PITFALLS under tools/site_done.py, fit/review.py).
**upsert_item returns an ABSOLUTE path** - assert the basename. An item with no
candidate docs stays open (resolved None; the site stays covered for the union
check). Export counts: a NEW item adds one to BOTH open and total (194: (345,358) ->
(346,359); 196: (346,359) -> (347,360)); an APPEND leaves both unchanged (191, 193).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs
(/tmp/aw306e_fit.py still alive); inverse-map the site point; build the 800 m box
LAYERS composite (/tmp/aw306e_layers.py, output name = d[-17:], /tmp/_<plan-suffix>.
{1842,plate,relief}.png) - 1842 six-inch-1st_ink.webp red-on-white, plate
luminance-ink mask (lo 118 / hi 200) blue-on-white via atv + bilinear, relief grey;
100 m grid + 100-500 m circles centred on the site point; raw jpgs at
data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the doc's sizes (books:
data/books/full/...); for a DENSE/hatched plate read the composite/screenshots, not
an ink histogram (182 PITFALLS); for stone-scale works the relief's dark dots decide
(194 PITFALLS); for a whole-complex displacement the repo 1842 webp may not even
cover the real works - then modern Esri aerial (VM has internet; z18 tile math: x =
((lon+180)/360)*2^z, y = (1 - asinh(tan(lat_rad))/pi)/2*2^z - 195 DECISIONS gotcha,
0.376 m/px at 51 N) and the web are the deciding layers. The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp
was wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 14 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby,
richborough, stanton-drew, taunton - between the 306d block and '## The site markers
become arrowheads (task 308, 2026-10-13)') - continue it after the taunton line. DONE
sites (do not touch again): offa (KEEP), okehampton (KEEP), old-sarum (item holds
both), oxford (new item), pilsbury (KEEP), pontefract (item holds the c_d135
append), portus (item holds both portus candidates), raby (new open item, lead
c_fe1d6c7f0ba858cb), richborough (item now holds [c_1dcd5a7171573663,
c_edad7da41d234534]), stanton-drew (new open item, lead c_59a5c636a9e00703), taunton
(new open item, lead c_05cb4a02bd58e82e, created 196).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 14 of 17
lines; tick when all 17 are in. Box 3 PARTIAL: 10 deletions executed (old-sarum x2,
oxford, pontefract c_d135, portus x2, raby, richborough, stanton-drew, taunton);
the rest awaits the final 2 sites' verdicts (york x2 = two docs; windmill-hill x1).
Box 4 satisfied so far (no `by: hand` doc touched; suite = baseline at the 196 run).
