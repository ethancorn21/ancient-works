# Finder, Amazon: geometric earthworks under forest

Ethan 2026-10-10: Amazon first, big geometric works (ditched enclosures, geoglyphs, ring ditches), he reviews
candidates now and then. Candidates stay on this Mac (`data/finder/` is gitignored); this file holds methods and
aggregate numbers only, never coordinates of unrecorded candidates. A candidate is a shape in a ground model, not a
find. "Unknown" can only ever mean "not in the public lists below"; the national register (IPHAN CNSA) and the
researchers' own files hold more than is public, and a real find is reported to IPHAN, not visited.

## 1. Test plan (written 2026-10-10 16:10 CDT, before any detector has run; not to be moved)

### Data

| Source | What | Use |
|---|---|---|
| EBA L1A strips (INPE, Zenodo 7636454, 7689693, 7689210, 7689909; CC BY 4.0) | 899 strips, 12.5 km x ~0.5 km, 2016-2018, ~4 pts/m2 | ground built here (`amazon_dtm.py`); test set; SW-Amazon search |
| SFB forest concessions (Zenodo 18683137 and siblings; processed by Fischer et al. 2025; CC BY 4.0 for the products, raw data owned by the Brazilian Forest Service, research and education use, credit required, contact requested) | wall-to-wall 1 m `dtm.tif` per survey, 2017-2025, Jamari, Jacunda, Bom Futuro, Altamira, Caxiuana, Saraca-Taquera, Crepori, Amapa | main search ground |

EBA's class 2 is only "last return" (2026-10-10, strip 0414): ground is re-derived (lowest return per 2 m cell,
progressive morphological filter). Checked on the pasture geoglyph in strip 0414: the filtered ground keeps the
ditch and its outer bank within 0.1 m of the raw lowest returns.

### Positives

Peripato et al. 2023 (Science 382:103, Zenodo 10214943) list 961 known earthworks; 24 are marked `TREES/INPE`, the
ones that team found in LiDAR under forest. A TREES point is a positive here only if it lies inside the swath of an
EBA strip as rasterised here (cells with returns, after `amazon_dtm.py`), checked per strip; points outside are
listed and not counted. Candidate pre-count from the strip outlines: 11 points in 6 strips (0126 x3, 0470 x2, 0476,
0333, 0621, 0414 x3), but strip 0414's three lie 50-200 m beyond its rasterised swath, so n is at most 8. The
frozen list goes to `data/finder/amazon/positives.json` with its sha256 below, before any detector runs on those
strips.

Frozen 2026-10-10 16:11 CDT, from the swath masks only (no relief looked at): n = 8 in-swath positives (0126 x3,
0470 x2, 0476, 0333, 0621); 0414's points are 95 m and 228 m outside its swath (third beyond 200 m), not counted.
`positives.json` sha256 `1109efe4ac495404089509135814a907eaf4f2db4a469fb740cb5270bb154e06`. The test strips' ground
models were rebuilt at 16:17 after the ground-filter change (section 2); recomputing the list from the rebuilt swaths
gives the same sha256.

Pasture geoglyphs (open ground, plain in satellite imagery) are NOT positives for the gate: they test nothing a
satellite cannot. They are a sanity check only.

### Tuning vs scoring

Tuning (filter, detector, thresholds): EBA strip 0414 and Jamari survey JAM02-2020 only (both already looked at).
The five strips holding positives (0126, 0470, 0476, 0333, 0621) are scored once with the frozen pipeline; their
ground models are built but not looked at before that.

### Metrics

- K = 20 candidates per 100 km2 of swath (EBA strips: about 1.3 per strip).
- A positive is recalled if a top-K candidate centre lies within max(60 m, half its radius) of the point.
- n is at most 8, below the 15 needed to call a pass: recall is reported as "k of n, indicative", never "passed".
- Precision by eye: the top 20 candidates of each search area are labelled by Claude before any comparison with the
  known lists: `geometric` (closed or near-closed regular ditch/bank, not explained by streams, roads or logging),
  `natural` (stream heads, oxbows, sinks, tree throws), `modern` (logging roads, skid trails, log decks, ponds,
  field edges), `unsure`. Ethan's verdicts (page buttons) are added as they come and reported separately.

### What counts as working

The detector goes on the page for a search area if it recalls at least half of the positives that turn out to be
in-swath at K = 20, and fewer than half of its top 20 in the tuning areas are `modern`. Either way the numbers are
reported as they are.

## 2. Detectors (frozen 2026-10-10 16:24 CDT, before any detector ran on a test strip)

Tuned on strip 0414 and Jamari JAM02-2020 only, as section 1 says.

**Ground (`amazon_dtm.py`).** Lowest return per 2 m cell, low outliers dropped, progressive morphological filter
(windows 6-50 m), kept if within 0.25 m + 0.06 m per metre of half-window of the opened surface. The first setting
(0.4 + 0.25) let understory through: 9% of 0414's swath stood >1 m above a 30 m opening, and those canopy blobs, with
ordinary ground around them, were 21 of the top 24 rings. At 0.25 / 0.06 that share is 2%. The geoglyph's ditch is
unchanged and its bank is shaved under 0.5 m. The test strips were rebuilt with this setting (16:17), unseen.

**A. Rings (`amazon_find.py`).** Unchanged from the module docstring (trench maps, 8 sectors, second-lowest
sector), then a stricter verify. On each of 32 spokes the ditch floor is the lowest point within 0.75-1.25 r and the
shoulders are the median ground 6-18 m beyond its edges on both sides. The first version read the far field instead
(out to 1.8 r), which on a ridge-top site is the next valley. Wall = lower shoulder minus floor. Score = the 25th
percentile of the 32 walls, so the ditch must hold its depth round three-quarters of the ring. That is the physical
difference from a stream channel, which shallows to nothing at its head. A ring is dropped if the inside and outside
shoulders differ by more than 1.5 m, or if more than 10% of its spokes leave the swath before the outer shoulder.
Strip edges read as ditches: 9 of the 0414 top 20 sat on them before this rule.

**B. Enclosures.** As in the docstring. Gaps up to 20 m are bridged (was 10 m; at 10 the 0414 geoglyph leaked out
through 28 m where it meets a valley side; at 30 nothing survived).

**Ranking.** One list per area: rings score their 25th-percentile wall and enclosures their median ditch depth x
closure x solidity, both in metres. Candidates within max(60 m, r/2) of a stronger one are merged into it.

**Tuning-area labels (Claude, by eye, top 20):** 0414: 1 geometric (the known pasture geoglyph, rank 1, found by both
detectors), 1 modern (track), 3 unsure, 15 natural. JAM02: 0 geometric, 0 modern, 1 unsure, 19 natural. Top score
0.39 m in JAM02, against 1.15 m for the geoglyph.

**Reading of K for scoring (fixed here, before scoring).** 20 per 100 km2, pooled: the top round(0.2 x total km2)
candidates across the five test strips by score. Also reported: each positive's rank inside its own strip.

**Said before scoring:** pooled K for ~40 km2 of strips is about 8 slots for 8 positives, so "at least half recalled"
needs 4 positives among the 8 highest candidates in five strips of forest. The gate was set too tight for strip-shaped
swaths. It is not moved; the in-strip ranks are reported next to it so the detector can be judged anyway.

**Known blind spots.** Rings within about 1.25 r + 18 m of a swath edge are not verified; enclosures touching the
edge are dropped. Square or D-shaped works show up only through B. Mounds, causeways and roads are not looked for.

Frozen files (sha256): `amazon_dtm.py` 2eb55b9a..., `amazon_find.py` 8a478f07..., `amazon_score.py` 3c5842b1...,
`aw.py` 1e852d2c..., `positives.json` 1109efe4....

## 3. Results

**Test, run once 2026-10-10 16:25 CDT with the frozen files (hashes re-checked before the run):** five strips, 42.1 km2,
pooled K = 8. Recall 0 of 8. No positive is near any candidate in its strip's full list either (lists of 5-24
candidates per strip). The detector does not go on the page on this evidence. Tuning-area precision: 1 of 20 modern
in each area (0 in JAM02), so that half of the gate held, but it is moot.

**Post-hoc, after scoring (these 8 are now seen and can never be a clean test again).** Relief of the ground model,
400 m around each positive:

| # | strip | what the ground model shows at the point |
|---|---|---|
| 1, 2 | 0126 | paired parallel banks ~30 m apart (a banked road), more pairs beside them |
| 3 | 0126 | faint raised oval ring, ~90 m across |
| 4, 5 | 0470 | paired parallel banks, as 1-2 |
| 6 | 0476 | faint raised ring, ~150 m across |
| 7 | 0333 | angular ditched enclosure in pasture, running off the swath edge (enclosures touching the edge are dropped) |
| 8 | 0621 | a large depression in a valley; unclear |

Positive 7 turned out to be open ground (ground share 0.79 at the point, pasture): by section 1's own rule a sanity
check, not a positive. It was counted because the rule keyed on the TREES/INPE label, which does not guarantee forest.
The verdict is the same either way: 0 of 8, or 0 of 7 under forest. Against Ethan's target (big geometric works) the
eight split into 4 banked roads (not the target), 3 in the target class (the two raised rings, 0 found by design; the
ditched enclosure, dropped by the edge rule chosen in section 2) and 1 unclear.

So the miss is in the design, not the tuning. Under forest these works show as low banks (raised roads, raised rings),
while both detectors look for ditches, and the speck opening and ground filter are built to keep ditches and shave
what stands up. Seven of the eight are visible by eye in this ground model, which means the data carries them. Next
detector, if pursued: raised rings and paired parallel banks. It needs a fresh test set, because these 8 have been
looked at.

Post-hoc exploration, not a test (one run, nothing tuned): detector A with the sign flipped (crest rings instead of
trench rings), same pre-steps, on 0126 and 0476. Neither raised ring (positives 3 and 6) is in its top 400. The rings
are faint next to the canopy texture left in the forest ground model, so flipping the sign is not enough for a
raised-feature detector.
