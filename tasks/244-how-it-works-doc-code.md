Status: done
Depends on: 239
Touches: docs/how-it-works.md

# 244: how-it-works.md's "Doc vs code" audit is stale - reword it for the retired fit pass

## Goal
`docs/how-it-works.md`'s "Doc vs code" section is a point-in-time audit (written around
2026-10-10/11) and is out of date in more than one place:

- the Qwen bullet says "the code uses Qwen through `pipeline/llm.py` (`books.py`,
  `catalog_triage.py`, `fit/batch_us.py --working`)" - `fit/batch_us.py --working` no longer
  exists: 239 retires the vision-model fitting pass (GOAL point 2: the local Qwen models never
  place a drawing and never write point pairs or coordinates; the pretrained matcher is the only
  automatic fitter). `books.py`/`catalog_triage.py` still use Qwen, and the cover search/
  classify phases (212a) keep their model use, so the bullet's point (Qwen keeps its
  non-placement jobs) survives - only the `--working` mention is false now.
- other bullets predate 211/212/230: it says `fit/merge.py` (211) and `fit/cover.py` (212)
  "neither file exists" (both exist and are merged), "the working tree still carries
  uncommitted matcher work" (committed long ago), and it pins queue/item counts that moved
  since (117 entries / "340 open of 341" vs today's files).

Fix the section: reword the Qwen bullet to the post-retirement division (Qwen: the book
pipeline's find/triage plus the cover search/classify; matcher: the only automatic fitter, via
the one-site line), then make the rest of the section truthful - either re-verify each bullet
against the current tree and correct it, or (recommended: the per-task rewrites keep going
stale again) mark the section as a dated snapshot of 2026-10-10/11 with a pointer to the docs
of record (site_flow.md, matchfit.md, gate.md). If re-verifying, check every bullet against
the tree before rewriting it.

## Acceptance criteria
- [x] The section no longer names `fit/batch_us.py --working` (or any `--working`/`--model-json`
      fitting flag), and the Qwen statement matches GOAL point 2's post-retirement division
      (the models never place a drawing or write point pairs; the matcher is the only automatic
      fitter; the models keep find/classify/tie/code).
- [x] No bullet left claiming a file that exists "does not exist"; the section is either
      verified bullet-by-bullet against the current tree or marked a dated snapshot with the
      pointer to the docs of record.
- [x] The file's other sections are byte-unchanged (this is an audit-section fix, not a
      re-write of the page docs).

## Notes
- Filed by 239 (it.221, agent a): the retirement falsified the bullet's `--working` mention in
  a present-tense page doc (the docs/batch_us.md/batch_eu.md historical-report exemption from
  239's notes does not apply here). The remaining staleness predates 239 (211/212/230 era), so
  the task covers the section's freshness as a whole rather than a one-line fix.
- 239 also reworded `server/serve.py::_fit_line`'s docstring (the same "no model answer"
  wording) as part of the retirement; no serve.py work is part of this task.

## Hand-over

(2026-10-14, iteration 229, agent a - done this session; all three boxes ticked and verified, Status: done.)

What was done (one step, docs-only, `docs/how-it-works.md` `## Doc vs code` section):
1. Added a dated-snapshot note under the section header (the task's recommended approach):
   verified against the tree 2026-10-10/11 (the document's commit d3b24b4, 2026-10-11 22:27),
   kept as written, file names and counts are point-in-time (notes `fit/merge.py`/`fit/cover.py`
   exist now); pointers to the docs of record: docs/site_flow.md (one-site line + queues),
   docs/matchfit.md (the matcher), docs/gate.md (the frozen rule).
2. Reworded only the Qwen bullet to the post-retirement division (no `--working`/`--model-json`
   fitting flag anywhere in the section): Qwen via `pipeline/llm.py` = the book pipeline's
   find/triage (`books.py`, `catalog_triage.py`) plus the cover's classification phase (212a's
   one-off `fit/cover_qwen8080.py` on the VM's own vLLM answering Clef's questions, since
   Clef-flash is not running anywhere - its 5060 Ti now serves the matcher); the batch
   modules' vision-model fitting pass is retired (239, 2026-10-13): the models never place a
   drawing and never write point pairs or coordinates - they find, classify and tie pictures
   and write code; the pretrained matcher (`fit/matchfit.py`) is the only automatic fitter,
   run first in the one-site line (`tools/site_done.py`); Clef stopped after the Finder
   bake-off failed (kept from the original bullet).

Facts checked against the tree before writing: docs/PLAN.md:21 still carries the "NOT used by
this project" quote; `fit/cover.py`'s default classifier is Clef-flash via `pipeline/clef.py`
but Clef-flash is not running anywhere (per `fit/cover_qwen8080.py`'s header: the 5060 Ti now
serves the matcher), and the 212a live run used the one-off Qwen3.8-27B on the VM's vLLM
127.0.0.1:8080 answering the same Clef questions; `fit/batch_us.py`'s header confirms the
retirement (GOAL point 2, 2026-10-13); `tools/site_done.py` runs the matcher first; commit
d3b24b4 = 2026-10-11 22:27:07 -0500; docs/matchfit.md, docs/gate.md, docs/site_flow.md exist.

Box verification: (1) `grep -n "working\|model-json" docs/how-it-works.md` -> the only hit is
"working tree" in the kept-as-written bullet at line 205, not a fitting flag; (2) the snapshot
note is in place with the site_flow/matchfit/gate pointers; (3) `git diff` -> only the
`## Doc vs code` section changed (14 insertions, 2 deletions). No test pins this file
(`grep -rn "how-it-works" tests/` empty), so no test impact.

Nothing left to do. If the done claim is rejected: the only debatable detail is the
Clef-flash/5060 Ti phrasing in the Qwen bullet (quoted from `fit/cover_qwen8080.py`'s header);
the snapshot note's "fit/merge.py and fit/cover.py exist now" is verifiable from `ls fit/`.
