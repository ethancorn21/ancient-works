# The one-site line: finish a site all the way to the map (task 300)

From 2026-10-11 (Ethan) the work goes one site at a time, all the way to the map: fit its old
drawings, put them over the ground, count them in its entry, publish its review item. The batch
(203a/203b) stops at writing documents and review items; this line is the rest of the way, as
one command the next site's session reuses:

```
.venv/bin/python tools/site_done.py <site id> [--working | --model-json FILE]
```

`--root DIR` redirects the data paths (the test runs the line on a copy of one site's files).
Exit codes: 2 = the site is not built, 1 = a document failed to sync, 0 = done.

## The line, step by step (as the next site's session runs it)

1. **fit** — `fit/batch_us.py run_sites`, but only when the site has candidate pictures in
   `web/data/plans.json` that have NEITHER a platefit document (`data/db/platefits/<site>.<plan>.json`)
   NOR a review-item entry yet. Covered pictures are never re-fitted: the batch's item upsert
   replaces a candidate's entry whole, so a blind re-run would swap the rich entries (gate
   scores, pairs, the why) for "no model answer" stubs. A site whose candidates are all covered
   skips the batch run entirely (Stonehenge: 13 candidates, 7 documented, 6 in the item).
   A brand-new site needs a model here: `--working` (the local vision model on the AI box) or
   `--model-json` (recorded answers, a dry run); with neither, unfitted pictures land in the
   review item as "no model answer".
2. **sync** — before any of them, the line's fabrication check: `plan_fit.fabrication_pattern`
   on every document's stored page-px pairs (the batch's gate passes the model's pattern class
   by construction — see What broke on Stonehenge). A document that hits is never synced: its
   candidate is upserted into the site's review item with the reason, the document is deleted
   (a later batch run re-fits the picture from scratch), and the line prints where it went. Then
   `pipeline/plan_fit.py build` for every remaining document: the big
   picture (a Commons file is downloaded once and cached in `data/raw/commons/big/`, paced like
   `pipeline/commons.py`), the similarity or homography fit, `plan_<id>.webp` + `plan_<id>_ink.webp`
   in `web/data/sites/<site>/`, and the entry in its `depictions.json` (kind "plan"/"view",
   corners, fit record, the source line). A document whose overlay is already current (same
   `at`, same doc id) is skipped, so re-running the line is a no-op.
3. **entry** — `pipeline/build_site.py set_drawings`: the site's drawing count in
   `web/data/sites.json` (plate + plans + views; survey maps don't count). The page colours
   the site's square by it — this is what makes a site a flagship on the map.
4. **review** — `fit/review.py export`, scoped to the site: it writes `web/data/review.json`
   (the whole open queue, as always) but records a resolving document into item files only for
   this site, so a one-site run never touches another site's files.

The output names every picture of the site and where it ended up: *synced to the map (gate X m)*,
*sent to the review queue (why)*, or *skipped: overlay already current*.

Stonehenge (the first site through the line, 2026-10-11): all 13 candidates were already covered
by the batch (7 automatic documents, 6 in one review item), so no batch run was needed — but the
line re-checked all 7 documents before syncing and found every one of them to be the model's
documented fabrication class (the batch's gate passed that class by construction, see below), so
not one was synced: the line sent all 7 into the site's review item with the reason and deleted
the documents. The site ends with 0 drawings, its entry stays at 0, and its one review item grew
from 6 to 13 candidates (the page then has 339 open of 340 items). A human's saved fit is what
puts the first drawing on this site. What the page shows now:

- `docs/site_flow/stonehenge.png` — Stonehenge open on the aerial photograph with no drawing on
  it at all: the panel's group is "Old maps and aerials" and offers only the 1842 six-inch OS
  survey (the 1900 one-inch map is hidden by the 150-year rule), the map's marker is uncoloured,
  and all 13 of the site's candidate pictures wait in its review item (one of the 339 open).
  The old 7 drawings that the first run put here are the fabricated pattern fits described
  below; they sit in the review item until a human places a real one.

Argentoratum (Strasbourg, the second site through the line, 2026-10-11): all 42 candidate pictures
were already covered by the batch (8 automatic documents, 34 in one review item), so no batch run
was needed — and the pre-sync fabrication check hit all 8 automatic documents, exactly as it had on
Stonehenge: each went into the site's review item with the reason and its gate score, and its
document was deleted. The site ends with 0 drawings, its entry stays at 0, and its one review item
grew from 34 to 42 candidates (the page still has 339 open of 340 items). Nothing new broke on this
site: the check caught the class before a single download, and a second run of the command is a
no-op (the item file byte-identical, only the page's timestamp refreshed). A human's saved fit is
what puts the first drawing on this site. What the page shows now:

- `docs/site_flow/argentoratum.png` — Argentoratum open on the aerial photograph with no drawing on
  it at all: the panel's group is "Old maps and aerials" and offers the Cassini map (1756-1815) and
  the Etat-major map (1820-1866) (the 1950 aerial is hidden by the 150-year rule), the map's marker
  is uncoloured, the panel's "old plans in books" box waits for a human to place one of the site's 42
  candidate pictures, and all 42 sit in its review item (one of the 339 open). The 8 automatic
  documents the batch had scored are the fabricated pattern class, so they wait there too.

## What broke on Stonehenge, and the fix (so the next site does not meet it again)

- **The download burst got 429'd.** `plan_fit.load_picture` used bare `urllib` for the Commons
  API answer and the big picture; seven back-to-back fits are 14 requests and Wikimedia 429s
  bursts (PITFALLS). Fix: `_fetch` in `pipeline/plan_fit.py` paces like `commons.get`
  (1 s apart, honours `Retry-After`, backoff on 5xx). The next site's pictures download the same
  way; no flag, no work.
- **The source line lied.** `plan_fit.build` said "Placed by hand..." for the batch's automatic
  fits too. Fix: a document with `"auto": true` gets "Fitted automatically by the batch on N
  matching points ... (gate score X m)"; hand fits keep their old string.
- **The drawings line showed 7 -> 7.** `build` already refreshes the count after each fit, so a
  "before" read after the sync sees the final value. Fix: `site_done` reads the entry before the
  sync; the line then prints the true journey (0 -> 7).
- **A one-site run must not write other sites' files.** `review.export` records a derived
  `resolved` into any item file that has one; one other site (alligator-effigy-mound) had a
  derivable but unrecorded resolution, so a global export would have rewritten its item. Fix:
  `export(root, site_id)` scopes the record to that site (the page file is still the whole
  queue). The batch keeps calling it global.
- **Not a bug, a page rule:** survey maps younger than 150 years are hidden from the site panel
  (only plans/drawings and 150+ year-old surveys show). Stonehenge's 1900 OS map therefore never
  appears; its 1842 six-inch map does. A site with only recent maps will look aerial-only in the
  panel even though the files are built.
- **The gate passed 7 fabricated fits by construction.** Every one of Stonehenge's automatic
  documents was the model's documented fabrication class (the `batch_us.llm_model` docstring:
  "internally perfect regular patterns"): a regular ladder of round page-px coordinates mapped
  to a regular ladder of ground points, implied scale = the site box's width over the page's
  pixels. The batch never asks the model for a placement — it solves the similarity from the
  model's own pairs and the gate scores that solution against the same points — so the
  residuals (0–44 m) and all three pre-gate counterchecks passed by construction: gate.md
  section 7's registered limit verbatim ("a consistent global error passes"). None of the 7
  sat on the real sarsens (one was 2–3× too large and ~70 m off-centre). The line is the last
  gate before the map, so it catches the class itself: `plan_fit.fabrication_pattern` (grid
  roundness, a 2D lattice clause, a 1D ladder clause — on the document's stored page-px
  pairs, pure, no download) runs on every document in `tools/site_done.py` before any sync; a
  hit goes to the site's review item with the reason and its document is deleted, never to the
  map. Verified to fire on every batch document in the repo (110 of 110 at calibration, before
  the line deleted its 7) and on none of the 20 hand-fit documents.

## Files the line touches (one site only)

`web/data/sites/<site>/**` (the overlays, `depictions.json`), the site's entry in
`web/data/sites.json`, `web/data/review.json` (always the whole queue), the site's own item in
`data/review/` (a resolution, or a fabrication-pattern candidate before its document is
deleted), new big-picture caches in `data/raw/commons/big/`. It never rewrites a fit document —
it only deletes a document whose page-px pairs match the fabrication pattern (the candidate
goes to the review item first), so the rest of `data/db/platefits/` is byte-identical across
runs — never another site's files, and never the 20 hand-fit documents
(`tests/golden/hand_fit_docs.sha256` stays green).

## The one-shot held-out measurement of the ink fit (task 302b, pre-registered before the run)

Pre-registered 2026-10-11, before any document of the set below was measured. The method is
`fit/inkfit.py` as of commit f7dbba6 (task 302a, done). The run happens ONCE per document,
after this commit, and the table below is pasted verbatim from the checkpoint
(`data/inkfit/heldout/results.json`) - no cherry-picking, no re-tuning of anything on this
table (the single exception the parent task authorises: the sync/review confidence threshold,
set on this table and applied in 302c).

**The method never sees the hand fits.** `fit/inkfit.py` reads only the site catalog
(`web/data/sites.json`), the plate image and the site's relief; it never opens a platefit
document. The comparison with the hand fits happens only in the evaluator,
`fit/inkfit_heldout.py`, which reads each hand document's stored pairs solely to compute the
numbers in this table. The 21 documents below are the held-out truth set; no parameter of the
method is chosen or adjusted against them.

**The 21 held-out documents (sorted; the original 20 of `tests/golden/hand_fit_docs.sha256`
plus the lead's 21st, the DPLA Maiden Castle plan - all verified to carry no `auto` flag as of
this commit; 19 sites, Maiden Castle and Old Sarum twice each):**

1. arbor-low-q630312.earthworkenglan01allcgoog_n0597_1
2. avebury-q661855.earthworkenglan01allcgoog_n0581_1
3. aztalan-state-park-q4832928.antiquitiesofwis00saph_n0182_1
4. badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1
5. bergues-q244934.c_4bbca705be732b1c
6. berkhamsted-castle-q4892150.c_1699141d593ead5a
7. cadbury-castle-q1025082.c_1fab2a0abe5b99d7
8. cahokia-q333661.c_aff1b996dce7fe3a
9. calleva-atrebatum-q1027253.earthworkenglan01allcgoog_n0360_1
10. camp-d-attila-q18749222.c_6a912845c1e1aa28
11. castle-rising-castle-q1049485.c_70f937b71ae63d6a
12. hembury-q3784763.earthworkenglan01allcgoog_n0108_1
13. little-solsbury-hill-q548780.c_7ff7261c6b3574b6
14. maiden-castle-q1232816.c_c20ff6b1f16d173d
15. maiden-castle-q1232816.earthworkenglan01allcgoog_n0124_1
16. mayburgh-henge-q1469390.c_984782b9e35e8ded
17. mound-bottom-q14710093.c_0b98157d7af17d6e
18. old-sarum-q782719.c_8192abb966d030a3
19. old-sarum-q782719.earthworkenglan01allcgoog_n0142_1
20. serpent-mound-q968802.ancientmonuments00squi_n0210_1
21. whitley-castle-q7996561.c_802bb5ba395d4d29

**Frozen configuration (all in `fit/inkfit.py`; unchanged after this commit except bug fixes):**
- Ink extraction: `pipeline/autowalls.py` frozen config (docs/autofit.md section 3): ink level
  0..1 from grey (paper 85th / ink 1st percentile), 20 px border zeroed, Frangi sigmas
  (4, 6, 9) px beta 0.5 gamma 0.013, threshold 0.25, skeletonise, drop pieces under 50
  skeleton px or 50 px bounding box, 25 px orientation coherence >= 0.6, length filter,
  structure-tensor normals (4 px), about one skeleton pixel in two kept as template points.
- Variant: **no-model** - the AI box is not reachable from this VM, so there are no
  blanking boxes and no per-piece keep/drop: every surviving piece is kept (the model step
  is injectable but is not used in this run).
- Relief: `dem_sources` at 1.0 m/px (PX_M) over the catalog `site_bbox` (the site's `size_m`,
  all 19 sites have one), local relief = DEM minus a 24 m-radius smoothed copy, clipped to
  +/-1 m, water (flood plain) and OSM modern features masked to NaN.
- Seed (never a coordinate): `fit/propose.py` anchor - scale from the scale bar, else the
  ratio text at the book's recorded ppi, else the picture size; north from the arrow unless
  untrustworthy, else north-up; centre the site.
- Search: the seed is the only anchor; window rotation +/-25 deg, scale x0.74..x1.36, centre
  +/-200 m; coarse grid rotation 2 deg / scale 0.04 log / 4 m cells (FFT correlation of the
  rendered template against 8 per-direction contrast images), top 3 peaks per map per seed,
  8 best distinct candidates (apart by >4 deg / >8% scale / >30 m), pattern-search refine
  (1/0.5/0.25 deg, 2/1/0.5%, 4/2/1 m), n_refine = 8.
- Objective: mean over template points of max(contrast, -0.2 m) (fit_plate's ridge contrast:
  the line minus the higher of its two sides 20 m away, on the LRM); a placement with fewer
  than 50% of its points on valid relief scores -9.0 (no fit).
- **Null recipe (search-matched):** the SAME search (identical seed, window, grid, refine)
  run twice more: (a) on a scrambled template - each piece rigidly rotated U(0, 2 pi) about
  its centroid, centroid translated U(-0.4, 0.4) of the panel extent in x and y, clipped to
  the panel, normals rotated with the piece, one seeded RNG (seed 20261012, pieces in
  order); (b) on the DEM shifted half the box north and half the box east (the LRM grid
  shifted -H/2 and +W/2 px, order 0, NaN fill; the masks' NaN holes move with the terrain).
  null = the HIGHER of the two null objectives; margin = objective(fit) - null.
- Reported points: per piece the two points nearest the 0.23 / 0.71 quantiles of its own
  principal axis, at most 2 per piece, longest pieces first, at most 10 in total, at least 4;
  redrawn (quantiles jittered +/-0.03, seeded 20261012) until `plan_fit.fabrication_pattern`
  is silent, 8 attempts; the final pattern check is re-run on the mapped pairs (a firing is
  a method defect, recorded, never edited away).
- Gate: the frozen `fit_gate.gate` (docs/gate.md section 2) on the method's own reported
  pairs with the method's own placement as the transform.
- One-shot: the runner checkpoints per document into `data/inkfit/heldout/results.json` as
  each document completes (a cut session resumes from the checkpoint); each document is
  measured exactly once; network (DEM / big pictures) is used only in this working phase.

**Corner-error metric.** Both similarities are Web-Mercator similarities in the document's
size frame, `merc = a * (u - i v) + b`: the hand fit's from `plan_fit.similarity` on the
document's stored pairs, the method's from its placement. Let (W, H) be the size frame and
C the four full-image corners (0,0), (W,0), (W,H), (0,H). Corner error (ground metres) =
k0 * sqrt( mean over C of | (a_m - a_h)*(u - i v) + (b_m - b_h) |^2 ), where the term in
brackets is in Web-Mercator metres and k0 = aw.ground_scale(lat0) (ground metres per
Mercator metre at lat0, the mean of the hand pairs' latitudes) converts it - the
`autofit.Site.corner_rms` convention (four full-image corners, two placements, ground
metres). Rotation error = arg(a_m) - arg(a_h) normalised to (-180, 180] degrees. Scale
ratio = |a_m| / |a_h|. A document the method could not place gets the method's reason
instead of the three numbers.

**Measured one-shot, run at 2026-10-11T22:47:37.081160+00:00.** Method: `fit/inkfit.py` as of commit f7dbba6, the frozen no-model variant (the protocol above). Each document measured once; a document the method could not place carries the method's reason in the corner-error cell. Rounding: corner error 0.1 m, rotation 0.01 deg, scale 0.0001, objectives 0.0001.

| # | document | corner error (m) | rotation error (deg) | scale ratio | objective | null | null margin | gate | fabrication |
|---|---|---|---|---|---|---|---|---|---|
| 1 | arbor-low-q630312.earthworkenglan01allcgoog_n0597_1 | 1399.1 | 27.63 | 13.2140 | -0.0144 | 0.0076 | -0.0219 | accept | silent |
| 2 | avebury-q661855.earthworkenglan01allcgoog_n0581_1 | 376.1 | -13.41 | 0.5925 | 0.5460 | 0.5178 | 0.0281 | accept | silent |
| 3 | aztalan-state-park-q4832928.antiquitiesofwis00saph_n0182_1 | 544.1 | -50.71 | 0.9880 | 0.0147 | 0.0359 | -0.0212 | accept | silent |
| 4 | badbury-rings-q798831.earthworkenglan01allcgoog_n0132_1 | 264.5 | -1.16 | 0.7048 | 0.5913 | 0.4042 | 0.1871 | accept | silent |
| 5 | bergues-q244934.c_4bbca705be732b1c | 1283.0 | 20.97 | 0.4624 | 0.0826 | 0.0633 | 0.0192 | accept | silent |
| 6 | berkhamsted-castle-q4892150.c_1699141d593ead5a | 231.2 | 1.40 | 1.4181 | 0.1666 | 0.1431 | 0.0235 | accept | silent |
| 7 | cadbury-castle-q1025082.c_1fab2a0abe5b99d7 | 377.4 | 30.14 | 1.0667 | 0.2117 | 0.2303 | -0.0186 | accept | silent |
| 8 | cahokia-q333661.c_aff1b996dce7fe3a | 831.1 | 1.86 | 3.0468 | 0.0210 | 0.0728 | -0.0518 | accept | silent |
| 9 | calleva-atrebatum-q1027253.earthworkenglan01allcgoog_n0360_1 | 2203.6 | -17.79 | 0.2378 | 0.3386 | 0.2316 | 0.1070 | accept | silent |
| 10 | camp-d-attila-q18749222.c_6a912845c1e1aa28 | 634.3 | -19.95 | 0.9269 | 0.4540 | 0.9690 | -0.5150 | — | not enough wall ink (2 candidate points, need 4) |
| 11 | castle-rising-castle-q1049485.c_70f937b71ae63d6a | 313.2 | 19.85 | 1.9200 | 0.3466 | 0.2660 | 0.0806 | accept | silent |
| 12 | hembury-q3784763.earthworkenglan01allcgoog_n0108_1 | 424.0 | 23.15 | 0.5388 | 0.1271 | 0.1355 | -0.0083 | accept | silent |
| 13 | little-solsbury-hill-q548780.c_7ff7261c6b3574b6 | 784.6 | -6.45 | 3.1200 | 0.1059 | 0.2998 | -0.1940 | accept | silent |
| 14 | maiden-castle-q1232816.c_c20ff6b1f16d173d | 536.0 | -1.52 | 0.6134 | 0.2608 | 0.2462 | 0.0146 | accept | silent |
| 15 | maiden-castle-q1232816.earthworkenglan01allcgoog_n0124_1 | 1160.5 | 97.86 | 0.7809 | 0.2193 | 0.1345 | 0.0848 | accept | silent |
| 16 | mayburgh-henge-q1469390.c_984782b9e35e8ded | 469.2 | -27.28 | 0.9611 | 0.1155 | 0.1579 | -0.0424 | accept | silent |
| 17 | mound-bottom-q14710093.c_0b98157d7af17d6e | 488.8 | 23.65 | 0.4663 | 0.1536 | 0.0784 | 0.0752 | accept | silent |
| 18 | old-sarum-q782719.c_8192abb966d030a3 | 1138.6 | -90.85 | 0.9969 | 0.1207 | 0.1093 | 0.0114 | accept | silent |
| 19 | old-sarum-q782719.earthworkenglan01allcgoog_n0142_1 | 717.3 | 76.39 | 0.6658 | 0.1988 | 0.1295 | 0.0693 | accept | silent |
| 20 | serpent-mound-q968802.ancientmonuments00squi_n0210_1 | 478.8 | -12.62 | 2.0411 | 0.2007 | 0.2332 | -0.0325 | accept | silent |
| 21 | whitley-castle-q7996561.c_802bb5ba395d4d29 | 1078.7 | -126.09 | 2.0789 | 0.0173 | 0.0274 | -0.0101 | accept | silent |

## Shotwick Castle: the first agent-placed fit through the line (task 303, 2026-10-11)

206's session placed Shotwick's plan (Mackenzie, The Castles of England, 1897, a Wikimedia
Commons file) on the page's 1280-px thumbnail and saved it with four pairs of round page-px
coordinates (405,25 / 827,570 / 620,835 / 30,690). Before 303 such a document carried no mark
at all, and the line would have carried it to the map as though the owner had placed it.
303's migration stamped it `by: agent`, and from then on a document without `by: hand` is
treated as automatic, so this document went through the line's fabrication check like any
batch fit. The live run (`.venv/bin/python tools/site_done.py shotwick-castle-q7502621`,
2026-10-11):

- **fit** — the site's one candidate picture in `web/data/plans.json` (the Allcroft 1908
  "EARTHWORKS" plate, shared by four sites) has neither a fit document nor a model answer:
  it became the site's new review item, candidate why "no model answer". The 206 document is
  covered, so no batch run re-fits anything.
- **sync** — `who_placed` = agent (stamped; no auto mark, no gate score: a session, not the
  batch, placed it, so nothing is stamped back and no gate score exists). The fabrication
  check on the document's stored page-px pairs does NOT fire. Nearest margins: the 2D
  lattice clause comes closest, on the u axis (gap ratios max/median 1.744 against the
  <=1.3 threshold; v axis 3.759; the min/median ratios 0.963 and 0.828 pass their own
  0.67 floors); the 1D ladder clause has no run of three anchors sharing one coordinate
  (max run 1); grid roundness is 4 of 8 distinct coordinates on the 10-px grid (0.5 against
  0.9). The document is built: the big Commons picture is downloaded once (paced, cached in
  `data/raw/commons/big/`), the similarity fit has residuals 14.2 / 2.0 / 17.5 / 19.4 m
  (0.2289 m/px, rotation -0.2 deg), the overlay `plan_c_e6e5490609414bb9.webp` and its ink
  go into the site's panel, and the page's source line says who placed it:
  "Shotwick Castle, plan from Mackenzie, The Castles of England (1897) (1897), Wikimedia
  Commons: by The British Library; No restrictions; … Fitted automatically on 4 matching
  points; one rotation and scale fits them within 20 m." (the first "(1897)" is the
  picture's title, the second the document's label; both read the book's year).
- **entry** — the site's `drawings` in `web/data/sites.json` goes 0 -> 1: the page now
  colours Shotwick's square by it.
- **review** — the new Allcroft item is open (no resolving document): "review
  shotwick-castle-q7502621.earthworkenglan01allcgoog_n0575_1.json: 1 candidate(s), open;
  page now has 340 open of 341 items".

Outcome: **map** — Shotwick's agent fit passes the line's fabrication check and is built
with the honest automatic source line (no gate score, because a session placed it). A
second run of the line is a no-op: "skipped: overlay already current", "drawings 1 -> 1",
the item file and `depictions.json` byte-identical.

## The one-shot held-out measurement of the survey-sheet fit (task 304, pre-registered before the run)

Pre-registered 2026-10-12, before any document below was measured by this method. Two
automatic fits have failed: the vision model invents its points (301) and ink against LiDAR
relief lands 231-2204 m off on this same set (the 302b table above). This third try matches
the plan against the site's old survey sheet — both are ink drawings of the same banks and
ditches, often of the same decades — and carries the sheet's georeference over. The method
is `fit/surveyfit.py` as of the freeze commit **737508d** (frozen 2026-10-12; the exact API
parameters, thresholds and grids are restated in **The frozen configuration** below). This
section is amended at the freeze commit and at the run (the measured table), never otherwise.
**No parameter of the method is chosen or adjusted against the 21 held-out documents,
before or after the run.** Development and smoke tests use only non-held-out pictures of
sheet-carrying sites, recorded in `data/surveyfit/devlog.md`.

**What the method sees.** For a (site, plan) pair it reads only: the **plan panel** — the
doc's `crop` box in the page picture (book scans: `data/raw/books/<ia>/full/<file>`
resampled to the doc's `size` frame; Commons: the big picture `data/raw/commons/big/
<id>.jpg`); the **sheet** — the site's finest-scale `kind "map"` / `"topo"` depiction from
`web/data/sites/<site>/` (the `.webp` mosaic and its `corners`, which georeference it;
13 of the 19 sites carry the OS six-inch 1st edition (several also the 1-inch map, excluded
by scale), bergues and camp-d-attila the Cassini (no scale string on either depiction; it
wins over the 1840 Etat-major on the frozen file-order tie), aztalan / cahokia /
mound-bottom / serpent-mound USGS historical topo 1:62,500 or 1:48,000); and **priors** — the plan's
recorded scale bar (8 of the 21 docs; the plan's m/px from the 302b seed records) and its
recorded north arrow where trustworthy. It never opens a platefit document: the comparison
with the hand fits happens only in the evaluator `fit/surveyfit_heldout.py`, which reads
each hand doc's stored pairs solely to compute this table (the 302b separation).

**The match.** The lead's pre-trained cross-modal matcher MatchAnything-ELoFTR
(zju-community/matchanything_eloftr, Apache-2.0), served on the 5060 Ti behind the VM
tunnel at `http://127.0.0.1:8091`: `POST /match` `{image0, image1 (base64 png/jpg),
threshold (0.2), max_side (832)}` -> `{keypoints0, keypoints1 (original pixel frames),
scores, size0, size1}`; `GET /health` gates the run. The plan panel is image0, the sheet
image1. A RANSAC similarity (scale, rotation, translation) is fitted through the matched
pairs with a frozen inlier threshold. Priors shrink the search: where a scale bar exists
the scale is constrained to (plan m/px)/(sheet m/px, from the corners) within a frozen
tolerance band, otherwise the matcher's scale; where the arrow is trustworthy the
rotation is fixed, otherwise a frozen coarse-to-fine rotation sweep (the panel image
rotated before each match call) scored by inlier count; translation is then solved from
the matches and refined.

**The frozen configuration (all in `fit/surveyfit.py` as of commit 737508d; unchanged since):**
- Matcher: `POST http://127.0.0.1:8091/match` `{image0, image1 (base64 PNG), threshold 0.2,
  max_side 832}` (30 s timeout, one retry); each fit is gated by `GET /health`. The plan panel
  is image0, the sheet image1.
- RANSAC similarity: 2-pair exact samples, 400 iterations, one seeded RNG (seed 20261012),
  minimum 3 inliers, 8 px reprojection threshold (sheet px), least-squares refinement on the
  inliers; candidate scales outside (plan m/px)/(sheet m/px from the corners) x (1/1.5, 1.5)
  are rejected, only where a scale prior exists.
- Priors: a scale prior only from a recorded scale bar or a printed ratio at the recorded ppi
  (8 of the 21 docs; picture-size anchors are not priors); a fixed rotation only when the
  north arrow is recorded and |deg| <= 60 (propose._rotation's rule), otherwise the sweep.
- Sweep: coarse 0..360 by 12 deg (30 match calls), then +- one coarse step by 2 deg (13 calls,
  deduped only within itself, so a fine theta equal to a coarse one is sent twice); the best
  by score wins.
- Nulls (search-matched, at the chosen theta): (a) the 302b scramble of the panel (each piece
  rigidly rotated U(0, 2 pi) about its centroid, centroid translated U(-0.4, 0.4) of the panel
  extent, nearest integer, clipped, white background; one seeded RNG seed 20261012, pieces in
  (-length, idx) order, piece selection identical to 302b's) against the real sheet; (b) the
  real panel against the sheet image shifted half the box north and half east (order 0, white
  fill; the corners - the georeference - untouched). null = the higher of the two null scores;
  margin = score(fit) - null.
- Score: (inliers / pairs) / (1 + rms/8); 0.0 when there is no model or no pairs.
- Confidence: max(0, score x margin).

**Canaries (pre-freeze, recorded in `data/surveyfit/devlog.md`).** Before the freeze the
method ran against the live service on three sheet-carrying sites, all --no-null: the lead's
held-out doc (the Maiden Castle DPLA plan) - the lead's explicit direction as a pipeline check,
its numbers confirmation only (his raw smoke: 633 matches, 31 inliers, rotation 0.0 deg,
20-35-53 m at the three hand points) - and two non-held-out docs (barnard-castle, avaricum).
No parameter was chosen or adjusted from any of these numbers, before or after the freeze.
The stub suite (`tests/test_surveyfit.py`, 7 tests) proves the plumbing end to end and is
frozen as it stands.

This targets what the 302b table shows: scale ratios 0.24-13.2x
and rotations to 126 deg are what the relief search had to (and did) guess wrong.

**Carrying the georeference over.** Plan page-px -> (the similarity) -> sheet px -> (the
depiction corners' rectilinear map) -> Web Mercator; the reported placement is the plan
panel's corners on the ground.

**Null recipe (search-matched).** The same matcher and fit run twice more, through the
same service: (a) the 302b scramble of the plan panel (each piece rigidly rotated about
its centroid, centroid translated, one seeded RNG, the 302b seed convention) against the
real sheet; (b) the real panel against the sheet shifted half the box north and half east
(the 302b DEM shift, applied to the sheet image). null = the higher of the two null
scores; margin = score(fit) - null.

**Score and confidence.** Score = the RANSAC inlier fraction, reweighted by the inliers'
reprojection RMS: score = (inliers / pairs) / (1 + rms/8); confidence = max(0, score x
(score - null)), null = the higher of the two null scores - as restated in **The frozen
configuration** above.

**Aerial column.** The only held-out site with a `kind "aerial"` depiction is camp-d-attila
(`fr_ortho1950.webp`); where the matcher also works on the plan against that aerial, both
columns are reported, the sheet column first.

**The 21 held-out documents** are the list in the 302b section above, unchanged. A hand
fit whose site has no survey sheet is listed as "no sheet", not dropped (not expected:
all 19 sites carry a sheet).

**One-shot.** `fit/surveyfit_heldout.py` checkpoints per document into
`data/surveyfit/heldout/results.json` as each completes (a cut session resumes from the
checkpoint); each (document, ground) pair is measured exactly once, after the freeze
commit.

**Corner-error metric.** As in the 302b section: both similarities in the doc's size frame,
the four full-image corners, `k0 = aw.ground_scale(lat0)`.

**The verdict (from the task).** The method passes only if a confidence threshold exists
under which every accepted fit is within 60 m of the hand fit and at least 5 of the 21 are
accepted; the threshold is the pass criterion itself (as in 302b's one authorised choice),
not a method parameter, and the table is reported as it comes out. Pass -> task 304b wires
the fit into `tools/site_done.py`'s fit step (confident -> map, unsure -> review with the
reason). Fail -> this section says so and the method stops: no wiring, no fourth method.

(The measured table is pasted here after the one run, as in the 302b section.)

## Ready to fit: the owner clicks the points, the line does everything else (task 305, 2026-10-12)

The owner's hand fits are the only fits that land right (the automatic ones are 301/302b),
and he likes doing them, so the line now queues the hand fits: the built sites that still
have a candidate picture and no hand fit yet, one site at a time, the most worth seeing
first. The page shows him the next site with its best candidate already loaded in the
existing "Place an old plan" tool; he places the points and saves; the line takes the site
to the map. When he saves, that site is finished.

**The queue file.** `tools/fit_queue.py [--root DIR]` writes `web/data/fit_queue.json`
(`{"at", "entries": [...]}`), one entry per site: `{site, name, best: {plan, reason, row},
candidates: [{plan, title, book, view, draw_px}]}` — and, when the best row admits a
starting placement, the entry's `propose` key (below). A site is in the queue exactly when all
three hold:

- **built** — it has an entry in `web/data/sites.json` AND a `web/data/sites/<id>/` directory
  (the same rule as `tools/site_done.py`);
- **a candidate** — `web/data/plans.json` names it in a row's `sites` field, or one of its
  `data/review/` item files holds it a candidate (open and resolved items alike: the item's
  `site` field is the key, never the file name). The two sources are deduped by plan: a plan
  in both resolves to the plans.json row (the richer one; an item candidate without a plans
  row becomes the documented synthesis the page would build anyway);
- **no hand fit** — none of the site's `data/db/platefits/` documents carries
  `"by": "hand"` (agent documents do not disqualify: the owner is still free to place a
  better one).

The **best candidate** is the true plan over a bird's-eye view, then the larger drawing (a
book row: its map_box as a fraction of the page size in px; a row with no box, or a Commons
row: the whole page/image; an item candidate with no size stored: 0), then the plan id
(stable). The **one-word reason** says why it won: "the only candidate"; "a true plan" (a
plan chosen while a view exists); "the clearest scan" (the best of several plans); "the
clearest view" (the views win). **The order** applies that same key to each site's best
candidate, then by the site's name: the cleanest, most ink to click on comes first (as of
2026-10-12: 117 entries, starting with Devil's Dyke, Fort Ancient, Marietta — all clearest
scans). The tool is stdlib only and reads five inputs (the four above plus
data/books/index.jsonl, for the stage-B fields behind the `propose` key — fit/propose.py,
which computes it, is stdlib-only too), never an image, so the owner's Mac can run it with
any python; the private Finder/Amazon collections (PLAN.md) never enter it. The page
tolerates the file missing, stale or 404: no card, no error.

**The starting placement (the propose, 307ba).** An entry whose best row admits a starting
placement carries it as its `propose` key: the anchor mapping the picture's panel centre
onto the site's point at the recorded scale and rotation, re-emitted as the 3-5 page-px ->
lon/lat pairs the fit tool's preview and save use (`{pairs, scale_m_px, rot_deg,
scale_source, coarse, note}` — the four panel corners plus the centre). The scale climbs a
ladder: the book's printed scale bar where one is recorded, else the printed ratio at the
book's scan ppi, else the site's known size (the last two flagged `coarse`); the rotation
is the north arrow where it is trustworthy, else north-up. It is fit/propose.py's
`propose_for` over the row's stage-B fields (scale_text, blank_boxes, north_angle_deg,
north_arrow, map_box, full_size): a starting point, never a fit — the pairs are never
snapped or gate-checked. A row the proposal cannot anchor (no size, no site size_m, no
stage-B row) gets no `propose` key, and the page falls back to the ordinary three-point
flow for it, byte-identically. On the page, web/fitkit.js (loaded after fitqueue.js) reads
the key: opening the queued site's plan flies the map to the site's own box, hides the
site's earlier overlay, and seeds the anchor as the five draggable pairs — the drawing is
on the map before any clicking — and closing (back, Cancel, or the save) restores the
overlay exactly as it was. The gestures that move, scale and turn the placement, saving
from it, and the updated screenshots are 307bb/307c's.

**The card.** `web/fitqueue.js` loads after `web/review.js` and extends the page the same
way review does: a "Ready to fit (N to go)" card drawn into `#body` as the next sibling of
the home stats line (the tabs row and that line's text stay byte for byte — 201 pins them).
It names the next site — the first queue entry not done in this browser, not skipped this
session, and still a built site in this build — with its best candidate's row and the
one-word reason, and its buttons:

- **Place the drawing** — drives the existing fit tool in the fitqueue convention: `endFit`
  if a fit is active → `select(site)` → `setGround("relief", or "imagery" where the site has
  no LiDAR)` → `loadDeps` → `startFit(site)` → `openPlan(entry.best.row)`. `RV.pending` is
deliberately never set: the queue's row is the owner's clean slate (pre-placed machine
  pairs are the review flow's contract, not this one's). The tool's own clicking is
  unchanged — except that when the entry carries a `propose`, fitkit hooks into the chain at
  `openPlan` and opens place mode on the works (above).
- **Skip** — moves the card to the next site for this session only (an **Undo skips**
  button comes back with it and resets it in the card).
- **done** — when the owner's save lands, the card marks the site done in this browser
  (localStorage `aw.fitQueue.done` — the exact key/value its own saveFit wrapper writes)
  and moves on. The mark is self-healed against the file on load: a site that left the file
  (a hand fit saved from another window, or a regenerated queue) drops out, so the browser
  never asks for a fit the queue no longer needs.

A failed fetch of the queue file never breaks a page load.

**Save → the one-site line.** A save through the page PUTs to the `platefits` collection,
which `server/serve.py` stamps `"by": "hand"` (303: only the owner's fits are hand fits) and,
on that write, enqueues a job for a worker thread in the server process that runs
`tools/site_done.py`'s `main([site])` in-process with no model (the 2026-10-10 lesson:
never a subprocess from here). The line does the rest alone: the drawing lands on the map,
the site's `drawings` in `web/data/sites.json` refreshes and its square is recoloured, and
its review item resolves — without any other step. The page polls `depictions.json` for the
result; the server is never blocked (a write only enqueues and wakes, and two saves while a
line is busy both run). A DELETE keeps the old all-fits sweep (`pipeline/plan_fit.py`), so a
deleted overlay leaves the map. A tree without `tools/` writes no files at all (a stripped
test tree).

**What the check proves, and what only the owner can do.** `tests/test_fit_queue.py` covers
the whole line without any network, in three parts: (1) the queue rule on a synthetic tree
and on the real population (membership, the dedupe, the best-candidate rule, the one-word
reasons, the order, no Finder/Amazon input); (2) the save → line step through the real
server against a private copy of one site's files (PUT → the worker → the one-site line:
the overlay lands in the copy, the drawing count and the review item move, no network, no
other site's file touched); (3) the card in a real headless browser against the served tree
— the card renders, Place opens the fit tool with the queue row already loaded and its
plate image rendered, backing out keeps the same site, Skip moves on and Undo restores, and
a pre-seeded done mark (the exact key/value the wrapper writes) moves the card to the next
site on load. The step only the owner can do is the acceptance click-through on his own Mac
(`server/serve.py --lan`, port 8642): real points on the plate, save, the drawing on the
map.

**Place mode (task 307bb).** When the queue entry carries a `propose`, Place opens with the
drawing already on the map: the map flies to the site's box, the site's earlier overlay is
hidden, and the drawing sits where the proposal puts it - its panel centre on the site, at
the proposal's scale and rotation. That placement is the *anchor* (`web/fitkit.js`: the page
point it pins, the ground point, metres per page pixel, rotation), shown as five numbered
points (the panel's corners and centre). The owner moves the drawing itself: **drag** moves
it, the **wheel** scales it about its centre, **shift+wheel** turns it a degree per notch;
the map's own pan and zoom are off while placing and the panel reads the live scale and
rotation. Clicking a spot on the plate and then on the map still pins a point on top, and
each pin refines the anchor by least squares over all points (Undo and Clear step back
through the anchors). **Save** writes the ordinary platefit doc - the five placed points as
page-px to lon/lat pairs plus any pins, `"by": "hand"` - and the one-site line puts the
overlay on the map; **Cancel** brings the earlier overlay back. Part 4 of
`tests/test_fit_queue.py` drives exactly this in headless Chrome on a full temp tree: one
drag, wheel and shift+wheel, each checked against the page's own fit; Save from the
placement alone (the doc read back from the tree, its fit equal to the placed anchor, the
overlay the same similarity); and a second page's Cancel. Pinning on top is the owner's
check (307d).

**The working space (task 307c).** While placing, the map is the surface. The page picture
shrinks to a small reference card in the map's bottom-right corner (top-left on a phone, so
the sheet below keeps Save in reach); **Bigger** brings the old full pane back for pinning a
spot on the page, **Smaller** tucks it away again, and **Hide plan** still folds it to its
title bar. The side panel keeps only what placing uses - the plan's title and book, what to
do, the live scale and rotation, the opacity slider, Undo/Clear for pins, Save and Cancel -
and drops the plan/view switch, the per-point list and "Another plan". The fly-to fills the
free map with the site's box (it starts from no padding: MapLibre had been adding the
previous camera move's 390 px to this one's, which left the box a third of the free map).
All of it hangs off `body.placing` in `web/fitkit.js`, so every other layout of the page is
unchanged.

- `docs/site_flow/place_before.png` - place mode before 307c (Fort Ancient, 1440x900): the
  page picture in the big middle pane, a strip of map on the right.
- `docs/site_flow/place_after.png` - the same placement after 307c: the site's box fills the
  map, the plate is the corner card, the panel says how to move, scale and turn it.

- `docs/site_flow/fit_queue_card.png` — the card in the home view: "READY TO FIT — 117 TO
  GO", Devil's Dyke, "The Devil's Dyke Camp, near Brighton · Allcroft 1908 · Fig. 217 — the
  clearest scan", with **Place the drawing** and **Skip**.
- `docs/site_flow/fit_queue_place.png` — Place opens the existing fit tool with the queue
  row already loaded: the sheet pane's header "ALLCROFT 1908 · FIG. 217 · THE DEVIL'S DYKE
  CAMP, NEAR BRIGHTON", the plate's scan rendered, the "Plan, drawn from above" tab, and
  "SAVE ON THE MAP" (disabled until at least three points are placed: "Saving needs at
  least 3 points.")
- `docs/site_flow/fit_queue_skip.png` — after a Skip: "116 TO GO", Fort Ancient ("'Fort
  Ancient,' Warren county, Ohio Squier & Davis 1848 · Plate VII — the clearest scan"), with
  **Undo 1 skip**.
- `docs/site_flow/fit_queue_done.png` — with Devil's Dyke marked done in this browser's
  localStorage (the exact mark the card's saveFit wrapper writes when a save lands): the
  card starts at Fort Ancient — the mark self-heals against the file, and the card moves on.

## The matcher fit (the lead, 2026-10-11)

`fit/matchfit.py` is the first automatic fit that lands right. It sends the plan and an image of the ground whose
position is known (the site's LiDAR relief, its aerial photograph, its survey sheets) to a pretrained matcher,
MatchAnything-ELoFTR (Hugging Face `zju-community/matchanything_eloftr`, Apache-2.0) on the AI box's 5060 Ti
(port 8091; Local-AI-Lab `server/matcher`). Each ground is matched whole and as centred windows of 0.7-0.25 of
its size (the matcher fails past a 2-3x scale gap), the best RANSAC similarity is kept, and a fit is written only
with at least 10 consistent points and a rotation within 30 degrees of north. `tools/site_done.py` runs it first
in its fit step whenever the matcher answers.

A picture ELoFTR is not sure of goes to MatchAnything-RoMa (port 8092, `ROMA_URL`), which returns ~5000 dense
matches per call, so it is judged by the fraction of matches that agree (>= 0.4), not a count, at any rotation
(`matchfit.judge`; old town plans are often drawn along a river axis, Strasbourg at 32-39 degrees). Both matchers
go through the spread guard. On the 21 hand fits RoMa placed 10-11 at 0 wrong against ELoFTR's 7; on the queue
the only wrong accepts sat between 0.3 and 0.4 (docs/matchfit.md sections 7-8; the rules were read off those
tables). Every automatic fit still gets an eye check.

A look at the owner's hand fits (not a held-out test: the windows and the thresholds came from it): every result
with 10 or more consistent points landed 26-76 m from the hand fit; results with 2-7 points were 100-2000 m off.

First run over the Ready-to-fit queue (116 sites, 240 candidate pictures): 6 confident fits. Looked at on the page:
Fort Hill (Fowke 1902, on top of the hand-fitted Squier & Davis plate), Strasbourg 1819 (streets and the river bend),
Azincourt cadastre 1810 (the castle mark on the LiDAR motte, the Douai road) and Portus Lemanis (on the slope above the
canal) stay. Aesica's bath-house plan (one building, scale in feet) was matched at the wrong scale over ~250 m of
fields: rejected, back in the review queue with the reason. Castle Neroche's matcher points were stopped by the line's
fabrication check (the matcher's coarse grid looks like a ladder). The other 234 had 3-8 consistent points: mostly
side views, town panoramas and faint scans that do not match the ground. They stay in the owner's queue.

Fixed on the way: a review item's recorded resolution counted even after its document was deleted, so a fit taken
off the map left its picture out of the queue (`fit/review.resolved_doc`).

## The right-place check: the queue pairs a drawing with the right place, not a namesake (task 309, 2026-10-12)

The queue's first entry paired Allcroft 1908 Fig. 217, "The Devil's Dyke Camp, near Brighton" (a Sussex hillfort),
with the Devil's Dyke in Cambridgeshire (devil-s-dyke-q3307343) - same name, 150 km apart; the owner could not find
it on the map. So every pairing in the queue must now show the same *place* as its site, not just the same name,
before it reaches the page. `tools/right_place.py` is that check, and the `tools/fit_queue.py` build runs it as a
second phase: every flag decision is computed over the pre-mutation candidate sets (a move into a site can never
feed that site's own decision in the same build), then the drops, moves and review upserts are applied, and only
then are the entries derived.

**What it reads.** Stored files only, stdlib, no network: the catalog (`data/catalog/sites.jsonl`: the site's
classic county/state, plus a town-word -> classic-county index built from the catalog's admin values), the book
index (`data/books/index.jsonl`: the row's title, place, and the names read off the page) and the book lists
(`data/books/lists/*.json`: the printed list title, which beats the machine-read one). With none of those stores
present the check is a no-op and the build is exactly 305's.

**How it decides.** Two rules, both fail-open - a picture or site with an unknown place is never flagged:

- **H1, the explicit word.** The caption prints a county word (the matcher's UK county list, plus the extended
  Scottish and -shire spellings and the county abbreviations the books use) or a US state word. When the site's
  classic county (UK) or state (US) - read from its catalog record - is a different word, or the word belongs to
  the other side of the Atlantic, the pairing is flagged.
- **H2, the towns' county** - UK sites only, book rows only, and only when H1 has no word. The caption's town
  words (the parts after the name, minus county words and the matcher's generic words) resolve to classic
  counties through the catalog (a word pointing at more than four distinct counties is too broad to be a town
  and drops). When every resolved county is other than the site's, the pairing is flagged. H2 does not apply to
  Commons rows: their file titles are descriptions, not the book's "Name, Place" lists - the first full run got
  nine false positives from that (dunster, oakham, pontefract, stonehenge).

The flag's reason is `same name, other place: <caption place> vs <site place>`.

**Where a flagged picture goes.** The check runs the matcher's own rule against the catalog - the core of
`tools/right_place.py` is a verbatim copy of `pipeline/books_match.py`'s norm/tokens/place_of/score_candidate core
(marked VERBATIM; the drift test `tests/test_right_place_drift.py` pins it) - the exact-name and shared-token
channels scored the way the matcher scores them, the picture's implied county as the place gate, and a top
candidate of at least 0.5 (the matcher itself accepts at 0.75) counts as the "right site". Then: the right site
is built and in the queue -> the candidate moves into its entry (the row's sites narrowed to it); unbuilt -> it
is upserted into that site's review item with the reason; no catalog site passes 0.5 -> it is upserted into the
source site's own item. A target item that already holds the plan is not written (the batch's own entry keeps its
pairs and evidence) - a re-run over unchanged inputs is stable, zero churn.

**What it found in the committed queue.** The rebuild (`python3 tools/fit_queue.py --root .` plus the in-process
`fit/review.py export`) checked the 324 pairings of the then-116-entry queue - the 305 baseline was 117 entries /
325 candidates, and Shotwick Castle had already left on main when the lead's Oct 12 review export rebuilt the
site's state (the site is no longer "built": no `web/data/sites/` directory; the queue holds built sites only; its
review item stays in the review list) - and flagged 15 pairings over 9 sites, all true namesakes (verified one by
one). The caption is what the check read (the book's list title where the figure/plate key resolved, else the
machine-read index title - n0599_1 is the latter; the batch's item records the printed "CASTLE DYKE, AYSGARTH."):

| site | candidate | caption | reason (all `same name, other place: ...`) |
|---|---|---|---|
| Alauna | n0438_1 | Defences of York, Roman, Norman, and Mediseval | Roman, Norman, and Mediseval, York vs Maryport, Cumbria, England |
| Bokerley Dyke | n0599_1 | Castle Dyke, Aysgai-th, Yorks | Aysgai-th, Yorks, Aysgarth vs Dorset, England |
| Castle Neroche | n0438_1 | Defences of York, Roman, Norman, and Mediseval | Roman, Norman, and Mediseval, York vs Curland, Somerset, England |
| Clun Castle | n0575_1 | EARTHWORKS | EARTHWORKS, Devonshire vs Clun, Shropshire, England |
| Coria | n0354_1 | ARDOCH, PERTHSHIRE. | PERTHSHIRE vs Corbridge, Northumberland, England |
| Devil's Dyke | n0599_1 | Castle Dyke, Aysgai-th, Yorks | Aysgai-th, Yorks, Aysgarth vs Stetchworth, Cambridgeshire, England |
| Devil's Dyke | n0686_1 | The Devil's Dyke Camp, near Brighton | near Brighton vs Stetchworth, Cambridgeshire, England |
| Eaton Socon Castle | n0285_1 | British Village on Hampton Down, Bath | Bath vs St Neots, Cambridgeshire, England |
| Eaton Socon Castle | n0557_1 | SITE OF WINDMILL, FIRLE HILL. | FIRLE HILL vs St Neots, Cambridgeshire, England |
| Eaton Socon Castle | n0558_1 | WINDMILL SITES, LEWES DOWN | LEWES DOWN vs St Neots, Cambridgeshire, England |
| Eaton Socon Castle | n0558_2 | WINDMILL SITES, LEWES DOWN | LEWES DOWN vs St Neots, Cambridgeshire, England |
| Vindomora | n0354_1 | ARDOCH, PERTHSHIRE. | PERTHSHIRE vs County Durham, England |
| Windmill Hill | n0557_1 | SITE OF WINDMILL, FIRLE HILL. | FIRLE HILL vs Avebury, Wiltshire, England |
| Windmill Hill | n0558_1 | WINDMILL SITES, LEWES DOWN | LEWES DOWN vs Avebury, Wiltshire, England |
| Windmill Hill | n0558_2 | WINDMILL SITES, LEWES DOWN | LEWES DOWN vs Avebury, Wiltshire, England |

**The disposition.** Ten of the flags found a right site in the catalog - all unbuilt, so no candidate moved into
a queue entry: the candidates left the queue and were upserted, with the reason, into the right site's review
item. Six candidate writes landed in five new items: n0686_1 (the Brighton camp) -> devil-s-dyke-hillfort-q17674160
(Devil's Dyke hillfort, Sussex - the owner's case, score 0.65); n0599_1 (Aysgarth) -> castle-dyke-q31112898
(Castle Dyke, Yorkshire, 1.25); n0285_1 (Bath) -> down-end-castle-q5302812 (Down End Castle, Somerset, 0.50);
n0557_1 (Firle Hill) -> oval-barrow-and-adjacent-bowl-barrow-220-q17672356 (Oval barrow 220 m west of Firle
Beacon, Sussex, 0.75); n0558_1 + n0558_2 (Lewes Down) -> a-saucer-barrow-and-a-bowl-barrow-600m-n-q17677473 (a
saucer barrow and a bowl barrow 600 m north west of Lewes Prison, Sussex, 0.58). The other four flags were the
same (target, plan) pairs re-flagged from a second source site (the row's sites list carried the picture under
both) and were written once. Five flags found no catalog site passing 0.5: n0354_1 (Ardoch - the catalog has no
Ardoch) on Coria and Vindomora, n0438_1 (Defences of York) on Alauna and Castle Neroche, n0575_1 (Devonshire) on
Clun Castle. Those candidates left the queue and stayed in their source site's review item, where the batch had
already parked them (the upsert is skipped: the item holds the plan, and the batch's record stays as written).

**The queue's size: 117 -> 114.** 117 entries / 325 candidates (305 baseline) -> 116 / 324 (Oct 12, the lead's
re-export drops Shotwick) -> **114 / 309** after the rebuild. Two sites left entirely - Vindomora (its one
candidate was flagged) and Windmill Hill (all three were flagged) - and seven narrowed to their remainders -
Alauna, Bokerley Dyke, Castle Neroche, Clun Castle, Coria, Devil's Dyke, Eaton Socon Castle. Devil's Dyke's entry
is now its only remaining candidate (n0662_1 "SWEALD"), and n0686_1, the Brighton hillfort camp, sits in the
Sussex hillfort's review item, not in the queue. The five new items appear in the review list
(`web/data/review.json` was re-exported in the same run: 336 open of 346; the live count moves as items get
resolved - the lead's RoMa export of the same day resolved three more: Carisbrooke, Dudley, Newark). A re-run of the check over the rebuilt
tree re-flags the same 15; a re-run of the build writes no new bytes.

Two things to read in the reasons above: Bokerley Dyke's `sites.json` place is "Dorset, England" though the
catalog has it in Cambridgeshire (Dorchester, Cambs) - the flag decision used the catalog, but the human-readable
side of the reason quotes the `sites.json` string. And n0599_1's caption is the machine-read index title ("Castle
Dyke, Aysgai-th, Yorks"), not the printed "CASTLE DYKE, AYSGARTH." the batch's item records.

**Running it by hand.** `tools/right_place.py --root . [FILTER]` prints every flag with its signal (the explicit
word, or the towns and where they resolve), the stored reason, and the right-site candidates it would move to;
`--all` lists the pairs it passes as well. It reads only stored files. The original spec's `--live` path -
re-resolving caption place words through the cached Wikidata (`pipeline/catalog_wd.py`) - was for a human re-run
only and never part of the build; the check that ships is the stored-fields one above.

## The agent fits, looked at (task 306)

One line per agent-placed fit document, judged from the visitor's own view (the site opened, the
depiction active, 1440x900: aerial photograph, plus the LiDAR relief where the site has one;
screenshots in `docs/site_flow/agent_fits/`). 306a: the 23 documents on the map; 306b-f append
their review-queue and orphan fits below this list.

- aldenhaag-q23650779.c_71c4ef3170b44288 - 1832 kadasterkaart detail, identity fit (resid 0 m,
  gate 0.0): the ink follows the real village, roads and terp ring exactly. STAYS.
- alligator-effigy-mound-q4732645.c_618a6be74dfaff32 - 1891 Historical Collections of Ohio map,
  identity fit (gate 0.0): georeferenced town sheet; the effigy-mound park (looped paths) is the
  covered centre. STAYS.
- avaricum-q281826.c_d457524470ca0ab3 - Caesar, Allen & Greenough 1898, near-identity (gate 0.1):
  map of modern Cher with the Roman castra box drawn over the real town centre. STAYS.
- barnard-castle-q4185811.c_eacf8c673afcd863 - Alnmouth Tithe Map 1843, identity fit (gate 0.0):
  georeferenced; ink on the real streets and river, the "Barnard Castle" label over the real
  castle position at the river bend. STAYS.
- barwick-in-elmet-castle-q4865964.c_81c1ff143a862ee7 - Gott Collection at Hepworth Gallery (116),
  identity fit (gate 0.0): hachured contours track the real hill - summit hachures on the real
  summit, the rampart/ditch rings on the real earthworks above the village (confirmed on the
  LiDAR relief). STAYS.
- binche-q95121.c_957d7ce2933eb332 - town plan by Jacob van Deventer 1545, georeferenced (resid
  <=0.3 m, 6 points, gate 0.2): the medieval town core and street network sit on the real urban
  core; the sheet's frame extends over the surrounding farmland, as drawn. STAYS.
- bolsover-castle-q2968590.c_5531262b52faaea8 - Mackenzie 1897, similarity (4 points, rot -1.8 deg,
  gate 5.6 m): the drawn moat ring sits on the real moat around the castle park and the Great
  House range is drawn on the park's east side where the real house stands (confirmed on the
  LiDAR relief, where the drawn moat follows the real moat ring). STAYS.
- burlington-house-q225471.c_17e8fb3cf9037e19 - bird's-eye view by Johannes Kip (c. 1707),
  identity fit (8 points, gate 0.0 m): the Thames with its barges runs along the real river, the
  plate's street grid (incl. the upper-right diagonal) is parallel to the modern streets, the
  park at lower left. STAYS.
- forthill.b24849959_n0269_1 - Fowke 1902 Fig. 61, similarity (8 points, resid 0, rot -3.5 deg):
  the hachured oval, inner works and causeway sit on the real ridge and earthworks in the LiDAR
  (the aerial is uniform forest; the relief is the deciding view). STAYS.
- newark.ArcheologicalAtlasOfOhio_n0098_1 - Mills 1914, georeferenced (8 points, resid <=0.1 m,
  rot 1.2 deg): the surveyed 1848 earthworks (great circles, Mound City, the octagon complex)
  sit on the modern park grounds where the survivors stand, and the sheet's grid aligns with the
  city's street grid. STAYS.
- shotwick-castle-q7502621.c_e6e5490609414bb9 - Mackenzie 1897, similarity (4 points, resid
  2-19 m): WRONG SIZE - the drawn moated ring spans ~188 m at the fitted 0.2289 m/px (the moat
  fills the whole plate), but the real earthworks are at most ~90 m across (40 m x 20 m hexagonal
  motte, 25 m-wide ditch, 38 m bailey - NHLE 1016616): the fit is ~2x too big, and the 2-19 m
  anchor residuals are that scale mismatch, not placement error. The drawn ring sits on bare
  lawn in the park's north with no works of that size beneath it. REMOVED from the map (2026-10-12):
  the picture went to the site's review item with this reason, the document was deleted, the
  overlay pruned, the count re-exported.
- bethlehem-q2523914.c_075db5049e2fb635 - Survey of Palestine, Bethlehem 01-beit-jala (British
  military survey, 1940s: a sheet of the Bethlehem/Beit Jala area of Judaea), near-identity (4 pts,
  resid 13-23 m, rot 0.6 deg): WRONG PLACE - toponymic collision: this site is the Dutch hamlet
  Bethlehem (Het Hogeland, Groningen; Wikidata Q2523914), not the Judean town. The sheet frame
  spans the whole 1.2 km polder and the Beit Jala hamlet and field hatching land on the polder's
  parcel grid by local pattern coincidence - the small residuals measure that match, not the
  truth. REMOVED from the map (2026-10-12); the doc record is in the site's review item with this
  reason.
- bethlehem-q2523914.c_1c20017970e54a01 - Survey of Palestine, Bethlehem 06, identity fit (4 pts,
  resid 0 m): the same collision as sheet 01 - anchors sit where the Judean sheet grid coincides
  with the polder parcel grid 2000 km away; the sheet's hatched fields and contours cover the
  whole site. REMOVED (wrong place).
- bethlehem-q2523914.c_5ce1836b12e8e294 - Survey of Palestine, Bethlehem 03, similarity (4 pts,
  resid 6-26 m, rot 4.7 deg): same collision; the hatched Beit Jala contour field lands on the
  polder, densest over the village centre and the light field at upper right. REMOVED (wrong
  place).
- bethlehem-q2523914.c_67ed5d45466db19e - Plan of the Basilica of the Nativity, Sandys 1615,
  identity (6 pts, resid 0 m): WRONG KIND - an interior plan of the basilica building (the nave,
  chapels, the grotto square, the caption legend), not a ground map, fitted as if it were ground
  over the Dutch polder. REMOVED (wrong kind); the doc record is in the review item.
- bethlehem-q2523914.c_7ee79582ebdab559 - (1881) PLAN SOUTERRAINS DE LA BASILIQUE, identity rotated
  -18.4 deg (4 pts, resid 0 m): WRONG KIND - the grotto's subterranean plan (concentric rings and
  the title band) drawn diagonally across the polder as if it were a ground map. REMOVED (wrong
  kind); the doc record is in the review item.
- bethlehem-q2523914.c_993872ffecfce2cf - Survey of Palestine, Bethlehem 11, near-identity (6 pts,
  resid 14-41 m): same collision; the sheet's hatched hamlet and field area lands on the polder's
  upper-right parcels. REMOVED (wrong place).
- bethlehem-q2523914.c_a164ee440558d66c - Plan de Maestricht et environs 1748, detail Severen &
  Kanjel (a local map of the polder itself), similarity (4 pts, rot 0.6 deg, resid 34-112 m):
  the drawn Severen and Cantel hamlets sit on the real hamlets (the church and houses match), the
  village centre on the village centre, and the hatched field-boundary network follows the real
  polder parcels, the watercourse by Severen on the real one. The 34-112 m residuals are the 1748
  map's own hand-drawn inaccuracy (one rotation + scale cannot correct sheet-level distortion),
  not a placement error. STAYS.
- bethlehem-q2523914.c_a42a93d9589acd4d - same 1748 parent map, detail "Limmel" (the ink shows the
  local Bethlehem/Jerusalem/Leumel area of the polder), similarity (6 pts, rot 3.2 deg, resid
  6-28 m): the drawn houses line up on the real village centre, the watercourse on the real
  watercourse, the field parcels on the real parcels; the Bethlehem, Jerusalem and Leumel labels
  sit on the real places. STAYS.
- bethlehem-q2523914.c_a8499553451a203c - Survey of Palestine, Bethlehem 09, identity fit (6 pts,
  resid 0 m): same collision as sheet 01; the hatched field area lands on the polder's upper-left
  parcels. REMOVED (wrong place).
- bethlehem-q2523914.c_ba63da7d782b9648 - Survey of Palestine, Bethlehem 08, identity fit (4 pts,
  resid 0 m): same collision; the hatched hamlet/field hatching lands on the polder parcels,
  densest lower left. REMOVED (wrong place).
- bethlehem-q2523914.c_d624c308cd860a1e - same 1748 parent map, detail Limmel, Jerusalem &
  Bethlehem, similarity (6 pts, rot -4.1 deg, resid 3-18 m): the village centre and house symbols
  on the real hamlet, the watercourse on the real watercourse, the drawn farm complex on the
  light field at upper right. STAYS.
- bethlehem-q2523914.c_fc4566d6947287f4 - Survey of Palestine, Bethlehem 05-beit-jala, identity
  fit (4 pts, resid 0 m): same collision as sheet 01; the dense hatched Judean contour field lands
  on the polder's upper parcels. REMOVED (wrong place).

306b - the 21 review-queue documents. All ten of these sites' review items are resolved by these
documents today (none is in the open list), so the review tab shows nothing for them; each line's
item-cand note records the coarse candidate the tab would pre-place for the same plan if/when the
item reopens. All twenty-one stay (2026-10-12: judged from the 42 shots, none removed).

- argentoratum-q2361353.c_191c6221a81caad0 - Plan de Strasbourg, réduit, d'après Villot 1833,
  similarity (score 7.8; 0.0-0.1 m, 2.17 m/px, -32.3°): the 19th-c star-fort ring and street grid
  sit on the real town; the etatmajor ink (the 19th-c survey, still the visible texture) follows
  it, on the aerial and the relief. Item cand: coarse 6-pt anchor, median 54.8 m > 45, rejected.
  STAYS.
- argentoratum-q2361353.c_436bea5010beea89 - Strasbourg-Krutenau-Plan de 1852 (12) (score 4.3;
  0 m, 0.55 m/px, -36.3°): the Krutenau island district - Ill running through the plate's middle,
  Porte des Pêcheurs top, dense 1852 streets - sits on the real eastern old town; the plate's Ill
  lands on the real river (aerial + relief). Same 1852 survey as (13)/(15); the three crops agree
  (centres 7.75274/7.75375/7.75374). Item cand: coarse, median 133.4 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_5badc8c867ef5d98 - Plan Strasbourg projet Conrath 1880 (score 9.2;
  0.1-0.2 m, 4.03 m/px, +1.6°): old town + star-fort ring on the real core and ring. Item cand:
  coarse, median 122.7 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_5bfb0472f266c056 - 1831. Strasbourg (Tirage avec changement), after
  Villot (score 10.0; 0-0.2 m, 2.99 m/px, -32.1°): the full redrawing of the same source as the
  réduit above, on the same ground. Item cand REJECTED AS FABRICATED (10/10 anchors grid-round,
  the gate's 0.0 m measures their internal consistency only) - the document's fit is the real
  one. STAYS.
- argentoratum-q2361353.c_6acfd94dec8c011b - 91 of 'Strassburg und seine Bauten' (1894),
  'Argentoratum nach v. Appell' (score 1.8; 0 m, 0.62 m/px, +32.2°): the Roman castrum - wall
  rectangle, Decumane/Kreuzgasse grid, cathedral inside, Ill south - on the real built-up core,
  the grid on the real streets; independent of, and agreeing with, the 1775 wall plan
  (c_8bdbed9b69d51319). Item cand: coarse, median 47.8 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_87dc28a9645f0e59 - Strasbourg-Krutenau-Plan de 1852 (15) (score 4.6;
  0-0.1 m, 0.99 m/px, -36.3°): the Krutenau strip on the real eastern old town; one of the three
  crops of the same 1852 survey (see c_436bea5010beea89). Item cand: coarse, median 78.8 m > 45,
  rejected. STAYS.
- argentoratum-q2361353.c_8bdbed9b69d51319 - 1775 'Plan mur et tours Argentoratum', Weiss (score
  2.5; 0 m, 0.55 m/px, +39.0°): the Roman wall with its towers and the hatched interior blocks
  (cathedral etc.) on the real core; agrees with the independent 1894 castrum plan. Item cand:
  coarse, median 65.8 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_b3533cd48dfc6452 - Strasbourg-Krutenau-Plan de 1852 (13) (score 4.9;
  0 m, 0.58 m/px, -35.3°): the third crop of the same 1852 survey, on the real eastern old town.
  Item cand: coarse, median 101.6 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_e882645cc479c889 - 1819 'Plan topographique ... quatre Cantons' (score
  9.0; 0-0.1 m, 2.56 m/px, -10.7°): the 1819 star-fort line on the real ring (today's park belt)
  around the core. This is the item's recorded resolver - verified right, so the item stays
  resolved by a fit that is actually good. Its candidate carried a sheet-level 'Ville' Q1165252
  evidence conflict (~350 km west, near Paris) - a red herring (the plate is titled
  'Strasbourg'); the weak matcher count (32/1822) reflects the sheet-style drawing. Item cand:
  coarse, median 50.5 m > 45, rejected. STAYS.
- argentoratum-q2361353.c_ec1930f8ba9bbabb - 'Strasbourg plan 1870', Villot (score 8.7; 0.1 m,
  2.23 m/px, -32.3°): the four-cantons plan, fort line on the real ring. Item cand rejected
  (only 38% of its recorded feature points sit on textured ground: 'features are not visible
  where claimed'). STAYS.
- carisbrooke-castle-q328595.c_c280ff908ad8318d - Mackenzie 1897, The Castles of England (score
  3.0; 0.50 m/px, +16.2°, 8 anchors exact): the drawn Keep, Queen Elizabeth Gate, Woodhull Gate,
  K. Charles prison and Tilt yard sit on the 1842 OS 6-inch first edition's same-named features
  (3783/5000 line inliers against that surveyed map) - the real castle on its hill, visible on
  the aerial and the relief; the fitted 0.50 m/px is within 20% of the plate's stated 0.415.
  Item cand: a coarse 3-pt rectangle (0.695 m/px from picture size) whose eight hand-tied
  features the gate rejected (points give 0.901 m/px, disagreeing with the stated 0.415) - that
  rejected version is what the tab would pre-place. STAYS.
- castle-neroche-q5050201.c_44529cdbe2d10a9c - Bothamley 1911 'Somerset Map', hachured hillfort
  plan (score 3.6; 0.86 m/px, +1.8°, 8 anchors exact): the summit platform, ditch rings and the
  NE Plantation patch sit on the real Castle Neroche hill - summit anchors on the flat forested
  summit (aerial + relief), ditch anchors on the real SW ditch, the Plantation on the real NE
  plantation, drawn hachures following the real slopes; the weak matcher count (52/98) reflects
  the hachure style. Item cand REJECTED AS FABRICATED (8/8 anchors on a 10-px grid; the gate's
  0.0 m measures internal consistency only) - the tab would pre-place that grid-regular
  version. STAYS.
- castle-neroche-q5050201.earthworkenglan01allcgoog_n0110_1 - Allcroft 1908 Fig. 13, hachured
  summit + ditches (score 6.5; 0.39 m/px, -3.1°, 8 anchors exact): the summit platform ('856'),
  the concentric ditch rings and the Castle Farm buildings sit on the real summit, ditch ring
  and farm cluster (aerial + relief); fitted 0.39 m/px matches the plate's own 300-ft scale bar
  (0.397 m/px); the weak matcher (15/26) reflects the hachure style. The item cand holds the
  same pairs as this document (offset 0 m - the only 306b doc whose versions agree) but was
  flagged by the gate as a 1D-ladder anchor pattern; the placement itself is verified on the
  image. STAYS.
- castra-lemanis-q499898.c_be12fb0f9a87000b - 'Plan Portus Lemanis' (19th c.) (score 2.0;
  0.76 m/px, +0.5°, 8 anchors exact): the drawn port quadrangle spans the real headland slope
  above the sea - NE corner on the 1848 Squire & Davis red-ink 'STVTFAE CASTLE / Roman port'
  identification, SW corner ('Cutle') on the 'PORTVS LEMANIS (Site of)' one; fitted 0.76 m/px
  matches the plate's 500-ft scale bar (0.726); the weak matcher (15/25) reflects the sketch
  style. Item cand: coarse 2.667 m/px, median 63.0 m > 45, rejected - the tab would pre-place
  that ~3.5x too big version. STAYS.
- cawthorne-camp-q5055239.earthworkenglan01allcgoog_n0325_1 - Allcroft 1908 Fig. 97, the three
  Roman camps (score 2.2; 0.30 m/px, +0.4°, 8 anchors exact): the three drawn camps sit on the
  real Cawthorn Camps as the 1848 Squire & Davis map records them - the small square camp (1) on
  the red-ink square ring, the irregular camp (2) on the red-ink oval, the large camp (3) on the
  red-ink 'C A M P S' field complex - with 4625/4997 (93%) inliers against the LiDAR relief and
  the fitted 0.30 m/px equal to the plate's 300-ft scale bar. Item cand (not coarse): its point
  scale 0.790 m/px disagrees with the plate's scale bar (0.259) - gate-rejected, and it sits
  644 m north of this placement, off the 1848 camps; that is what the tab would pre-place.
  STAYS.
- cenabum-q2710144.c_e73dc8c09b2fea43 - Jollois 1833 'Plan général de la ville et des
  environs d'Orléans en 1828' (score 9.3; 5.41 m/px, +1.1°, 8 anchors, resid 0.1-0.3):
  the drawn 1828 city of Orléans - the radial old town, the fortified quays with the
  Portefeu de Todelaie/Du Coq river gates, the bridges, Faubourg St-Vincent, St-Jean-le-Blanc,
  Marceau - sits on the real city of Orléans, which is where this site's own point (the
  Wikidata 'Cenabum') lies: the radial centre and St-Vincent line up with the georeferenced
  1850s état-major survey within ~100-200 m, and the fitted 5.41 m/px is the plate's own
  ~1:20000 printed scale (2537/5000 matcher inliers against that survey). Item cand: the
  'Epinal' (Q173695, ~350 km NE) 200-sheet hit is a sheet-level red herring, and the coarse
  1.25 m/px candidate (median 161.9 m > 45, rejected) is what the tab would pre-place.
  STAYS.
- dudley-castle-q5311832.c_e66ec095ee45aed0 - 1885 'Plan of Dudley Castle Grounds' (score
  2.5; 0.69 m/px, +24.9°, 8 anchors exact): the hachured castle hill with its 26-36 contours,
  the Priory Ruins, St. Edmund's Church and the railway station on the Bingham Road sit on
  the real Castle Rock - summit anchor on the real summit (aerial + relief), drawn contours
  following the real cone; 2639/4998 inliers against the 1842 OS 6-inch first edition. Item
  cand: coarse 0.4379 m/px with 33% textured features (gate-rejected), centre 268 m off -
  the tab would pre-place that version. STAYS.
- ferme-d-azincourt-q20669811.c_804aa7af3eb2ac7c - 'Azincourt - cadastre de 1810' (score 4.7;
  1.23 m/px, -1.5°, 8 anchors, resid 0-0.1): the sheet is the 1810 cadastre of the Ferme
  d'Azincourt hamlet ('Monts d'Azincourt') of the Émerchicourt commune (Nord) - this site
  itself, not the Agincourt village of the Somme: the red farm cluster sits on the real
  hamlet, the drawn 'Chemin d'Émerchicourt', 'Chemin de Boursolain' and 'Bonnay' roads on
  the real roads, the drawn river on the real Scarpe near Aniche; fitted 1.23 m/px agrees
  with the item's own points (1.171), its stated 0.55 does not; the weak matcher (11/203)
  reflects the parcel style. Item cand: coarse 0.7246 m/px, 50x50 m rectangle, centre 363 m
  off - the tab would pre-place that. STAYS.
- watson-brake-q2552689.c_5e7bb19c79b509ed - 'Watson Brake - Map' (score 4.4; 1.28 m/px,
  -0.9°, 8 anchors, resid 0-0.1): the drawn round Gentry Mound, the S-shaped ring of North
  and South Mounds, the Watson Bayou meanders and the Watson School road sit on the real
  earthworks - over the LiDAR relief the ink traces the real ring and bayou, over the aerial
  the drawn ring aligns with the real ringed hill; 2399/5000 inliers against the relief; the
  fitted 1.28 agrees with the item's own points (1.448), its stated 0.625 does not. Item
  cand: coarse 0.625 m/px, 200x199 m rectangle (vs 635x743 here), centre 146 m off - the tab
  would pre-place that. STAYS.
- watson-brake-q2552689.c_b52ddcad2ee295c4 - 'Watson Brake Mounds - Map' (score 2.2; 0.52
  m/px, -1.6°, 8 anchors exact): the closer version of the same plate - the central Gentry
  Mound, the North and South Mounds bands and the bayou sit on the real earthworks (over the
  relief the ink traces the real ring; over the aerial the drawn central mound is on the real
  one, the bayou on the real meanders); 2926/4999 inliers against the relief. Item cand:
  coarse 0.625 m/px with 0% textured features (the strongest rejection of this batch), 94x248
  m rectangle, centre 187 m off - the tab would pre-place that. STAYS.
- zwolle-q793.c_f9cddae6b944a648 - van Deventer 1563 Zwolle town plan (score 10.2; 2.53
  m/px, -6.2°, 8 anchors, resid 0-0.1): the drawn walled medieval town (dense block grid,
  wall ring) and the meandering Swol river sit on the real Zwolle core and the real river
  meanders (aerial + relief); 1981/4998 inliers against the 1850 TMK. Item cand: coarse
  1.5625 m/px from hand-tied bastion/gate points, 38% textured (gate-rejected), a thin
  800x99 m rectangle, centre 455 m off - the tab would pre-place that. STAYS.

306c - the 16 US orphan documents: in the store, but no overlay built on the site and no
review item referencing them, so the page shows them to a visitor not at all; each was rendered
the way the page would if it ever showed it (the fit tool over the aerial, and over the LiDAR
relief, with the doc's stored pairs placed and refitted; shots in docs/site_flow/agent_fits/).
The eight serpent-mound docs were judged against the site's hand fit (n0210_1, S&D 1848 Plate
XXXV), which traces the real effigy on the LiDAR (head (-83.4288, 39.0254), tail
(-83.4314, 39.0258)) and is the reference placement. All sixteen were judged (2026-10-12):
nine sit wrong and were deleted the 303 way - the picture and the doc's own points went into
the site's review item with the reason, the document was deleted, the site's page file
re-exported scoped - and the site stays covered for the union check (an open item counts;
serpent-mound also keeps its hand overlay). The other 7 sit right and keep their document:
the drawn works land on the real ones, and each line below says which.

- marietta.b24849959_n0195_1 - Fowke 1902 Fig. 15 "The Marietta works", similarity (4 points,
  resid 0, 1.0 m/px, 0 deg): the scale agrees with the plate's own bar (1.073 m/px measured),
  but the placement is wrong - the drawn fort (50 Acres, 27 Acres, the old stockade) and the
  60-ft Conus mound profile at the page's foot land ~1.3 km S-E of the real Marietta earthworks
  (the ringed disc of Mound Cemetery on the LiDAR); farm ground with a parcel grid lies beneath
  the placement. DELETED - an orphan today, invisible on the page (the 303 way: the picture and
  its 4 points went to the site's review item with this reason; the document was deleted 2026-10-12).
- serpent-mound-q968802.b24849959_n0313_1 - Fowke 1902 Fig. 81 (the Holmes serpent; 5 points,
  resid 9-66 m, 0.41 m/px, +2 deg): the Holmes serpent runs N-S down the page and the fit
  stretches it to ~800 m of ground span (the real effigy runs E-W, ~400 m; the 66 m mid-residual
  is that stretch); head/tail coils and hatched hills sit NW/SE of the real ones, which the hand
  fit traces on the LiDAR. DELETED - an orphan today (the 303 way, 2026-10-12).
- serpent-mound-q968802.c_15ff865e5f3d8ddb - Baer 1889 engraving (a view row; 4 points,
  homography, resid 22/61/27/0 m): the 4 near-collinear pairs make the fit exact by construction,
  so the resid proves nothing; the engraved serpent lands ~180 m NW of the real effigy (whose
  hand fit traces it on the LiDAR). DELETED - an orphan today (the 303 way, 2026-10-12).
- serpent-mound-q968802.c_2c260a03d1f8df1c - S&D Plate XXXV via Commons (a second copy of the
  very plate the owner hand-placed; 4 points, resid 0, 1.0 m/px, 0 deg): it sits ~145-190 m SE of
  the hand fit and at ~4x the true scale (the Commons file is the plate alone: 1280 px = 1.28 km
  at the fitted 1 m/px, the real figure ~320 m) - the drawn S is bigger than and offset from the
  real effigy; not a duplicate of the hand fit. DELETED - an orphan today (the 303 way, 2026-10-12).
- serpent-mound-q968802.c_52dfe1fc979edf2c - Harper's New Monthly Magazine 1902 engraving (a view
  row; 8 near-collinear points, homography, resid 0 m): the 8 points sit along the north ridge
  line, so the fit is exact by construction and under-constrained perpendicular to it; the
  engraved serpent lands ~200 m NE of the real effigy (the plate centre maps to
  (-83.43055, 39.02681) vs the effigy's (-83.4301, 39.0256)). DELETED - an orphan today (the 303
  way, 2026-10-12).
- serpent-mound-q968802.c_7b01a4bb50d68b56 - "A School History of the United States" p. 26,
  full-page copy (4 points, resid 1-6 m, 0.94 m/px, +0.3 deg): the page-26 serpent lands ~230 m
  north of the real effigy, over the hatched hill in the farmland; the real effigy carries the
  hand fit only. DELETED - an orphan today (the 303 way, 2026-10-12).
- serpent-mound-q968802.c_8ebd42607fbb96d8 - the same figure, cropped copy (8 points, resid 0,
  1.0 m/px, 0 deg): the serpent and its "Mound 10 ft. high" spiral land ~255 m north of the real
  effigy, on the hatched hill in the farmland/NE hills; the real effigy carries the hand fit only.
  DELETED - an orphan today (the 303 way, 2026-10-12).
- serpent-mound-q968802.c_dd2c553d611e610b - the same figure, "no cap" copy (8 points, resid 0,
  1.0 m/px, 0 deg): the serpent lands ~265 m north of the real effigy, on the hatched hill in
  the farmland/NE hills (the twin of the cropped copy above). DELETED - an orphan today (the 303
  way, 2026-10-12).
- cahokia-q333661.annualreportofbu1218901891smit_n0200_1 - Thomas 1894 Plate VI "Map of the
  Cahokia group, Madison county, Illinois" (8 points, 1.3 m/px, -3 deg, resid 9.5-174.7 m): the
  plate's dense mound-group cluster (its subject) sits on the real Cahokia mound complex on the
  LiDAR (the bright mound cluster in the dark floodplain depression); the dashed "St. Louis and
  Collinsville Road" line follows the real road, the Mississippi hatch sits on the real river
  (dark band at the right edge) and the Horse-Shoe slough is at the NE end. The residuals are
  frame-level (the 1894 survey grid's page skew, -3 deg), not subject misplacement. STAYS.
- etowah-indian-mounds-q4533107.annualreportofbu1218901891smit_n0386_1 - Thomas 1894 Fig. 182
  "Plat of the Etowah group (original)" (8 points, 1.0 m/px, 0 deg, resid 0): a georeferenced
  plate - the drawn great ditch traces the real ditch band in the aerial, the hatched platform
  mound "a" sits on the real grassy mound, mounds b/c on the real mounds, and the Etowah River
  line follows the real channel. STAYS.
- fort-ancient-q5470727.b24849959_n0264_1 - Fowke 1902 Fig. 59 "Fort Ancient, Warren county"
  (from Squier & Davis; 8 points, 1.0 m/px, 0 deg, resid 0): the drawn walled loops (north and
  south forts) trace the real ditch/bank bands (the light lines in the aerial), the creek line
  follows the real meander at the SE, and the park is centred. STAYS.
- hodgen-s-cemetery-mound-q5876069.b24849959_n0353_1 - Fowke 1902 Fig. 96 "Plan of mound at Mt.
  Vernon" (8 points, 0.78 m/px, -0.1 deg, resid 8-33 m): the drawn hatched mound ring is
  concentric on the real cemetery mound - the distinct round LiDAR bump (bright centre, dark
  ring) in the residential block by the Big Sandy; the drawn ring is ~2x the real diameter but
  centred on it. STAYS.
- hodgen-s-cemetery-mound-q5876069.ArcheologicalAtlasOfOhio_n0092_1 - Mills 1914 "Plan of
  Cemetery Mound, Mt. Vernon." (4 points, 1.0 m/px, 0 deg, resid 0): the 100x100 m anchor
  square (and the drawn mound it encloses) sits ~110 m S-E of the real mound's LiDAR bump, on
  flat residential ground - the real mound lies just outside the drawn extent at its NW. Same
  mound as n0353 above, which sits right. DELETED - an orphan today (the 303 way: the picture
  and its 4 points went to the site's review item - merged into the item that already held the
  Thomas n0563 candidate, which stays open - with this reason; the document was deleted
  2026-10-12).
- mound-cemetery-q6919104.annualreportofbu1218901891smit_n0563_1 - Thomas 1894 Fig. 306 "Plan of
  Cemetery mouud, Mt. Vernon. Knox county, Ohio" (8 points, 1.0 m/px, 0 deg, resid 0): the
  drawn big concentric "Cemetery Mound" circle sits on the real conical mound (the ringed disc
  of Mound Cemetery, Marietta - the bright LiDAR bump with the dark ring), the drawn fence
  circle spans the real cemetery parcel, and the drawn streets (Market/High/North St) follow the
  real street grid; the page's "MARIETTA WORKS" label is centred in the drawing. (The caption's
  "Mt. Vernon, Knox county" is the source's own labelling; the plan matches the Marietta
  cemetery.) STAYS.
- mount-horeb-earthworks-complex-q6921321.c_d1dff07f0da57b0e - S&D 1848 Plate XIV Fig. 3 "Peter
  Village enclosure" (drawn by C. Rafinesque; 5 points, 1.0 m/px, 0 deg, resid 0): the drawn
  bank/ditch arc (hatched double line) lies on the real bright bank band + dark ditch line of
  the earthwork in the LiDAR, following the real ditch's S-bend near anchor 3; the plate's own
  "500 ft to the inch" is consistent with the fitted 1.0 m/px. STAYS.
- pyramid-mound-q7263260.ancientmonuments00squi_n0134_1 - S&D 1848 n0134 (the plate is FIG. 9:
  a big double-ring circular earthwork with an entrance gap at the SW + a small square
  enclosure at the left; 4 points, 0.54 m/px, -5.5 deg, resid 17.7-33.9 m): the drawn
  double-ring circle (~230 m outer diameter) encloses the real dark-ringed ~100 m mound at
  ~(-87.5056, 38.6705): the drawn centre works out at ~(-87.5065, 38.6706), ~80 m west of the
  mound's centre, so the real mound sits in the eastern part of the drawn ring, its rim just
  touching the drawn outer ring - concentric-ish (the same class as the Fowke Mt. Vernon ring
  above: larger than the real works but centred on them), not the serpent-mound class of miss
  (145-265 m off, on foreign ground). The drawn square enclosure (anchor 4's feature) lands
  ~340 m west over residential ground with no visible earthwork - a secondary plate feature
  that does not change the call; the 18-34 m residuals reflect anchor quality, not the
  subject's placement. STAYS.

306d - the 18 UK orphan documents (sites a-l): in the store, but no overlay built on the site
and no review item referencing them, so the page shows them to a visitor not at all; each was
rendered the way the page would if it ever showed it (the fit tool over the aerial, and over
the LiDAR relief, with the doc's stored pairs placed and refitted; shots in
docs/site_flow/agent_fits/). Each line below says what the drawing's lines sit on (the real
banks, walls, ditches, streets) and the verdict; a fit whose drawn works visibly miss the real
ones is deleted the 303 way (the picture and the doc's own points go to the site's review item
with the reason, the document is deleted, the site's page file re-exported scoped to the site -
the site stays covered for the union check, an open item counts).

- bury-castle-q5001077.c_de779031cda8a0dc - Bury Castle Somerset Map 1911 (Bothamley's 'Ancient
  Earthworks' chapter; 8 points, similarity, resid 10.9-39 m, 2.63 m/px, +1.1 deg): the 8 anchors
  are a 100-px grid ladder (three on the left edge) whose 200-px and 100-px lat steps span
  0.0054 and 0.0018 deg (a 1.5:1 per-pixel ratio no similarity can hit) - the residuals only
  measure the grid's internal inconsistency, and the fit's 2.63 m/px is ~1.8x the plate's own
  'SCALE OF FEET 0-300' bar (~1.45 m/px); it places the drawn hachured hillfort (~280-340 m
  across, entrance gap at the SW) at (-3.5187, 51.0370), ~550-580 m N-NW of the real Burr Castle
  hillfort (the ~80-90 m hachured ring just NW of the site point on the OS maps, the LiDAR bump
  at the same spot), on a small hachured wood hill instead. DELETED - an orphan today, invisible
  on the page (the 303 way: the picture and its 8 points went to the site's review item with this
  reason - merged into the item that already held the Allcroft 1908 n0136_1 candidate, which stays
  open; the document was deleted 2026-10-12).
