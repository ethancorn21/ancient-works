Status: open
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
- [ ] `main`'s `requirements.txt` is the fully pinned + hashed file (every package `==`-pinned
      with sha256 hashes; zero unpinned lines) and agrees with `requirements.in`
- [ ] `pip install --require-hashes -r requirements.txt` into a fresh venv succeeds, and the
      existing test suite runs in that venv

## Notes
- The fix is to land the pinned compiled file on main (agent/c already carries it) or to
  regenerate it from `requirements.in` in a throwaway venv (pip-tools in `/tmp/aw-pto`, per
  the PITFALLS entry "The driver's .venv build needs a fully pinned and hashed
  requirements.txt"). Do not add, remove or bump packages: the set in `requirements.in` is
  the contract of the other tasks; if one of them needs a new package, that task adds it to
  `requirements.in` itself.
- Filed by agent c (task 001) from the PROGRESS driver note; verified 2026-10-10:
  `git show origin/main:requirements.txt` has 9 unpinned lines, agent/c's copy has 0.
