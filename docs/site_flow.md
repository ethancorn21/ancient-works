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
