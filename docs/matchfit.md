# The matcher fit: a pretrained cross-modality image matcher places old plans (held-out test)

Fourth attempt at an automatic fit, after three that failed or were never measured:
the batch vision model invented its points (task 301), hand-built ink features against LiDAR relief landed
231-2204 m off (302b, docs/site_flow.md), and the drawing-vs-survey-sheet idea (304) was never started.

`fit/matchfit.py` (the lead, 2026-10-11) asks MatchAnything-ELoFTR (Hugging Face
`zju-community/matchanything_eloftr`, Apache-2.0; served on the AI box's RTX 5060 Ti at port 8091,
Local-AI-Lab `server/matcher`) for matching points between the plan's picture and each ground image of the
site (LiDAR relief, aerial, and every georeferenced survey sheet of kind "map"), whole and as centred windows
(0.7, 0.5, 0.35, 0.25 of the ground), then RANSACs a similarity and keeps the candidate with the most inliers.
A fit is written only with >= `MIN_INLIERS` = 10 inliers and |rotation| <= 30 deg. Both thresholds were set
by the lead from a look at a few hand fits BEFORE the run below; nothing was changed after it.

## 1. Protocol (same truth set and metric as 302b)

- Truth: the 21 hand-fit documents pinned in `tests/golden/hand_fit_docs.sha256` (bytes verified, no auto
  flags). The method never reads a hand document; only the evaluator does, after the method has answered.
- Runner: `fit/matchfit_heldout.py run` (checkpoint `data/matchfit/heldout/results.json`), one pass,
  2026-10-11 ~22:05 CDT. It records EVERY candidate (ground x window) so an accept rule can be read off the
  whole table, not only the best candidate.
- Metrics against the hand similarity (both in the document's size frame, Web Mercator, ground metres):
  corner RMS over the four full-image corners (302b's metric; it magnifies scale and rotation error at the
  sheet corners), and centre error (the plan centre's displacement; what a visitor sees as "where the works
  landed").
- Pass bar from task 304, applied to this method: an accept rule under which every accepted fit is within
  60 m (corner) and at least 5 of 21 are accepted. The owner's bar (2026-10-11): within 100 m is good enough.

## 2. Result (verbatim `fit/matchfit_heldout.py table`, best candidate by inliers per document)

| doc | best ground | window | inliers/matches | rot deg | corner m | centre m |
|---|---|---|---|---|---|---|
| arbor-low n0597 | none | | | | | |
| avebury n0581 | relief | 0.35 | 18/45 | 3.8 | 77.3 | 15.4 |
| aztalan n0182 | aerial | 0.7 | 3/15 | 18.1 | 1318.9 | 403.2 |
| badbury-rings n0132 | OS six-inch | 0.35 | 22/61 | 3.6 | 58.6 | 2.9 |
| bergues (Van Deventer) | relief | 0.25 | 4/67 | -70.0 | 2129.5 | 475.9 |
| berkhamsted (Mackenzie) | relief | 0.5 | 4/53 | -114.4 | 606.6 | 160.0 |
| cadbury-castle 1911 | OS six-inch | 1.0 | 148/689 | 0.9 | 85.3 | 23.3 |
| cahokia 1876 | relief | 0.7 | 7/42 | -18.3 | 1461.3 | 1069.1 |
| calleva n0360 | OS six-inch | 1.0 | 78/809 | -1.3 | 114.4 | 45.5 |
| camp-d-attila 1859 | relief | 1.0 | 12/278 | -4.3 | 138.9 | 48.7 |
| castle-rising (Mackenzie) | relief | 0.25 | 8/29 | 7.4 | 27.7 | 11.0 |
| hembury n0108 | OS six-inch | 0.5 | 45/57 | -0.6 | 88.9 | 55.1 |
| little-solsbury 1911 | OS six-inch | 0.5 | 9/12 | 1.8 | 24.7 | 12.0 |
| maiden-castle (DPLA plan) | relief | 1.0 | 67/578 | 0.7 | 111.4 | 28.3 |
| maiden-castle n0124 | relief | 0.25 | 3/8 | -142.1 | 1469.1 | 123.7 |
| mayburgh-henge | none | | | | | |
| mound-bottom 1923 | relief | 1.0 | 6/29 | -11.9 | 409.1 | 9.4 |
| old-sarum 1761 | relief | 1.0 | 5/80 | 29.3 | 1556.3 | 493.4 |
| old-sarum n0142 | relief | 0.25 | 4/33 | 174.3 | 660.5 | 117.7 |
| serpent-mound S&D XXXV | relief | 0.5 | 5/82 | -27.8 | 862.4 | 143.7 |
| whitley-castle 1853 | OS one-inch | 0.5 | 6/11 | 7.0 | 981.4 | 195.4 |

Accept-rule sweep (`rules`), best-by-inliers candidate over any ground:

| min inliers | accepted | centre <= 100 m | corner <= 100 m | worst centre m | worst corner m |
|---|---|---|---|---|---|
| 5 | 14 | 10 | 6 | 1069 | 1556 |
| 8 | 9 | 9 | 6 | 55 | 139 |
| **10 (pre-set)** | **7** | **7** | **4** | **55** | **139** |
| 15 | 6 | 6 | 4 | 55 | 114 |

## 3. Verdict

- With the pre-set rule (>= 10 inliers), 7 of 21 are accepted and **none is wrong**: every accepted plan
  centre is within 55 m of the hand fit. The three accepted fits over 100 m by the corner metric (calleva 114,
  maiden 111, camp d'Attila 139) are 2-6% scale / 1-7 deg errors on large sheets, not misplacements.
- Task 304's bar (>= 5 accepted, all within 60 m) is met on the centre metric, not on the corner metric
  (worst 139 m). The owner's 100 m bar is met on the centre metric.
- Lowering to >= 8 inliers adds castle-rising and little-solsbury (both within 12 m) with still no wrong
  accept, but that threshold was read off this table, so it is a lead, not a measured result. Keep 10 for
  the line; re-test 8 on the next batch of hand fits.
- Inlier count separates right from wrong cleanly here: every wrong placement has <= 7 inliers. 12 of 21
  documents fall below the bar and go to the Ready-to-fit queue, where the owner finishes by hand. That is the
  cost: about one third of the queue places itself, two thirds still need a person.
- Where it works: OS six-inch sheets (ink vs ink) and clear hillforts on relief. Where it fails: the 1850s US
  plates against relief (aztalan, cahokia, serpent, mound bottom), a Van Deventer town plan, two Mackenzie
  castle plans, Old Sarum's 1761 sketch. Mostly too few matches, not wrong matches; the rejection is right.

## 4. Next (evidence-led, in order)

1. Wire it into the line as the first fitter (tools/site_done.py already does this, uncommitted): accepted ->
   map through the gate and fabrication check as any automatic fit; rejected -> queue.
2. Recall: the windows are always centred on the site box. A two-stage search (coarse match on the whole
   ground, then a 0.35 window CENTRED ON THE COARSE HIT) should raise inliers where the plan is off-centre.
   Measure it on the same 21 before trusting it; the threshold stays 10.
3. Bake-off against `zju-community/matchanything_roma` (the denser, slower sibling) on the same 21 docs and
   the same rule; the 5060 Ti is free for it.
4. The 12 rejected documents here are the test set for 2 and 3; the 7 accepted are not to be re-tuned on.

## 5. Located windows (fit/matchfit2.py, run 2026-10-11 ~22:20 CDT, results data/matchfit/heldout_located/)

Stage 1 matches the whole ground and its centred half; stage 2 re-matches windows of 1.3x / 1.8x / 2.5x the
plan's coarse footprint, centred on the coarse hit. Same 21 documents, same rule (>= 10 inliers):

| variant | accepted | wrong | worst centre m | worst corner m |
|---|---|---|---|---|
| centred windows (section 2) | 7 | 0 | 55 | 139 |
| located windows | 8 | 0 | 54 | 139 |

Gains little-solsbury (9 -> 10 inliers), raises hembury 45 -> 62 and badbury's centre error to 2 m; loses
castle-rising (its only hit was the centred 0.25 window, which this variant does not try). Net +1. The 12
failures are unchanged: too few raw matches on the 1850s US plates against relief and on the town/castle
sketches. Windowing is not the lever for those; the matcher's own recall on that material is. Union of both
window sets is the cheap step (9 of 21 on this table); a different matcher (ROMA; needs the
image-matching-models package, not transformers) is the next real test.

## 6. Queue failure modes the 21 hand fits cannot show (from the line lead's per-site runs, 2026-10-11)

- **Sub-feature plan at whole-site scale.** Aesica, "Befundplan Therme Great-Chesters" (one bath-house, ~30 m):
  13 of 32 inliers on the OS six-inch sheet, rotation 6 deg, residual 2 m, placed ~8x too big over the fields.
  The page check caught it. The inliers lie along one column of the plan: spread ratio 0.054, minor sd 15.6 px
  (`fit/matchfit2.py spread()`); every accepted hand-fit match has ratio >= 0.138 and minor sd >= 30 px.
  Proposed guard for the line: accept only if ratio >= 0.1 and minor sd >= 20 px (passes all 8 accepted, rejects
  Aesica). Measured on 21 + 1, so a lead with one confirming case, not a result.
- **Fabrication "1D ladder" clause fires on real matcher pairs.** Castle Neroche's matcher pairs were refused as a
  ladder: ELoFTR keypoints sit on a coarse grid, so real inliers can be grid-regular. The spread guard above
  catches the degenerate (collinear) case for the right reason; grid-regular but two-dimensional pairs should pass.
  Proposal: for fitter "matcher" docs, replace the ladder clause by the spread guard (line lead's call).

## 7. RoMa bake-off (MatchAnything-RoMa via vismatch, AI box 5060 Ti port 8092; run 2026-10-11 ~22:40 CDT, results data/matchfit/heldout_roma/)

Same 21 documents, same centred windows, same evaluator. RoMa returns ~5000 dense matches per call, so the
ELoFTR count rule means nothing here; the sweep is on inlier FRACTION (RANSAC inliers / matches), best
candidate by fraction. RoMa samples its matches, so counts vary a few percent between calls (180-207 inliers
on four repeats of one pair); this is one run.

| rot rule | min fraction | accepted | centre <= 100 m | corner <= 100 m | worst centre m | worst corner m |
|---|---|---|---|---|---|---|
| abs(rot) <= 30 | 0.1 | 15 | 15 | 9 | 78 | 1003 |
| abs(rot) <= 30 | 0.3 | 9 | 9 | 6 | 53 | 103 |
| within 10 deg of k x 90 | 0.1 | 17 | 17 | 11 | 78 | 1003 |
| **within 10 deg of k x 90** | **0.3** | **11** | **11** | **8** | **53** | **103** |

Readings:
- **Proposed RoMa rule: fraction >= 0.3 and rotation within 10 deg of a multiple of 90 deg: 11 of 21, 0 wrong**
  (centre 7-53 m; corner 16-103 m; scale ratio vs hand 0.90-1.08). ELoFTR's best was 7 (8 located).
- The 90-degree clause exists because three plans are printed sideways on the page (maiden n0124, old-sarum
  n0142 at rot 90.5; whitley at -117 is a wrong-ish one and is still rejected). The clause was motivated by
  this table, so it is a lead; it would also apply to ELoFTR's MAX_ROT_DEG.
- Below 0.3 the centre stays right but the scale drifts: bergues 0.24 (corner 457 m, scale 1.14) and the
  Old Sarum 1761 sketch 0.18 (corner 1003 m). "Within 100 m" at the centre is not enough for a sketch
  stretched to the wrong size; the corner metric is the one to keep for the queue.
- Still rejected, rightly: arbor-low (rot -33, 500 m), aztalan (0.07), cahokia (0.05), the Van Deventer town
  at full scale. US 1850s plates vs relief: serpent-mound now 0.12 / 9 m centre / 78 m corner (a near miss);
  mound-bottom 0.12 / 10 m / 171 m.
- Both the fraction and the rotation rule were read off this table. Treat 11/21 as the ceiling to confirm on
  the next hand-checked fits (the line lead's and the owner's eye checks on queue fits are that test set).
- Cost: RoMa ~4 s per window pair on the 5060 Ti vs ~1 s for ELoFTR; 21 docs took ~14 min.
