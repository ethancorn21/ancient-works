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
(2026-10-13, iteration 181, agent c - **OFFA and OKEHAMPTON both judged KEEPS and both lines
are now WRITTEN: the 306e block (header + 2 lines) sits in docs/site_flow.md between the 306d
ludlow line and the 308 arrowheads section. 15 lines remain.** This session's project change
is docs/site_flow.md (+39 lines) - committed with the 181 hand-over; the 181 DECISIONS entry
is appended. The suite was NOT run (no test reads site_flow.md); its state is unchanged from
180: 149 passed, 1 skipped, 1 red = agent a's in-flight 307 placement seed (pre-existing on
main).

**OFFA (doc 1/17) - KEEPS, DONE.** The 180-drafted line is verbatim in site_flow.md. Evidence:
page simFit replicated EXACTLY (1.44 m/px, +2.1 deg, resid 42-73 m); site point inverse-maps to
the sheet's own 'Lodge' at the NW end of its hatched Nantcribba wood; composite of the sheet
(warped by the page's own transform) over the 1842 ink + LiDAR shows the 1884 and 1841/42
surveys agree on the lodge, the Nantcribba stream running S-SE past Port Faen and Ford into the
wood, the parkland and the roads; the sheet's caption places the Dyke on it.

**OKEHAMPTON (doc 2/17) - KEEPS, DONE.** The open question (drawn chain length vs the real
outcrop) is settled: the chain is NOT too big. This session's measurements (scripts wiped from
/tmp, but the recipe is below):
- simFit replica matches the page [eval] EXACTLY (1.196 m/px, +0.33 deg, resid 0.8-1.1 m); the
  site point (-4.0083, 50.7306) inverse-maps to plate px (334,333) = the dead centre of the
  plate and of the drawn chain.
- The drawn chain A->G is 702 m centre-to-centre (~920 m tip-to-tip), axis azimuth 220
  (NE-SW): A (small two-room bldg, NE end) at E +253 / N +308, G (larger block, SW end) at
  E -199 / N -230, central B-F cluster centroid E +41 / N +40.
- The real outcrop runs NE-SW, NOT N-S (the 180 "a few deg west of north" note is WRONG): an
  angular contrast profile of the LiDAR through the site point (line peak-median, 100 m flanks)
  peaks at azimuth 25-55 (100-121 grey levels) while N-S is 47 and E-W 16; the drawn chain's
  axis (40) sits inside that peak. Both the 1842 hatched rocky band and the LiDAR bright ridge
  with steep flanks span the whole 800 m site box, and the hatching reaches the box edges
  beyond BOTH ends of the drawn chain. So the 920 m chain is right-sized for (slightly smaller
  than) the real outcrop - not the goodrich/ludlow "2-3x too big, walls through the town" class.
- The 1842 'Okehampton Castle (Remains of)' label sits ~175 m W of the site point, its leader
  pointing east to the hatched building cluster that sits under the drawn B-F centre at the
  site point; the plate's building order matches the documented castle (keep SW, great hall /
  lodgings middle, gatehouse + barbican NE). The West Okement loops round the NE end at Lady
  Bridge and a spring at the SW end ('Springt') - the drawn chain sits between them, on the
  rock, same side of the river as the real ruins.

**Pitfalls NOT yet filed to PITFALLS.md (next agent files all four; the first two are the
180 carry-overs):** (1) the 1842 `six-inch-1st_ink.webp` is a SURVEY-RED ink overlay (every
non-transparent pixel rgb.sum ~330, colour (206,46,78)) - the "dark ink" recipe
(alpha>40 & rgb.sum()<300) finds ZERO pixels; ink mask = alpha>40, hatched band =
uniform_filter(ink,15)>0.06. (2) Inverting simFit: w=(z-b)/a = u - i v, so u=(q0*a0+q1*a1)/a2,
v=(q0*a1-q1*a0)/a2 (v = -Im); a wrong v sign = mirrored ghost ink; verify by the 4-point
round-trip. (3) 180-carry-over: an ink webp's transparent pixels carry the ink colour as RGB
(a plain .convert('RGB') crop comes out solid pink) - composite with the alpha channel
(paste onto a background with im, or getchannel('A')). (4) 180-carry-over: web_fetch returns
page TEXT without image URLs - curl the raw HTML and grep src/data-src. Also this session:
the okehampton outcrop is NE-SW (azimuth ~40), not N-S - where an old note says N-S, trust a
fresh angular profile (centre-bright peak-median lines through the site point).

**Remaining work - 15 docs (11 sites).** Continue the batch, one or a few per session:
- old-sarum-q782719: c_041083ec68b532f8 (Ancient Plan of Old Sarum) + c_ff62c9585a92b375
  (Plan & elevations of Old Sarum, DPLA). NOTE: the site already has 2 built depictions -
  check web/data/sites/old-sarum-q782719/depictions.json first (an orphan's overlay might have
  been built since the 134 inventory).
- oxford-castle-q2600886.c_ba6b308580428184 - Mackenzie 1897 (mackenzie-class: check the drawn
  scale vs the plate's own bar, as 306d did).
- pilsbury-castle-q7194511.c_7ff765c177ca7bae - Pilsbury Castle plan.
- pontefract-castle-q1949590: c_3213330a52fe6018 + c_d135fb32326df430 (two pages of the 1807
  borough history, 8 pairs each).
- portus-adurni-q762664: c_42bedb90fffce1d4 + c_4912bb54aa79f3ea (twin Penny Cyclopaedia 1836
  plans; one German-titled 'Burg von Portchester').
- raby-castle-q4583646.c_fe1d6c7f0ba858cb - Mackenzie 1897.
- richborough-roman-fort-q1309736.c_edad7da41d234534 - Penny Cyclopaedia 1836.
- stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 - Penny Magazine 1836 druidical
  temple.
- taunton-castle-q7688781.c_05cb4a02bd58e82e - Mackenzie 1897.
- windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 - Allcroft 1908, **model None** (the
  page's default plan model fits it: relief shot resid 0, 1.0 m/px, 0 deg, rowMapBox
  [0.56,0.38,0.85,0.58]). The site's item already holds n0557_1 + n0558_1 - if deleted, merge
  into that item (do not create a second item).
- york-castle-q80637: c_8dac5aacd73916b8 ('York Castle in 1820' watercolour, score 31.7) +
  c_a7db545536f13e24 ('Plan of Center, Broome County 1855' = Center is a TOWN in Broome County,
  NEW YORK - the devil-s-dyke / bethlehem toponymic-collision class, almost certainly DELETED
  wrong place).

**Verdict recipe (per doc):** read the committed shot's [eval] line (the page's own fit:
resid, m/px, deg) and the committed aerial + relief shots; replicate simFit on the doc's stored
pairs (below) to inverse-map the site point and key features; build the box-aligned composite
(relief grey + 1842 red ink [alpha>40] + plate ink [luminance: alpha = clip((170-L)*1.9,0,255)
via atv] + site cross) and READ it. KEEPS -> write the line into the 306e block (after the
okehampton line, before the 308 section). DELETED -> the 303 way (fit/review.py upsert_item,
delete the doc, scoped export; see the 161 DECISION for the exact entry shape).

**The 303 way (per 306d/303):** fit/review.py API, no hand-edited JSON: upsert_item(root, site,
[entry]) with entry = {plan, title, url, pairs (the doc's own), coarse:false, evidence (from
the data/commons/files.jsonl row), label, cite, ref, size, place_reason '306e audit 2026-10-13:
... Document deleted.'} appended AFTER the item's existing candidates (lead candidate first,
item filename unchanged); then delete data/db/platefits/<doc>.json; then
export(root, site) scoped to the site (NEVER another site's item file). Sites WITH existing
review items: old-sarum [c_b2701b5231da42f2], pontefract [c_ba5dfa2d2dbc645e + 6 more],
richborough [c_1dcd5a7171573663], windmill-hill [earthworkenglan01allcgoog_n0557_1,
_n0558_1], york-castle [c_81ecab4a9284f156 + 4 more]. NO item (create if deleted): oxford,
pilsbury, portus-adurni, raby-castle, stanton-drew, taunton. (offa and okehampton KEEPT, so
they needed no item.)

**/tmp recipe (re-writable in ~40 lines):** .venv/bin/python (has PIL + scipy). (a) merc =
([lon,lat]) => [lon*R*pi/180, log(tan(pi/4 + lat*pi/360))*R], R=6378137 (web/index.html L360,
TRUE mercator, not R*angle). (b) simFit replica: W=[u,-v], Z=merc; wm,zm means; nr=sum(zr*wr+
zi*wi), ni=sum(zi*wr-zr*wi), d=sum(wr^2+wi^2) over centred; a0=nr/d, a1=ni/d; b=[zm0-(a0*wm0-
a1*wm1), zm1-(a0*wm1+a1*wm0)]; at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1]; atv(X,Y): q=(X-b0,Y-b1),
u=(q0*a0+q1*a1)/a2, v=(q0*a1-q1*a0)/a2; k=cos(lat0*pi/180); mpx=hypot(a0,a1)*k; rot=atan2(a1,
a0) deg; resid=hypot(at-pair)*k. (c) composite 800x800: (X,Y)=Wx+i/799*(Ex-Wx), Ny-j/799*(Ny-
Sy) with Wx,Ex=N/SE lon merc, Ny,Sy=NW/SE lat merc, corners from web/data/sites.json (key
'sites' -> list, corners [NW,NE,SE,SW]; centre = site point). Base = relief.jpg resized 800
(L); 1842 = six-inch-1st_ink.webp resized 800, red (235,60,75) with its alpha; plate ink BLUE
(25,25,200) via atv + bilinear sample of the plate's luminance-alpha mask. (d) geographic
offsets: off(X,Y) = (dlon*111194.9266*cos(lat0), (lat2-sy)*110900) with dlon = (X-SM0)/R*180/
pi and lat2 = invert-merc(Y) = (2*atan(exp(Y/R)) - pi/2)*180/pi.

**Box status:** Box 1 ticked (34/34 shots committed 129590d, all in the repo). Box 2 NOT
ticked yet: 2 of 17 lines written (offa, okehampton); it ticks when all 17 lines are in.
Box 3 NOT ticked: no deletions executed yet (both verdicts so far are KEEPS); it ticks once
the batch is done and any deletions are executed the 303 way. Box 4 satisfied so far (no `by:
hand` touched; no new test failures - docs-only change).

**Re-read:** the 306e block I wrote in docs/site_flow.md (header + offa line + okehampton
line, between the 306d ludlow line and '## The site markers become arrowheads (task 308)') -
verify a later session's new lines continue the block in the same format (one line per doc,
KEEPS/DELETED - an orphan today, invisible on the page).
