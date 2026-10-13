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
(2026-10-13, iteration 194, agent c - **judged stanton-drew-stone-circles c_59a5c636a9e00703
(Penny Magazine 1836 116): DELETED the 303 way, site had NO item -> CREATED a new one with
this doc as lead (export 346/359), 13th of 17 lines written. Suite 154/1/1 = baseline, no
new red. NEXT: taunton-castle c_05cb4a02bd58e82e (Mackenzie 1897; NO item -> create).**

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed**. The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Expect exactly that in every run; any other failure = my new red. Latest
log /tmp/aw306e_suite194.log (may be wiped; numbers in the 194 DECISIONS entry).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181);
okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED
(183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED (190);
portus-adurni c_4912bb54aa79f3ea DELETED (191); raby-castle c_fe1d6c7f0ba858cb DELETED
(192); richborough-roman-fort c_edad7da41d234534 DELETED (193); stanton-drew-stone-circles
c_59a5c636a9e00703 DELETED, executed (194). **4 docs (3 sites) remain:** taunton,
windmill-hill n0558_2, york x2.

**What 194 did:**
1. **Judged stanton-drew c_59a5c636a9e00703** ('Penny Magazine 1836 116 Plan of the
   Druidical Temple at Stanton Drew'). Fit replicated: 1.0000 m/px, -0.00 deg, all 6
   residuals 0.0 (/tmp/aw306e_fit.py, still in /tmp): the 6 anchors are a 100-px diagonal
   ladder (100,100)..(600,600); the site point inverse-maps to plate (499.5, 499.5) of
   [1280,1551] = the 5th anchor - the fit pins the plate centre onto the site point, no
   placement information (ladder class). The plate is a genuine plan of the circle group
   (Great Circle, Circle of 8, South-west Circle, The Cove, Hackett's Quoit, River Chew -
   right names/layout vs the 1842 six-inch and LiDAR) drawn at ~10 m/px. Measured
   (scripts in /tmp: _stzoom/_stcluster/_strel/_string): drawn Great Circle = 879 dots,
   least-sqs centre plate (657,653) r=218 px = 435 m across, centred E+157 N-153; the real
   stone cluster = ~50 m of dark dots at E+100..150 N-50 on the LiDAR relief (the 1842
   webp is 666 px/800 m - stones sub-pixel there; NEW PITFALLS: the relief's dark dots are
   the deciding layer for stone-circle sites); the drawn Circle of 8 (E-91 N+240) and
   South-west Circle (E+705 N-554) sit on open farmland (the real SW circle is near Church
   Farm, E-100 N-200); the drawn river lies west of the real River Chew. ~4-10x too big.
   VERDICT: DELETED the 303 way.
2. **Executed the 303 way** (script /tmp/aw306e_stexec.py): fr._find_item (None, None)
   BEFORE; entry = {plan, title 'File:Penny Magazine 1836 116 Plan of the Druidical
   Temple at Stanton Drew.jpg' (fr._sha16 asserted == plan; files.jsonl line 707), url
   media/commons/stanton-drew-stone-circles-q1516300/59a5c636a9e00703.jpg, pairs (the 6),
   coarse False, evidence (line 707: category, 'Stanton Drew stone circles'), label
   '1836', cite+ref, size [1280,1551], place_reason '306e audit 2026-10-13: ... Document
   deleted.'}; fr.upsert_item CREATED data/review/stanton-drew-stone-circles-q1516300.
   c_59a5c636a9e00703.json (lead = this plan, sole candidate) - GOTCHA: it returns an
   ABSOLUTE path, my relative-string assert tripped after the write (NEW PITFALLS under
   fit/); doc deleted; fr.export -> **(346, 359)** (a NEW item adds one to BOTH open and
   total, as predicted); item + page entry = [c_59a5c636a9e00703], resolved None,
   no_picture_found None. git status: exactly 3 files (D doc, M web/data/review.json, ??
   item) - no other site's item touched.
3. **Wrote the 13th of 17 lines** in the 306e block of docs/site_flow.md (after the
   richborough line, before '## The site markers become arrowheads (task 308, 2026-10-13)')
   and the two new PITFALLS entries.
4. **Suite 154/1/1** = baseline (no new red; union/coverage green - stanton-drew stays
   covered by its new open item).

**NEXT STEP - judge taunton-castle-q7688781.c_05cb4a02bd58e82e** ('Taunton Castle, plan
from Mackenzie, The Castles of England (1897)' - same source as the deleted raby doc
c_fe1d6c7f0ba858cb, which was the ~10x-too-big idealised-complex class). The site has
**NO** review item - if DELETED, CREATE one (lead = this plan, sole candidate; expect
(346,359) -> **(347, 360)**). (a) `.venv/bin/python /tmp/aw306e_fit.py
taunton-castle-q7688781.c_05cb4a02bd58e82e` for fit stats + site-point inverse-map
(/tmp still has the scripts; if wiped, the pattern is in the 188-194 DECISIONS entries).
(b) Read the committed shots docs/site_flow/agent_fits/
taunton-castle-q7688781_c_05cb4a02bd58e82e.png + _relief.png. (c) If the drawn works
visibly miss: build the LAYERS composite (`.venv/bin/python /tmp/aw306e_layers.py
taunton-castle-q7688781.c_05cb4a02bd58e82e` -> /tmp/_05cb4a02bd58e82e.{1842,plate,
relief}.png - d[-17:] naming; raw jpg data/raw/commons/taunton-castle-q7688781/
05cb4a02bd58e82e.jpg) and judge on it (dense/hatched plate -> read the composite, not an
ink histogram; for earthwork-scale works the 1842 hachure/ink extent is fine, for
stone-scale works use the relief's dark dots - new PITFALLS). (d) DELETED -> the 303 way
with a NEW item (verify fr._find_item == (None, None) before the upsert; assert
fr.candidate_evidence(plan) non-None). KEEPS -> just the 14th line.
**After taunton, 3 docs (2 sites):** windmill-hill-q4348373.
earthworkenglan01allcgoog_n0558_2 (Allcroft 1908 'WINDMILL SITES, LEWES DOWN', **model
None** - the page's default plan model fits it: relief shot resid 0, 1.0 m/px, 0 deg; the
site's item already holds n0557_1 + n0558_1 -> if deleted, APPEND to THAT item, do not
create a second); york-castle-q80637 c_8dac5aacd73916b8 ('York Castle in 1820' watercolour,
score 31.7) + c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a TOWN
in Broome County, NEW YORK - toponymic-collision class, almost certainly DELETED wrong
place; existing item [c_81ecab4a9284f156 + 4 more] -> append).

**The 303 way (summary; full recipe in the 189-194 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the files.jsonl row title
WITH its 'File:' prefix - no space after the colon; fr._sha16(title) asserted == plan),
url, pairs (the doc's own), coarse False, evidence (fr.candidate_evidence(plan) - returns
None if the row is missing/unevidenced; assert non-None; kind category OR hand_tied),
label, cite, ref, size, place_reason '306e audit 2026-10-13: ... Document deleted.'};
fr.upsert_item(fr.ROOT, site, [entry]) - new plans APPEND, the lead/file name stay (an
item with this plan already present gets the entry replaced in place - the stanton-drew
re-run proved idempotence); a site with no item gets CREATED (lead = the one candidate);
then os.remove the doc; then fr.export(fr.ROOT, site) (scoped: writes `resolved` only
into that site's item file - the page file is recomputed over the whole queue, intended;
keeps other branches' re-stamps - see PITFALLS under tools/site_done.py, fit/review.py).
**upsert_item returns an ABSOLUTE path** (PITFALLS) - assert the basename. An item with
no candidate docs stays open (resolved None; the site stays covered for the union check).
Export counts: a NEW item adds one to BOTH open and total (194: (345,358) -> (346,359));
an APPEND to an existing item leaves both unchanged (191, 193: (345,358)).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs;
inverse-map the site point; build the 800 m box LAYERS composite (1842
six-inch-1st_ink.webp red-on-white, plate luminance-ink mask (lo 118 / hi 200)
blue-on-white via atv + bilinear, relief grey; 100 m grid + 100-500 m circles centred on
the site point; raw jpgs at data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the
doc's sizes); for a DENSE/hatched plate read the composite/screenshots, not an ink
histogram (182 PITFALLS); for stone-scale works the relief's dark dots decide (194
PITFALLS). Where size is in question: 1842 ink density in 25 m annuli / 16 az bins
(i*22.5 in a plain list, NOT range(0,360,22.5)). The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp was
wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 13 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby, richborough,
stanton-drew - between the 306d block and '## The site markers become arrowheads
(task 308, 2026-10-13)') - continue it after the stanton-drew line. DONE sites (do not
touch again): portus (item holds both portus candidates), raby (new open item, lead
c_fe1d6c7f0ba858cb), richborough (existing item now holds [c_1dcd5a7171573663,
c_edad7da41d234534]), stanton-drew (new open item, lead c_59a5c636a9e00703).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 13 of 17 lines;
tick when all 17 are in. Box 3 PARTIAL: 9 deletions executed (old-sarum x2, oxford,
pontefract c_d135, portus x2, raby, richborough, stanton-drew); the rest awaits the
remaining 3 verdicts (york x2 counts as two). Box 4 satisfied so far (no `by: hand` doc
touched; suite = baseline, re-verified at the 194 run).
