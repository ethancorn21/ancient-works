Status: open
# 229: Pin `imagecodecs` in requirements - the AHN Float32 DEM decode
Depends on: 302a, 304
Touches: requirements.in, requirements.txt, PITFALLS.md

## Goal
The Dutch AHN DEMs arrive as Float32 rasters from PDOK's WCS service, and
`pipeline/build_site.py:load_dem` decodes them with Pillow through
`aw.fetch_dem` -> `pipeline/dem_sources.fetch`. Pillow decodes the FLOATINGPOINT
predictor only via the `imagecodecs` package (PITFALLS, "Libraries and
frameworks / pillow"): without it every one of the seven AHN-sourced sites fails
to build (amsterdam-q727, alkmaar-q972, enkhuizen-q9918, haarlem-q9920,
rotterdam-q34370, the-hague-q36600, utrecht-q803). imagecodecs 2026.10.10 was
installed ad hoc into the project .venv on 2026-10-12 (211's box-3 build run) and
is in neither requirements.in nor requirements.txt: the driver's in-place .venv
rebuild keeps it for now, but a venv built from scratch off requirements.txt
loses it, and a machine rebuilt from the repo notes can no longer build an AHN
site. This task closes that gap with the standard recipe (task 800's Notes): add
`imagecodecs` to requirements.in, regenerate requirements.txt with
`pip-compile --generate-hashes` from a throwaway venv outside the project,
commit both. It depends on 302a and 304 because both are in flight on
requirements.in/.txt; by the time it runs it adds exactly one package on top of
whatever they landed.

## Acceptance criteria
- [ ] requirements.in lists imagecodecs, and requirements.txt is the regenerated
      pip-compile --generate-hashes output: `imagecodecs==2026.10.10` pinned with
      its sha256 hash, zero unpinned lines, the `via -r requirements.in` block
      equal to requirements.in, and the diff against the file committed when this
      task starts is the imagecodecs addition only (no other package's version or
      hash moves; if the version pulls a transitive dependency not already
      pinned, that addition is expected and recorded in the decision entry)
- [ ] A fresh throwaway venv (e.g. /tmp/aw-229) built from the new requirements.txt
      with `pip install --require-hashes` succeeds with `pip check` clean, and in
      that venv the exact AHN path the build uses works: `aw.fetch_dem` for one of
      the seven sites' boxes (a working-phase network fetch, not a test) returns
      the decoded Float32 grid without
      `ValueError: <PREDICTOR.FLOATINGPOINT: 3> requires the 'imagecodecs' package`
- [ ] The PITFALLS entry ("Libraries and frameworks / pillow", "A Float32 DEM (the
      Dutch AHN) needs ... imagecodecs ...") is corrected to match reality: the
      package is pinned in requirements, and the ad-hoc-install workaround line is
      gone

## Notes
- Pin 2026.10.10 exactly - the version proven in the .venv by all seven AHN sites
  211 built (0 failures). Do not bump to a newer release.
- imagecodecs 2026.10.10's only hard dependency is numpy (already pinned;
  numba/llvmlite are NOT in the .venv), so the regenerated file should add one
  direct package and its hash lines only.
- Regeneration recipe (800): pip-tools in a throwaway venv outside the project
  (e.g. /tmp/aw-229), `pip-compile --generate-hashes -o requirements.txt
  requirements.in`, commit both. The driver builds .venv from requirements.txt
  with `pip install --require-hashes` before every test run - an unhashed or
  changed package fails that install, so fix the file rather than work around it.
- data/raw holds no AHN raw files (the WCS response is decoded in flight; only
  dem.npy persists beside each site.json), so the decode proof is a live fetch in
  the fresh venv, not a replay of a stored file.
- If 302a or 304 land the pin themselves while in flight, this task degenerates to
  verifying their version is 2026.10.10 and correcting the PITFALLS entry -
  finish (or drop, with a note) accordingly.
