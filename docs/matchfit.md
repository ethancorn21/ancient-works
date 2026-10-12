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
