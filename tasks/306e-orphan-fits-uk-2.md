Status: open
# 306e: Look at the orphan agent fits, UK part 2 (o-y) - 17 docs, 13 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306e.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 17
UK platefit documents with `by: agent` (sites o-y) that are ORPHANS - in the store, but with no
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
(2026-10-13, iteration 179, agent c - **offa JUDGED: KEEPS (evidence complete); okehampton still
UNDECIDED. No project files modified this session** - all work was /tmp throwaways, web checks
and reading the committed shots; the suite is exactly as of iteration 178 (149 passed, 1 skipped,
1 red = agent a's in-flight 307 placement seed, pre-existing; tests were NOT run this session).

**Offa (doc 1/17) - KEEPS. Evidence assembled this session (all re-derivable; /tmp is wiped per
session, so re-run the recipes, they are small).**
1. Web check (DONE, the one the 178 hand-over asked for): the Commons page of
   File:OS1902_Nantcribba_02.jpeg (cached /home/agent/.cache/pi-web/50d4fe074fc3495c.txt) has caption
   **"Site of Nantcribba Hall and Parkland with Offa's Dyke"** - OS 2nd ed 1902, surveyed 1884,
   revised 1901, Montgomeryshire Sheet xxx8. Web search confirms Nantcribba = the wood/hall/stream
   W of Knighton, Powys, on the Dyke line ('Nantcribba Castle, Powys' is a vanished castle -
   castlewales.com; 'the Dyke avoids west-flowing streams ... Nantcribba ... Knighton (Powys)').
   So the sheet IS the site's local area: the 178 hand-over's 'leaning deleted / placed 1-2 km E
   over the town' is RETIRED - the drawn sheet is centred ON the site point, not offset from it.
2. Exact page transform (the page's simFit, web/index.html L1004, is complex least squares
   `merc = a*(u - i v) + b`: W=[u,-v], Z=merc([lon,lat]) with R=6378137, k=cos(lat0*deg),
   resid=hypot(q-Z)*k, mpx=hypot(a)*k, rot=atan2(a1,a0); inverse: w=(z-b)/a, u=Re(w), v=-Im(w);
   forward: X=a0*u+a1*v+bx, Y=a1*u-a0*v+by; inverse: u=(a0*dx+a1*dy)/det, v=(a1*dx-a0*dy)/det,
   det=a0^2+a1^2). My Python replica on offa's 4 pairs reproduces the page's [eval] EXACTLY
   (1.44 m/px, +2.1 deg, resid [42.2,72.5,42.2,43.0], score 42.6) - so the transform can be used
   for feature-level checks. The 4 anchors are a 100-px 45-deg diagonal ladder (bury-castle
   class): the residuals only measure the ladder's internal inconsistency, not a placement miss.
3. Inverse-mapped the site point (-3.049, 52.344; Q1127343 = the GENERAL Offa's-Dyke article point,
   kind earthwork, NOT a specific Dyke section) onto the plate: plate px (174,234) of 725x773 =
   the NW end of the sheet's hatched wood, right at the sheet's 'Lodge' (anchor 1 (150,250) maps
   34 m W/24 m N of the site point; plate centre maps to (-3.0449,52.3421)).
4. COMPOSITE (the decisive check): the 1902 plate (blue, ink = inverted luminance as alpha,
   warped with the exact transform above) drawn over the site's relief.jpg (2000x2000 = 1 m/px,
   box corners (-3.0637,52.3530)..(-3.0343,52.3350), row 0 = north; g2r(X,Y) =
   ((X-W_)/(E_-W_)*(rw-1), (1-(Y-S_)/(N_-S_))*(rh-1)), W_/N_ = merc(NW corner), E_/S_ =
   merc(SE corner)) PLUS the site's 1842 six-inch ink
   (web/data/sites/offa-s-dyke-q1127343/six-inch-1st_ink.webp, 1333x1333, box-aligned; resize to
   2000) in red (the same layer the page draws). RESULT - the two independent surveys (1841/42
   and 1884) AGREE: (a) the 1902 'Lodge' + hatched building sit ON the 1842 'Lodge' + building at
   the site point (within ~20-30 m); (b) the 1902 'Nant-cribau' stream label (plate (575,505) ->
   (-3.0403,52.3407)) sits on the 1842 stream that runs S-SE past 'Port Faen' and 'Ford' into the
   hatched wood on the LiDAR (the real Nantcribba stream, a Wye tributary); (c) 1902 hatched 'P'
   bldg (plate (590,280)) = 1842 'Port Faen'; (d) the drawn parkland wood overlaps the 1842
   trees, the LiDAR dark wood and the aerial's dark green wood (the committed aerial shot's SE
   corner); (e) the roads align. The sheet's own caption says the Dyke is on it. Verdict: KEEPS -
   an orphan today, invisible on the page (its drawn works sit on the real Nantcribba
   hall/parkland/stream at the site point; the Dyke passed this wood). NOTE for the line: the
   sheet's content is tilted ~45 deg in its own frame; the fit's +2.1 deg is near-identity
   because the parkland's wood axis IS a 45-deg ground line - the composite proves the fit is
   the sheet's true orientation, not an accident of the ladder. (Optional belt-and-braces before
   writing the line: one real-page zoomed shot, zoom ~17, of the stream/wood corner - this
   composite is NOT the 306d mpp/256 judge-composite trap: it uses the exact page transform and
   the page's own ink layer; but a real-page zoom removes the last doubt cheaply.)

**Okehampton (doc 2/17) - UNDECIDED (178 state, unchanged).** The plate (Commons 1915 'Plan of
Okehampton Castle', 'Underlying map Edward H. Young (d. 1932)', 618x674, 4 pts a 100-px grid,
page fit 1.20 m/px -0.3 deg resid<=1.1, score 1.0) is a long NE-SW CHAIN of ~10 multi-room
buildings with radial tree hatching - NOT a motte-and-bailey; centred on the site point
(-4.0083, 50.7306, kind motte), its buildings line up with the real town-centre cluster
(aerial + 1842 red overlay). Wikipedia (cached /home/agent/.cache/pi-web/1387d53e134165ed.txt):
the real castle = Norman keep on a long thin rocky outcrop (mote 29.5x15.5 m, 32 m high), ~1 km
from the town. NEXT: (a) re-read the 2 committed shots
(docs/site_flow/agent_fits/okehampton-castle-q1419982_c_0edd7f87db67ff20{,_relief}.png) and pin
the plate centre vs the town cluster vs the red 1842 'Okehampton Castle' label; (b) web check
where the real castle sits relative to the town centre ('Okehampton Castle' outcrop position /
Higham 1984; the site point's kind=motte + coords say which of castle-vs-town it is); (c)
verdict: if the site point is the TOWN (the castle is 1 km away): the plate is a correctly
georeferenced map of the WRONG KIND of subject for a motte site (the bethlehem 'wrong kind'
class) - likely DELETED the 303 way (the 306c precedent for right-map/wrong-kind was deletion);
if the site point is genuinely the castle 1 km out: wrong PLACE, DELETED. Either way the line
says what it is (a 1915 town-centre plan by Edward Young) and where it sits.

**Where I am / state.** All 34 shots committed (129590d) - box 1 is done. NO 306e block exists in
docs/site_flow.md yet: the 306d block ends at the ludlow line (line 1267) and
'## The site markers become arrowheads (task 308)' starts at line 1268; the 306e block header
(306c/306d style: '306e - the 17 UK orphan documents (sites o-y): ...') goes AFTER the 306d
block, BEFORE the 308 section. docs/site_flow.md is in my Touches; the 308 section belongs to
agent a's territory only via the merge - I only ADD the 306e block at the 306d/308 boundary
(306c/306d did the same). No deletions to do for offa (it keeps). If okehampton ends up DELETED,
its site has NO review item yet - create one the 306d way (see below).

**Exact next step.** 1) (Optional) one real-page zoom shot of the offa stream/wood corner.
2) Write the 306e block header + the OFFA line (KEEPS, per the evidence above) into
docs/site_flow.md between the ludlow line and the 308 section. 3) Finish okehampton per (a)-(c)
above; write its line (if DELETED: 303 way - create the site's review item with the picture +
the doc's 4 pairs + place_reason, delete data/db/platefits/okehampton-castle-q1419982.
c_0edd7f87db67ff20.json, export scoped to the site; web/data/review.json 'at' = known agent-a
merge-conflict point, keep the newer). 4) Commit. 5) Continue batches: old-sarum x2 (c_0410
Ditchfield 1901 - the site already has 2 built depictions, check
web/data/sites/old-sarum-q782719/depictions.json for what they are; c_ff62 the 1806
Camden/Basire DPLA plate), oxford (Mackenzie 1897), pilsbury (Cox 1905), pontefract x2 (two
pages of the 1807 borough history, 8 pairs each), portus-adurni x2 (twin Penny Cyclopaedia 1836
plans, one German-titled), raby, richborough, stanton-drew (Penny Magazine druidical temple),
taunton (Mackenzie), windmill-hill (Allcroft 1908 n0558_2; the site's item already holds
n0557_1+n0558_1 - merge into that item if deleted), york x2 (c_8dac 'York Castle in 1820'
watercolour; c_a7db = 'Plan of Center, Broome County 1855' - Center is a TOWN in Broome County,
NEW YORK: the devil-s-dyke/bethlehem toponymic-collision class, almost certainly DELETED wrong
place). Box 2 ticks when all 17 lines are in; box 3 after any deletions; box 4 = suite check
(merged-tree red set must be the 307 one only).

**The 303 way (per 306d, for any deletion):** fit/review.py API, no hand-edited JSON:
upsert_item(root, site, [entry]) with entry = {plan, title, url, pairs (the doc's own),
coarse:false, evidence (from the data/commons/files.jsonl row), label, cite, ref, size,
place_reason '306e audit 2026-10-13: ... Document deleted.'} appended AFTER the item's existing
candidates (lead candidate first, item filename unchanged); then delete
data/db/platefits/<doc>.json; then export(root, site) scoped to the site (NEVER another site's
item file). Sites WITH existing items: old-sarum [c_b2701b5231da42f2], pontefract [c_ba5dfa2d2dbc645e
+ 6 more], richborough [c_1dcd5a7171573663], windmill-hill [earthworkenglan01allcgoog_n0557_1,
_n0558_1], york-castle [c_81ecab4a9284f156 + 4 more]. NO item (create one): offa-s-dyke,
okehampton, oxford-castle, pilsbury, portus-adurni, raby-castle, stanton-drew, taunton.

**Metadata (from the doc JSONs).** All by:agent. Scores: offa 42.6 (4 pairs), okehampton 1.0
(4), old-sarum c_0410 19.1 (6) + c_ff62 0.0 (6), oxford 0.0 (4), pilsbury 15.8 (4), pontefract
c_3213 9.5 (8) + c_d135 24.5 (8), portus-adurni both 0.0 (6+6), raby 0.0 (4), richborough 0.0
(6), stanton 0.0 (6), taunton 0.0 (4), windmill-hill 0.0 (6, **model None** - the page's
default plan model fits it: relief shot shows resid 0, 1.0 m/px, 0 deg, rowMapBox [0.56,0.38,
0.85,0.58] from plans.json), york c_8dac 31.7 (4) + c_a7db 13.6 (4).

**Pitfalls that bite here (all in PITFALLS.md, don't re-learn).** The mpp/256 judge-composite
bug (line 314) - judge from the real 1440x900 shots (my composite was safe: exact page
transform + the page's own ink layer). In-checkout A/B only (locally-built site dirs are
gitignored). Geographic distances: dx=dlon*111194.9266*cos(lat0), dy=dlat*110900 (not raw
Mercator). The page's simFit flips plate v (W=u-iv) - a naive least squares WITHOUT the flip
gives GARBAGE (my first attempt: -45 deg/0.85 m/px, resid 200-800 m); the pane's [eval] fit
line is the truth, and the formulas in point 2 of the offa section above replicate it exactly.
PIL Image.transform AFFINE tuple is (a,b,c,d,e,f) with src_x=a*i+b*j+c, src_y=d*i+e*j+f - b
and d are the easy-to-swap pair (swapping mirrors the image); a similarity is exactly affine.
A JPEG has no alpha channel: for an ink overlay use inverted luminance as the alpha, warped
with the same affine. PIL Image.open(...).convert("RGBA") on a JPEG = opaque everywhere.
**Suite state:** last full run (178, merged tree): 149 passed, 1 skipped, 1 red (agent a's 307
placement seed, pre-existing, A/B-proven on pure main at 161/176/177). .venv present. This
session ran no tests and changed no project files. The audit server is not running;
/tmp/audit_306e.log had the [eval] record for all 34 shots (the audit script regenerates and
skips existing shots).
