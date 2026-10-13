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
(2026-10-13, iteration 189, agent c - **suite re-run FIRST (as 188 demanded): 3 failed, 152
passed, 1 skipped (308.93 s)** - the 3 reds are exactly the known set (test_batch_eu.py::
test_sample_run_real_gate + ::test_batch_adds_files_rewrites_none = the 203b-owned bibracte
pair; test_fit_queue.py::test_placement_gestures_and_save_in_the_browser = agent a's 307). NO
new red from 188's pontefract deletion - 188's change is VERIFIED. Log: /tmp/aw306e_suite189.log.
**portus-adurni c_42bedb90fffce1d4 JUDGED DELETED** (wrong place, wrong size, right kind) - all
measurements done this session, EXECUTION (the 303 way) is the next session's only remaining
work, then the line. No project file changed this session (read-only audit + /tmp scripts).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181); okehampton-castle
c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED (183, 303 way); old-sarum
c_041083ec68b532f8 DELETED (183, 303 way); oxford-castle c_ba6b308580428184 DELETED (184/185,
303 way - item CREATED); pilsbury-castle c_7ff765c177ca7bae KEEPS (187); pontefract-castle
c_3213330a52fe6018 KEEPS (188); pontefract-castle c_d135fb32326df430 DELETED (188, 303 way -
item APPENDED); portus-adurni c_42bedb90fffce1d4 JUDGED DELETED (189, NOT yet executed). 8 docs
(7 sites) remain after portus: portus c_4912 (the German-titled twin), raby, richborough,
stanton-drew, taunton, windmill-hill, york x2.

**The portus verdict (all numbers verified this session - re-derive with the /tmp scripts if
needed; committed shots are the source of truth if /tmp is wiped):** fit = 1.0000 m/px,
+0.00 deg, all 6 residuals 0.0 (the 6 anchors are a perfect 900-px grid: corners
(100,1000)/(100,100)/(1000,1000)/(1000,500) + interior (200,200)/(850,800) = the bury-castle/
oxford ladder class - the fit carries no placement information). Site point (-1.115, 50.8381)
inverse-maps to plate (799.5, 799.5) of [1280,1292]. Drawn outer-wall square: strong wall lines
at u 183..1147 / v 77..1016 = 954 x 927 m, centre E -135 N +252 = ~437 m NW of the real fort's
centre (E +185 N -45). Real fort (1842 zoom /tmp/port_zoom1842.png): outer ramparts E
+60..+310, N +60..-150 (~250 x 210 m) with the hatched keep at E +80..+160 (centre ~E +120
N -10) and St Mary's at E +180 N -95; the site point sits just W of the west rampart. Drawn
keep (densest 120-px block, plate (322,185)) lands at E -478 N +614 = ~865 m NW of the real
keep, over village farmland. Drawn Church of St Mary (the hatched cross, plate 837..1023 x
728..875, centre (967,793) = E +168 N +6) is the ONE feature near its real counterpart (~100 m
N-S off the real church). The site point lands on the plate's open interior just NW of the
drawn church. Scale bar: main line v 1141 spans u 271..1032 (761 px), 6 ticks at 150 px = 100 ft
divisions -> at 1.0 m/px, 100 ft (30.5 m) draws as 150 m = ~4.9x the true scale; the drawn
square is 3.8x the real fort - the 1836 plate is a drawing, not a survey, internally
inconsistent (the pilsbury class note). Page shots (aerial + relief, committed) confirm: status
line "Scale 1.00 m per page pixel, turned +0.0 deg ... within 1 m"; the drawn square covers most
of the aerial view, offset NW, with the real castle near its SE corner. VERDICT: DELETED the
303 way.

**NEXT STEP - execute the 303 way (exact recipe, all inputs verified):** script
`sys.path.insert(0, "fit"); import review as fr` (fit/ has NO __init__.py). doc = json.load
from the store. t = "File:Portchester Castle, derived from the Penny Cyclopaedia (1836) V6
page 354.jpg" (files.jsonl line 656; assert fr._sha16(t) == "c_42bedb90fffce1d4").
evidence = fr.candidate_evidence("c_42bedb90fffce1d4") = {rec evidence/1, kind category,
checked 2026-10-10, site_cat "Portus Adurni", file_cat "Portus Adurni", via []}. entry keys in
188's order: plan, title (=t), url (doc's "media/commons/portus-adurni-q762664/
42bedb90fffce1d4.jpg"), pairs (the doc's 6), coarse False, evidence, label "1836", cite
(doc's), ref (doc's, keeps the "File: " prefix), size [1280,1292], place_reason
'306e audit 2026-10-13: similarity (6 pts, resid 0.0 m, 1.00 m/px, 0.0 deg). The 6 anchors
are a perfect 900-px grid, so the fit carries no placement information (the bury-castle
ladder class). The drawn outer-wall square spans 954 x 927 m against the real fort's ~250 x
210 m (~3.8x too big) with its centre ~440 m NW of the real fort; the drawn NW keep lands
~865 m NW of the real keep, over village farmland west of the site; only the drawn Church of
St Mary sits near its real church (~100 m N). The plate's own 0-500 ft bar implies ~5x the
true scale - a 1836 drawing, not a survey. Wrong place, wrong size, right kind. Document
deleted.' (or equivalent). fr.upsert_item(fr.ROOT, "portus-adurni-q762664", [entry]) - the
site has NO item yet (data/review/ has none for it), so this CREATES
data/review/portus-adurni-q762664.c_42bedb90fffce1d4.json with this doc as lead; then
os.remove the doc; then fr.export(fr.ROOT, "portus-adurni-q762664") -> expect (344, 357)
(343/356 before). Verify: item file has 1 candidate, no_picture_found None, resolved None;
web/data/review.json has the portus entry (lead c_42bedb90fffce1d4). LATER twin c_4912bb54aa79f3ea:
upsert_item finds the item by SITE field (_find_item scans data/review/ by item["site"]),
appends after the lead, lead/file name stay - do NOT create a second item. Then write the
line in docs/site_flow.md AFTER the pontefract c_d135 line and BEFORE "## The site markers
become arrowheads (task 308, 2026-10-13)" (= 9 of 17 lines; format: see the c_d135 line -
"DELETED - an orphan today, invisible on the page (the 303 way: ...)", here say the item was
NEW - the site had none). Then re-run the FULL suite (expect the same 3 known reds, 152
passed, 1 skipped) - my change touches store + review item + page file, so the union checks
and test_platefits_docs_match_sites must stay green. /tmp scripts alive this session:
aw306e_fit.py (fit replicate), aw306e_port_meas3.py (wall lines + keep), aw306e_port_zoom.py
(1842 zoom -> /tmp/port_zoom1842.png + scale bar).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 8 of 17 lines (portus =
9th, after execution). Box 3 PARTIAL: 4 deletions executed (old-sarum x2, oxford, pontefract
c_d135); the 5th (portus) awaits this execution. Box 4: suite as above (no new reds).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181); okehampton-castle
c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED (183, 303 way); old-sarum
c_041083ec68b532f8 DELETED (183, 303 way); oxford-castle c_ba6b308580428184 DELETED (184/185,
303 way - item CREATED); pilsbury-castle c_7ff765c177ca7bae KEEPS (187); pontefract-castle
c_3213330a52fe6018 KEEPS (188); pontefract-castle c_d135fb32326df430 DELETED (188, 303 way -
item APPENDED). The 303-removal details of the executed deletions are in the DECISIONS entries
183/184/185 and 188. The 186/187 journal entries are LOST (the 187 context limit died before
they were committed; the driver's harness-save commit 9c40f48 carried only site_flow.md + this
file) - so the pilsbury evidence survives only in the 187 hand-over text, recoverable via
`git show 9c40f48:tasks/306e-orphan-fits-uk-2.md`; its verdict summary (drawn castle hill on the
real hill; the plate's own scale bar is ~1/3 of the drawing's actual scale = a feet/yards
mix-up in the doc, not a fit error) is in the 188 entry's discovery note.

**What 188 changed in this checkout (uncommitted at hand-over; the harness saves them):**
D data/db/platefits/pontefract-castle-q1949590.c_d135fb32326df430.json;
M data/review/pontefract-castle-q1949590.c_ba5dfa2d2dbc645e.json (the d135 entry APPENDED after
the 7 coarse candidates - lead + file name unchanged, now 8 candidates, no_picture_found None,
resolved None - stays open); M web/data/review.json (export scoped to the site, 343 open of
356 = UNCHANGED - the item was open before and stays open: no candidate has a doc);
M docs/site_flow.md (the two pontefract lines, after the pilsbury line, before '## The site
markers become arrowheads (task 308, 2026-10-13)'); M PITFALLS.md (one new entry, `### web/`);
M DECISIONS.md (the 188 entry). No `by: hand` doc touched.

**Tests:** last run was 187, after the main merge: 152 passed, 1 skipped, 3 failed (311 s).
The 3 reds: 2 = the 203b-owned bibracte pair (212a's merge-induced reds, NOT mine), 1 = agent
a's standing 307 test_fit_queue::test_placement_gestures_and_save_in_the_browser. The 188
change is expected to keep exactly that state - verify with `.venv/bin/python -m pytest
tests/ -q -p no:cacheprovider` and confirm NO new red beyond those 3 (union checks and
test_platefits_docs_match_sites must stay green: the site stays covered by its open item, and
every remaining doc names a built site).

**Remaining work - 9 docs (7 sites):**
- portus-adurni-q762664 c_42bedb90fffce1d4 (Penny Cyclopaedia 1836 v6 p 354, 'Portchester
  Castle') + c_4912bb54aa79f3ea (same source, German-titled 'Burg von Portchester') - twin
  plans, NO review item.
- raby-castle-q4583646.c_fe1d6c7f0ba858cb (Mackenzie 1897). NO item.
- richborough-roman-fort-q1309736.c_edad7da41d234534 (Penny Cyclopaedia 1836 v6 p 353). Existing
  item [c_1dcd5a7171573663].
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 (Penny Magazine 1836 druidical
  temple). NO item.
- taunton-castle-q7688781.c_05cb4a02bd58e82e (Mackenzie 1897). NO item.
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908 'WINDMILL SITES,
  LEWES DOWN', **model None** - the page's default plan model fits it: relief shot resid 0,
  1.0 m/px, 0 deg. The site's item already holds n0557_1 + n0558_1 - if deleted, merge into
  THAT item, do not create a second).
- york-castle-q80637 c_8dac5aacd73916b8 ('York Castle in 1820' watercolour, score 31.7 - to
  judge) + c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a TOWN in
  Broome County, NEW YORK - toponymic-collision class, almost certainly DELETED wrong place).
  Existing item [c_81ecab4a9284f156 + 4 more].

**Verdict recipe (per doc) - unchanged, still valid:** replicate simFit on the doc's stored
pairs (the /tmp/aw306e_fit.py pattern in the 188 DECISIONS entry: least squares over w=[u,-v]
against true-Mercator z; at(u,v) takes PAGE coords - v_page, NOT the flipped w: my 188 first
draft used the flipped v in at() and got 4.2e6 m residuals and garbage anchor geos; the fix is
v_page in at(), and the 182 simFit-inversion PITFALLS is the reference); inverse-map the site
point via atv; build the 800 m box LAYERS (the /tmp/aw306e_layers.py pattern - cleaner than the
single blend: 1842 six-inch-1st_ink.webp red-on-white, plate luminance-ink mask (lo 118 / hi
200) blue-on-white via atv + bilinear, relief grey; 100 m grid + 100-500 m circles centred on
the site point; the raw jpgs are exactly the docs' sizes - no rescale; note the raw file is
data/raw/commons/<site>/<plan-without-c_>.jpg). For a DENSE/hatched plate read the
composite/screenshots, not an ink histogram (182 PITFALLS). Where size is in question: 1842 ink
density in 25 m annuli / 16 az bins (use i*22.5 in a plain list, NOT range(0,360,22.5) - range
rejects float steps). The committed shots (docs/site_flow/agent_fits/<doc>.png + _relief.png)
are the source of truth if the /tmp files were wiped. KEEPS -> line in the 306e block.
DELETED -> the 303 way below.

**The 303 way (unchanged):** fit/review.py API, no hand-edited JSON. In the script
`sys.path.insert(0, "fit"); import review as fr` (fit/ has NO __init__.py - `import fit.review`
fails, ModuleNotFoundError; 188 hit exactly that). `fr.upsert_item(fr.ROOT, site, [entry])`
with entry = {plan, title (the files.jsonl row title WITH its 'File: ' prefix, sha16-asserted
== the plan, = the doc's ref), url, pairs (the doc's own), coarse False, evidence
(fr.candidate_evidence(plan)), label, cite, ref, size, place_reason '306e audit 2026-10-13: ...
Document deleted.'}; new plans APPEND, the lead/file name stay; an item with no candidate docs
stays open (verify after: resolved None on the page, and no candidate has a doc); then
os.remove the doc; then `fr.export(fr.ROOT, site)` (NEVER another site's item file; the page
file is recomputed over the whole queue - that is intended). Sites WITH an existing review
item: richborough [c_1dcd5a7171573663], windmill-hill [n0557_1, n0558_1], york-castle
[c_81ecab4a9284f156 + 4 more] - APPEND (pontefract's was appended at 188). NO item (create if
deleted): portus-adurni, raby-castle, stanton-drew, taunton. (oxford's was CREATED at 185;
offa, okehampton, pilsbury, pontefract c_3213 KEEPT - no item; old-sarum's existing item was
reused for both its deletions.)

**Re-read:** the 306e block in docs/site_flow.md (header + offa + okehampton + old-sarum x2 +
oxford + pilsbury + pontefract x2 lines, between the 306d ludlow line and '## The site markers
become arrowheads (task 308)') - continue it in the same format (one line per doc,
KEEPS/DELETED - an orphan today, invisible on the page). NEXT DOC TO JUDGE:
portus-adurni-q762664.c_42bedb90fffce1d4 (twin Penny Cyclopaedia 1836 plan, no item).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 8 of 17 lines (offa,
okehampton, old-sarum x2, oxford, pilsbury, pontefract x2); tick when all 17 are in. Box 3
PARTIAL: 4 deletions executed (old-sarum c_ff62, c_0410; oxford c_ba6b308580428184; pontefract
c_d135); the rest await the remaining 9 verdicts. Box 4 satisfied so far (no `by: hand`
touched; suite status as above - re-verify at the next run).
