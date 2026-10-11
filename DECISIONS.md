# Decisions and dead ends

Your journal: append only, newest at the bottom. When a task is finished, the driver moves its entries verbatim to
DECISIONS-archive.md (search it with grep) and lists the task in an index at the top of this file. Formats:

    ## <date> <task id> DECISION: <the choice>
    Chose X over Y because Z.

    ## <date> <task id> BLOCKER: <short title>
    - Attempt 1: tried A -> failed because B
    - Attempt 2: tried C -> failed because D

A fact that stays true after this task (a tool quirk, an environment limit, a trap in the code) is not a journal
entry: it goes to PITFALLS.md.

The task id is the task file's number, with its letters for a subtask (e.g. 025a).

## 2026-10-10 001 DECISION: the gate judges by metric conjunction, not by one score
Recon spikes (no code in the repo yet; scripts in /tmp, results in the task hand-over): (1) ALL-ink 4-neighbour
ridge contrast on the DEM fails (castle-rising true fit scored worst, -0.653 vs null -0.07); (2) autowalls-extracted
wall template + fit_plate's stroke-normal contrast separates true from 60 m/10°/15% on castle-rising but NOT on
bergues (flat town, ploughed walls: true -0.205 worst), and its one-sidedness lets any template score +0.53 on
hilly cross-site ground; (3) old-map ink proximity is saturated on dense maps. So the gate will combine: pair-
consistency residuals, old-map correlation (spike 4, pending), DEM-vs-search-matched-null where relief is strong.
Chosen over a single relief score because docs/autofit.md finding 2 already proved the relief score has false
peaks; the 4th wrong-fit type (best placement on another site's ground) is constructed to beat any single-score
gate, so evidence must be independent per layer.

## 2026-10-10 001 DECISION: held-out selection and test strategy
Held-out = 8 of the 21 fits by numpy.random.default_rng(20260101).choice over sorted filenames (to be written in
docs/gate.md before the run); the other 13 are the dev set for threshold selection only. Test re-run strategy:
commit per-fit input caches as data/gate/*.npz (DEM, map ink, plate ink, wall template, pairs) so the test is
offline and deterministic; the gate program itself fetches DEMs at runtime when its cache is absent. .npy is
gitignored globally but .npz is not (only data/autofit/*.npz is).

## 2026-10-10 001 BLOCKER: none yet - design iteration, not a repeated failure
Attempts so far are distinct metric experiments (spikes 1-3 failed, spike 4 pending), each with a different cause;
not a stuck blocker. If spike 4 (old-map correlation) also fails to separate the four wrong-fit types, next
candidate: placement-centre-vs-catalog-position + plate-extent-vs-site-box checks for the cross-site type.

## 2026-10-10 001 NOTE: environment
.venv created in this checkout (numpy scipy pillow tifffile pyproj rasterio requests scikit-image). requirements.txt
has no hashes (driver baseline is empty for 001) and lacks scikit-image, which pipeline/autowalls.py needs; if the
gate uses autowalls.extract, requirements.txt (root, outside this task's Touches) must gain skimage and be added
to the task's Touches line first.
