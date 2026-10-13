Status: in-progress
# 306d: Look at the orphan agent fits, UK part 1 (a-l) - 18 docs, 18 sites
Depends on: none
Touches: docs/site_flow.md, docs/site_flow/, data/db/platefits/, data/review/, web/data/review.json, tools/audit_306d.mjs, PITFALLS.md, DECISIONS.md

## Goal
Subtask of 306 (the parent's Hand-over holds the audit recipe and the full inventory): the 18
UK platefit documents with `by: agent` (sites a-l) that are ORPHANS - in the store, but with no
overlay built on the site and not referenced by any review item, so a visitor sees them not at
all. Render each the way the page would if it ever showed it: the fit tool over the aerial
photograph, and over the LiDAR relief where the site has a `relief.jpg`, with the doc's stored
pairs placed. The verdict records where the doc stands today (invisible) and whether the
placement is good enough to keep.

## Acceptance criteria
- [x] One screenshot per doc in `docs/site_flow/agent_fits/<site>_<plan>.png` (1440x900: the site
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

## Docs (18, 18 sites)
- bury-castle-q5001077.c_de779031cda8a0dc - Bury Castle Somerset Map
- cassiobury-house-q5049456.c_3446adfe7a8ed6c7 - Cassiobury House, bird's-eye view engraved by Johannes Kip
- chevening-q1070927.c_6049b89e4ab0570c - Chevening, bird's-eye view engraved by Johannes Kip
- cooling-castle-q5167493.c_7ebc7630f3197364 - Cooling Castle, plan from Mackenzie, The Castles of England (1897)
- coria-q3819299.c_d66bfb0db805d2cd - Knowles 1909, Corbridge Excavations, fig 1 site plan
- daw-s-castle-q5242247.c_8d2281628567a166 - Daws Castle Somerset Map
- desborough-castle-q5263651.earthworkenglan01allcgoog_n0465_1 - Desborough Castle, High Wycombe, Bucks (Allcroft 1908)
- devil-s-dyke-q3307343.earthworkenglan01allcgoog_n0662_1 - SWEALD (Allcroft 1908)
- duffield-castle-q2073299.c_e915cbfd3af009b4 - Duffield Castle, plan from Mackenzie, The Castles of England (1897)
- eaton-socon-castle-q5331372.c_beefc3808de9b125 - Plan of Eaton Socon (1897)
- framlingham-castle-q2524183.c_f43bc6196e097819 - Framlingham Castle, plan from Mackenzie, The Castles of England (1897)
- goodrich-castle-q5583571.c_cd89cb69f385859b - Goodrich Castle, plan from Mackenzie, The Castles of England (1897)
- gurnard-s-head-q5620199.earthworkenglan01allcgoog_n0262_1 - Castell-an-Dinas, Cornwall (Allcroft 1908)
- hardknott-roman-fort-q1584994.c_7dcdfcc9aceb62ec - Hardknott Roman Fort
- herstmonceux-castle-q2652207.c_8eb122e93e31c3f6 - Herstmonceux Castle, plan from Mackenzie, The Castles of England (1897)
- king-arthur-s-round-table-q283800.c_cfc493f72253fa8e - Rude Stone Monuments 0154
- leicester-castle-q6519156.c_581a9f82b6a805a0 - Leicester Castle, plan from Mackenzie, The Castles of England (1897)
- ludlow-castle-q576369.c_b24730fd9038ae4a - Ludlow Castle, plan from Mackenzie, The Castles of England (1897)

## Hand-over
(2026-10-13, iteration 163, agent c - batch 2 in progress: fit-reproduction machinery built and validated; COOLING judged RIGHT (its composite read); coria, daw-s, chevening, cassiobury composites generated but NOT yet read. **NEXT STEP: read /tmp/j306d/<doc>_ink_on_<clip>.png for coria + daw-s (re-run the scripts if /tmp was cleared - recipe below), then judge the two Kip VIEW docs (chevening, cassiobury), write the lines in docs/site_flow.md, delete any wrong one the 303 way.**)

**State:** box 1 done (36 shots, 159). Box 2: 1 of 18 lines (bury-castle, in the 306d block at the END of docs/site_flow.md). Box 3: 1 removal (bury-castle). Box 4 stays open until the final batch's suite run. NO data files changed this session (judging only) - the committed tree is 162's state, so no A/B is owed yet.

**Fit reproduction (throwaway, /tmp - rebuild in <1 min if lost):** /tmp/j306d_fit.py = EXACT port of web/index.html simFit (L983) + homFit (L1015-1053): merc([lon,lat]) = [lon*pi/180*R, ln(tan(pi/4+lat*pi/360))*R], R=6378137; simFit: W=[u,-v], Z=merc, a = sum((z-zm)*conj(w-wm))/sum|w-wm|^2 (nr=sum(zr*wr+zi*wi), ni=sum(zi*wr-zr*wi), d=sum(wr^2+wi^2)), b = zm - a*wm, at(u,v)=[a0*u+a1*v+b0, a1*u-a0*v+b1]; resid=|at-Z|*cos(lat0); mpx=|a|*cos(lat0); rot=atan2(a1,a0). homFit: normalised 8x8 normal equations with the page's Gaussian elim w/ row pivot, H=Tzi*Hn*Tu, keep Hi. The port REPRODUCES 159's page [eval] values: chevening resid 14.6/14.6/4.2/4.2/9.3/9.3/17.9/17.9 (159: 4.2-17.9), coria 0.8/1.1/0.2/0.7/0.5/0.4 (159: <=1.1), daw-s 5.6/1.4/3.4/1.6 (159: <=5.6), cassiobury 0.0 (4-pt exact), cooling 0.0 (159's '0.8' was summary rounding, not a real difference). PITFALLS candidates found: (1) Mercator X is LINEAR in lon (lon = X/R*180/pi) - only Y needs atan(sinh(y/R)); using atan(sinh) for both axes made E ~3.5M m. (2) the page's solve() normal equations: M[i][n] = sum_k A[k][i]*b[k] where b has 2n entries (X and Y per pair) - np.hstack([A.T@A, b]) is a shape bug. /tmp/j306d_comp.py: clip_info (web/data/sites/<site>/: os1inch.webp 1600px or six-inch-1st.webp 1066px cover the site's size_m box -> ppm = box[0]/px; else relief.jpg) + fit_inverse (vectorised: sim: q=(Z-b)/a complex division, U=q.real, V=-q.imag; hom: (x,y,1)@Hi.T / w) + plate_to_clip (full plate composite) + overlay (50/100 m ground-grid on the downsampled plate, bold E=0/N=0 axes = site point, yellow anchor rings). /tmp/j306d_ink.py: plate INK ONLY (L<140, alpha 200) over the clip - THE decisive judge for plan docs (plate lines and map lines visible at once). Run: `.venv/bin/python /tmp/j306d_ink.py <docid>...` (~7 s for all five).

**Batch 2 facts.** The page's model comes from the web/data/plans.json row's `view` flag (rvResolveRow returns the real row when the plan id is in it), NOT the doc's own `model` field (all five say 'similarity'): cassiobury + chevening are `view: true` -> homFit; cooling/coria/daw-s -> simFit. Anchor grids (per-pixel metric spans): cooling 0.797 (fit 0.800 m/px, rot 0, 6 pts, grid consistent - NOT a bury-style ladder); coria 1.181 (fit 1.187, rot 0.02); daw-s 4.284 N/4.295 E (fit 4.318, rot -0.13); chevening hom ~1.13-1.18 m/px near-affine, 8 pts well spread; cassiobury hom 4 pts in a near-collinear band (u,v): (1150,450),(600,400),(800,600),(1000,700) -> ground (E,N): (650,249),(-49,298),(200,49),(450,-100) m, ~1.27-1.33 m/px consistent but the homography EXTRAPOLATES outside that band (image corners fly to ~1.5 km) - judge its anchors individually, never the fitted far field. Image-centre placements (site point = 0,0): cooling (+0.5,+8.3) m; coria (-39.9,+0.2); daw-s (-57.4,+1.2); chevening (-58.7,+148.5); cassiobury (+6.8,+223.1). Site boxes: cooling 800 m, others 1600 m.

**VERDICT SO FAR - cooling-castle-q5167493.c_7ebc7630f3197364: RIGHT (its lines keep their document).** Read its ink-on-6-inch composite (/tmp/j306d/cooling-castle-..._ink_on_six-inch-1st.png): the plate's Inner Ward square lands exactly on the castle square the 1842 OS 6-inch map draws (same position and size, moat lines coincide), the Outer Ward boundary follows the map's moat/ditch line, the plate's 'Water' stream matches the OS stream, 'Modern houses and farm' sits where the map's village buildings are, the 'Cooling' village label below. The 1897 Mackenzie plan georeferences true at 0.8 m/px over the site's 800 m box. Line still to write in the 306d block.

**REMAINING (judge in this order):** (1) coria - read /tmp/j306d/coria-q3819299.c_d66bfb0db805d2cd_ink_on_os1inch.png: Knowles 1909 Fig 1 site plan (Roman fort; plate 1.187 m/px, centre -40 m E of the site point, image 1280x1347 ~ 1.5 km square vs the 1600 m box) over the 1-inch OS clip (the fort was mapped long before 1909 - the drawn fort rectangle + the Stanegate/Wall road + the Tyne should align with the 1-inch's fort, roads and river). (2) daw-s-castle - read its _ink_on_os1inch.png: Somerset map inset 340x367 at 4.32 m/px over the 1-inch clip - Daw's Castle is a small sea-cliff hillfort west of Watchet; check the drawn ring sits on the real cliff hillfort (centre -57 m E). The inset's hachures make the ink mask ~16% of px (noisy) - zoom a 400-px crop around the drawn subject if the full 1600px composite is unreadable. (3) chevening (VIEW): ink-only is too dense (87% of px are engraving lines) - judge instead: where the drawn HOUSE is in the raw 1280x1056 image, map that region through the homFit, compare to the real Chevening House at the site point (image-centre placement is 148 m N of it, so the house region matters, not the centre) + the full semi-transparent plate composite on six-inch-1st (/tmp/j306d_comp.py writes it) if useful; the 8 anchors' ground band is (E: -306..+107, N: 49..709). (4) cassiobury (VIEW, 4-pt hom, NEAR-DEGENERATE anchors): the /tmp/j306d/..._on_relief.png composite is unreliable outside the anchor band - judge the ANCHORS: do their 4 ground points (listed above) sit on real features the Kip 1707 engraving shows there (house + park; house demolished 1927, site point = the house)? Check where the house region of the image maps (centre is +223 m N of the site point - if the house in the engraving maps away from the site point, the doc is wrong). If the anchors are a grid guess (round-ish lon/lat with no feature logic) it is the bury-castle trap in view-clothing -> DELETE the 303 way; if they are real features at a consistent ~1.3 m/px -> KEEPS.

**If any doc is wrong:** the 303 way (fit/review.py upsert_item(root, site, [entry]) appended to the site's EXISTING item if one exists - check data/review/<site>*.json first; entry: plan short id, title, url, pairs = the doc's own, coarse false, evidence from the data/commons/files.jsonl row, label, cite, ref, size, place_reason '306d audit 2026-10-13: ... Document deleted.'), then delete the doc, then export(root, site) scoped to that ONE site; study 306c's items via `git log --oneline -- data/review/` + git show first. Then RE-RUN the full suite: if the reds differ from the 162 baseline (9 failed: placement_gestures seed-fail + the 8 in-flight 211/222-228 family), flip my changed files to pristine in-checkout and re-run just those files to prove none are mine (~25 s; 161's A/B idiom, now a PITFALLS entry). df -h first (keep >=5G free), `.venv/bin/python -m pytest --ignore=tests/test_gate.py -q -p no:cacheprovider` (~4.5 min, ~3.5G into /tmp/loop-ancient-works.c/pytest-of-agent - rm -rf after).

**Then:** write each judged doc's line in the 306d block of docs/site_flow.md (format = the bury-castle line: doc id + source, fit stats, where the lines sit, verdict KEEPS/DELETED + 'an orphan today, invisible on the page'), commit, and on to batch 3 (duffield, eaton-socon, framlingham, goodrich - all Mackenzie plans, sim; fit facts in the DECISIONS 159 entry / re-derive with /tmp/j306d_fit.py).

Re-read: /tmp/j306d/{j306d_fit.py, j306d_comp.py, j306d_ink.py} - the judging machinery (rebuild from the DECISIONS 163 entry if /tmp was cleared).
Re-read: docs/site_flow.md (tail) - the 306d block + bury-castle line for the line format; extend the block, do not start a new section.
Re-read: fit/review.py:upsert_item/export - the exact call shapes before the next removal.
