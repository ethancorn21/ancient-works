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
(2026-10-13, iteration 185, agent c - **oxford-castle c_ba6b308580428184 DELETED the 303 way this
session** (new review item created, doc deleted, page re-exported 343/356) **and its line written
- 5 of 17 lines done**. 12 docs (9 sites) remain to judge; next = pilsbury.)

**State of the 17 docs (o-y):** offa-s-dyke c_1cca85e7b4b5a89e KEEPS (181); okehampton-castle
c_0edd7f87db67ff20 KEEPS (181); old-sarum c_ff62c9585a92b375 DELETED (183, 303 way); old-sarum
c_041083ec68b532f8 DELETED (183, 303 way); oxford-castle c_ba6b308580428184 DELETED (judged 184,
executed 185, 303 way - item CREATED, not appended). The 303-removal detail of the oxford
deletion (the exact entry fields, the export numbers) is in the DECISIONS 185 entry.

**oxford-castle (executed this session, 185):** fit/review.py API only, no hand-edited JSON
(the script was /tmp/aw306e_oxford.py): upsert_item(ROOT,'oxford-castle-q2600886',[entry]) created
data/review/oxford-castle-q2600886.c_ba6b308580428184.json - this doc = lead and only candidate
(no_picture_found None, resolved None, item stays open); entry = {plan, title (the files.jsonl row
title, sha16-asserted), url, pairs (the doc's own 4), coarse False, evidence (candidate_evidence
-> the mackenzie hand_tied row {evidence/1, hand_tied, 2026-10-10, pipeline/sources.py
mackenzie}), label '1897', cite, ref (keeps the 'File: ' prefix), size, place_reason '306e audit
2026-10-13: ... Wrong place, right kind (the bury-castle class). Document deleted.'}; then the
doc deleted; export(ROOT, site) -> 343 open of 356 (342/355 before). Only 3 files changed
(D the doc, A the item, M web/data/review.json). The oxford line is in the 306e block of
docs/site_flow.md (after the old-sarum c_0410 line) - that is 5 of 17 lines.

**Remaining work - 12 docs (9 sites):**
- pilsbury-castle-q7194511.c_7ff765c177ca7bae. NO item.
- pontefract-castle-q1949590 c_3213330a52fe6018 + c_d135fb32326df430 (two pages of the 1807 borough
  history, 8 pairs each - LADDER class, expect the bury-castle treatment). Existing item
  [c_ba5dfa2d2dbc645e + 6 more].
- portus-adurni-q762664 c_42bedb90fffce1d4 + c_4912bb54aa79f3ea (twin Penny Cyclopaedia 1836 plans;
  one German-titled 'Burg von Portchester'). NO item.
- raby-castle-q4583646.c_fe1d6c7f0ba858cb (Mackenzie 1897). NO item.
- richborough-roman-fort-q1309736.c_edad7da41d234534 (Penny Cyclopaedia 1836). Existing item
  [c_1dcd5a7171573663].
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 (Penny Magazine 1836 druidical temple). NO
  item.
- taunton-castle-q7688781.c_05cb4a02bd58e82e (Mackenzie 1897). NO item.
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908, **model None** - the
  page's default plan model fits it: relief shot resid 0, 1.0 m/px, 0 deg. The site's item already
  holds n0557_1 + n0558_1 - if deleted, merge into THAT item, do not create a second).
- york-castle-q80637 c_8dac5aacd73916b8 ('York Castle in 1820' watercolour, score 31.7 - to judge)
  + c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a TOWN in Broome County,
  NEW YORK - toponymic-collision class, almost certainly DELETED wrong place). Existing item
  [c_81ecab4a9284f156 + 4 more].

**Verdict recipe (per doc) - unchanged, still valid:** replicate simFit on the doc's stored pairs
(the /tmp recipe block below); inverse-map the site point; build the 800x800 box composite (relief
grey + six-inch-1st_ink.webp red alpha>40 + plate ink blue via atv + bilinear of the
luminance-alpha mask; for a DENSE/hatched plate the blue ink saturates - read the composite /
screenshots instead of an ink histogram, per the PITFALLS entry); add a 100 m grid (50 px) and
100-500 m circles centred on the site point to read radii off; where size is in question, measure
the real earthworks as 1842 ink density in 25 m annuli / 16 az bins (template
/tmp/aw306e_profile.py). The committed shots (docs/site_flow/agent_fits/<doc>.png + _relief.png)
are the source of truth if the /tmp crops were wiped. KEEPS -> line in the 306e block; DELETED
-> the 303 way below.

**The 303 way (per 306d/303, unchanged):** fit/review.py API, no hand-edited JSON:
`upsert_item(root, site, [entry])` with entry = {plan, title, url, pairs (the doc's own),
coarse:false, evidence (from the data/commons/files.jsonl row via fit.review.candidate_evidence),
label, cite, ref, size, place_reason '306e audit 2026-10-13: ... Document deleted.'} appended AFTER
the item's existing candidates (lead candidate first, item file name unchanged); then delete
data/db/platefits/<doc>.json; then `export(root, site)` scoped to the site (NEVER another site's
item file; the page file is recomputed over the whole queue - that is intended). Sites WITH an
existing review item: pontefract [c_ba5dfa2d2dbc645e + 6 more], richborough [c_1dcd5a7171573663],
windmill-hill [earthworkenglan01allcgoog_n0557_1, _n0558_1], york-castle [c_81ecab4a9284f156 + 4
more]. NO item (create if deleted): pilsbury, portus-adurni, raby-castle, stanton-drew, taunton.
(oxford now HAS one - created for c_ba6b308580428184 this session; offa, okehampton KEEPT - no
item; old-sarum's existing item was reused for both deletions.)

**/tmp recipe (re-writable in ~40 lines):** .venv/bin/python (has PIL + scipy). (a) merc =
([lon,lat]) => [lon*R*pi/180, log(tan(pi/4 + lat*pi/360))*R], R=6378137 (web/index.html L360, TRUE
mercator, not R*angle). (b) simFit replica: W=[u,-v], Z=merc; wm,zm means; nr=sum(zr*wr+zi*wi),
ni=sum(zi*wr-zr*wi), d=sum(wr^2+wi^2) over centred; a0=nr/d, a1=ni/d; b=[zm0-(a0*wm0-a1*wm1),
zm1-(a0*wm1+a1*wm0)]; at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1]; atv(X,Y): q=(X-b0,Y-b1), u=(q0*a0+
q1*a1)/a2, v=(q0*a1-q1*a0)/a2; k=cos(lat0*pi/180); mpx=hypot(a0,a1)*k; rot=atan2(a1,a0) deg;
resid=hypot(at-pair)*k. (c) composite 800x800: (X,Y)=Wx+i/799*(Ex-Wx), Ny-j/799*(Ny-Sy) with
Wx,Ex=N/SE lon merc, Ny,Sy=NW/SE lat merc, corners from web/data/sites.json (key 'sites' -> list,
corners [NW,NE,SE,SW]; centre = site point). Base = relief.jpg resized 800 (L); 1842 =
six-inch-1st_ink.webp resized 800, red (235,60,75) with its alpha; plate ink BLUE (25,25,200) via
atv + bilinear sample of the plate's luminance-alpha mask. (d) geographic offsets: off(X,Y) =
(dlon*111194.9266*cos(lat0), (lat2-sy)*110900) with dlon=(X-SM0)/R*180/pi and lat2 = invert-merc(Y)
= (2*atan(exp(Y/R)) - pi/2)*180/pi. (e) annulus profile: resize the six-inch-1st_ink.webp to the
site box (1600 px for old-sarum), ink = alpha>40, r and compass-az from the box centre, density per
25 m annulus and per 22.5 deg az bin (use i*22.5 in a plain list, NOT range(0,360,22.5) - range
rejects float steps).

**Box status:** Box 1 TICKED (34/34 shots, 129590d). Box 2 NOT ticked: 5 of 17 lines (offa,
okehampton, old-sarum x2, oxford); tick when all 17 are in. Box 3 PARTIAL: 3 deletions executed
(old-sarum c_ff62, c_0410; oxford c_ba6b308580428184); the rest await the remaining 12 verdicts.
Box 4 satisfied (no `by: hand` touched; suite this session: 149 passed, 1 skipped, 1 failed
(270.6 s) = IDENTICAL to the 183 baseline - the 1 is agent a's in-flight 307
test_fit_queue::test_placement_gestures_and_save_in_the_browser, the pre-existing red on every
tree that merged main since 7e61147; no new failure from this change - the union tests and
test_platefits_docs_match_sites are green).

**Re-read:** the 306e block in docs/site_flow.md (header + offa + okehampton + old-sarum x2 +
oxford lines, between the 306d ludlow line and '## The site markers become arrowheads (task 308)')
- continue it in the same format (one line per doc, KEEPS/DELETED - an orphan today, invisible on
the page). NEXT DOC TO JUDGE: pilsbury-castle c_7ff765c177ca7bae (the /tmp/aw306e_doc.py helper,
re-writable from the /tmp recipe above; the committed shots are the fallback).
