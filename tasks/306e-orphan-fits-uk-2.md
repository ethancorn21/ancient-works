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
(2026-10-13, iteration 180, agent c - **offa KEEPS (evidence complete since 179; its line is
drafted below, still UNWRITTEN); okehampton investigated hard this session: the 178-179
'town-centre / wrong-kind' hypothesis is RETIRED - the site point IS the castle (inside the
1842 ruins cluster, at the dead centre of the drawn chain); the verdict now hangs on the
drawn chain's LENGTH vs the real outcrop - leaning KEEPS, one measurement left. NO project
files modified this session** - all work was /tmp scripts, web fetches, reading the committed
shots and the raw plate. Suite state unchanged from 178: 149 passed, 1 skipped, 1 red (agent
a's in-flight 307 placement seed, pre-existing, A/B-proven on pure main); tests NOT run this
session; the audit server is not running.

**OFFA (doc 1/17) - JUDGED KEEPS at 179; line drafted, just write it.** Evidence (all
re-derivable; see git history of this task file for the 179 details): the OS 1902 Nantcribba 02
sheet (Commons File:OS1902_Nantcribba_02.jpeg, caption 'Site of Nantcribba Hall and Parkland
with Offa's Dyke') is centred ON the site point (-3.049, 52.344, kind earthwork; Q1127343 =
the general Offa's-Dyke article point). The page's simFit (web/index.html L1004) replicated in
Python reproduces [eval] EXACTLY (1.44 m/px, +2.1 deg, resid [42.2,72.5,42.2,43.0]) - replica
formulas: W=[u,-v], Z=merc([lon,lat]) (R=6378137); wm,zm = means; nr=Σ(zr*wr+zi*wi),
ni=Σ(zi*wr-zr*wi), d=Σ(wr²+wi²) over centred values; a0,a1=nr/d,ni/d; b=zm-a*wm (complex);
forward (X,Y)=(a0*u+a1*v+b0, a1*u-a0*v+b1); INVERSE: (z-b)/a = (x+iy)(a0-ia1)/a2 with
x=X-b0, y=Y-b1, u=Re, v=-Im (a naive unflipped least squares gives garbage - see PITFALLS).
The site point inverse-maps to plate px (174,234) of 725x773 = the sheet's 'Lodge' at the NW
end of its hatched Nantcribba wood. The composite (plate warped with the exact transform over
relief.jpg 2000x2000 + six-inch-1st_ink.webp 1333x1333, box-aligned, resized) shows the 1884
and 1841/42 surveys AGREE: the lodge, the 'Nant-cribau' stream (= the real Nantcribba stream,
Wye tributary running S-SE past Port Faen/Ford into the hatched wood on the LiDAR), the 'P'
bldg = Port Faen, the parkland wood, the roads; the sheet's own caption places the Dyke on it.
Nantcribba = the wood/hall/stream W of Knighton, Powys, on the Dyke line. NOTE for the line:
the sheet's content is tilted ~45 deg in its own frame; the fit's +2.1 deg is near-identity
because the parkland's wood axis IS a 45-deg ground line. LINE DRAFT (306c/306d style):
'- offa-s-dyke-q1127343.c_1cca85e7b4b5a89e - OS 2nd ed 1902, Montgomeryshire xxx8, 'Site of
Nantcribba Hall and Parkland with Offa's Dyke' (similarity, 4 pts, resid 42-73 m, 1.44 m/px,
+2.1 deg, score 42.6): the 4 anchors are a 100-px 45-deg diagonal ladder, so the residuals
only measure the ladder's internal inconsistency, not a placement miss; the site point
inverse-maps to the sheet's own 'Lodge' at the NW end of its hatched Nantcribba wood, and a
composite of the sheet (warped by the page's own transform) over the 1842 six-inch ink and the
LiDAR shows the 1884 and 1841/42 surveys agree on the lodge, the Nantcribba stream running
S-SE past Port Faen and Ford into the wood, the parkland trees and the roads, and the sheet's
caption places the Dyke on it. KEEPS - an orphan today, invisible on the page (its drawn
works sit on the real Nantcribba hall/parkland/stream at the site point; the Dyke passed this
wood).'

**OKEHAMPTON (doc 2/17) - investigated this session. The site point is the castle; the open
question is the drawn chain's LENGTH (is it 2-3x too big, the 306d ludlow/goodrich/bury class,
or comparable to the real outcrop?). LEANING KEEPS.**
- The raw plate (data/raw/commons/okehampton-castle-q1419982/0edd7f87db67ff20.jpg, 618x674,
  1915, 'Underlying map Edward H. Young (d. 1932)') is a NE-SW CHAIN of ~10 multi-room
  buildings (A-G lettered) with radial tree hatching around; A (NE end) is a small two-room
  building, G (SW end) a larger block; no title in the image (the page draws the title).
  A->G spans ~570-600 m at the fit's 1.2 m/px; chain axis ~28 deg west of south on the map.
- simFit replica on its 4 pairs (the doc's pairs are a 100-px grid but the fit is clean)
  matches [eval] EXACTLY (resid [0.9,1.1,0.8,1.0], 1.196 m/px, +0.33 deg). Site point
  (-4.0083, 50.7306) -> plate px (333.8, 333.2) = DEAD CENTRE of the plate; plate centre ->
  (-4.00872, 50.73056), ~5 m from the site point.
- 1842 six-inch-1st_ink.webp (533x533 RGBA, box-aligned to sites.json corners; the site box is
  797.5 m real - 1264 m in merc units - relief.jpg 800x800 ~1 m/px). PITFALL: its transparent
  pixels carry the pink ink colour as RGB - always composite onto a background USING THE ALPHA
  CHANNEL; a plain .convert('RGB') gives solid pink. It shows: label 'Okehampton Castle
  (Remains of)' at 1x px (150,245) = E -174 m / N -50 m from the site point, leader pointing
  EAST to a cluster of elongated NE-SW building footprints (the 1842 ruins) centred ON the
  site point; the West Okement river runs along the castle's east side and loops round the
  outcrop to the NW; Lady Bridge NE; 'Springt' hamlet + the railway SE. So the site point sits
  INSIDE the real castle ruins cluster; the town is ~1 mile NE (English Heritage: the castle
  is '1 mile south-west of Okehampton town centre') - this is why the 178-179 'town-centre /
  wrong kind' reading was wrong.
- Building inventory from web sources (Wikipedia, cached pi-web/1387d53e134165ed.txt;
  legendarydartmoor.co.uk 2016 visit, cached pi-web/e69f7851c44c536b.txt): real castle =
  keep/motte at the SW end ('the keep towered on a separate hillock to the south-west of the
  ruin', mote 29.5x15.5 m, 32 m high), the bailey buildings (Great Hall with dais, kitchens,
  buttery, chapel, priest's + eastern + western lodgings) in the middle, gatehouse + long
  barbican passage + barbican at the NE end ('a small two storied guardroom on the side of the
  gatehouse'; 'visitors entering from the barbican in the north-east, along a long passageway
  up the hill'). The plate's A (small two-room bldg, NE) / central cluster / G (SW) match that
  inventory in order. English Heritage: 'the remains ... stretch from the keep mound to the
  tall gatehouse'; 'built along a long, thin rocky outcrop'.
- LiDAR: the outcrop ridge runs ~N-S (a few deg west) through the site point and spans the
  whole 550 m relief window examined (relief.jpg (150,100)-(650,650)) and beyond - the real
  outcrop is at least ~600 m long, comparable to the drawn chain.
- NEXT (exact): 1) measure the outcrop's N-S extent on the FULL 800x800 relief (the sharp
  bright band with steep dark flanks; the 550 m window already shows it crossing the whole
  frame) and/or the 1842 hatched band (scipy: dark=(alpha>40)&(rgb.sum()<300), dens=
  uniform_filter(dark,15)>0.06, like /tmp/okeham_hatch recipe) - if it is ~500-700 m the
  drawn chain is right-sized -> KEEPS; if only ~200-300 m -> DELETED the 303 way (site has NO
  review item yet: upsert_item(root,'okehampton-castle-q1419982',[entry]) with the doc's 4
  pairs + place_reason '306e audit 2026-10-13: ... Document deleted.', delete
  data/db/platefits/okehampton-castle-q1419982.c_0edd7f87db67ff20.json, export(root, site)
  scoped to the site; web/data/review.json 'at' = agent-a merge-conflict point, keep newer).
  2) Optionally: curl https://www.legendarydartmoor.co.uk/2016/03/18/okehampton_castle/ and
  grep data-src/src for the aerial + clickable-plan images (the cached text has no URLs; the
  raw HTML was saved to /tmp/okeham_page.html and a plain src-grep found only sidebar
  thumbnails - try data-src / image maps / a .plan file); a georeferenced plan (Higham 1977/
  1980 or Endacott 1999) would settle the extent at a stroke. 3) Write the okehampton line.
  4) Write the 306e block into docs/site_flow.md: header in the 306d style (copy the 306d
  header at L1048: '306d - the 18 UK orphan documents (sites a-l): ...' -> '306e - the 17 UK
  orphan documents (sites o-y): ...') + the offa line (draft above) + the okehampton line,
  inserted BETWEEN the ludlow line (ends 'the document was deleted 2026-10-13).', ~L1267) and
  '## The site markers become arrowheads (task 308, 2026-10-13)' (L1268). 5) Commit.
  6) Continue the batch (15 docs left): old-sarum c_0410 (Ditchfield 1901 - the site already
  has 2 built depictions; check web/data/sites/old-sarum-q782719/depictions.json) + c_ff62
  (1806 Camden/Basire DPLA plate), oxford (Mackenzie 1897), pilsbury (Cox 1905), pontefract
  x2 (two pages of the 1807 borough history, 8 pairs each), portus-adurni x2 (twin Penny
  Cyclopaedia 1836 plans, one German-titled 'Burg von Portchester'), raby (Mackenzie),
  richborough, stanton-drew (Penny Magazine 1836 druidical temple), taunton (Mackenzie),
  windmill-hill (Allcroft 1908 n0558_2, **model None** - the page's default plan model fits
  it: relief shot resid 0, 1.0 m/px, 0 deg, rowMapBox [0.56,0.38,0.85,0.58]; the site's item
  already holds n0557_1+n0558_1 - merge into that item if deleted), york c_8dac ('York Castle
  in 1820' watercolour, 31.7) + c_a7db ('Plan of Center, Broome County 1855' = Center is a
  TOWN in Broome County, NEW YORK - the devil-s-dyke/bethlehem toponymic-collision class,
  almost certainly DELETED wrong place). Box 2 ticks when all 17 lines are in; box 3 after
  any deletions; box 4 = suite check (merged-tree red set must be the 307 one only).

**State / housekeeping.** All 34 shots committed (129590d) - box 1 done. NO 306e block in
docs/site_flow.md yet. No deletions executed yet. Sites WITH existing review items:
old-sarum [c_b2701b5231da42f2], pontefract [c_ba5dfa2d2dbc645e + 6 more], richborough
[c_1dcd5a7171573663], windmill-hill [earthworkenglan01allcgoog_n0557_1, _n0558_1],
york-castle [c_81ecab4a9284f156 + 4 more]. NO item (create if deleted): offa-s-dyke,
okehampton, oxford-castle, pilsbury, portus-adurni, raby-castle, stanton-drew, taunton.
**The 303 way (per 306d):** fit/review.py API, no hand-edited JSON: upsert_item(root, site,
[entry]) with entry = {plan, title, url, pairs (the doc's own), coarse:false, evidence (from
the data/commons/files.jsonl row), label, cite, ref, size, place_reason '306e audit
2026-10-13: ... Document deleted.'} appended AFTER the item's existing candidates (lead
candidate first, item filename unchanged); then delete data/db/platefits/<doc>.json; then
export(root, site) scoped to the site (NEVER another site's item file).

**/tmp recipe from this session (re-writable in ~30 lines; constants above):** a Python script
(.venv/bin/python) that (a) replicates simFit (formulas above) on the doc's pairs, (b)
inverse-transforms any box/feature point to plate px, (c) builds the composite: for each
800x800 output pixel (i,j): (X,Y) = Wx+i/799*(Ex-Wx), Ny-j/799*(Ny-Sy) with
Wx,Ex,Ny,Sy = merc(x) of the NW/NE corners and merc(y) of the NW/SE corners from
web/data/sites.json site.corners [NW,NE,SE,SW]; base grey = relief.jpg (resized 800x800);
1842 ink RED with alpha = the webp's alpha channel (resized); plate ink BLUE = inverted
luminance thresholded (alpha 0 for L>=170 else (170-L)*1.9 capped 255) at the inverse
transform, bilinear. Outputs made this session (all in /tmp, wiped per session):
okeham_comp2.png (composite with yellow site-point cross + white anchor dots),
okeham_1842_ink_preview.png (1842 composited on grey), okeham_1842_castle_zoom2.png (4x zoom
on the ruins cluster - the one that settled castle-vs-town), okeham_hatch.png
(hatch-density map), okeham_sidebyside2.png (LiDAR vs 1842, same 300 m window),
okeham_page.html (legendarydartmoor raw HTML), okeham_relief_area.png (500x550 LiDAR crop),
okeham_comp.py / okeham_comp2.py (the scripts).

**Pitfalls that bite here (all in PITFALLS.md, don't re-learn).** The mpp/256 judge-composite
bug (line 314) - my composites are safe (exact page transform + the page's own ink layers),
but the final verdict stands on the real 1440x900 shots. In-checkout A/B only (locally-built
site dirs are gitignored). Geographic distances: dx=dlon*111194.9266*cos(lat0),
dy=dlat*110900 (NOT raw Mercator; the site's corners box is 1264 m in merc units = 797 m
real). The page's simFit flips plate v (W=u-iv) - a naive least squares WITHOUT the flip
gives garbage (first attempt: -45 deg/0.85 m/px, resid 200-800 m). A JPEG has no alpha
channel (ink overlay = inverted luminance as alpha); an RGBA webp MUST be composited WITH
its alpha (transparent pixels carry the ink colour as RGB).
