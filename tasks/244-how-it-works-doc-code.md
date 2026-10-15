Status: open
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
- [ ] The section no longer names `fit/batch_us.py --working` (or any `--working`/`--model-json`
      fitting flag), and the Qwen statement matches GOAL point 2's post-retirement division
      (the models never place a drawing or write point pairs; the matcher is the only automatic
      fitter; the models keep find/classify/tie/code).
- [ ] No bullet left claiming a file that exists "does not exist"; the section is either
      verified bullet-by-bullet against the current tree or marked a dated snapshot with the
      pointer to the docs of record.
- [ ] The file's other sections are byte-unchanged (this is an audit-section fix, not a
      re-write of the page docs).

## Notes
- Filed by 239 (it.221, agent a): the retirement falsified the bullet's `--working` mention in
  a present-tense page doc (the docs/batch_us.md/batch_eu.md historical-report exemption from
  239's notes does not apply here). The remaining staleness predates 239 (211/212/230 era), so
  the task covers the section's freshness as a whole rather than a one-line fix.
- 239 also reworded `server/serve.py::_fit_line`'s docstring (the same "no model answer"
  wording) as part of the retirement; no serve.py work is part of this task.
