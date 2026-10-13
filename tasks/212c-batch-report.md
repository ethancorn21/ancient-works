Status: open
# 212c: docs/batch.md - the final report for the owner
Depends on: 212b
Touches: fit/cover.py, docs/batch.md, tests/test_cover.py

## Goal
The report the owner reads: counts per outcome (fit: hand / matcher / human-saved;
review item; no picture found), a seeded 20-sample of automatic (matcher) fits with a
page URL each for the owner's 18/20 check, and the "no picture found" list with what was
searched per site.

## Acceptance criteria
- [ ] `python3 fit/cover.py report` writes docs/batch.md from the store, seed recorded in the file.
- [ ] Test: the sample is reproducible from the recorded seed; the counts add up to the built-site total.
