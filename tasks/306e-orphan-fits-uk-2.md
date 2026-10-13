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
(2026-10-13, iteration 190, agent c - **merged main, then executed the 303 way on portus
c_42bedb90fffce1d4 (NEW item = lead, doc deleted, scoped export 344/357), and wrote the 9th
of 17 lines. Suite after the change = the post-merge baseline 154/1/1, no new red. NEXT:
judge the twin c_4912bb54aa79f3ea (same source plate -> almost certainly DELETED, APPENDED
to the same item).**

**Baseline (changed by the main merge, commit 9f92b3a):** post-merge suite = **154 passed,
1 skipped, 1 failed**. The 203b bibracte pair (tests/test_batch_eu.py::test_sample_run_real_gate
+ ::test_batch_adds_files_rewrites_none) now PASSES after main's 0685a4c (burcht-van-leiden
matcher fits; the no-picture fixture moved to Yeavering Bell). The ONLY known red:
tests/test_fit_queue.py::test_placement_gestures_and_save_in_the_browser (agent a's in-flight
307). Expect exactly that in every run; any other failure = my new red. Logs
/tmp/aw306e_merge190.log + /tmp/aw306e_suite190.log (may be wiped; the numbers are in the 190
DECISIONS entry). Run: `.venv/bin/python -m pytest tests/ -q -p no:cacheprovider` (~5 min).

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181); okehampton-castle
c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED (183); old-sarum
c_041083ec68b532f8 DELETED (183); oxford-castle c_ba6b308580428184 DELETED (184/185);
pilsbury-castle c_7ff765c177ca7bae KEEPS (187); pontefract-castle c_3213330a52fe6018 KEEPS
(188); pontefract-castle c_d135fb32326df430 DELETED (188); portus-adurni c_42bedb90fffce1d4
**DELETED, executed at 190** (new item is lead; doc deleted; scoped export 344/357; 9th line
written). **8 docs (7 sites) remain:** portus c_4912bb54aa79f3ea (next), raby, richborough,
stanton-drew, taunton, windmill-hill n0558_2, york x2.

**What 190 did:**
1. **Merged main** (9f92b3a). Only conflict in web/data/review.json = the `at` timestamp (both
   branches are full re-exports) -> took main's newer stamp (10:58:34). Per-item regions
   auto-merged: my oxford/old-sarum/pontefract items kept + main's burcht-van-leiden (renamed
   to lead c_2da8ced53ce1c3da, 3 candidates), moundville (lead c_ca57b707992bb337) and the 234
   no-picture re-stamps. Before touching anything, verified the page file is a PURE FUNCTION
   of the item files (0 no_picture_found diffs across all 343 page items vs their item files;
   the 234 re-stamps live in the item files - 9c48d94 committed them, a7f5dda only re-derived
   the page). New PITFALLS entry under `### tools/site_done.py, fit/review.py` (search:
   "full re-export of data/review/").
2. **Executed the 303 way on portus c_42bedb90fffce1d4** exactly per the 189 recipe (script:
   `sys.path.insert(0,"fit"); import review as fr` - fit/ has NO __init__.py): entry
   {plan, title 'File:Portchester Castle, derived from the Penny Cyclopaedia (1836) V6 page
   354.jpg' (fr._sha16-asserted == plan), url (the doc's media/commons/.../42bedb90fffce1d4.jpg),
   pairs (the doc's 6), coarse False, evidence (files.jsonl row: rec evidence/1, kind
   category, checked 2026-10-10, site_cat/file_cat 'Portus Adurni', via []), label '1836',
   cite (the doc's), ref (the doc's, 'File: ' prefix kept), size [1280,1292], place_reason
   '306e audit 2026-10-13: similarity (6 pts, resid 0.0 m, 1.00 m/px, 0.0 deg) ... Wrong
   place, wrong size, right kind. Document deleted.'}; fr.upsert_item **CREATED**
   data/review/portus-adurni-q762664.c_42bedb90fffce1d4.json (the site had NO item; this doc
   is the lead; no_picture_found None; resolved None); os.remove the doc; fr.export(fr.ROOT,
   "portus-adurni-q762664") -> **(344, 357)** as predicted; page entry = lead
   c_42bedb90fffce1d4, 1 candidate, no_picture_found None; item stays open (no candidate doc).
3. **Wrote the 9th of 17 lines** in the 306e block of docs/site_flow.md (after the pontefract
   c_d135 line, before '## The site markers become arrowheads (task 308, 2026-10-13)'): the 6
   anchors are a perfect 900-px grid -> no placement info; drawn square 954 x 927 m vs the
   real ~250 x 210 m, centre ~440 m NW; keep ~865 m NW over farmland; only St Mary's near its
   real church; the plate's own 0-500 ft bar ~5x the true scale (a 1836 drawing, not a
   survey); DELETED - an orphan today, invisible on the page (the 303 way: a NEW review item
   - the site had none).
4. **Suite 154/1/1** = the post-merge baseline (no new red).

**NEXT STEP - judge the twin portus-adurni-q762664.c_4912bb54aa79f3ea** ('Burg von
Portchester (GB) Plan von 1836 aus der Penny Cyclopaedia, Seite 354' = the German-titled twin
of the plate just deleted; SAME 1280x1292 Penny Cyclopaedia 1836 v6 p 354 plate). (a) Its 6
stored pairs: (100,100),(100,1000),(1000,1000),(800,800),(1000,500),(100,500) - all on the
same 2 lon lines (-1.1249502/-1.1121479) x 2 lat lines (50.8443833/50.8362988) plus the
(800,800) centre -> a perfect grid ladder, the fit carries NO placement information (the
bury-castle/oxford class); replicate it if you want the exact numbers (the /tmp/aw306e_fit.py
pattern in the 188/189 DECISIONS entries: least squares over w=[u,-v]; **at(u,v) takes PAGE
coords - v_page, NOT the flipped w** - the 182 simFit-inversion PITFALLS is the reference;
expect 1.00 m/px, 0.0 deg, resid 0.0). (b) Read the committed shots
docs/site_flow/agent_fits/portus-adurni-q762664_c_4912bb54aa79f3ea.png + _relief.png (both
exist from box 1) - if they show the same drawn geometry as the c_42bedb twin (the square
~954 x 927 m, centre ~440 m NW of the real ~250 x 210 m fort, keep ~865 m NW over farmland,
only St Mary's near its real church; 1842 ramparts E +60..+310 / N +60..-150 with the hatched
keep NW and St Mary's SE) -> **DELETED the 303 way, APPENDED to the existing portus item**:
fr.upsert_item(fr.ROOT, "portus-adurni-q762664", [entry2]) - _find_item matches by the SITE
field and finds the c_42bedb file; the new plan APPENDS after the lead; **lead and file name
stay c_42bedb90fffce1d4 - do NOT create a second item**. entry2 = {plan c_4912bb54aa79f3ea,
title 'File:Burg von Portchester (GB) Plan von 1836 aus der Penny Cyclopaedia, Seite 354.jpg'
(assert fr._sha16 == plan; row exists in data/commons/files.jsonl with kind-category
evidence), url (the doc's .../4912bb54aa79f3ea.jpg), pairs (the doc's 6), coarse False,
evidence (that row's), label '1836', cite (the doc's), ref (the doc's, 'File: ' prefix), size
[1280,1292], place_reason '306e audit 2026-10-13: ... the German-titled twin of the deleted
c_42bedb90fffce1d4: same source (Penny Cyclopaedia 1836 v6 p 354), same 1280x1292 plate and
drawn geometry ... Wrong place, wrong size, right kind. Document deleted.'}; then os.remove
the doc; then scoped export - **counts stay (344, 357)** (the item already exists and stays
open: neither candidate has a doc). (c) Write the **10th of 17 lines** (after the c_42bedb
line, same format; say it was APPENDED to the existing portus item). (d) Re-run the full
suite (expect 154/1/1). If the twin's shots instead showed a correct fit (they should not -
it is the same plate as one just deleted), KEEPS: just the line, no 303 way.

**Remaining work after the twin - 7 docs (6 sites):**
- raby-castle-q4583646.c_fe1d6c7f0ba858cb (Mackenzie 1897). NO item (create if deleted).
- richborough-roman-fort-q1309736.c_edad7da41d234534 (Penny Cyclopaedia 1836 v6 p 353).
  Existing item [c_1dcd5a7171573663] -> append.
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 (Penny Magazine 1836 druidical
  temple). NO item (create if deleted).
- taunton-castle-q7688781.c_05cb4a02bd58e82e (Mackenzie 1897). NO item (create if deleted).
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908 'WINDMILL SITES,
  LEWES DOWN', **model None** - the page's default plan model fits it: relief shot resid 0,
  1.0 m/px, 0 deg. The site's item already holds n0557_1 + n0558_1 -> if deleted, merge into
  THAT item, do not create a second).
- york-castle-q80637 c_8dac5aacd73916b8 ('York Castle in 1820' watercolour, score 31.7 - to
  judge) + c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a TOWN in
  Broome County, NEW YORK - toponymic-collision class, almost certainly DELETED wrong place).
  Existing item [c_81ecab4a9284f156 + 4 more] -> append.

**The 303 way (summary; full recipe in the 189/190 DECISIONS entries):** fit/review.py API,
no hand-edited JSON. entry = {plan, title (the files.jsonl row title WITH its 'File: '
prefix, fr._sha16-asserted == plan), url, pairs (the doc's own), coarse False, evidence
(fr.candidate_evidence(plan)), label, cite, ref, size, place_reason '306e audit 2026-10-13:
... Document deleted.'}; fr.upsert_item(fr.ROOT, site, [entry]) - new plans APPEND, the
lead/file name stay; a site with no item gets CREATED (lead = first candidate); then
os.remove the doc; then fr.export(fr.ROOT, site) (scoped: writes `resolved` only into that
site's item file; recomputes the whole page file - that is intended and keeps other
branches' re-stamps, see the new PITFALLS). An item with no candidate docs stays open
(resolved None; the site stays covered for the union check).

**Verdict recipe (per doc, unchanged):** replicate the fit on the doc's stored pairs;
inverse-map the site point; build the 800 m box LAYERS composite (1842 six-inch-1st_ink.webp
red-on-white, plate luminance-ink mask (lo 118 / hi 200) blue-on-white via atv + bilinear,
relief grey; 100 m grid + 100-500 m circles centred on the site point; raw jpgs at
data/raw/commons/<site>/<plan-without-c_>.jpg are exactly the doc's sizes); for a DENSE/
hatched plate read the composite/screenshots, not an ink histogram (182 PITFALLS). Where
size is in question: 1842 ink density in 25 m annuli / 16 az bins (i*22.5 in a plain list,
NOT range(0,360,22.5)). The committed shots (docs/site_flow/agent_fits/<doc>.png +
_relief.png) are the source of truth if /tmp was wiped. KEEPS -> line only. DELETED -> the
303 way.

**Re-read:** the 306e block in docs/site_flow.md (header + the 9 lines: offa, okehampton,
old-sarum x2, oxford, pilsbury, pontefract x2, portus c_42bedb - between the 306d ludlow
line and '## The site markers become arrowheads (task 308, 2026-10-13)') - continue it after
the portus c_42bedb line. data/review/portus-adurni-q762664.c_42bedb90fffce1d4.json - the
item to append the twin into (lead + file name must stay).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 9 of 17 lines; tick
when all 17 are in. Box 3 PARTIAL: 5 deletions executed (old-sarum c_ff62 + c_0410; oxford
c_ba6b308580428184; pontefract c_d135; portus c_42bedb); the rest awaits the remaining 8
verdicts. Box 4 satisfied so far (no `by: hand` doc touched; suite = baseline, re-verify at
the next run).
