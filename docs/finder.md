# Finder: methods, gate, results

The Finder looks in LiDAR for earthworks nobody has recorded. Its candidates stay on this Mac: `data/finder/`,
`data/scan/` and `web/data/scan/` are gitignored. This file holds methods and aggregate numbers only; it never
lists coordinates of unrecorded candidates.

A candidate is a shape in the relief, not a find. It becomes more than a candidate only through independent
evidence (an old map symbol, a survey plate, a record) or a person checking the ground.

## 1. Test set and gate (written 2026-10-10, before any tuning; not to be moved)

### Areas

Tuning and held-out data are separated by county. Detector settings, re-ranker prompts and views are chosen on the
tune area only. Held-out areas are scored once, with the frozen pipeline, by `finder_eval.py --final`, which writes a
timestamped result file; numbers in section 6 come from that file.

| Area | County | Box (lon0, lat0, lon1, lat1) | Role |
|---|---|---|---|
| ross | Ross | -83.12, 39.24, -82.88, 39.42 (existing 2 m scan, ~414 km2) | tune |
| newark | Licking | -82.53, 39.97, -82.33, 40.09 (~226 km2) | held out |
| fortancient | Warren | -84.29, 39.30, -84.06, 39.43 (~285 km2) | held out |
| miamisburg | Montgomery | -84.47, 39.57, -84.20, 39.68 (~283 km2) | held out |

The held-out boxes were picked for the density of known works with mapped coordinates (OSM, GNIS), before any
detector ran on them. Caveat: Newark appeared in the Clef-flash smoke test (`docs/finder_models.md`), so re-ranker
wording was shaped with some exposure to its relief; no model was trained on it.

### Positives

Known earthworks with mapped coordinates, from: `specs/known_ross.json`, the built sites (`data/sites/*/site.json`),
OpenStreetMap `historic=archaeological_site` / tumulus (Geofabrik Ohio extract), GNIS mound summits, Wikidata items
already fetched by the catalog agent, and `data/catalog/sites.jsonl` (+ its relief triage) if present at freeze time.
Village sites, petroglyphs and other non-earthwork records are left out. Duplicates within 50 m are merged.
Each positive has a kind: `mound` (closed feature or point, diameter up to 60 m) or `enclosure` (walls, rings,
squares, hill forts).

Every positive is labelled by eye from a 300 m x 300 m relief crop at 1 m/px **before any detector output for its
area is seen**: `visible`, `faint`, `none` (destroyed or not in the relief) or `coord_off` (the record's point is
not on any feature but one is plainly nearby). The file `data/finder/positives.jsonl` is then frozen; its sha256
is recorded below. Recall denominators use `visible` + `faint`.

### Negatives / baseline

Random points on the same ground: sampled uniformly over land (water excluded, modern-masked ground included,
because positives can sit there too), more than 150 m from any positive, stratified to the positives' mix of
valley-floor vs upland ground (height above the lowest point within 1 km: under 15 m = valley). Mills 1914
neighbourhoods are NOT excluded. The baseline hit rate is the share of random points that a top-k candidate list
"hits" under the same tolerance as a positive.

### Metrics

- k is counted per 100 km2 of scanned area: K = round(k x area / 100). Main operating point: k = 20.
- A `mound` positive is recalled if a top-K candidate lies within 40 m of its point.
- An `enclosure` positive is recalled if a top-K ring or enclosure candidate's centre lies within max(60 m, half
  the enclosure's radius) of its centre.
- recall@k with a Wilson 95% interval; enrichment = recall@k / baseline hit rate@k.
- precision_known@k = share of the top K that hit a known positive. This is a LOWER BOUND: unrecorded real works
  count as misses.

### Gate (held-out areas pooled; final pipeline output)

| | Pass if |
|---|---|
| G1 mounds | n(visible + faint held-out mounds) >= 15, AND recall@20 >= 0.60, AND enrichment@20 >= 10 |
| G2 enclosures | n(visible + faint held-out enclosures) >= 15, AND recall@20 >= 0.50. If n < 15: "not measurable", ranks reported |
| G3 re-ranker | adopted only if, on held-out, recall@20 with it >= recall@20 without it, and positives-vs-hard-negatives AUC >= 0.70 (hard negatives = the detector's own top candidates that hit no known site) |

If a class has fewer than 15 visible held-out positives the gate for it is "not measurable", never "passed".
Reported alongside, with no pass bar: precision_known@k for k = 5, 10, 20, 50; recall at k = 5, 10, 50; the tune-area
numbers; and the Mills 1914 enrichment (share of candidates within the georeferencing error of a 1914 symbol vs the
same share for terrain-matched random points), with the chance that a random valley point lies near some symbol.

Frozen positives (2026-10-10): `data/finder/positives.jsonl`, 54 records in the four areas, sha256
`39f1cb53330a3a57cc917a9e94367b5882f9b2463fa7b7eaff1517ddba1deedc`. Labels are in `data/finder/positive_labels.json`.

| Area | mounds visible / faint / none | enclosures visible / faint / none / other labels |
|---|---|---|
| ross (tune) | 2 / 2 / 2 | 5 / 1 / 2, 1 coord_off |
| newark | 14 / 1 / 0 | 4 / 0 / 0 (+4 wall fragments, kind `other`) |
| fortancient | 5 / 1 / 2 | 1 / 0 / 0, 1 coord_off, 1 unsure |
| miamisburg | 1 / 0 / 3 | 0 / 1 / 0 |

Held out: 22 visible + faint mounds, so G1 is measurable; 8 of the 22 are the Newark Octagon's gateway mounds (one
site, one kind of mound), so results are also reported per site complex. Held-out enclosures: 6, so G2 is "not
measurable" by the rule above. The tune area has only 4 visible + faint mounds; tuning also uses known mounds
elsewhere in Ohio outside the three held-out counties (Licking, Warren, Montgomery).

### Re-ranker selection rule (written 2026-10-10, before any tune AUC was read)

Tune set: detector positions that hit tune mounds (Ross area + known mounds elsewhere in Ohio outside the held-out
counties) vs the detector's own top candidates in the Ross area that hit no known record (hard negatives). Every
crop is centred on a detector position. Configs: `s150` (5 m relief, 300 m crop), `m150` (15 m relief, 300 m),
`m300` (15 m relief, 600 m), `s150j` (`s150` plus the detector's measurements as JSON in the state).

1. Default config is `s150`. Another config replaces it only if its tune AUC (mounds) is higher by >= 0.05.
2. Ordering: pure Clef probability over the top 50 per 100 km2 vs a rank blend (mean of detector rank and Clef rank),
   chosen by tune-area mound recall@20; then stop.
3. Exactly two final runs on the held-out areas: `detector` and `clef` (as declared in G3). No third.

### Frozen pipeline (2026-10-10, before the held-out evaluation)

- Detector code: `finder_mounds.py` (detect / measure / keep) and `finder_scan.py detect_tile` (with the unchanged
  `scan.py` ring stage; big rings r >= 60 m kept down to snr 0.3) are not edited after the held-out detection runs
  started. Masks: `aw.modern_mask` (roads, rails, buildings, water, quarries) from the Geofabrik Ohio extract
  (2026-10-09) + `aw.water_mask`, exactly as pre-registered; golf courses and residential land are NOT masked
  (flagged in the export instead).
- Mound ranking: logistic model on 3 standardised features, fitted on tune data only
  (`data/finder/tune/mound_model.json`): log height prominence +0.99, log snr +0.63, log(0.5 + base slope) -1.11,
  intercept -1.98. Larger feature sets (adding elongation, roundness, top flatness, diameter) gave the same
  leave-one-out recall on the 39 tune mounds (0.31 at k = 20) and one gave a wrong-signed elongation term, so
  the smallest set was kept.
- Ring ranking: rings with r >= 60 m only, snr x exp(-ring-line slope / 2 deg). Ring share of every top-K: 0.2
  (tune: no mound crossed a k threshold because of it; High Bank's circle enters the top 50 per 100 km2).
- Re-ranker: Clef-flash, config `s150j` (5 m relief, 300 m crop, detector measurements as JSON in the state),
  rank blend (mean of detector rank and Clef rank) over the top 50 per 100 km2.

Tune results behind the re-ranker choice (30 tune mounds with a detection vs 186 hard negatives):

| Config | AUC (mounds) |
|---|---|
| s150 (default) | 0.524 |
| m150 | 0.499 |
| m300 | 0.652 |
| s150j | 0.675 |

k-equivalent recall of the 39 tune mounds (in-sample for the ranking model): detector 0.31 at k = 20 (0.44 at 50);
pure Clef ordering 0.26; rank blend 0.38. Rule step 2 therefore picked the blend.

sha256 at freeze: mound_model.json `df282fc2...a8942791`, finder_mounds.py `f26b5b2b...490e0b45e`, scan.py `3e7ec560...039080d27b5`.

## 2. Detectors

Both run on 2 m/px bare-earth DEM tiles (USGS 3DEP, 4 km core + 560 m pad, Web Mercator; `finder_scan.py`).
Modern features are masked with `aw.modern_mask` fed from the Geofabrik Ohio extract (`finder_osm.py`, no Overpass;
on two cached Ross tiles it reproduced the Overpass masks to 99.99% of pixels) plus `aw.water_mask`.

**Mounds** (`finder_mounds.py`). For basal diameters 8-64 m (8 scales; 36 m and up at 4 m/px) every pixel is
scored as a centre: mean height of a top disc (0.3 x radius) minus a plane fitted to a ring just outside the foot
(1.1-1.6 x radius), minus the second-highest of the ring's 8 sector residuals. The top has to stand above the
ground in every direction but one, so ridges, terrace edges and hill shoulders score near zero and a leftover
slope cancels. All sums are FFT correlations (about 9 s per tile). Peaks over space and scale (>= 0.12 m) are
then measured from 16 radial profiles: height above the ring plane, half-height diameter, roundness (min/max
radius), elongation (blob second moments), top flatness, ring-plane slope, ring roughness, snr, distance to the
nearest masked pixel. Plausibility limits: height 0.15-15 m, diameter 6-70 m, roundness >= 0.35, elongation <= 3.

**Rings** (`scan.py` stage 1 + verify, unchanged), plus: a size prior (rings under 60 m radius are not ranked;
small natural rings flood the list) and the slope of the ground along the ring line (geometric enclosures sit on
level terraces). On the tune area this moved High Bank's great circle from #729 of 7,231 (old scan) to #33 of 5,687
big rings and Hopeton's from #966 to #152. Those are tune-area numbers on two circles: indicative only.

**Fusion**: mound and ring lists are interleaved so that each top-K holds 20% rings (frozen value above).

What the top of the tune list holds, by eye (top 36, Ross area): reconstructed mounds inside Mound City, a few clean
isolated mounds in fields, golf-course landscaping (tees, greens), building remnants the bare-earth DEM did not
remove (rows of rectangular blobs), urban clutter, one DEM void filled with flat triangles.

## 3. Re-ranker

Clef-flash 9B (Cloudflare decision model) on the AI box's 5060 Ti, `127.0.0.1:18083`, one batch of 6 in flight,
about 1 s per crop. The smoke test separated whole-site renders from random ground (AUC 0.82-0.86); the Finder's
real task is harder: separating true mounds from the detector's own top false positives. On that task, plain relief
crops scored at chance (AUC 0.50-0.52 for 300 m crops); a 600 m crop (0.65) and the detector's measurements passed
as JSON (0.675) did better. 30 positives: differences under ~0.05 are noise. Selection followed the rule written
before the AUCs were read (section 1). Qwen was not used (servers belong to other agents).

## 4. Evidence: Mills 1914, Ross County

Source: W. C. Mills, Archeological Atlas of Ohio (1914), Ross County map (p. 71; IA ArcheologicalAtlasOfOhio leaf
153, 2053 x 1643 px). Legend (p. IV): solid triangle = mound, outlines = enclosures (square, circle, crescent),
arc = burial, other small symbols = village, cemetery, quarry, etc.

Georeferencing (`finder_mills.py`): Census TIGERweb county subdivisions (16 townships, the same names as in 1914)
were matched to the scan's own line work. Four county corners read by eye started an affine; a chamfer fit
(truncated distance from projected TIGER lines to the nearest dark pixel) refined it to a second-order polynomial.
Scale comes out at 31.5 m/px, i.e. 153 px per inch at "one inch equals three miles", consistent with a ~150 dpi scan.
Line residual after the fit: median 1.5 px (47 m), 69% of boundary samples within 3 px; the long tail (p90 8.5 px)
is township lines that have moved since 1914. The Scioto and the county outline sit on the 1914 lines.

Symbols: red pixels (r > 150, r - g > 70, r - b > 60), connected components classed by shape: 378 components,
240 single triangles + 43 merged triangle groups (353 mounds counted by area; Mills's own table for Ross County says
370), 12 enclosure outlines, 83 other. Output: `data/finder/mills_1914_ross.jsonl` (lon, lat, type, count, err_m).

Error on known works (symbol identified by eye on the scan, distance after georeferencing):

| Work | Symbol | Error |
|---|---|---|
| Hopeton Works | enclosure plan | 364 m |
| Liberty Works | enclosure plan | 599 m |
| Seip Earthworks | enclosure plan | 680 m |
| Mound City | enclosure plan | 949 m |
| Hopewell Mound Group | enclosure plan | 1,132 m |
| High Bank Works | enclosure plan | 1,556 m |
| Story Mound | triangle | 302 m |
| Adena Mound | triangle | 487 m |

The georeferencing itself is good to ~50 m along township lines; the error is Mills's placement. Enclosure plans are
drawn several times too large and pushed aside to fit (High Bank's plan sits 1.6 km SSE of the works, beside the
1914 river bend, while the township corner next to it lines up). Error radii used: enclosure plans 1,600 m (the
largest seen); triangles 750 m plus half the symbol size (about 1 km in practice; only two triangles could be checked).

What that means for "lost" (`lost` = a mound candidate inside the error radius of a 1914 triangle / triangle group /
small red symbol, or a ring candidate inside the radius of an enclosure plan): in the Ross tune area, 50% of random
ground (57% of valley ground, 46% of upland) lies inside the radius of some mound-type symbol. The top candidates are
not enriched near 1914 mound symbols: 49% of the top 20 per 100 km2 (detector ranking) lie inside one, vs 54% of
random points with the same valley/upland mix (ratio 0.91; 0.79 at k = 5, 0.94 at k = 50; the Clef blend gives
0.63-0.94). Counting enclosure plans too (1.6 km radii around mostly known works) the ratio is 1.3, but that only
says candidates cluster near the famous works. So a Mills 1914 match is weak evidence for any single candidate, and
the top of the list is not dominated by plowed-down 1914 mounds.

## 5. Classification and export (schema `finder-2`)

`finder_export.py <area> <label> [n_per100] [ranker] [county]` writes `web/data/scan/<area>/candidates.json`, one
relief crop per candidate in `web/data/scan/<area>/c/<id>.jpg` (1 m DEM, crop half-width max(150 m, 3 x r_m), the
same framing the current page assumes), and the area's entry in `web/data/scans.json`; a copy goes to
`data/finder/classified_<area>.json`. All of these are gitignored.

Product-only post-filter (not part of the gate pipeline): candidates on OSM industrial, commercial, retail,
military, landfill, quarry, construction, brownfield or railway land are moved below the exported top K (kept and
flagged, never deleted). In the Ross tune area 28 of the top 83 sat on such land (mostly one industrial site with
dozens of landscaped heaps). Residential land, golf courses and cemeteries are only flagged: known mounds sit in all
three. `DEMOTE=0` turns the post-filter off.

Classes:
- `known`: a modern public record lies within its tolerance: Wikidata (catalog), OSM historic=archaeological_site,
  GNIS, `specs/known_<area>.json`. Tolerance: enclosure records cover their radius + 60 m; OSM ways and specs 40 m;
  point records (OSM nodes, GNIS, Wikidata, catalog) max(150 m, 1.5 x coordinate precision).
- `lost`: no modern record, but inside the error radius of a kind-matched Mills 1914 symbol (mound candidates:
  triangles, triangle groups, small red symbols; ring candidates: enclosure plans). Weak evidence (section 4).
- `new`: no record we have. Means "unrecorded in these sources", not "a find".

Area entry (in `scans.json` and at the top of `candidates.json`), old fields kept: `name, label, area, size_km,
px_m, radii_m, n_total, n_shown, known[]`; added: `schema` ("finder-2"), `ranker`, `per100km2` (K = per100km2 x
area / 100), `kinds` {mound, ring: count}, `classes` {known, lost, new: count}, `demoted_settings`,
`mills1914_chance` {all, valley, upland, n}: share of random ground inside a mound-symbol radius, i.e. the chance a
mound candidate is called `lost` by coincidence.

Candidate, old fields kept: `id, lon, lat, r_m, score_m, snr, rough_m, sectors, rank, known, crop, corners,
clip_m`. For mounds `r_m` = half the half-height diameter, `score_m` = height above the ring plane (m), `sectors` = 8.
Added:
- `kind`: "mound" | "ring"
- `rank_score`: detector ranking score (mounds: logistic score; rings: damped snr)
- `p_reranker`: Clef-flash probability (null outside the re-ranked head or with ranker "detector")
- `measurements`: mounds {D, score, h_m, diam_m, round, elong, flat_top, snr, rough_m, base_slope, modern_m};
  rings {r_m, score_m, snr, rough_m, sectors, stage1_m, band_slope}
- `evidence`: {records: [{name, src, ref, dist_m}] within tolerance, nearest_record {name, src, dist_m},
  mills1914 {nearest_type, dist_m, err_m, nearest_matching_m, n_within_err, types_within_err},
  setting: [OSM land uses containing the point], dem_smooth: bool (very smooth surround, possible DEM void)}
- `class`: "known" | "lost" | "new"

## 6. Results (2026-10-10)

### Held-out gate (newark + fortancient + miamisburg pooled, 795 km2; 22 mounds, 6 enclosures)

First final run, `detector` ranking (`data/finder/eval/final_detector_20261010_125516.json`):

| | k = 5 | k = 10 | k = 20 | k = 50 |
|---|---|---|---|---|
| mound recall (n = 22) | 0.05 | 0.18 | **0.27** (6/22, 95% CI 0.13-0.48) | 0.36 |
| enclosure recall (n = 6) | 0.17 | 0.17 | 0.17 | 0.17 |
| precision_known (newark / fortancient / miamisburg) | 0.09 / 0.07 / 0 | 0.17 / 0.03 / 0 | 0.13 / 0.02 / 0 | 0.07 / 0.01 / 0 |

- **G1 mounds: FAIL.** recall@20 = 0.27 against the 0.60 bar. The enrichment clause (910 at k = 20) passes but
  carries no information: random ground lands within 40 m of a known mound 0.03% of the time at k = 20, so any
  detector that finds anything clears it. precision_known and the Mills comparison are the informative contrasts.
- **G2 enclosures: not measurable** (6 held-out enclosures < 15). 1 of 6 recalled (the Observatory Circle).
- Per site complex: 4 of the 6 hits are Octagon gateway mounds (8 of the 22 positives: low, regular, in mown
  parkland). Excluding them, recall@20 is 2 of 14 (Tippett Mound and one Fort Ancient mound).
- Tune vs held-out: tune leave-one-out recall@20 was 0.31; held-out 0.27. The ranking is not overfit; it is weak.

Why the misses. Of the 22, 6 are hit at k = 20, 11 are in the candidate list but ranked lower (per 100 km2:
5-65 for five of them, 140-8,300 for the other six), and 5 are not in the list at all. Point re-detection on 600 m
crops around the 5 total misses (same detector, diagnostic only; the frozen detector was not changed):
- 3 are rejected by the plausibility limits, not missed by the scorer: Miamisburg Mound is the strongest peak in
  its crop (18 m high) but over the 15 m height cap; Observatory Mound (attached to the Observatory Circle wall,
  roundness 0.26) and one Fort Ancient mound (0.29) fall under the 0.35 roundness floor.
- 2 are weak and half-masked: Twin Mounds (0.4 m score, 43% of the surround masked) and one small Fort Ancient
  mound (8 m across, 56% masked; found in the crop, not in the tile run).
- The ranked-too-low group is the main failure: typical true mounds here stand 1.5-2.5 m over the ring plane, and
  dozens of modern landscaping heaps, building remnants and spoil piles per 100 km2 score as high or higher.

Second and last final run, `clef` ranking (rank blend over the top 50 per 100 km2;
`data/finder/eval/final_clef_20261010_131225.json`):

| | k = 5 | k = 10 | k = 20 | k = 50 |
|---|---|---|---|---|
| mound recall (n = 22) | 0 | 0.09 | **0.23** (5/22, 95% CI 0.10-0.43) | 0.36 |
| enclosure recall (n = 6) | 0.17 | 0.17 | 0.17 | 0.17 |
| precision_known (newark / fortancient / miamisburg) | 0.09 / 0 / 0 | 0.09 / 0.03 / 0 | 0.11 / 0.02 / 0 | 0.07 / 0.01 / 0 |

- **G3 re-ranker: FAIL on both clauses.** recall@20 0.23 with it vs 0.27 without; positives-vs-hard-negatives
  AUC 0.44 (17 positives, 305 hard negatives) against the 0.70 bar. Clef-flash is not adopted. The tune AUC (0.675
  for `s150j`) did not carry over to held-out ground.
- The bake-off is over: two final runs, as declared. The detector ranking stays the product ranking; the 5060 Ti
  goes back to its harness agent.
