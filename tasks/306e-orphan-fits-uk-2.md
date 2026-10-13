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
(2026-10-13, iteration 195, agent c - **judged taunton-castle c_05cb4a02bd58e82e
(Mackenzie 1897): DELETED - wrong place, the ~640 m site-point-shift class. VERDICT ONLY
this session (investigation complete); the 303-way execution + 14th line + suite are the
NEXT session's step.**)

**Baseline (unchanged since the 190 main merge, commit 9f92b3a):** full suite
`.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min) = **154 passed, 1
skipped, 1 failed** (last run: the 194 run; NOT re-run in 195 - no code changed this
session, git tree was clean). The ONLY known red:
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
c_59a5c636a9e00703 DELETED, executed (194); **taunton-castle c_05cb4a02bd58e82e JUDGED
DELETED (195), execution pending**. **3 docs (2 sites) remain after taunton:**
windmill-hill n0558_2, york x2.

**What 195 did (judgement of taunton-castle c_05cb4a02bd58e82e; no files touched):**
1. Fit replicated (.venv/bin/python /tmp/aw306e_fit.py, script still alive):
   **0.5000 m/px, +0.00 deg, 4 residuals 0.0**; anchors plate (800,200),(800,400),
   (800,800),(400,1000) -> E+100 N+199, E+100 N+99, E+100 N-100, E-99 N-200 = a 200-px
   (100 m) grid ladder, no placement information. Site point (-3.11380, 51.0153)
   inverse-maps to plate **(599,599) of [1280,1461]** = near-centre: the fit pins the
   plate centre on the site point.
2. LAYERS composites rebuilt (/tmp/aw306e_layers.py -> /tmp/_05cb4a02bd58e82e.
   {1842,plate,relief}.png; plus an overlay script I wrote inline: /tmp/_05cb4a02bd58e82e
   .overlay.png = 1842 red + plate blue, and /tmp/_05cb4a02bd58e82e.map42.png = the FULL
   1842 six-inch-1st.webp (the site dir has it, 533 px over the 800 m box - coarse, but
   the base map) + plate blue; all may be wiped, committed shots are the fallback).
   The site's 1842 webp covers ONLY the 800 m corners box, so it does not even contain
   the real castle (see 4).
3. **The real Taunton Castle is ~640 m EAST of the catalog site point** (the key fact):
   Wikipedia 'Taunton Castle' (en.wikipedia.org/wiki/Taunton_Castle, fetched this
   session) gives **51.0158 N, 3.1046 W = E+643, N+55 m from the site point**: a living
   castle - the inner ward/Great Hall (37 m x 9 m) is the **Museum of Somerset** (opened
   2011), the outer ward is two crenellated hotels, the outer bailey is the modern
   'Castle Green'. Verified on modern Esri World_Imagery z18 (this VM HAS internet;
   tiles at z18: 128811/87787 region - /tmp/taunton_castle_z18.png + _grid +
   tt_castle_zoom.png if alive): the red-roofed Great Hall complex + hotel row + a
   tree-lined moat ring + the green sit exactly at the Wikipedia point, the Tone on the
   NW, a railway on the E. (Earlier I fetched z19 at 257609/175484 and z18 at 257609/
   175484/2 - wrong tile math, y needs asinh(tan)/pi; the centre-point z18 5x5 at
   /tmp/taunton_z18.png was correct.)
4. **Drawn works vs real works (measured off the plate composite, 1 m/px, site point
   (400,400)):** N. Gate E+140 N+150; Great Hall E+55 N+110; Outwork E+145 N+100; Inner
   Bailey E+50 N+60; 'Site of Saxon Castle' E+165 N+25; Inner Moat (now filled in, label)
   E+50 N-20; Outer Bailey E+30 N-90; Bo Langford E+90 N-90; Bishop's House E+145 N-90;
   Castle Green E+50 N-170; E. Gate E+190 N-170; Bp Fox's E-5 N-230; College-School
   E-10 N-265; Outer Moat (south edge) E+30 N-315; Porwater (left edge) E-205 N-30;
   Barbican E-185 N-90. Plate ground extent E-299.5..+340.5, N-191..+299.5. So the whole
   drawn complex (E-205..+190) sits on the 1842's **Wellington Terrace house cluster**
   (big dark hatched building right at the site point E-25..+40 N-50..+10 + the hatched
   house row W of it) and on the 'Stepps Water' dotted stream (E+50 N+62 -> E+95 N-125)
   - houses and a stream, no castle, no moat, no 'Castle' label anywhere in the 800 m
   box. The drawn river band (N+175..+250) does match the real Tone near the site point
   (z18: E+98..+143, N+100..+150; 1842: E+65..+103, N+84..+400) - that is how the agent's
   anchors (E+100, N+199/N+99) locked the plate. The real castle (E+643) is 545-655 m
   EAST of the drawn complex, beyond the plate's E+340.5 edge AND beyond the 800 m site
   box (E+400 max) - the 1842 webp in the repo does not even show it.
   **VERDICT: DELETED the 303 way** - wrong place (the oxford-castle/bury-castle class;
   the oxford line's 'wrong place, right kind' fits: this IS the genuine 1897 plan of
   THIS castle - features match the real complex: Great Hall/inner ward, outwork,
   filled-in moats, Castle Green = outer bailey, E. gate, Bishop Foxe's school - so the
   picture is worth keeping in the review item; the fit's site point is the error).
5. **Site state verified:** `ls data/review/ | grep taunton` = **NO item**; depictions
   .json holds only the 1842 map (orphan confirmed). files.jsonl **line 1457**: title
   **'File:Plan of Taunton Castle (1897).jpg'** (fr._sha16 asserts == plan), by
   'pipeline/sources.py mackenzie', **evidence {rec evidence/1, kind HAND_TIED,
   checked 2026-10-10, source 'pipeline/sources.py mackenzie'}**, url
   https://upload.wikimedia.org/wikipedia/commons/b/b3/Plan_of_Taunton_Castle_%281897%
   29.jpg... (use the row's url verbatim), page = the commons page. Doc size [1280,1461].

**NEXT STEP (session 196) - execute taunton the 303 way with a NEW item, then line 14:**
1. Script (pattern /tmp/aw306e_stexec.py, still alive): sys.path.insert(0,'fit');
   import review as fr; doc = json.load('data/db/platefits/taunton-castle-q7688781.
   c_05cb4a02bd58e82e.json'); site='taunton-castle-q7688781'. First assert
   fr._find_item(fr.ROOT, site) == (None, None) AND fr.candidate_evidence(doc['plan'])
   non-None (it is the hand_tied row 1457 above). entry = {plan c_05cb4a02bd58e82e,
   title 'File:Plan of Taunton Castle (1897).jpg', url (row's), pairs (the doc's 4),
   coarse False, evidence (the row's - kind hand_tied, source 'pipeline/sources.py
   mackenzie'), label '1897', cite+ref (the doc's), size [1280,1461], place_reason
   '306e audit 2026-10-13: similarity (4 pts, resid 0.0 m, 0.5 m/px, +0.0 deg; 200-px
   grid ladder, site point at plate centre (599,599) of [1280,1461]) ... genuine 1897
   plan of this castle (Mackenzie: Great Hall/inner ward, outwork, filled-in moats,
   Castle Green = outer bailey) but pinned ~545-655 m WEST of the real works - the
   catalog site point itself sits ~640 m west of the castle (real: 51.0158, -3.1046 =
   Museum of Somerset, east bank of the Tone); the drawn complex lands on the 1842
   Wellington Terrace house cluster and the Stepps Water stream, no works there. Wrong
   place, right kind. Document deleted.'} (tighten to the established style; end '...Document deleted.').
2. fr.upsert_item(fr.ROOT, site, [entry]) -> CREATES data/review/taunton-castle-
   q7688781.c_05cb4a02bd58e82e.json (lead = this plan, sole candidate). **Returns an
   ABSOLUTE path - assert the basename, not a repo-relative string (PITFALLS).**
3. os.remove the doc; fr.export(fr.ROOT, site) -> expect **(346,359) -> (347, 360)**
   (NEW item adds one to BOTH open and total, as 194 proved).
4. Verify: item file = [c_05cb4a02bd58e82e], resolved None, no_picture_found None; page
   entry under name 'Taunton Castle' shows it; git status = exactly 3 files (D doc, M
   web/data/review.json, ?? item).
5. **Write the 14th of 17 lines** in the 306e block of docs/site_flow.md (after the
   stanton-drew line, before '## The site markers become arrowheads (task 308,
   2026-10-13)') - same shape as the raby/oxford lines; state: ladder pins the plate
   centre on the site point; the plate is the genuine Mackenzie 1897 plan of this castle
   (features match the real works - today the Museum of Somerset + crenellated hotels +
   moat + Castle Green); the site point is ~640 m WEST of the real castle (51.0158,
   -3.1046, E+643 N+55, east bank of the Tone, confirmed on modern aerial + Wikipedia),
   so the drawn complex (E-205..+190) sits on the Wellington Terrace houses and the
   Stepps Water stream where the 1842 shows no works; the real castle is beyond the
   plate's edge. DELETED - an orphan today, invisible on the page (the 303 way: the
   picture and its 4 points went to a NEW review item for the site with this reason -
   the site had none before - the document was deleted, the site's review page file
   re-exported scoped to the site; the site stays covered by the new open item).
6. Run the full suite (expect 154/1/1 = baseline).
7. **Then the last 2 sites (3 docs):** windmill-hill-q4348373.earthworkenglan01allcgoog_
   n0558_2 (Allcroft 1908 'WINDMILL SITES, LEWES DOWN', **model None** - the page's
   default plan model fits it: relief shot resid 0, 1.0 m/px, 0 deg; the site's item
   already holds n0557_1 + n0558_1 -> if deleted, APPEND to THAT item, do not create a
   second); york-castle-q80637 c_8dac5aacd73916b8 ('York Castle in 1820' watercolour,
   score 31.7) + c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a
   TOWN in Broome County, NEW YORK - toponymic-collision class, almost certainly
   DELETED wrong place; existing item [c_81ecab4a9284f156 + 4 more] -> append).

**The 303 way (summary; full recipe in the 189-194 DECISIONS entries):**
fit/review.py API, no hand-edited JSON. entry = {plan, title (the files.jsonl row title
WITH its 'File:' prefix - no space after the colon; fr._sha16(title) asserted == plan),
url, pairs (the doc's own), coarse False, evidence (fr.candidate_evidence(plan) -
returns None if the row is missing/unevidenced; assert non-None; kind category OR
hand_tied), label, cite, ref, size, place_reason '306e audit 2026-10-13: ... Document
deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new plans APPEND, the lead/file
name stay (an item with this plan already present gets the entry replaced in place);
a site with no item gets CREATED (lead = the one candidate); then os.remove the doc;
then fr.export(fr.ROOT, site) (scoped; keeps other branches' re-stamps - see PITFALLS
under tools/site_done.py, fit/review.py). **upsert_item returns an ABSOLUTE path** -
assert the basename. An item with no candidate docs stays open (resolved None; the site
stays covered for the union check). Export counts: a NEW item adds one to BOTH open and
total (194: (345,358) -> (346,359)); an APPEND leaves both unchanged (191, 193).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs;
inverse-map the site point; build the 800 m box LAYERS composite (1842
six-inch-1st_ink.webp red-on-white, plate luminance-ink mask (lo 118 / hi 200)
blue-on-white via atv + bilinear, relief grey; 100 m grid + 100-500 m circles centred
on the site point; raw jpgs at data/raw/commons/<site>/<plan-without-c_>.jpg are
exactly the doc's sizes); for a DENSE/hatched plate read the composite/screenshots, not
an ink histogram (182 PITFALLS); for stone-scale works the relief's dark dots decide
(194 PITFALLS); for a whole-complex displacement like this one, the repo 1842 webp may
not even cover the real works - then modern Esri aerial (VM has internet; z18 tile
math: x = ((lon+180)/360)*2^z, y = (1 - asinh(tan(lat_rad))/pi)/2*2^z, 0.376 m/px at
51 N) and the web are the deciding layers. The committed shots
(docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp was
wiped. KEEPS -> line only. DELETED -> the 303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 13 lines: offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2, portus x2, raby,
richborough, stanton-drew - between the 306d block and '## The site markers become
arrowheads (task 308, 2026-10-13)') - continue it after the stanton-drew line. DONE
sites (do not touch again): portus (item holds both portus candidates), raby (new open
item, lead c_fe1d6c7f0ba858cb), richborough (existing item now holds [c_1dcd5a7171573663,
c_edad7da41d234534]), stanton-drew (new open item, lead c_59a5c636a9e00703); taunton
c_05cb4a02bd58e82e (judged DELETED, execution pending).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 13 of 17 lines;
tick when all 17 are in. Box 3 PARTIAL: 9 deletions executed (old-sarum x2, oxford,
pontefract c_d135, portus x2, raby, richborough, stanton-drew); taunton judged (10th
verdict) but not yet executed; the rest awaits the remaining 2 verdicts (york x2 counts
as two). Box 4 satisfied so far (no `by: hand` doc touched; suite = baseline at the 194
run).
