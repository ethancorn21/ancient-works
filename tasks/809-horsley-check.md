Status: in-progress
Depends on: 808
Touches: fit/src_roman_horsley.py, tests/test_src_roman_horsley.py, tests/golden/src_roman_horsley_sample.json, data/commons/files_roman.jsonl, data/commons/classified_roman.jsonl, data/catalog/extras_roman.jsonl

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
- [ ] Full suite (.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py
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

(2026-10-15, iteration 198, agent c) **Boxes 1-3 done and committed (box 3 = this session's commit).** Wrote `tests/test_src_roman_horsley.py` per the 197 spec and ran it alone: **5 passed in 11.87 s, no network** (the autouse no_network fixture raises on any socket connect; the LLM never runs; the real staging/catalog files are sha256-verified untouched inside the negative-control test). The 5 tests: `test_register` (books.BOOKS 5-tuple == the module constants, HAND_FIGS == HORSEY_FIGS, 24 lines / 17 kind-s); `test_check_offline` (exit 0, no join: line, "evidence: 17 rows, 17 pass, 0 fail, 0 no-tie", three exact PASS lines built with `f"{'PASS':4s} {'caption_coords':15s} {site}|{title}"`); `test_join_problems` (== [] + non-vacuous facts: 17 mine / 18 files / 18 classified 1:1 / 9 staged sites all with >=1 picture / every file site in the known-id union); `test_check_negative_controls` (tmp copies of the 5 path constants, real basenames kept so the (e) message reads "in extras.jsonl": (a) cilurni dist_m 48000 -> the exact "stored distance 48000 m does not reproduce (0 m)" FAIL; (b) cilurni title -> "…to WEST CHESTERS." + desc "" -> "the caption does not name '<original>'" FAIL (the classified copy moves with the title so the 1:1 join stays clean and isolates the evidence FAIL); (c) n0236 -> no-such-site = exactly 2 join lines, n0114 cascade = exactly 3 (unknown site + ardoch no-picture + 1:1); (d) the 211-merge three states hermetically: pre-merge (canonical extras minus the 9 staged ids) clean, merged-identical clean, same-id-different-row (canonical ardoch qid Q99999999) -> exactly the (e) line, plus (d-f) pre-merge staged ardoch qid Q39671 (holder stonehenge-q39671, computed by the join's own rule) -> exactly the (f) line); `test_golden_matches_staged` (full dict equality against the module's own _norm/GOLDEN_LEAVES selection, leaf order [114, 185, 236, 278], count 17/17/8).

**Freshly re-verified on the current tree before writing (198):** branch up-to-date with main; --check under the socket-block wrapper: exit 0, zero join: lines, 17/17; all 9 staged roman sites are in the canonical extras.jsonl (none in sites.jsonl) and byte-identical to the staged rows under _canon_norm, so (e) is live and passing; the staging files and the golden are byte-identical to HEAD (files ba6b3893 / classified fa9e270c / extras_roman 2ff61cee / golden af87ec84). **Q4788225 (Ardoch's Wikidata item) is held by NO canonical row on current main - that is why the (f) collision control uses Q39671 (stonehenge), not Ardoch's own QID.**

**Next session - step 4 (box 4): the full suite.** First measure the baseline with NO 809 changes: temporarily move tests/test_src_roman_horsley.py out of tests/ (e.g. to /tmp), run `.venv/bin/python -m pytest tests/ --ignore=tests/test_gate.py -p no:cacheprovider`, then restore the file and re-run with it. "No new reds" = nothing red that (a) fails in the no-809 baseline and (b) is not in that measured baseline (the 241-187/306d-161 precedent; the split baseline 1 failed / 156 passed / 1 skipped is stale - the 207b luguvallium red is RESOLVED on current main, and agent a's in-flight 230/242/810/812/814 work is the only expected red source, so expect 0 reds or only agent-a-attributable reds). COMMIT EVERYTHING before starting either run (PITFALLS: mid-suite working-tree edits fail the integrity snapshot tests). The owner-check tests re-encode docs/site_flow/307d_*.png during a run - if the run dirties them, restore main's bytes in the commit (the 808 done-commit precedent; 816 owns the permanent fix). After a green run: tick box 4, `Status: done`, final commit with this hand-over.

**Do NOT touch:** fit/evidence.py, fit/merge.py, the canonical data files (230 is agent a's), the 207b module/test/golden, docs/lead_roman.md, tests/test_gate.py, agent a's stores (web/data/*, data/merge/, data/db/platefits, docs/site_flow/).
