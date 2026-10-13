Status: open
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
(2026-10-13, iteration 192, agent c - **judged raby-castle c_fe1d6c7f0ba858cb (Mackenzie 1897):
DELETED the 303 way, NEW review item created (lead = this doc), scoped export (345, 358), 11th
of 17 lines written. Suite 154/1/1 = baseline, no new red. NEXT: richborough c_edad7da41d234534
(existing item -> APPEND).**

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed**. The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Expect exactly that in every run; any other failure = my new red. Latest
log /tmp/aw306e_suite192.log (may be wiped; numbers in the 192 DECISIONS entry).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181);
okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED
(183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED, executed
(190); portus-adurni c_4912bb54aa79f3ea DELETED, executed (191); raby-castle
c_fe1d6c7f0ba858cb **DELETED, executed (192)**. **6 docs (5 sites) remain:** richborough,
stanton-drew, taunton, windmill-hill n0558_2, york x2. (Correction to 191: its "6 docs (5
sites)" actually listed 7 docs - raby was forgotten in the count; the list was right.)

**What 192 did:**
1. **Judged raby-castle c_fe1d6c7f0ba858cb** ('Raby Castle, plan from Mackenzie, The Castles
   of England (1897)'). The 4 stored pairs = the plate's 900-px corner square -> 0.6667 m/px,
   0.0 deg, all residuals 0.0 (ladder class: no placement information; the fit pins the plate
   centre (549,549) of [1280,1080] onto the site point). The drawing is an idealised 1897
   castle complex filling the whole 600 m fit box (plate = 853 x 720 m on the ground): Great
   Keep, Great Hall, Gate House, Main Street, Market Cross, St Mary's, N/S Towers. Real Raby
   Castle (1842 six-inch + LiDAR): a ~50 m ruin on a ~90 m round terrace with a moat, centred
   on the site point just north of Low Pond. Drawn features on open parkland (Gate House
   E-139 N-214, St Mary's E-93 N+45, N Tower E+34 N+281, S Tower E+34 N-12). ~10x too big,
   works miss. VERDICT: DELETED the 303 way.
2. **Executed the 303 way** (script, `sys.path.insert(0,"fit"); import review as fr`):
   verified `fr._find_item` == (None,None) first; entry = {plan c_fe1d6c7f0ba858cb, title
   'File:Plan of Raby Castle (1897).jpg' (fr._sha16 asserted == plan; the row title has NO
   space after the colon), url media/commons/raby-castle-q4583646/fe1d6c7f0ba858cb.jpg,
   pairs (the doc's 4), coarse False, evidence (files.jsonl line 1456: rec evidence/1,
   kind hand_tied, checked 2026-10-10, source 'pipeline/sources.py mackenzie'), label
   '1897', cite (the doc's), ref (the doc's), size [1280,1080], place_reason '306e audit
   2026-10-13: ... Document deleted.'}; fr.upsert_item CREATED data/review/
   raby-castle-q4583646.c_fe1d6c7f0ba858cb.json (lead = this plan, sole candidate);
   os.remove the doc; fr.export(fr.ROOT, "raby-castle-q4583646") -> **(345, 358)**: a NEW
   item adds to BOTH the open count (344->345) and the total (357->358). Verified: item
   [c_fe1d6c7f0ba858cb], resolved None, no_picture_found None; page entry under 'Raby
   Castle'; page items 345 == open, item files 358 == total. git status: exactly 3 files
   (D doc, M web/data/review.json, ?? new item) - no other site's item touched.
3. **Wrote the 11th of 17 lines** in the 306e block of docs/site_flow.md (after the portus
   c_4912 line, before '## The site markers become arrowheads (task 308, 2026-10-13)'), same
   format as the portus line (a NEW review item - the site had none before).
4. **Suite 154/1/1** = the post-merge baseline (no new red; union/coverage green - raby
   stays covered by its new open item).

**NEXT STEP - judge richborough-roman-fort-q1309736.c_edad7da41d234534** ('Richborough
Castle, derived from the Penny Cyclopaedia (1836) v6 p 353' - the SAME volume/series as the
two deleted portus docs; the doc is data/db/platefits/
richborough-roman-fort-q1309736.c_edad7da41d234534.json). The site HAS an existing review
item: data/review/richborough-roman-fort-q1309736.c_1dcd5a7171573663.json (lead
c_1dcd5a7171573663) - if DELETED, APPEND to THAT item (lead/file name stay unchanged); no
new item. (a) `.venv/bin/python /tmp/aw306e_fit.py
richborough-roman-fort-q1309736.c_edad7da41d234534` for the fit stats + the site-point
inverse-map (script still in /tmp; if /tmp was wiped, the pattern is in the 188-192
DECISIONS entries: least squares over w=[u,-v]; at(u,v) takes PAGE coords - v_page, NOT the
flipped w; the 182 simFit-inversion PITFALLS is the reference). (b) Read the committed
shots docs/site_flow/agent_fits/richborough-roman-fort-q1309736_c_edad7da41d234534.png
+ _relief.png (both exist from box 1). (c) If the drawn works visibly miss the real ones:
build the 800 m box LAYERS composite with `.venv/bin/python /tmp/aw306e_layers.py <docid>`
(generic; writes /tmp/<last-17-chars-of-docid>.{1842,plate,relief}.png; 1842
six-inch-1st_ink.webp red-on-white, plate luminance-ink mask lo 118 / hi 200 blue-on-white
via atv + bilinear, relief grey; 100 m grid + 100-500 m circles centred on the site point;
raw jpg at data/raw/commons/richborough-roman-fort-q1309736/edad7da41d234534.jpg) and judge
on it; for a DENSE/hatched plate read the composite/screenshots, not an ink histogram (182
PITFALLS). /tmp/aw306e_raby2.py is the measurement template (real-ruin densest block +
drawn feature centres). (d) DELETED -> the 303 way with an APPEND (expect the export counts
to STAY (345, 358) - the item already exists and stays open; re-verify the page entry lists
both plans, lead first). KEEPS -> just the 12th line.
**After richborough, 5 docs (4 sites):** stanton-drew-stone-circles c_59a5c636a9e00703
(Penny Magazine 1836 'druidical temple at Stanton Drew'; NO item -> create if deleted);
taunton-castle c_05cb4a02bd58e82e (Mackenzie 1897 - same source as the deleted raby doc; NO
item -> create); windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908
'WINDMILL SITES, LEWES DOWN', **model None** - the page's default plan model fits it:
relief shot resid 0, 1.0 m/px, 0 deg; the site's item already holds n0557_1 + n0558_1 ->
if deleted, APPEND to THAT item, do not create a second); york-castle-q80637
c_8dac5aacd73916b8 ('York Castle in 1820' watercolour, score 31.7) + c_a7db545536f13e24
('Plan of Center, Broome County 1855' = Center is a TOWN in Broome County, NEW YORK -
toponymic-collision class, almost certainly DELETED wrong place; existing item
[c_81ecab4a9284f156 + 4 more] -> append).

**The 303 way (summary; full recipe in the 189/190/191/192 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the files.jsonl row title
WITH its 'File:' prefix - no space after the colon; fr._sha16 asserted == plan), url,
pairs (the doc's own), coarse False, evidence (fr.candidate_evidence(plan) - returns None
if the row is missing/unevidenced; assert non-None; the kind is category OR hand_tied),
label, cite, ref, size, place_reason '306e audit 2026-10-13: ... Document deleted.'};
fr.upsert_item(fr.ROOT, site, [entry]) - new plans APPEND, the lead/file name stay; a site
with no item gets CREATED (lead = the one candidate); then os.remove the doc; then
fr.export(fr.ROOT, site) (scoped: writes `resolved` only into that site's item file - the
page file is recomputed over the whole queue, which is intended and keeps other branches'
re-stamps, see PITFALLS under tools/site_done.py, fit/review.py). An item with no
candidate docs stays open (resolved None; the site stays covered for the union check).
Export counts: a NEW item adds one to BOTH open and total (192: (344,357) -> (345,358));
an APPEND to an existing item leaves both unchanged (191: (344,357)).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs;
inverse-map the site point; build the 800 m box LAYERS composite (1842 six-inch-1st_ink.webp
red-on-white, plate luminance-ink mask (lo 118 / hi 200) blue-on-white via atv +
bilinear, relief grey; 100 m grid + 100-500 m circles centred on the site point; raw
jpgs at data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the doc's sizes); for
a DENSE/hatched plate read the composite/screenshots, not an ink histogram (182
PITFALLS). Where size is in question: 1842 ink density in 25 m annuli / 16 az bins
(i*22.5 in a plain list, NOT range(0,360,22.5)). The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp was
wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 11 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby - between the
306d block and '## The site markers become arrowheads (task 308, 2026-10-13)') - continue
it after the raby line. DONE sites (do not touch again): portus (item holds both portus
candidates) and raby (new open item, lead c_fe1d6c7f0ba858cb).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 11 of 17 lines;
tick when all 17 are in. Box 3 PARTIAL: 7 deletions executed (old-sarum x2, oxford,
pontefract c_d135, portus x2, raby); the rest awaits the remaining 5 verdicts (6 docs:
york x2 counts as two). Box 4 satisfied so far (no `by: hand` doc touched; suite =
baseline, re-verified at the 192 run).
