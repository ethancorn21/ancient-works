Status: done
Depends on: 808
Touches: fit/src_roman_horsley.py, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl, PITFALLS.md

# 809: Horsley - the offline --check, the golden sample, the no-network test

## Goal
Close the Horsley book: build the module's --check leg (offline: the join over the staged
roman rows - every staged row names an existing or staged site, every new extra site has its
plans - and fit/evidence.py's check over this book's staged rows, from stored fields alone,
no network even for the new extra sites), --golden (tests/golden/src_roman_horsley_sample.
json), and tests/test_src_roman_horsley.py (no network: the no_network socket-blocking
fixture as in tests/test_src_van_deventer.py; the module imported by path via importlib and
register() in-process; the LLM never runs in tests). This makes 207a's moved boxes 4-5
stand on a hermetic, re-runnable check.

## Acceptance criteria
- [x] --check in fit/src_roman_horsley.py, run offline (the socket-block wrapper), passes on
      the staged set: the join holds (every one of this book's 17 staged rows names an
      existing catalog site or a staged extras_roman.jsonl site; every NEW extra site row
      this book created has at least one staged plan row) and fit/evidence.py's check passes
      on all 17 of this book's rows (the 200 evidence field verified offline from the stored
      fields - check_caption / check_book / check_book_caption, per fit/evidence.py).
- [x] --golden writes tests/golden/src_roman_horsley_sample.json: a stable, deterministic
      subset of this book's staged rows (fixed ordering; regenerated only for an intended
      change).
- [x] tests/test_src_roman_horsley.py passes with NO network (the no_network fixture: import
      urllib.request/ssl FIRST, then patch socket.socket.connect + socket.create_connection
      to raise - a naive `socket.socket = fn` breaks the ssl import, PITFALLS): it imports
      fit/src_roman_horsley.py by path via importlib, calls register() in-process, and
      asserts the join, the evidence check over the book's rows, and that the golden sample
      matches the current staged files; the LLM never runs in the test.
- [x] Full suite (.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py
      -p no:cacheprovider): no new reds against the split baseline (1 failed / 156 passed /
      1 skipped; the lone red = agent a's 307d placement test, known pre-existing).

## Notes (operational facts carried from the 207a split, 2026-10-14 iteration 221)

**The --check design (219 step 4):** offline join + fit/evidence.py over the book's rows.
Read fit/evidence.py in full first (it was only skimmed at 220): check_caption (~line 190),
check_book (~265), check_book_caption (~290) - book rows re-derive books_match's one-pair
rule from the row's printed text + the current catalog row at the stored score; only the
runner-up margin stays stored. The join over the roman staging files follows the parent's
mechanics (every row tagged with its book; rows from 207a/207b coexist in the same files -
809 checks the whole staged roman set for the join, but the evidence check and the golden
sample cover this book's rows only).

**Row fixes:** the three staging files are in this task's Touches for ROW FIXES ONLY (a row
808 staged that fails --check gets corrected in place - e.g. distance/named-place fields -
and the fix is recorded in a DECISIONS entry); new rows or drops belong to 808. If a staged
row cannot pass the evidence contract, say so in a DECISIONS entry and propose the fix
here rather than weakening the check.

**The socket-block wrapper (for --check and the test's fixture), as used by 807:**

    import urllib.request, ssl, socket   # FIRST - the ssl import must precede the patch
    def dead(*a, **k): raise RuntimeError("network blocked in this run")
    socket.socket.connect = dead; socket.create_connection = dead

**The validate_book one-liner** (807's Notes) is the same pattern if the test wants the
recall figures; books_lists.validate_book is offline (cached bookreader.json + the A file +
ink() over local triage images).

**Staged state at the split of the parts:** 808 lands first (17 files_roman rows + 17
classified rows + the new extras_roman site rows); the module already documents --check /
--golden in its docstring ("Later legs") - implement per that.

**Suite baseline at the split:** 1 failed / 156 passed / 1 skipped (389 s; the lone red =
agent a's 307d placement test: seed check + /tiles/relief 404, PITFALLS). No test imports
this module yet; re-baseline on the final run.

(Unblocked 2026-10-14, iteration 137, agent c, from the parent 207: same owner lift as
807/808 - DECISIONS 2026-10-14 207. Runs last of the chain.)

## Hand-over

(2026-10-15, iteration 199, agent c) **DONE - all four boxes ticked.** This is the final
hand-over. The book is closed: 207a/808 staged the 17 horsley rows (17 of the 18 staged roman
file rows, 17 of 18 classified, 8 new sites of the 9 staged roman sites), 809 built the
offline --check (whole-set join (a)-(f) + evidence over this book's rows, 17/17), the
deterministic --golden (the 4-tie-flavour leaves 114/185/236/278 + whole-book counts
8/17/17) and the 5-test no-network suite; 199 ran the box-4 A/B.

**Box 4 (199, this session):** the full-suite A/B, both runs on the committed tree
(`.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider`):
baseline with the 809 test file moved out = **3 failed / 183 passed / 1 skipped in 548.7 s**;
with the file restored = **3 failed / 188 passed / 1 skipped in 580.8 s**. The FAILED sets
are byte-identical (diffed): (1) owner_check A - the 307d mid-transition/subpixel flake at
"toolbar scale and turn change the drawing on screen" (242/810/812/814's lane, agent a is on
810/812/814; 816 carries the settle+subpixel recipe); (2) owner_check B - fails only because
A failed in the same invocation (the documented pair dependency, PITFALLS); (3)
maclauchlan (e) - the now()-stamp date skew, below. 188 = 183 + the 5 horsley tests (all
in-run green). No new reds against the measured baseline (the box's definition; the
carried-over split baseline was stale as expected).

**The maclauchlan red (pre-existing in the no-809 baseline - not 809's):** root cause
measured, not just attributed: stage() stamps location_check.checked = now() (the fresh row
carries 2026-10-15), the canonical row carries 230's 2026-10-14 re-stamp, and _canon_norm is
a full-row dump - (e) fires on the date field alone (all 9 staged roman site rows verified
dict-identical to their canonical twins; the fresh-vs-canonical diff is that one field).
Daily and self-healing (green on 10-14, red on 10-15; the 197 "resolved" lasted one day).
It is the same red that made the driver reject 814's done-claim (816's Why section), so it
keeps biting other agents' gates. **Permanent fix filed as two parallel tasks (the lowest
free numbers, one module each, both hermetic, no 230 dependency): 817 = zero the checked
date in the 207b _canon_norm + the date-only-differs-does-not-fire control; 818 = the same
in this book's copied _canon_norm (this module is green today only because its check reads
committed rows - a fresh re-stage after any re-stamp would flake identically).**
fit/merge.py's own full-row norm was deliberately left alone (the 211 merge regenerates
canonical rows from the staged source - a re-stamp is a rewrite, not a conflict; and it is
211/230's module).

**Ops for anyone running suites on this branch until 816 lands:** each full-suite run
re-encoded some of the ten docs/site_flow/307d_*.png (run 1: B_2/B_3/B_4/B_5; run 2:
B_1/B_4/B_5) - main's bytes were restored before each run and in this final commit
(`git checkout main -- docs/site_flow/307d_*.png`; the branch is byte-identical to main on
the goldens, the conflict-free-merge rule). The run logs live at /tmp/809ab/ (the temp dir
outside the project, as the rules allow).
