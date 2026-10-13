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
(2026-10-13, iteration 182, agent c - **the four pending PITFALLS entries are FILED**
(306e iteration 181, 3 in the web/ section: survey-red `*_ink.webp` = alpha-only ink, the
transparent-pixels-carry-ink-colour/compositing twin, and the simFit inverse formula; 1 in
Agent tools: web_fetch has no image URLs). **Old-sarum judged in depth this session:**
c_ff62 (Basire 1806) is a clear DELETED (wrong place - see below); c_0410 (Ditchfield 1901)
is leaning DELETED (oversize + SE shift) and its precise ring measurement script is written
but never ran (syntax error) - finish it before writing the line. No lines written yet for
either; no deletions executed yet. Suite state unchanged from 180/181: 149 passed, 1
skipped, 1 red = agent a's in-flight 307 placement seed (not run this session; this session
touched only PITFALLS.md, which no test reads).

**PITFALLS filed (iteration 182):** see the file - four new #### entries: under 'web/'
(1) every web/data/sites `*_ink.webp` is a survey-red (206,46,78) overlay, ink in ALPHA only
(mask = a>40; hatched band = uniform_filter(ink,15)>0.06); (2) the transparent pixels carry
the ink colour as RGB - .convert('RGB') crops come out solid pink, composite through the
alpha channel; (3) simFit inverse: u=(q0*a0+q1*a1)/a2, v=(q0*a1-q1*a0)/a2, a2=a0^2+a1^2
(v = -Im; wrong sign = mirrored ghost; verify 4-point round-trip). Under 'Agent tools and
harness': web_fetch returns page text without image URLs - curl the raw HTML and grep
src/data-src.

**Old-sarum facts (both docs):** site (-1.804722, 51.093333), 1600x1600 m box, kind hillfort,
the hill above Salisbury. The site ALREADY has 2 built depictions (c_8192abb966d030a3 and
earthworkenglan01allcgoog_n0142_1 in web/data/sites/old-sarum-q782719/depictions.json) -
NEITHER of my two orphan docs; both stay orphans. The site's review item is
data/review/old-sarum-q782719.c_b2701b5231da42f2.json with ONE coarse candidate (c_b2701b5231da42f2
'Plan of Old Sarum', rejected, gate_score 59.7) - a 303-deletion appends AFTER it, item
filename unchanged. The 1842 six-inch (web/data/sites/old-sarum-q782719/six-inch-1st_ink.webp,
1066 px for the 1600 m box, 0.666 px/m) shows the real earthworks: the hatched oval labelled
'OLD SARUM 74.778 Acres' (that's the HILL parcel, incl. slope hatching; the giant 'SUB
CASTLE'/'UNDER' letters are the neighbouring parcels' names, not drawing), the outer bank
ring and the central moated 'Castle' circle (labels: SORVIODUNUM, Castle, Site of Well, Roman
Coins found, Watch Tower (Remains of), Site of Cloisters, Site of Bishop's Hall, Cross Banks,
Cathedral (Site of); spot heights 320 E, 348 S, 300 SE; Holy Cross Church + 'Castle Villa'
SE, 'Old Sarum Farm' E, the modern A345 to the NE).

**Real earthwork geometry, measured this session (1842 ink density in 25 m annuli, 16 az bins
0=N cw, from /tmp/aw306e_profile.py - re-runnable):** inner 'Castle' moated circle: dense to
r~75 m, trough 100-150 m (the sub-castle court) -> r~85 m, centre ~16 m W / 6 m N of the site
point (i.e. ON the site point). Outer bank: dense peaks 175-225 m N/NE/NW, 200-250 m E/W, 
225-275 m SE/S -> the outer oval is ~400-550 m across (N 210-225 / E 250 / S 250-275 / W
200-250 m radii), centre ~25 m SE of the site point. LiDAR agrees: bright summit r<100 m,
dark ditch ring 100-175 m (N/E/S), 200-275 m W, flat beyond. (The az profile is at the end
of the 182 DECISION entry if needed.)

**c_ff62c9585a92b375 (Basire 1806, Camden's Britannia, DPLA) - DELETED (wrong place):** the
plate is a book page (1280x1858): a text column, four hill ELEVATIONS, and a small PLAN at
the bottom (outer ditch ring ~390 px across, inner 'Castle' circle ~90 px, 'Cornfields' and
a road through the S, caption 'PLAN & ELEVATIONS OF OLD SARUM', 'James Basire Sc.' / 'W.
Basker del.'). The 6 stored pairs are a PERFECT 100-px grid ladder (5 distinct points: 
u 300/400/500 at v 1400, u 400 at v 1300/1500) -> the fit is EXACTLY 2.000 m/px, 0.0 deg,
residuals all 0.0 m (reproduces the page [eval]; trivial - the ladder has no inconsistency
and no placement information). The site point inverse-maps to plate px (399.7, 1399.7) =
BLANK PAPER west of the drawn plan (the drawn plan centre is at plate (620,1490) = 220 px
E / 90 px S of the site point = 440 m E, 180 m S at 2 m/px). So the page renders the site
point on blank paper and the drawn castle plan over the flat farmland SE of the hill (the
1842 'Old Sarum Farm' / 'Castle Villa' ground); the drawn ring (780 m across, a schematic
to boot) misses the real 400-550 m oval. Same class as bury-castle: right kind of picture,
anchors on blank paper, drawn works over the wrong ground. DELETED the 303 way (upsert into
the existing item after c_b2701b5231da42f2, delete the doc, scoped export).

**c_041083ec68b532f8 (Ditchfield 1901, 'Ancient Plan of Old Sarum' = an engraving titled
'The Ichnography', a bird's-eye of the concentric ring-castle with radial roads N/E/S/W/SE
'Leaving Street'/SW, inner 'Castle Well' circle, 'Part of the Wall of the Cathedral' NW,
'City of Old Sarum' E) - LEANING DELETED (oversize + SE shift), finish the measurement:**
fit 1.294 m/px, +0.23 deg, residuals 15.3/40.2/21.6/9.0/27.9/16.5 m (max 40.2 - the 6 pairs
are a ~350x400 px rough ladder with ~14% anisotropy, so the residuals measure ladder
inconsistency, like the 306c/306d ladders). The site point inverse-maps to plate (326.1,
396.0) of 686x892. Read off the 800 m box composite (100 m grid + 100-500 m circles, 1842
red, plate blue - /tmp/aw306e_osarum_grid_041083ec68b532f8.png, re-runnable from
/tmp/aw306e_osarum_grid.py): the drawn inner circle is r~90-110 m vs the real r~85 m and
shifted ~60-80 m SE of the site point (its NW edge cuts the SE quadrant of the real inner
circle); the drawn outer ring spans ~150-175 m on the NW side (sits ON the real NW arc)
to ~450-480 m on the S/SE side (the real S outer edge is 250-275 m) - so the drawn
S/SW quarter of the ring runs 150-200 m PAST the hill over flat fields, and the drawn S
road extends ~150 m past the real hill edge; the drawn SE 'Leaving Street' runs ESE ~50-100
m S of the real SE road. The NW half of the drawn complex roughly matches the real
eastworks; the S half misses. Leans DELETED (goodrich class: centre ~right, drawn works
bigger than the real complex, walls past the town/fields) - but FIRST run the precise
measurement to pin the drawn centres/radii: /tmp/aw306e_meas.py has a syntax error on its
3rd print (one extra close paren on the 'inner ring radii' line: ...percentile(rr,90)),1)))
should be ...percentile(rr,90)),1)) - fix that one char and run it; it finds the drawn inner
circle centre (search u/v 250-520, band 45-110 px, strongest ink fraction) and the drawn
outer ring's farthest ink per azimuth from both the drawn centre and the site point
(rmax 320 px). If the numbers confirm the SE shift / oversize (they should), write the line
DELETED and execute the 303 way; if the drawn complex turns out to sit within ~25-30% of
the real one all round, it is a KEEPS-with-caveats call - decide then.

**Remaining work - 13 docs (10 sites) after old-sarum:** oxford-castle-q2600886
.c_ba6b308580428184 (Mackenzie 1897 - mackenzie-class: check drawn scale vs the plate's own
bar, as 306d did); pilsbury-castle-q7194511.c_7ff765c177ca7bae; pontefract-castle-q1949590
c_3213330a52fe6018 + c_d135fb32326df430 (two pages of the 1807 borough history, 8 pairs
each - LADDER CLASS, expect the bury-castle treatment); portus-adurni-q762664
c_42bedb90fffce1d4 + c_4912bb54aa79f3ea (twin Penny Cyclopaedia 1836 plans; one German-titled
'Burg von Portchester'); raby-castle-q4583646.c_fe1d6c7f0ba858cb (Mackenzie 1897);
richborough-roman-fort-q1309736.c_edad7da41d234534 (Penny Cyclopaedia 1836);
stanton-drew-stone-circles-q1516300.c_59a5c636a9e00703 (Penny Magazine 1836 druidical
temple); taunton-castle-q7688781.c_05cb4a02bd58e82e (Mackenzie 1897);
windmill-hill-q4348373.earthworkenglan01allcgoog_n0558_2 (Allcroft 1908, **model None** -
the page's default plan model fits it: relief shot resid 0, 1.0 m/px, 0 deg, rowMapBox
[0.56,0.38,0.85,0.58]; the site's item already holds n0557_1 + n0558_1 - if deleted, merge
into that item, do not create a second item); york-castle-q80637 c_8dac5aacd73916b8 ('York
Castle in 1820' watercolour, score 31.7) + c_a7db545536f13e24 ('Plan of Center, Broome
County 1855' = Center is a TOWN in Broome County, NEW YORK - toponymic-collision class,
almost certainly DELETED wrong place).

**Verdict recipe (per doc) - unchanged from 181, still valid:** replicate simFit on the
doc's stored pairs (the /tmp recipe block below; the aw306e_osarum module in /tmp if it
survives has all of it importable: simfit/merc/off/K/LON/LAT - but note importing it re-runs
the old-sarum judges, which is harmless); inverse-map the site point; build the 800x800
box composite (relief grey + six-inch-1st_ink.webp red alpha>40 + plate ink blue via atv +
bilinear of the luminance-alpha mask alpha=clip((170-L)*1.9,0,255); for a thin-line plate
like Basire's use a lower threshold, am>0.12, else the plan is nearly invisible); add a 100 m
grid (50 px) and 100-500 m circles centred on the site point to read radii off; and where
size is in question, measure the real earthworks as 1842 ink density in 25 m annuli / 16 az
bins (the old-sarum profile script is the template: /tmp/aw306e_profile.py). The committed
shots (docs/site_flow/agent_fits/<doc>.png + _relief.png) are the source of truth if /tmp
crops were wiped. KEEPS -> line in the 306e block (after the okehampton line, before the 308
section); DELETED -> the 303 way below.

**The 303 way (per 306d/303, unchanged):** fit/review.py API, no hand-edited JSON:
upsert_item(root, site, [entry]) with entry = {plan, title, url, pairs (the doc's own),
coarse:false, evidence (from the data/commons/files.jsonl row), label, cite, ref, size,
place_reason '306e audit 2026-10-13: ... Document deleted.'} appended AFTER the item's
existing candidates (lead candidate first, item filename unchanged); then delete
data/db/platefits/<doc>.json; then export(root, site) scoped to the site (NEVER another
site's item file). Sites WITH existing review items: old-sarum [c_b2701b5231da42f2],
pontefract [c_ba5dfa2d2dbc645e + 6 more], richborough [c_1dcd5a7171573663], windmill-hill
[earthworkenglan01allcgoog_n0557_1, _n0558_1], york-castle [c_81ecab4a9284f156 + 4 more].
NO item (create if deleted): oxford, pilsbury, portus-adurni, raby-castle, stanton-drew,
taunton. (offa and okehampton KEEPT, so they needed no item.)

**/tmp recipe (re-writable in ~40 lines):** .venv/bin/python (has PIL + scipy). (a) merc =
([lon,lat]) => [lon*R*pi/180, log(tan(pi/4 + lat*pi/360))*R], R=6378137 (web/index.html
L360, TRUE mercator, not R*angle). (b) simFit replica: W=[u,-v], Z=merc; wm,zm means;
nr=sum(zr*wr+zi*wi), ni=sum(zi*wr-zr*wi), d=sum(wr^2+wi^2) over centred; a0=nr/d, a1=ni/d;
b=[zm0-(a0*wm0-a1*wm1), zm1-(a0*wm1+a1*wm0)]; at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1];
atv(X,Y): q=(X-b0,Y-b1), u=(q0*a0+q1*a1)/a2, v=(q0*a1-q1*a0)/a2; k=cos(lat0*pi/180);
mpx=hypot(a0,a1)*k; rot=atan2(a1,a0) deg; resid=hypot(at-pair)*k. (c) composite 800x800:
(X,Y)=Wx+i/799*(Ex-Wx), Ny-j/799*(Ny-Sy) with Wx,Ex=N/SE lon merc, Ny,Sy=NW/SE lat merc,
corners from web/data/sites.json (key 'sites' -> list, corners [NW,NE,SE,SW]; centre = site
point). Base = relief.jpg resized 800 (L); 1842 = six-inch-1st_ink.webp resized 800, red
(235,60,75) with its alpha; plate ink BLUE (25,25,200) via atv + bilinear sample of the
plate's luminance-alpha mask. (d) geographic offsets: off(X,Y) =
(dlon*111194.9266*cos(lat0), (lat2-sy)*110900) with dlon = (X-SM0)/R*180/pi and lat2 =
invert-merc(Y) = (2*atan(exp(Y/R)) - pi/2)*180/pi. (e) annulus profile: resize the
six-inch-1st_ink.webp to the site box (1600 px for old-sarum), ink = alpha>40, r and
compass-az from the box centre, density per 25 m annulus and per 22.5 deg az bin (use
i*22.5 in a plain list, NOT range(0,360,22.5) - range rejects float steps).

**Box status:** Box 1 ticked (34/34 shots, 129590d). Box 2 NOT ticked: 2 of 17 lines
(offa, okehampton); ticks when all 17 are in. Box 3 NOT ticked: no deletions executed yet;
forgoing the 303 way for c_ff62 (and c_0410 if it lands DELETED) is the next action. Box 4
satisfied so far (no `by: hand` touched; PITFALLS.md is in this task's Touches and no test
reads it, so the suite state is unchanged).

**Re-read:** the 306e block in docs/site_flow.md (header + offa + okehampton lines, between
the 306d ludlow line and '## The site markers become arrowheads (task 308)') - continue it
in the same format (one line per doc, KEEPS/DELETED - an orphan today, invisible on the
page).
