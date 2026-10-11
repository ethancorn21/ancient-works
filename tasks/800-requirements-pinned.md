Status: done
# 800: Pin requirements.txt on main (the driver's venv build fails there)
Depends on: none
Touches: requirements.in, requirements.txt

## Goal
The driver rebuilds `.venv` before every test run with `pip install --require-hashes` from
`requirements.txt`. The copy on `main` is the bare unpinned source list (commit e2d4060: 9
unpinned lines — numpy, scipy, pillow, tifffile, pyproj, rasterio, laspy[lazrs], requests,
pyshp — no `==`, no hashes), so the venv build fails on main and on any checkout that has
not received the compiled file (driver note in PROGRESS.md: "ERROR: In --require-hashes
mode, all requirements must have their versions pinned with ==. These do not: ...").
The fully pinned + hashed `requirements.txt` for the same package set already exists on the
agent/c branch (committed at iteration 1, generated with `pip-compile --generate-hashes`)
and is proven buildable: that checkout's `.venv` runs the whole test suite and the
pipeline tools.

## Acceptance criteria
- [x] `main`'s `requirements.txt` is the fully pinned + hashed file (every package `==`-pinned
      with sha256 hashes; zero unpinned lines) and agrees with `requirements.in`
- [x] `pip install --require-hashes -r requirements.txt` into a fresh venv succeeds, and the
      existing test suite runs in that venv

## Hand-over
**Done (2026-10-11, iteration 14).** No new file was needed: agent/a has carried the fully
pinned+hashed `requirements.txt` (blob fda2210: 23 packages, all `==`+sha256, zero unpinned
lines) and `requirements.in` (10 direct packages incl. pytest) since 676a0d4 (iteration 1).
Verified: the `via -r requirements.in` set in `requirements.txt` equals `requirements.in`
exactly; `pip install --require-hashes -r requirements.txt` into a fresh throwaway venv
(`/tmp/aw-800-venv`) succeeded (`pip check` clean) and the whole 12-test suite passes in that
venv (and in the driver's `.venv`).
Why main was still broken: `origin/main:requirements.txt` (93511f2, from e2d4060) is
byte-identical to the agent/a/main merge base 52dd748, so earlier merges never carried my
side's change. Now only my side differs from the base, and the file is in this task's
Touches, so the driver's merge of 800 into main lands the pinned file with no conflict;
agent/c carries the same blob fda2210, so main→c syncs are no-ops for this file. The
driver's 2026-10-10 venv-build failure clears on that merge.
Nothing further to do. If a later task needs a new package: add it to `requirements.in`,
regenerate `requirements.txt` with `pip-compile --generate-hashes` from a throwaway venv
(e.g. `/tmp/aw-pto`), commit both.

## Notes
- The fix is to land the pinned compiled file on main (agent/c already carries it) or to
  regenerate it from `requirements.in` in a throwaway venv (pip-tools in `/tmp/aw-pto`, per
  the PITFALLS entry "The driver's .venv build needs a fully pinned and hashed
  requirements.txt"). Do not add, remove or bump packages: the set in `requirements.in` is
  the contract of the other tasks; if one of them needs a new package, that task adds it to
  `requirements.in` itself.
- Filed by agent c (task 001) from the PROGRESS driver note; verified 2026-10-10:
  `git show origin/main:requirements.txt` has 9 unpinned lines, agent/c's copy has 0.
