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
(2026-10-13, iteration 191, agent c - **judged the twin portus c_4912bb54aa79f3ea: DELETED
the 303 way, APPENDED to the existing portus item (lead/file name stayed c_42bedb90fffce1d4),
scoped export (344, 357), 10th of 17 lines written. Suite 154/1/1 = baseline, no new red.
NEXT: raby-castle c_fe1d6c7f0ba858cb (Mackenzie 1897, NO item - create if deleted).**

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed**. The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's
in-flight 307). Expect exactly that in every run; any other failure = my new red. Latest
log /tmp/aw306e_suite191.log (may be wiped; numbers in the 191 DECISIONS entry).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181);
okehampton-castle c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED
(183); old-sarum c_041083ec68b532f8 DELETED (183); oxford-castle
c_ba6b308580428184 DELETED (184/185); pilsbury-castle c_7ff765c177ca7bae KEEPS (187);
pontefract-castle c_3213330a52fe6018 KEEPS (188); pontefract-castle
c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4 DELETED, executed
(190); portus-adurni c_4912bb54aa79f3ea **DELETED, executed (191)**. **6 docs (5 sites)
remain:** raby, richborough, stanton-drew, taunton, windmill-hill n0558_2, york x2.

**What 191 did:**
1. **Judged portus c_4912bb54aa79f3ea** ('Burg von Portchester (GB) Plan von 1836 aus der
   Penny Cyclopaedia, Seite 354' = the German-titled twin of the plate deleted at 190;
   same 1280x1292 Penny Cyclopaedia 1836 v6 p 354 scan). The 6 stored pairs replicate to
   1.0000 m/px, -0.00 deg, residuals 0.0 (/tmp/aw306e_fit.py, still alive in /tmp): the
   perfect 900-px grid ladder (corners (100,1000)/(100,100)/(1000,1000)/(1000,500) + centre
   (800,800)), no placement information; the site point inverse-maps to plate (799.5,
   799.5) - the open interior just NW of the drawn Church of St Mary, exactly as on its
   twin. The committed shots (aerial + relief) show the identical drawn geometry (huge
   outer-wall square offset NW; only St Mary's near its real church). VERDICT: DELETED
   the 303 way.
2. **Executed the 303 way** (script, `sys.path.insert(0,"fit"); import review as fr`):
   entry2 = {plan c_4912bb54aa79f3ea, title 'File:Burg von Portchester (GB) Plan von 1836
   aus der Penny Cyclopaedia, Seite 354.jpg' (fr._sha16 asserted == plan), url
   media/commons/portus-adurni-q762664/4912bb54aa79f3ea.jpg, pairs (the doc's 6), coarse
   False, evidence (files.jsonl line 654: rec evidence/1, kind category, checked
   2026-10-10, site_cat/file_cat 'Portus Adurni', via []), label '1836', cite (the doc's),
   ref (the doc's, 'File: ' prefix kept), size [1280,1292], place_reason '306e audit
   2026-10-13: similarity (6 pts, resid 0.0 m, 1.00 m/px, -0.0 deg)... the German-titled
   twin of the deleted c_42bedb90fffce1d4: same source, same plate and drawn geometry...
   Wrong place, wrong size, right kind. Document deleted.'}; fr.upsert_item returned the
   SAME file data/review/portus-adurni-q762664.c_42bedb90fffce1d4.json (_find_item
   matches by the SITE field; the new plan APPENDS after the lead; lead + file name
   unchanged); os.remove the doc; fr.export(fr.ROOT, "portus-adurni-q762664") -> (344,
   357) unchanged (the item stays open: neither candidate has a doc). Verified: item and
   page entry both = [c_42bedb90fffce1d4, c_4912bb54aa79f3ea], resolved None,
   no_picture_found None.
3. **Wrote the 10th of 17 lines** in the 306e block of docs/site_flow.md (after the
   portus c_42bedb line, before '## The site markers become arrowheads (task 308,
   2026-10-13)'), same format, saying it was APPENDED to the existing portus item.
4. **Suite 154/1/1** = the post-merge baseline (no new red; union/coverage green - portus
   stays covered by its open item).

**NEXT STEP - judge raby-castle-q4583646.c_fe1d6c7f0ba858cb** (Mackenzie, The Castles of
England 1897; the doc is data/db/platefits/raby-castle-q4583646.c_fe1d6c7f0ba858cb.json).
(a) `.venv/bin/python /tmp/aw306e_fit.py raby-castle-q4583646.c_fe1d6c7f0ba858cb` for the
fit stats + where the site point lands on the plate (the script prints anchor offsets and
the site-point inverse-map; if /tmp was wiped, the pattern is in the 188/189/190
DECISIONS entries: least squares over w=[u,-v]; at(u,v) takes PAGE coords - v_page, NOT
the flipped w; the 182 simFit-inversion PITFALLS is the reference). (b) Read the
committed shots docs/site_flow/agent_fits/raby-castle-q4583646_c_fe1d6c7f0ba858cb.png +
_relief.png (both exist from box 1). (c) If the drawn works visibly miss the real ones:
build the 800 m box LAYERS composite (1842 six-inch-1st_ink.webp red-on-white, plate
luminance-ink mask (lo 118 / hi 200) blue-on-white via atv + bilinear, relief grey; 100 m
grid + 100-500 m circles centred on the site point; the raw jpg at
data/raw/commons/raby-castle-q4583646/fe1d6c7f0ba858cb.jpg is exactly the doc's size) and
judge on it; for a DENSE/hatched plate read the composite/screenshots, not an ink
histogram (182 PITFALLS). (d) DELETED -> the 303 way: **the site has NO item - upsert_item
CREATES data/review/raby-castle-q4583646.c_fe1d6c7f0ba858cb.json with this doc as lead**
(entry = {plan, title (the files.jsonl row title WITH its 'File: ' prefix, fr._sha16
asserted == plan), url, pairs (the doc's own), coarse False, evidence (fr.candidate_evidence
(plan) - the files.jsonl row; verify it exists and returns the dict before use), label,
cite, ref, size, place_reason '306e audit 2026-10-13: ... Document deleted.'}); then
os.remove the doc; then fr.export(fr.ROOT, "raby-castle-q4583646") - the portus export
went from (343,356) to (344,357) when a NEW item was created, so expect (345, 357) now
(re-verify the two counts against the page file after: open items vs total). KEEPS ->
just the 11th line.
**After raby, 5 docs (4 sites):** richborough-roman-fort c_edad7da41d234534 (Penny
Cyclopaedia 1836 v6 p 353; existing item [c_1dcd5a7171573663] -> APPEND);
stanton-drew-stone-circles c_59a5c636a9e00703 (Penny Magazine 1836 druidical temple; NO
item -> create); taunton-castle c_05cb4a02bd58e82e (Mackenzie 1897; NO item -> create);
windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908 'WINDMILL SITES,
LEWES DOWN', **model None** - the page's default plan model fits it: relief shot resid 0,
1.0 m/px, 0 deg; the site's item already holds n0557_1 + n0558_1 -> if deleted, APPEND to
THAT item, do not create a second); york-castle-q80637 c_8dac5aacd73916b8 ('York Castle
in 1820' watercolour, score 31.7) + c_a7db545536f13e24 ('Plan of Center, Broome County
1855' = Center is a TOWN in Broome County, NEW YORK - toponymic-collision class, almost
certainly DELETED wrong place; existing item [c_81ecab4a9284f156 + 4 more] -> append).

**The 303 way (summary; full recipe in the 189/190/191 DECISIONS entries):** fit/review.py
API, no hand-edited JSON. entry = {plan, title (the files.jsonl row title WITH its
'File: ' prefix, fr._sha16-asserted == plan), url, pairs (the doc's own), coarse False,
evidence (fr.candidate_evidence(plan) - returns None if the row is missing/unevidenced;
assert non-None), label, cite, ref, size, place_reason '306e audit 2026-10-13: ...
Document deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new plans APPEND, the
lead/file name stay; a site with no item gets CREATED (lead = the one candidate); then
os.remove the doc; then fr.export(fr.ROOT, site) (scoped: writes `resolved` only into
that site's item file; recomputes the whole page file - that is intended and keeps other
branches' re-stamps, see PITFALLS under tools/site_done.py, fit/review.py). An item with
no candidate docs stays open (resolved None; the site stays covered for the union check).

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

**Re-read:** the 306e block in docs/site_flow.md (header + the 10 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2 - between the 306d
ludlow line and '## The site markers become arrowheads (task 308, 2026-10-13)') -
continue it after the portus c_4912 line. data/review/portus-adurni-q762664.
c_42bedb90fffce1d4.json now holds BOTH portus candidates (lead c_42bedb90fffce1d4 +
c_4912bb54aa79f3ea) - the portus site is DONE, do not touch it again.

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 10 of 17 lines;
tick when all 17 are in. Box 3 PARTIAL: 6 deletions executed (old-sarum x2, oxford,
pontefract c_d135, portus x2); the rest awaits the remaining 6 verdicts. Box 4
satisfied so far (no `by: hand` doc touched; suite = baseline, re-verified at the 191
run).
