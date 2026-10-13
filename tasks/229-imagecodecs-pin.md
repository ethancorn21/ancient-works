Status: done
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
- [x] requirements.in lists imagecodecs, and requirements.txt is the regenerated
      pip-compile --generate-hashes output: `imagecodecs==2026.10.10` pinned with
      its sha256 hash, zero unpinned lines, the `via -r requirements.in` block
      equal to requirements.in, and the diff against the file committed when this
      task starts is the imagecodecs addition only (no other package's version or
      hash moves; if the version pulls a transitive dependency not already
      pinned, that addition is expected and recorded in the decision entry)
- [x] A fresh throwaway venv (e.g. /tmp/aw-229) built from the new requirements.txt
      with `pip install --require-hashes` succeeds with `pip check` clean, and in
      that venv the exact AHN path the build uses works: `aw.fetch_dem` for one of
      the seven sites' boxes (a working-phase network fetch, not a test) returns
      the decoded Float32 grid without
      `ValueError: <PREDICTOR.FLOATINGPOINT: 3> requires the 'imagecodecs' package`
- [x] The PITFALLS entry ("Libraries and frameworks / pillow", "A Float32 DEM (the
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

## Hand-over

(2026-10-13, iteration 235, agent a - **DONE in one session.** Both dependencies were
already terminal: 302a is done and merged (its scikit-image pin is in this branch's
requirements, commit e46f5fd) and 304 is DROPPED (lead note 2026-10-12: superseded by
fit/matchfit.py), so no in-flight task owns requirements.in/.txt anymore (203b/207/306
never touch it) - the prompt's "agent c is working on 304" line was stale against the
file state, and the driver had handed out 229, so I proceeded.

What landed: `imagecodecs==2026.10.10` in requirements.in (pinned there deliberately -
a bare name would resolve to whatever is newest on PyPI at compile time; the notes
forbid bumping, and 2026.10.10 is today's latest and not yanked, so nothing else was
possible); requirements.txt regenerated with pip-compile 7.6.2 (the 800 version) from
/tmp/aw-229 WITHOUT --upgrade, so every existing pin was kept - the diff is only the
imagecodecs block (23 sha256 hashes) plus its `via` note on the already-pinned numpy
block (its one hard dependency; no numba/llvmlite, as the notes predicted). Verified:
(a) a from-scratch venv /tmp/aw-229b from the new file installs with --require-hashes
in 26 s, pip check clean; (b) in that venv `aw.fetch_dem` for the exact utrecht-q803
box (data/sites/utrecht-q803/dem_box.json: 2000x2000) fetched PDOK live in 37 s and
returned the decoded grid - 1.00 finite-nonzero share (build's own >=0.5 bar), median
2.73 m, identical to the cached build dem.npy (0.000 m mean abs diff, corr 1.00000);
(c) negative control in a pillow+tifffile-only scratch venv: the same AHN tile fails
with exactly `ValueError: <PREDICTOR.FLOATINGPOINT: 3> requires the 'imagecodecs'
package` (plus the known-benign GDAL_NODATA tag warning, see dem_sources). Suite:
1 failed (the pre-existing test_fit_queue gesture failure, 307bb baseline) / 155
passed / 1 skipped - no new failures. PITFALLS pillow entry rewritten (Where now says
dem_sources._read_geotiff -> Pillow; the ad-hoc workaround line is gone). The
`Depends on: 302a, 304` line is left as-is (historical); nothing further to do.)
